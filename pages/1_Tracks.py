import pandas as pd
import streamlit as st
from utils.auth import get_access_token
from utils.api import fetch_tracks_by_ids
from utils.parsing import parse_multi_spotify_ids
from utils.tools import to_excel
from utils.data_processing import process_track_data

def main():
    st.title("🎵 Spotify Track Info")
    user_input = st.text_area("Enter Spotify track IDs, URIs, or URLs (one per line)")

    if st.button("🔍 Get Track Info"):
        if not user_input.strip():
            st.warning("Please enter at least one track ID, URI, or URL.")
            return

        track_ids = parse_multi_spotify_ids(user_input, 'track')
        if not track_ids:
            st.warning("No valid track IDs found.")
            return

        with st.status("⏳ Processing...", expanded=True) as status:
            access_token = get_access_token()
            if not access_token:
                status.update(label="Authentication failed.", state="error", expanded=False)
                return
            
            status.update(label="Fetching track data...", state="running", expanded=True)
            tracks = fetch_tracks_by_ids(track_ids, access_token)

        if tracks:
            df = pd.DataFrame(process_track_data(tracks))
            st.dataframe(df, use_container_width=True, hide_index=True)
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name="spotify_tracks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            status.update(label="✅ Done!", state="complete", expanded=False)
        else:
            status.update(label="No valid tracks found.", state="warning", expanded=False)

if __name__ == "__main__":
    main()