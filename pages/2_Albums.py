import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api_improved import SpotifyAPIClient
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_multi_spotify_ids_secure
from utils.tools import to_excel
from utils.data_processing import process_album_track_data

def main():
    st.title("💿 Spotify Album Info")
    user_input = st.text_area("Enter multiple Spotify album URIs, URLs, or IDs (one per line)")
    
    if st.button("🔍 Get Album Info"):
        if not user_input:
            st.warning("Please enter at least one album ID, URI, or URL.")
            return
            
        album_ids = parse_multi_spotify_ids_secure(user_input, 'album')
        if not album_ids:
            st.warning("No valid album IDs found.")
            return

        # Show processing info
        st.info(f"🎯 Processing {len(album_ids)} albums with super-optimized batch processing")
        st.info(f"🚀 This optimization reduces API calls from {len(album_ids)*2}+ to just 3-4 calls, virtually eliminating rate limit issues!")

        access_token = get_access_token()
        if not access_token:
            return
        
        # Initialize the improved API client
        spotify_client = SpotifyAPIClient(access_token)
        
        all_dataframes = []
        album_details_list = []

        with st.status("⏳ Processing albums...", expanded=True) as status:
            try:
                # STEP 1: Batch fetch all album details
                status.update(label="Fetching album details in super-optimized batches...", state="running")
                album_details_map = {}
                all_track_ids = []
                track_to_album_map = {}
                
                # Process albums in batches of 20 (Spotify API limit)
                for i in range(0, len(album_ids), 20):
                    batch_ids = album_ids[i:i+20]
                    
                    # Get detailed album information in one API call
                    album_batch_data = spotify_client._make_request(f"albums?ids={','.join(batch_ids)}")
                    
                    if album_batch_data and "albums" in album_batch_data:
                        for album_data in album_batch_data["albums"]:
                            if album_data:
                                album_details_map[album_data["id"]] = album_data
                                # Extract track IDs for batch fetching
                                track_items = album_data.get("tracks", {}).get("items", [])
                                for track_item in track_items:
                                    if track_item.get("id"):
                                        all_track_ids.append(track_item["id"])
                                        track_to_album_map[track_item["id"]] = album_data["id"]
                
                # STEP 2: Batch fetch ALL track details at once
                status.update(label=f"Fetching {len(all_track_ids)} track details in optimized batches...", state="running")
                all_full_tracks = spotify_client.fetch_tracks_by_ids(all_track_ids)
                
                # Create a map of track ID to full track data
                track_data_map = {track["id"]: track for track in all_full_tracks if track}
                
                # STEP 3: Process albums with pre-fetched data
                status.update(label="Processing albums with pre-fetched data...", state="running")
                for i, album_id in enumerate(album_ids):
                    status.update(label=f"Processing album {i+1}/{len(album_ids)} with pre-fetched data...", state="running")
                    
                    if album_id in album_details_map:
                        album_data = album_details_map[album_id]
                        track_items = album_data.get("tracks", {}).get("items", [])
                        
                        # Get full track data for this album
                        full_tracks = []
                        for track_item in track_items:
                            if track_item.get("id") and track_item["id"] in track_data_map:
                                full_tracks.append(track_data_map[track_item["id"]])
                        
                        if album_data and full_tracks:
                            simplified_data = process_album_track_data(album_data, track_items, full_tracks)
                            df = pd.DataFrame(simplified_data)
                            all_dataframes.append(df)
                            album_details_list.append({
                                "df": df,
                                "name": album_data.get("name", "Unknown Album"),
                                "image_url": album_data["images"][0]["url"] if album_data.get("images") else None,
                                "id": album_data["id"]
                            })
                        else:
                            st.warning(f"⚠️ Failed to process album {i+1} - no track data found")
                    else:
                        st.warning(f"⚠️ Failed to process album {i+1} - album not found")
                
                status.update(label=f"✅ Optimized processing complete! Used only {len(all_track_ids)//50 + len(album_ids)//20 + 2} API calls instead of {len(album_ids)*2}+", state="complete", expanded=False)
                        
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - returning partial results", state="error", expanded=False)
                st.error("**Rate limit hit!** The optimized version uses better retry logic, but Spotify's API has usage limits.")
                st.info("💡 **Tips:** Wait a few minutes, then try fewer albums at once")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if all_dataframes:
            status.update(label="✅ Done processing albums!", state="complete", expanded=False)
            
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            if not combined_df.empty:
                global_excel = to_excel(combined_df)
                if global_excel is not None:
                    st.download_button(
                        label="📦 Download All Albums to Excel",
                        data=global_excel,
                        file_name="All_Albums_Tracks.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all_albums"
            )

            for album_details in album_details_list:
                st.divider()
                col1, col2 = st.columns([1, 3])
                with col1:
                    if album_details["image_url"]:
                        try:
                            image = Image.open(urlopen(album_details["image_url"]))
                            st.image(image, caption=album_details["name"])
                        except:
                            st.write(f"🖼️ {album_details['name']}")
                    album_excel = to_excel(album_details["df"])
                    if album_excel is not None:
                        st.download_button(
                            label=f"📥 Download Excel",
                            data=album_excel,
                            file_name=f"{album_details['name']}_tracks.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{album_details['id']}"
                        )
                with col2:
                    st.dataframe(album_details["df"], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()