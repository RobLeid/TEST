import streamlit as st
import pandas as pd
import time
from utils.auth import get_access_token
from utils.api_improved import SpotifyAPIClient
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_multi_spotify_ids_secure
from utils.tools import to_excel
from utils.data_processing import process_artist_album_data

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
    st.title("🎤 Multiple Artist Catalog")
    
    artist_input = st.text_area("Enter Spotify artist URIs, URLs, or IDs (one per line)")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))

    if st.button("🔍 Process Artists"):
        artist_ids = parse_multi_spotify_ids_secure(artist_input, 'artist')
        if not artist_ids:
            st.error("Please enter at least one valid artist ID.")
            return

        access_token = get_access_token()
        if not access_token:
            return
        
        # Initialize the improved API client
        spotify_client = SpotifyAPIClient(access_token)
            
        # Show processing info
        st.info(f"🎯 Processing {len(artist_ids)} artists with super-optimized batch processing")
        st.info("💡 Uses maximum batch sizes: 50 for tracks, 20 for albums to minimize API calls")
        
        all_data = []
        start_time = time.time()

        with st.status("⏳ Processing with optimized batching...", expanded=True) as status:
            try:
                status.update(label="Starting super-optimized batch processing...", state="running")
                results = spotify_client.fetch_multiple_artists_catalogs(
                    artist_ids, market
                )
                
                total_albums = 0
                total_tracks = 0
                total_failed = 0
                
                status.update(label="Processing artist data...", state="running")
                
                for i, (artist_id, artist_data) in enumerate(results.items(), 1):
                    albums = artist_data['albums']
                    album_data = artist_data['album_data']
                    failed_albums = artist_data['failed_albums']
                    
                    total_albums += len(albums)
                    total_failed += len(failed_albums)
                    
                    status.update(
                        label=f"Processing artist {i}/{len(artist_ids)} - {len(albums)} albums found...", 
                        state="running"
                    )
                    
                    for album in albums:
                        album_id = album["id"]
                        
                        if album_id in album_data:
                            album_info = album_data[album_id]
                            track_items = album_info.get("tracks", {}).get("items", [])
                            
                            full_tracks = []
                            for track_item in track_items:
                                for track in artist_data['tracks']:
                                    if track and track.get('id') == track_item.get('id'):
                                        full_tracks.append(track)
                                        break
                                else:
                                    full_tracks.append(None)
                            
                            valid_pairs = [(item, full) for item, full in zip(track_items, full_tracks) if full is not None]
                            
                            if valid_pairs:
                                valid_track_items, valid_full_tracks = zip(*valid_pairs)
                                tracks = process_artist_album_data(album_info, valid_track_items, valid_full_tracks)
                                all_data.extend(tracks)
                                total_tracks += len(tracks)
                
                elapsed = time.time() - start_time
                
                status_message = f"✅ Completed! Processed {len(artist_ids)} artist(s), {total_albums} albums, {total_tracks} tracks in {elapsed:.2f}s"
                if total_failed > 0:
                    status_message += f" ({total_failed} albums failed)"
                    status.update(label=status_message, state="complete", expanded=False)
                    st.warning(f"⚠️ {total_failed} albums failed to process due to API limits or errors.")
                else:
                    status.update(label=status_message, state="complete", expanded=False)
                
            except RateLimitExceeded:
                elapsed = time.time() - start_time
                st.error("⚠️ Rate limit exceeded after maximum retries. Returning partial data collected so far.")
                st.info("💡 **The optimized version:**\n- Uses maximum batch sizes to minimize requests\n- Intelligent retry logic with exponential backoff\n- Processes multiple artists efficiently")
                status.update(label=f"❌ Rate limit exceeded - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)
            except Exception as e:
                elapsed = time.time() - start_time
                st.error(f"❌ Unexpected error: {e}")
                status.update(label=f"❌ Error occurred - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)

        if all_data:
            df = pd.DataFrame(all_data)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                excel_data = to_excel(df)
                if excel_data is not None:
                    st.download_button(
                        label=f"📥 Download Excel File ({len(all_data)} tracks)",
                        data=excel_data,
                        file_name=f"Multiple_Artists_Releases_{len(artist_ids)}_artists.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.warning("No track data to display")
                
        else:
            st.error("❌ No data was successfully retrieved. This could be due to:")
            st.markdown("""
            - Invalid artist IDs
            - Severe API rate limiting (the optimized version uses maximum batch sizes and intelligent retries)
            - Network connectivity issues
            - Artists with no available releases in the selected market
            """)

if __name__ == "__main__":
    main()