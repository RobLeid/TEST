import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api_improved import SpotifyAPIClient
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_spotify_id_secure
from utils.tools import to_excel
from utils.data_processing import process_track_data

def main():
    st.title("📃 Spotify Playlist Info")
    st.caption("Note: this does not work for Spotify generated playlists...")
    user_input = st.text_input("Enter a Spotify playlist URI, URL, or ID")

    if user_input:
        playlist_id = parse_spotify_id_secure(user_input, 'playlist')
        if not playlist_id:
            return

        st.info("🎯 Using optimized playlist processing with better rate limit handling")

        # Initialize variables for results
        tracks_df = None
        excel_data = None
        playlist_name = None
        playlist_image_url = None
        track_count = 0
        
        with st.status("⏳ Fetching playlist...", expanded=True) as status:
            access_token = get_access_token()
            if not access_token:
                status.update(label="Authentication failed.", state="error", expanded=False)
                return
            
            # Initialize the improved API client
            spotify_client = SpotifyAPIClient(access_token)
            
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
                        excel_data = to_excel(df)
                        status.update(label="✅ Done!", state="complete", expanded=False)
                    else:
                        status.update(label="No track data found.", state="warning", expanded=False)
                else:
                    status.update(label="No tracks found or invalid playlist.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again later", state="error", expanded=False)
                st.error("**Rate limit hit!** The optimized version uses maximum batch sizes and intelligent retry logic.")
                st.info("💡 **Tips:**\n- Wait a few minutes before trying again\n- Try a smaller playlist\n- The improved error handling automatically retries with delays")
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)
        
        # Display results outside the status box
        if tracks_df is not None and playlist_name:
            st.info(f"📊 Playlist contains {track_count} tracks")
            st.dataframe(tracks_df, use_container_width=True, hide_index=True)
            if excel_data is not None:
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name="playlist_tracks.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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