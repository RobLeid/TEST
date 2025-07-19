import pandas as pd
import streamlit as st
from utils.rate_limiting import RateLimitExceeded
from utils.validation import parse_multi_spotify_ids_secure
from utils.data_processing import process_track_data
from utils.ui_components import (
    create_download_button,
    display_processing_info,
    display_rate_limit_error
)
from utils.common_operations import get_authenticated_client

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
        display_processing_info(f"Processing {len(track_ids)} tracks in {num_batches} batch(es) of up to 50 tracks each")

        # Initialize variables for results
        tracks_df = None
        
        with st.status("⏳ Processing...", expanded=True) as status:
            spotify_client = get_authenticated_client()
            if not spotify_client:
                return
            
            try:
                status.update(label="Fetching track data with optimized batch processing...", state="running", expanded=True)
                
                # Use improved API client with better error handling
                tracks = spotify_client.fetch_tracks_by_ids(track_ids)
                
                if tracks:
                    df = pd.DataFrame(process_track_data(tracks))
                    if not df.empty:
                        tracks_df = df
                        status.update(label="✅ Done!", state="complete", expanded=False)
                    else:
                        status.update(label="No valid track data found.", state="warning", expanded=False)
                else:
                    status.update(label="No valid tracks found.", state="warning", expanded=False)
                    
            except RateLimitExceeded:
                status.update(label="⏱️ Rate limit exceeded - please try again in a few minutes", state="error", expanded=False)
                display_rate_limit_error()
            except Exception as e:
                status.update(label=f"Error: {str(e)}", state="error", expanded=False)
        
        # Display results outside the status box
        if tracks_df is not None:
            st.dataframe(tracks_df, use_container_width=True, hide_index=True)
            create_download_button(
                df=tracks_df,
                label="📥 Download as Excel",
                file_name="spotify_tracks.xlsx",
                key="download_tracks"
            )

if __name__ == "__main__":
    main()