import streamlit as st
import pandas as pd

from utils.validation import parse_spotify_id_secure
from utils.data_processing import process_artist_album_data
from utils.rate_limiting import RateLimitExceeded
from utils.constants import MARKETS
from utils.ui_components import (
    create_download_button,
    display_album_row,
    display_rate_limit_error
)
from utils.common_operations import get_authenticated_client

def main():
    st.title("🎤 Single Artist Catalog")
    st.caption("Get all releases by a single artist.")

    artist_input = st.text_input("Enter a Spotify artist URI, URL, or ID")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))

    if st.button("🔍 Get Artist Catalog"):
        artist_id = parse_spotify_id_secure(artist_input, 'artist')
        if not artist_id:
            return
<<<<<<< Updated upstream

        access_token = get_access_token()
        if not access_token:
            return

        # Initialize the improved API client
        spotify_client = SpotifyAPIClient(access_token)

        all_dataframes = []
        album_sections = {}

        # Create a single status container that will be updated
        status_container = st.empty()
        
        with status_container.container():
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
                    batch_count = (len(albums) + 19) // 20
                    for i in range(0, len(albums), 20):
                        current_batch = (i // 20) + 1
                        batch_albums = albums[i:i+20]
                        batch_ids = [album["id"] for album in batch_albums]
                        
                        status.update(label=f"Fetching album details batch {current_batch}/{batch_count}...", state="running")

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

                    status.update(label=f"✅ Processed {len(albums)} albums with {len(all_track_ids)} tracks using optimized batching!", state="complete", expanded=False)

                except RateLimitExceeded:
                    status.update(label="⏱️ Rate limit exceeded - returning partial data", state="error", expanded=False)
                    st.error("⏱️ Rate limit exceeded. Returning partial data.")
                    st.info("💡 **Tips:**\n- Wait a few minutes before trying again\n- Try processing fewer albums\n- The improved API automatically handles rate limiting and retries")
                except Exception as e:
                    status.update(label=f"❌ Error occurred: {str(e)}", state="error", expanded=False)
                    st.error(f"Error fetching albums: {str(e)}")

        if all_dataframes:
            # Clear the status container since we're done
            status_container.empty()
=======

        spotify_client = get_authenticated_client()
        if not spotify_client:
            return

        all_dataframes = []
        album_sections = {}

        with st.status("⏳ Fetching artist albums...", expanded=False) as status:
            try:
                status.update(label="Fetching artist discography...", state="running")
                albums = spotify_client.fetch_artist_albums_comprehensive(artist_id, market)
                if not albums:
                    status.update(label="No albums found for this artist.", state="warning", expanded=False)
                    return

                status.update(label=f"Found {len(albums)} albums...", state="running")

                # STEP 1: Get detailed album info for all albums in batches
                status.update(label="Fetching album details...", state="running")
                album_details = {}
                all_track_ids = []
                track_to_album_map = {}

                # Process albums in batches of 20 (Spotify API limit)
                total_batches = (len(albums) + 19) // 20  # Calculate total batches
                for batch_num, i in enumerate(range(0, len(albums), 20), 1):
                    status.update(label=f"Processing album batch {batch_num}/{total_batches}...", state="running")
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
                track_batches = (len(all_track_ids) + 49) // 50  # Calculate total track batches (50 per batch)
                status.update(label=f"Fetching {len(all_track_ids)} track details in {track_batches} batches...", state="running")
                
                def update_track_status(message):
                    status.update(label=message, state="running")
                
                all_full_tracks = spotify_client.fetch_tracks_by_ids(all_track_ids, status_callback=update_track_status)

                # Create a map of track ID to full track data
                track_data_map = {track["id"]: track for track in all_full_tracks if track}

                # STEP 3: Process each album group with pre-fetched data
                groups_to_process = {g: [a for a in albums if a.get("album_type") == g] for g in ["album", "single", "compilation"]}
                groups_to_process = {k: v for k, v in groups_to_process.items() if v}  # Remove empty groups
                
                for group_idx, (group_name, albums_list) in enumerate(groups_to_process.items(), 1):
                    status.update(label=f"Processing {group_name}s ({group_idx}/{len(groups_to_process)} groups, {len(albums_list)} items)...", state="running")
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
                display_rate_limit_error()
            except Exception as e:
                st.error(f"Error fetching albums: {str(e)}")

        if all_dataframes:
            status.update(label="✅ Done processing all albums!", state="complete", expanded=False)
>>>>>>> Stashed changes

            combined_df = pd.concat(all_dataframes, ignore_index=True)
            if not combined_df.empty:
                create_download_button(
                    df=combined_df,
                    label="📦 Download All Albums to Excel",
                    file_name="Single_Artist_Releases.xlsx",
                    key="download_all_albums"
                )

        for group_name, section_dataframes in album_sections.items():
            if section_dataframes:
                st.header(group_name.capitalize() + "s")
                st.divider()
                for df, album_name, album_image_url, album_id in section_dataframes:
                    album_data = {
                        "name": album_name,
                        "images": [{"url": album_image_url}] if album_image_url else []
                    }
                    display_album_row(album_data, df, album_id)

if __name__ == "__main__":
    main()
