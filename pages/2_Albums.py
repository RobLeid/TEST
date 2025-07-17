import pandas as pd
import streamlit as st
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api import fetch_album_details
from utils.parsing import parse_multi_spotify_ids
from utils.tools import to_excel
from utils.data_processing import process_album_track_data

def main():
    st.title("💿 Spotify Album Info")
    user_input = st.text_area("Enter multiple Spotify album URIs, URLs, or IDs (one per line)")
    
    if st.button("🔍 Get Album Info"):
        if not user_input:
            st.warning("Please enter at least one album ID, URI, or URL.")
            return
            
        album_ids = parse_multi_spotify_ids(user_input, 'album')
        if not album_ids:
            st.warning("No valid album IDs found.")
            return

        access_token = get_access_token()
        if not access_token:
            return
        
        all_dataframes = []
        album_details_list = []

        with st.status("⏳ Processing albums...", expanded=True) as status:
            for i, album_id in enumerate(album_ids):
                status.update(label=f"Processing album {i+1}/{len(album_ids)}...", state="running")
                album_data, track_items, full_tracks = fetch_album_details(album_id, access_token)
                if album_data and full_tracks:
                    simplified_data = process_album_track_data(album_data, track_items, full_tracks)
                    df = pd.DataFrame(simplified_data)
                    all_dataframes.append(df)
                    album_details_list.append({
                        "df": df,
                        "name": album_data.get("name", "Unknown Album"),
                        "image_url": album_data["images"][0]["url"] if album_data.get("images") else None,
                        "id": album_data["id"]
                    })
        
        status.update(label="✅ Done processing all albums!", state="complete", expanded=False)

        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            global_excel = to_excel(combined_df)
            st.download_button(
                label="📦 Download All Albums to Excel",
                data=global_excel,
                file_name="All_Albums_Tracks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all_albums" # Unique key for the global button
            )

            for album_details in album_details_list:
                st.divider()
                col1, col2 = st.columns([1, 3])
                with col1:
                    if album_details["image_url"]:
                        image = Image.open(urlopen(album_details["image_url"]))
                        st.image(image, caption=album_details["name"])
                    st.download_button(
                        label=f"📥 Download Excel",
                        data=to_excel(album_details["df"]),
                        file_name=f"{album_details['name']}_tracks.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{album_details['id']}" # Unique key for each album button
                    )
                with col2:
                    st.dataframe(album_details["df"], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()