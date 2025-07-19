"""
Common UI components for the Spotify ISRC Finder application.
This module contains reusable UI patterns to reduce code duplication across pages.
"""

import streamlit as st
import pandas as pd
from PIL import Image
from urllib.request import urlopen
from typing import Optional, Dict, Any
from .tools import to_excel


def create_download_button(
    df: pd.DataFrame,
    label: str,
    file_name: str,
    key: Optional[str] = None
) -> None:
    """
    Create a standardized Excel download button.
    
    Args:
        df: DataFrame to download
        label: Button label text
        file_name: Name for the downloaded file
        key: Optional unique key for the button
    """
    excel_data = to_excel(df)
    if excel_data is not None:
        st.download_button(
            label=label,
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=key
        )


def display_image_safe(
    image_url: Optional[str],
    caption: str,
    width: Optional[int] = None
) -> None:
    """
    Display an image with safe fallback for loading errors.
    
    Args:
        image_url: URL of the image to display
        caption: Caption for the image
        width: Optional width for the image
    """
    if image_url:
        try:
            image = Image.open(urlopen(image_url))
            st.image(image, caption=caption, width=width)
        except:
            st.write(f"🖼️ {caption}")
    else:
        st.write(f"🖼️ {caption}")


def display_album_row(
    album_data: Dict[str, Any],
    df: pd.DataFrame,
    album_id: str
) -> None:
    """
    Display an album row with image, data, and download button.
    
    Args:
        album_data: Album metadata dictionary
        df: DataFrame with track data
        album_id: Unique album ID for button keys
    """
    col1, col2 = st.columns([1, 3])
    
    with col1:
        album_name = album_data.get("name", "Unknown Album")
        album_image_url = album_data["images"][0]["url"] if album_data.get("images") else None
        display_image_safe(album_image_url, album_name)
        
        create_download_button(
            df=df,
            label="📥 Download Excel",
            file_name=f"{album_name}_tracks.xlsx",
            key=f"download_{album_id}"
        )
    
    with col2:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.divider()


def display_processing_info(message: str, icon: str = "🎯") -> None:
    """
    Display standardized processing information.
    
    Args:
        message: Message to display
        icon: Icon to use (default: 🎯)
    """
    st.info(f"{icon} {message}")


def display_rate_limit_error() -> None:
    """Display standardized rate limit error message."""
    st.error("⏱️ Rate limit exceeded. Returning partial data.")
    st.info(
        "💡 **Tips:**\n"
        "- Wait a few minutes before trying again\n"
        "- Try processing fewer items\n"
        "- The improved API automatically handles rate limiting and retries"
    )