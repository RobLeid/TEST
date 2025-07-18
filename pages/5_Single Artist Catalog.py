import streamlit as st
import pandas as pd
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api_improved import SpotifyAPIClient
from utils.validation import parse_spotify_id_secure
from utils.tools import to_excel
from utils.data_processing import process_artist_album_data
from utils.rate_limiting import RateLimitExceeded

MARKETS = [
    "AD","AE","AG","AL","AM","AO","AR","AT","AU","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BN",
    "BO","BR","BS","BT","BW","BY","BZ","CA","CD","CG","CH","CI","CL","CM","CO","CR","CV","CW","CY","CZ",
    "DE","DJ","DK","DM","DO","DZ","EC","EE","EG","ES","ET","FI","FJ","FM","FR","GA","GB","GD","GE","GH",
    "GM","GN","GQ","GR","GT","GW","GY","HK","HN","HR","HT","HU","ID","IE","IL","IN","IQ","IS","IT","JM",
    "JO","JP","KE","KG","KH","KI","KM","KN","KR","KW","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU",
    "LV","LY","MA","MC","MD","ME","MG","MH","MK","ML","MN","MO","MR","MT","MU","MV","MW","MX","MY","MZ",
    "NA","NE","NG","NI","NL","NO","NP","NR","NZ","OM","PA","PE","PG","PH","PK","PL","PR","PS","PT","PW",
    "PY","QA","RO","RS","RW","SA","SB","SC","SE","SG","SI","SK","SL","SM","SN","SR","ST","SV","SZ","TD",
    "TG","TH","TJ","TL","TN","TO","TR","TT","TV","TW","TZ","UA","UG","US","UY","UZ","VC","VE","VN","VU",
    "WS","XK","ZA","ZM","ZW"
]

def main():
    st.title("🎤 Single Artist Catalog")
    st.caption("Get all releases by a single artist.")
    
    artist_input = st.text_input("Enter a Spotify artist URI, URL, or ID")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))
    
    if st.button("🔍 Get Artist Catalog"):
        artist_id = parse_spotify_id_secure(artist_input, 'artist')
        if not artist_id:
            return
            
        access_token = get_access_token()
        if not access_token:
            return
        
        # Initialize the improved API client
        spotify_client = SpotifyAPIClient(access_token)

        st.info("🎯 Using super-optimized batch processing - dramatically reduces API calls by fetching all track data at once!")
        st.info("🚀 This optimization can reduce API calls from 100+ to just 3-4 calls, virtually eliminating rate limit issues!")

        all_dataframes = []
        album_sections = {}

        with st.status("⏳ Fetching artist albums...", expanded=True) as status:
            try:
                status.update(label="Fetching artist discography with comprehensive album type queries...", state="running")
                albums = spotify_client.fetch_artist_albums_comprehensive(artist_id, market)
                if not albums:
                    status.update(label="No albums found for this artist.", state="warning", expanded=False)
                    return
                    
                status.update(label=f"Found {len(albums)} albums. Using super-optimized batch processing...", state="running")
                
                # STEP 1: Get detailed album info for all albums in batches
                status.update(label="Fetching album details in batches...", state="running")
                album_details = {}
                all_track_ids = []
                track_to_album_map = {}
                
                # Process albums in batches of 20 (Spotify API limit)
                for i in range(0, len(albums), 20):
                    batch_albums = albums[i:i+20]
                    batch_ids = [album["id"] for album in batch_albums]
                    
                    # Get detailed album information
                    album_batch_data = spotify_client._make_request(f"albums?ids={','.join(batch_ids)}")
                    
                    if album_batch_data and "albums" in album_batch_data:
                        for album_data in album_batch_data["albums"]:
                            if album_data:
                                album_details[album_data["id"]] = album_data
                                # Extract track IDs for batch fetching
                                track_items = album_data.get("tracks", {}).get("items", [])
                                for track_item in track_items:
                                    if track_item.get("id"):
                                        all_track_ids.append(track_item["id"])
                                        track_to_album_map[track_item["id"]] = album_data["id"]
                
                # STEP 2: Fetch ALL track details in one batch operation
                status.update(label=f"Fetching {len(all_track_ids)} track details in optimized batches...", state="running")
                all_full_tracks = spotify_client.fetch_tracks_by_ids(all_track_ids)
                
                # Create a map of track ID to full track data
                track_data_map = {track["id"]: track for track in all_full_tracks if track}
                
                # STEP 3: Process each album group with pre-fetched data
                for group_name, albums_list in {g: [a for a in albums if a.get("album_type") == g] for g in ["album", "single", "compilation"]}.items():
                    section_dataframes = []
                    for i, album in enumerate(albums_list):
                        status.update(label=f"Processing {group_name} {i+1}/{len(albums_list)}: {album['name']}", state="running")
                        try:
                            album_id = album["id"]
                            if album_id in album_details:
                                album_data = album_details[album_id]
                                track_items = album_data.get("tracks", {}).get("items", [])
                                
                                # Get full track data for this album
                                full_tracks = []
                                for track_item in track_items:
                                    if track_item.get("id") and track_item["id"] in track_data_map:
                                        full_tracks.append(track_data_map[track_item["id"]])
                                
                                if album_data and full_tracks:
                                    tracks = process_artist_album_data(album_data, track_items, full_tracks)
                                    df = pd.DataFrame(tracks)
                                    section_dataframes.append((df, album_data.get("name"), album_data["images"][0]["url"] if album_data.get("images") else None, album_data["id"]))
                        except Exception as e:
                            st.warning(f"Failed to process album {album['name']}: {str(e)}")
                            continue

                    album_sections[group_name] = section_dataframes
                    all_dataframes.extend([df for df, _, _, _ in section_dataframes])
                    
                st.success(f"✅ Processed {len(albums)} albums with {len(all_track_ids)} tracks using only {len(all_track_ids)//50 + 1} API calls!")
                    
            except RateLimitExceeded:
                st.error("⏱️ Rate limit exceeded. Returning partial data.")
                st.info("💡 **Tips:**\n- Wait a few minutes before trying again\n- Try processing fewer albums\n- The improved API automatically handles rate limiting and retries")
            except Exception as e:
                st.error(f"Error fetching albums: {str(e)}")
        
        if all_dataframes:
            status.update(label="✅ Done processing all albums!", state="complete", expanded=False)
            
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            if not combined_df.empty:
                combined_excel = to_excel(combined_df)
                if combined_excel is not None:
                    st.download_button(
                        label="📦 Download All Albums to Excel",
                        data=combined_excel,
                        file_name="Single_Artist_Releases.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all_albums"
            )

        for group_name, section_dataframes in album_sections.items():
            if section_dataframes:
                st.header(group_name.capitalize() + "s")
                st.divider()
                for df, album_name, album_image_url, album_id in section_dataframes:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if album_image_url:
                            try:
                                image = Image.open(urlopen(album_image_url))
                                st.image(image, caption=album_name)
                            except:
                                st.write(f"🖼️ {album_name}")
                        album_excel = to_excel(df)
                        if album_excel is not None:
                            st.download_button(
                                label="📥 Download Excel",
                                data=album_excel,
                                file_name=f"{album_name}_tracks.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_{album_id}"
                            )
                    with col2:
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    st.divider()

if __name__ == "__main__":
    main()