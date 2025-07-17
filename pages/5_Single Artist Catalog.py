import streamlit as st
import pandas as pd
from PIL import Image
from urllib.request import urlopen

from utils.auth import get_access_token
from utils.api import fetch_artist_albums, fetch_album_details
from utils.parsing import parse_spotify_id
from utils.tools import to_excel
from utils.data_processing import process_artist_album_data

MARKETS = [
    "AD","AE","AG","AL","AM","AO","AR","AT","AU","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BN",
    "BO","BR","BS","BT","BW","BY","BZ","CA","CD","CG","CH","CI","CL","CM","CO","CR","CV","CW","CY","CZ",
    "DE","DJ","DK","DM","DO","DZ","EC","EE","EG","ES","ET","FI","FJ","FM","FR","GA","GB","GD","GE","GH",
    "GM","GN","GQ","GR","GT","GW","GY","HK","HN","HR","HT","HU","ID","IE","IL","IN","IQ","IS","IT","JM",
    "JO","JP","KE","KG","KH","KI","KM","KN","KR","KW","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU",
    "LV","LY","MA","MC","MD","ME","MG","MH","MK","ML","MN","MO","MR","MT","MU","MV","MW","MX","MY","MZ",
    "NA","NE","NG","NI","NL","NO","NP","NR","NZ","OM","PA","PE","PG","PH","PK","PL","PR","PS","PT","PW",
    "PY","QA","RO","RS","RW","SA","SB","SC","SE","SG","SI","SK","SL","SM","SN","SR","ST","SV","SZ","TD",
    "TG","TH","TJ","TL","TN","TO","TR","TT","TV","TW","TZ","UA","UG","US","UY","UZ","VC","VE","VN","VU",
    "WS","XK","ZA","ZM","ZW"
]

def main():
    st.title("🎤 Single Artist Catalog")
    st.caption("Get all releases by a single artist.")
    
    artist_input = st.text_input("Enter a Spotify artist URI, URL, or ID")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))
    
    if st.button("🔍 Get Artist Catalog"):
        artist_id = parse_spotify_id(artist_input, 'artist')
        if not artist_id:
            return
            
        access_token = get_access_token()
        if not access_token:
            return

        all_dataframes = []
        album_sections = {}

        with st.status("⏳ Fetching artist albums...", expanded=True) as status:
            albums = fetch_artist_albums(artist_id, market, access_token)
            if not albums:
                status.update(label="No albums found for this artist.", state="warning", expanded=False)
                return
            status.update(label=f"Found {len(albums)} albums. Processing...", state="running")
            
            for group_name, albums_list in {g: [a for a in albums if a.get("album_type") == g] for g in ["album", "single", "compilation"]}.items():
                section_dataframes = []
                for i, album in enumerate(albums_list):
                    status.update(label=f"Processing {group_name} {i+1}/{len(albums_list)}: {album['name']}", state="running")
                    album_data, track_items, full_tracks = fetch_album_details(album["id"], access_token)
                    if album_data and full_tracks:
                        tracks = process_artist_album_data(album_data, track_items, full_tracks)
                        df = pd.DataFrame(tracks)
                        section_dataframes.append((df, album_data.get("name"), album_data["images"][0]["url"] if album_data.get("images") else None, album_data["id"]))

                album_sections[group_name] = section_dataframes
                all_dataframes.extend([df for df, _, _, _ in section_dataframes])
        
        status.update(label="✅ Done processing all albums!", state="complete", expanded=False)

        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            st.download_button(
                label="📦 Download All Albums to Excel",
                data=to_excel(combined_df),
                file_name="Single_Artist_Releases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_all_albums" # Unique key for the global button
            )

        for group_name, section_dataframes in album_sections.items():
            if section_dataframes:
                st.header(group_name.capitalize() + "s")
                st.divider()
                for df, album_name, album_image_url, album_id in section_dataframes:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if album_image_url:
                            image = Image.open(urlopen(album_image_url))
                            st.image(image, caption=album_name)
                        st.download_button(
                            label="📥 Download Excel",
                            data=to_excel(df),
                            file_name=f"{album_name}_tracks.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{album_id}" # Unique key for each album button
                        )
                    with col2:
                        st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()