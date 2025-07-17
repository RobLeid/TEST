import streamlit as st
import pandas as pd
import time
from utils.auth import get_access_token
from utils.api import fetch_artist_albums, fetch_album_details
from utils.parsing import parse_multi_spotify_ids
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
    st.title("🎤 Multiple Artist Catalog")
    st.caption("Get all releases for multiple artists into a single file.")
    
    artist_input = st.text_area("Enter Spotify artist URIs, URLs, or IDs (one per line)")
    market = st.selectbox("Select Market (Country Code)", MARKETS, index=MARKETS.index("US"))

    if st.button("🔍 Process Artists"):
        artist_ids = parse_multi_spotify_ids(artist_input, 'artist')
        if not artist_ids:
            st.error("Please enter at least one valid artist ID.")
            return

        access_token = get_access_token()
        if not access_token:
            return
            
        all_data = []
        start_time = time.time()

        with st.status("⏳ Processing...", expanded=True) as status:
            for i, artist_id in enumerate(artist_ids, 1):
                status.update(label=f"Fetching albums for artist {i}/{len(artist_ids)}...", state="running")
                albums = fetch_artist_albums(artist_id, market, access_token)
                
                if not albums:
                    status.info(f"No albums found for artist ID: {artist_id}", icon="ℹ️")
                    continue
                
                status.update(label=f"Processing {len(albums)} albums for artist {i}/{len(artist_ids)}...", state="running")
                for album in albums:
                    album_data, track_items, full_tracks = fetch_album_details(album["id"], access_token)
                    if album_data and full_tracks:
                        tracks = process_artist_album_data(album_data, track_items, full_tracks)
                        all_data.extend(tracks)

        elapsed = time.time() - start_time
        status.update(label=f"✅ Done! Processed {len(artist_ids)} artist(s) in {elapsed:.2f} seconds.", state="complete", expanded=False)

        if all_data:
            df = pd.DataFrame(all_data)
            st.download_button(
                label="📥 Download Excel File",
                data=to_excel(df),
                file_name="Multiple_Artists_Releases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No releases found for the provided artists.")

if __name__ == "__main__":
    main()