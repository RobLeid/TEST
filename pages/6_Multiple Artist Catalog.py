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
    display_rate_limit_error,
    display_album_row
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

<<<<<<< Updated upstream
        # Initialize the improved API client
        spotify_client = SpotifyAPIClient(access_token)

        # Show processing info
        st.info(f"🎯 Processing {len(artist_ids)} artists with super-optimized batch processing")
        st.info("💡 Uses maximum batch sizes: 50 for tracks, 20 for albums to minimize API calls")
=======
        display_processing_info(f"Processing {len(artist_ids)} artists...")
>>>>>>> Stashed changes

        all_data = []
        all_dataframes = []
        album_sections = {}
        start_time = time.time()

<<<<<<< Updated upstream
        # Create a single status container that will be updated
        status_container = st.empty()
        
        with status_container.container():
            with st.status("⏳ Processing multiple artists...", expanded=True) as status:
                try:
                    status.update(label="Starting comprehensive batch processing for multiple artists...", state="running")
                    results = spotify_client.fetch_multiple_artists_catalogs(
                        artist_ids, market
                    )

                    total_albums = 0
                    total_tracks = 0
                    total_failed = 0
                    processed_albums = 0

                    status.update(label="Analyzing artist catalog data with optimized batch processing...", state="running")

                    for i, (artist_id, artist_data) in enumerate(results.items(), 1):
                        albums = artist_data['albums']
                        album_data = artist_data['album_data']
                        failed_albums = artist_data['failed_albums']

                        total_albums += len(albums)
                        total_failed += len(failed_albums)

                        status.update(
                            label=f"Processing artist {i}/{len(artist_ids)} - Found {len(albums)} albums, analyzing tracks...",
                            state="running"
                        )

                        for j, album in enumerate(albums):
                            album_id = album["id"]
                            processed_albums += 1
                            
                            status.update(
                                label=f"Artist {i}/{len(artist_ids)} - Album {j+1}/{len(albums)}: {album.get('name', 'Unknown Album')}",
                                state="running"
                            )

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
                    else:
                        status.update(label=status_message, state="complete", expanded=False)

                except RateLimitExceeded:
                    elapsed = time.time() - start_time
                    status.update(label=f"❌ Rate limit exceeded - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)
                    st.error("⚠️ Rate limit exceeded after maximum retries. Returning partial data collected so far.")
                    st.info("💡 **The optimized version:**\n- Uses maximum batch sizes to minimize requests\n- Intelligent retry logic with exponential backoff\n- Processes multiple artists efficiently")
                except Exception as e:
                    elapsed = time.time() - start_time
                    status.update(label=f"❌ Error occurred - returning partial data ({elapsed:.2f}s)", state="error", expanded=False)
                    st.error(f"❌ Unexpected error: {e}")

        # Clear the status container when processing is complete
        if all_data:
            status_container.empty()
            if total_failed > 0:
                st.warning(f"⚠️ {total_failed} albums failed to process due to API limits or errors.")

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
=======
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
                                
                                # Create dataframe for this album
                                df = pd.DataFrame(tracks)
                                all_dataframes.append(df)
                                
                                # Group by album type for display
                                album_type = album.get("album_type", "album")
                                if album_type not in album_sections:
                                    album_sections[album_type] = []
                                
                                album_sections[album_type].append((
                                    df,
                                    album_data.get("name"),
                                    album_data["images"][0]["url"] if album_data.get("images") else None,
                                    album_data["id"]
                                ))
                
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

        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            if not combined_df.empty:
                create_download_button(
                    df=combined_df,
                    label=f"📦 Download All Albums to Excel ({len(all_data)} tracks)",
                    file_name=f"Multiple_Artists_Releases_{len(artist_ids)}_artists.xlsx",
                    key="download_all_albums"
                )
                
                # Display albums by type (already grouped during processing)
                for group_name, section_dataframes in album_sections.items():
                    if section_dataframes:
                        st.header(group_name.capitalize() + "s")
                        st.divider()
                        for album_df, album_name, album_image_url, album_id in section_dataframes:
                            album_data = {
                                "name": album_name,
                                "images": [{"url": album_image_url}] if album_image_url else []
                            }
                            display_album_row(album_data, album_df, album_id)
>>>>>>> Stashed changes

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
