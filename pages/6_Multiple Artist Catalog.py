import streamlit as st
import pandas as pd
import time
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_multi_spotify_ids_secure
from utils.data_processing import process_artist_album_data
from utils.constants import MARKETS
from utils.ui_components import (
    create_download_button,
    display_processing_info,
    display_rate_limit_error
)
from utils.common_operations import get_authenticated_client

def main():
    st.title("🎤 Multiple Artist Catalog")

    artist_input = st.text_area("Enter Spotify artist URIs, URLs, or IDs (one per line)")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))

    if st.button("🔍 Process Artists"):
        artist_ids = parse_multi_spotify_ids_secure(artist_input, 'artist')
        if not artist_ids:
            st.error("Please enter at least one valid artist ID.")
            return

        spotify_client = get_authenticated_client()
        if not spotify_client:
            return

        display_processing_info(f"Processing {len(artist_ids)} artists...")

        all_data = []
        start_time = time.time()

        with st.status("⏳ Processing multiple artists...", expanded=False) as status:
            try:
                # Process each artist sequentially (like Single Artist Catalog does)
                for artist_idx, artist_id in enumerate(artist_ids, 1):
                    status.update(label=f"Processing artist {artist_idx}/{len(artist_ids)}: {artist_id}", state="running")
                    
                    # Fetch albums for this artist using the same method as Single Artist Catalog
                    albums = spotify_client.fetch_artist_albums_comprehensive(artist_id, market)
                    if not albums:
                        st.warning(f"No albums found for artist {artist_id}")
                        continue
                    
                    status.update(label=f"Artist {artist_idx}: Found {len(albums)} albums...", state="running")
                    
                    # Get detailed album info for all albums in batches (same as Single Artist)
                    album_details = {}
                    all_track_ids = []
                    track_to_album_map = {}
                    
                    # Process albums in batches of 20
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
                    
                    if not all_track_ids:
                        st.warning(f"No tracks found for artist {artist_id}")
                        continue
                    
                    # Fetch ALL track details in batch operation
                    status.update(label=f"Artist {artist_idx}: Fetching {len(all_track_ids)} track details...", state="running")
                    
                    def update_track_status(message):
                        status.update(label=f"Artist {artist_idx}: {message}", state="running")
                    
                    all_full_tracks = spotify_client.fetch_tracks_by_ids(all_track_ids, status_callback=update_track_status)
                    
                    # Create a map of track ID to full track data
                    track_data_map = {track["id"]: track for track in all_full_tracks if track}
                    
                    # Process each album with pre-fetched data
                    for album in albums:
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
                                all_data.extend(tracks)
                                
                                # Just add to all_data for bulk download
                                # No individual dataframes needed for bulk operation
                
                elapsed = time.time() - start_time
                status_message = f"✅ Completed! Processed {len(artist_ids)} artist(s), {len(all_data)} tracks in {elapsed:.2f}s"
                status.update(label=status_message, state="complete", expanded=False)

            except RateLimitExceeded:
                elapsed = time.time() - start_time
                display_rate_limit_error()
                status.update(label=f"❌ Rate limit exceeded - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)
            except Exception as e:
                elapsed = time.time() - start_time
                st.error(f"❌ Unexpected error: {e}")
                status.update(label=f"❌ Error occurred - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)

        if all_data:
            # Create summary statistics
            df = pd.DataFrame(all_data)
            
            if not df.empty:
                # Display summary information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Artists", len(artist_ids))
                with col2:
                    st.metric("Total Tracks", len(df))
                with col3:
                    if 'elapsed' in locals():
                        st.metric("Processing Time", f"{elapsed:.2f}s")
                    else:
                        st.metric("Processing Time", "N/A")
                
                # Show summary by artist
                st.subheader("📊 Summary by Artist")
                artist_summary = df.groupby('Artist').agg({
                    'Track': 'count',
                    'Album': 'nunique'
                }).rename(columns={'Track': 'Total Tracks', 'Album': 'Total Albums'})
                st.dataframe(artist_summary, use_container_width=True)
                
                # Single download button for all data
                create_download_button(
                    df=df,
                    label=f"📦 Download All Data to Excel ({len(df)} tracks)",
                    file_name=f"Multiple_Artists_Releases_{len(artist_ids)}_artists.xlsx",
                    key="download_all_albums"
                )

        else:
            st.error("❌ No data was successfully retrieved. This could be due to:")
            st.markdown("""
            - Invalid artist IDs
            - API rate limiting
            - Network connectivity issues
            - Artists with no available releases in the selected market
            - Check the warnings above for specific issues with each artist
            """)

if __name__ == "__main__":
    main()
