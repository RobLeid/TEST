import pandas as pd
import streamlit as st
from utils.auth import get_access_token
from utils.api_improved import SpotifyAPIClient
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_multi_spotify_ids_secure
from utils.tools import to_excel
from utils.data_processing import process_track_data

def main():
    st.title("🎵 Spotify Track Info")
    user_input = st.text_area("Enter Spotify track IDs, URIs, or URLs (one per line)")

    if st.button("🔍 Get Track Info"):
        if not user_input.strip():
            st.warning("Please enter at least one track ID, URI, or URL.")
            return

        track_ids = parse_multi_spotify_ids_secure(user_input, 'track')
        if not track_ids:
            st.warning("No valid track IDs found.")
            return

        # Show processing info
        num_batches = (len(track_ids) + 49) // 50  # 50 tracks per batch
        st.info(f"🎯 Processing {len(track_ids)} tracks in {num_batches} batch(es) of up to 50 tracks each")

        # Initialize variables for results
        tracks_df = None
        excel_data = None
        
        with st.status("⏳ Processing...", expanded=True) as status:
            access_token = get_access_token()
            if not access_token:
                status.update(label="Authentication failed.", state="error", expanded=False)
                return
            
            # Initialize the improved API client
            spotify_client = SpotifyAPIClient(access_token)
            
            try:
                status.update(label="Fetching track data with optimized batch processing...", state="running", expanded=True)
                
                # Use improved API client with better error handling
                tracks = spotify_client.fetch_tracks_by_ids(track_ids)
                
                if tracks:
                    df = pd.DataFrame(process_track_data(tracks))
                    if not df.empty:
                        tracks_df = df
                        excel_data = to_excel(df)
                        status.update(label="✅ Done!", state="complete", expanded=False)
                    else:
                        status.update(label="No valid track data found.", state="warning", expanded=False)
                else:
                    status.update(label="No valid tracks found.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again in a few minutes", state="error", expanded=False)
                st.error("**Rate limit hit!** The optimized version uses maximum batch sizes and intelligent retry logic, but Spotify's API has usage limits.")
                st.info("💡 **Tips to avoid rate limits:**\n- Wait a few minutes before trying again\n- Process fewer tracks at once\n- The improved error handling will automatically retry with delays")
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)
        
        # Display results outside the status box
        if tracks_df is not None:
            st.dataframe(tracks_df, use_container_width=True, hide_index=True)
            if excel_data is not None:
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name="spotify_tracks.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()