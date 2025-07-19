import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

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
    st.title("🎤 Spotify Artist Top Tracks")
    user_input = st.text_input("Enter a Spotify artist URI, URL, or ID")

    if user_input:
        artist_id = parse_spotify_id_secure(user_input, 'artist')
        if not artist_id:
            return

        display_processing_info("Using optimized artist processing with better rate limit handling")

        # Initialize variables for results
        tracks_df = None
        artist_name = None
        artist_image_url = None
        
        with st.status("⏳ Fetching artist info...", expanded=True) as status:
            spotify_client = get_authenticated_client()
            if not spotify_client:
                return
            
            try:
                status.update(label="Fetching artist data with improved retry logic...", state="running", expanded=True)
                artist_data, top_tracks = spotify_client.fetch_artist_metadata_and_top_tracks(artist_id, market="US")

                if artist_data and top_tracks:
                    artist_name = artist_data.get("name", "Unknown Artist")
                    artist_image_url = artist_data["images"][0]["url"] if artist_data.get("images") else None
                    
                    simplified_data = process_track_data(top_tracks)
                    df = pd.DataFrame(simplified_data)

                    if not df.empty:
                        tracks_df = df
                        status.update(label="✅ Done!", state="complete", expanded=False)
                    else:
                        status.update(label="No track data found.", state="warning", expanded=False)
                else:
                    status.update(label="No top tracks found or invalid artist.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again later", state="error", expanded=False)
                display_rate_limit_error()
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)
        
        # Display results outside the status box
        if tracks_df is not None and artist_name:
            st.info(f"📊 Found {len(tracks_df)} top tracks for {artist_name}")
            st.dataframe(tracks_df, use_container_width=True, hide_index=True)
            create_download_button(
                df=tracks_df,
                label="📥 Download as Excel",
                file_name="artist_top_tracks.xlsx",
                key="download_top_tracks"
            )
                
        # Display artist image outside the status box
        if artist_image_url and artist_name:
            col1, col2, col3 = st.columns(3)
            with col2:
                try:
                    image = Image.open(urlopen(artist_image_url))
                    st.image(image, caption=artist_name, width=300)
                except:
                    st.write(f"🎤 {artist_name}")

if __name__ == "__main__":
    main()