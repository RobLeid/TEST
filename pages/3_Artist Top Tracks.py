import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api import fetch_artist_metadata_and_top_tracks_optimized, RateLimitExceeded
from utils.parsing import parse_spotify_id
from utils.tools import to_excel
from utils.data_processing import process_track_data

def main():
    st.title("🎤 Spotify Artist Top Tracks")
    user_input = st.text_input("Enter a Spotify artist URI, URL, or ID")

    if user_input:
        artist_id = parse_spotify_id(user_input, 'artist')
        if not artist_id:
            return

        st.info("🎯 Using optimized artist processing with better rate limit handling")

        with st.status("⏳ Fetching artist info...", expanded=True) as status:
            access_token = get_access_token()
            if not access_token:
                status.update(label="Authentication failed.", state="error", expanded=False)
                return
            
            try:
                status.update(label="Fetching artist data with improved retry logic...", state="running", expanded=True)
                artist_data, top_tracks = fetch_artist_metadata_and_top_tracks_optimized(artist_id, access_token, market="US", max_retries=5)

                if artist_data and top_tracks:
                    artist_name = artist_data.get("name", "Unknown Artist")
                    artist_image_url = artist_data["images"][0]["url"] if artist_data.get("images") else None
                    
                    # Show artist info
                    st.info(f"📊 Found {len(top_tracks)} top tracks for {artist_name}")
                    
                    simplified_data = process_track_data(top_tracks)
                    df = pd.DataFrame(simplified_data)

                    st.dataframe(df, use_container_width=True, hide_index=True)
                    excel_data = to_excel(df)
                    st.download_button(
                        label="📥 Download as Excel",
                        data=excel_data,
                        file_name="artist_top_tracks.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    if artist_image_url:
                        col1, col2, col3 = st.columns(3)
                        with col2:
                            try:
                                image = Image.open(urlopen(artist_image_url))
                                st.image(image, caption=artist_name, width=300)
                            except:
                                st.write(f"🎤 {artist_name}")
                    
                    status.update(label="✅ Done!", state="complete", expanded=False)
                else:
                    status.update(label="No top tracks found or invalid artist.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again later", state="error", expanded=False)
                st.error("**Rate limit hit!** The optimized version uses better retry logic.")
                st.info("💡 **Tips:**\n- Wait a few minutes before trying again\n- Artist top tracks is a lightweight operation, so rate limits are rare here")
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)

if __name__ == "__main__":
    main()