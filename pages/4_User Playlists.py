import pandas as pd
import streamlit as st

from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_spotify_id_secure
from utils.data_processing import process_track_data
from utils.ui_components import (
    create_download_button,
    display_processing_info,
    display_rate_limit_error
)
from utils.common_operations import get_authenticated_client

def main():
    st.title("📃 Spotify Playlist Info")
    st.caption("Note: this does not work for Spotify generated playlists...")
    user_input = st.text_input("Enter a Spotify playlist URI, URL, or ID")

    if user_input:
        playlist_id = parse_spotify_id_secure(user_input, 'playlist')
        if not playlist_id:
            return

        display_processing_info("Using optimized playlist processing with better rate limit handling")

        # Initialize variables for results
        tracks_df = None
        playlist_name = None
        playlist_image_url = None
        track_count = 0
        
        with st.status("⏳ Fetching playlist...", expanded=True) as status:
            spotify_client = get_authenticated_client()
            if not spotify_client:
                return
            
            try:
                status.update(label="Fetching playlist with optimized pagination...", state="running", expanded=True)
                meta_data, playlist_tracks = spotify_client.fetch_playlist_tracks(playlist_id)
                
                if meta_data and playlist_tracks:
                    playlist_name = meta_data.get("name", "Unknown Playlist")
                    playlist_image_url = meta_data["images"][0]["url"] if meta_data.get("images") else None
                    track_count = len(playlist_tracks)
                    
                    tracks_only = [item.get("track") for item in playlist_tracks if item.get("track")]
                    simplified_data = process_track_data(tracks_only)
                    df = pd.DataFrame(simplified_data)

                    if not df.empty:
                        tracks_df = df
                        status.update(label="✅ Done!", state="complete", expanded=False)
                    else:
                        status.update(label="No track data found.", state="warning", expanded=False)
                else:
                    status.update(label="No tracks found or invalid playlist.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again later", state="error", expanded=False)
                display_rate_limit_error()
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)
        
        # Display results outside the status box
        if tracks_df is not None and playlist_name:
            st.info(f"📊 Playlist contains {track_count} tracks")
            st.dataframe(tracks_df, use_container_width=True, hide_index=True)
            create_download_button(
                df=tracks_df,
                label="📥 Download as Excel",
                file_name="playlist_tracks.xlsx",
                key="download_playlist"
            )
                
        # Display playlist image outside the status box
        if playlist_image_url and playlist_name:
            col1, col2, col3 = st.columns(3)
            with col2:
                try:
                    st.image(playlist_image_url, caption=playlist_name, width=300)
                except:
                    st.write(f"🎵 {playlist_name}")

if __name__ == "__main__":
    main()