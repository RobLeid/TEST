import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api import fetch_playlist_metadata_and_tracks
from utils.parsing import parse_spotify_id
from utils.tools import to_excel
from utils.data_processing import process_track_data

def main():
    st.title("📃 Spotify Playlist Info")
    st.caption("Note: this does not work for Spotify generated playlists...")
    user_input = st.text_input("Enter a Spotify playlist URI, URL, or ID")

    if user_input:
        playlist_id = parse_spotify_id(user_input, 'playlist')
        if not playlist_id:
            return

        with st.status("⏳ Fetching playlist...", expanded=True) as status:
            access_token = get_access_token()
            if not access_token:
                status.update(label="Authentication failed.", state="error", expanded=False)
                return
            meta_data, playlist_tracks = fetch_playlist_metadata_and_tracks(playlist_id, access_token)
            
        if meta_data and playlist_tracks:
            playlist_name = meta_data.get("name", "Unknown Playlist")
            playlist_image_url = meta_data["images"][0]["url"] if meta_data.get("images") else None
            
            tracks_only = [item.get("track") for item in playlist_tracks if item.get("track")]
            simplified_data = process_track_data(tracks_only)
            df = pd.DataFrame(simplified_data)

            st.dataframe(df, use_container_width=True, hide_index=True)
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name="playlist_tracks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            if playlist_image_url:
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.image(playlist_image_url, caption=playlist_name, width=300)
            
            status.update(label="✅ Done!", state="complete", expanded=False)
        else:
            status.update(label="No tracks found or invalid playlist.", state="warning", expanded=False)

if __name__ == "__main__":
    main()