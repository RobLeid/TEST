"""
Common operations for the Spotify ISRC Finder application.
This module contains reusable logic patterns to reduce code duplication across pages.
"""

import streamlit as st
from typing import Optional, Tuple, Any, Dict
from .auth import get_access_token
from .api_improved import SpotifyAPIClient
from .rate_limiting import RateLimitExceeded


def get_authenticated_client() -> Optional[SpotifyAPIClient]:
    """
    Get an authenticated Spotify API client.
    
    Returns:
        SpotifyAPIClient instance if authentication successful, None otherwise
    """
    access_token = get_access_token()
    if not access_token:
        return None
    
    return SpotifyAPIClient(access_token)


def handle_rate_limit_exception(
    exception: RateLimitExceeded,
    context: str = "processing"
) -> None:
    """
    Handle rate limit exceptions with consistent messaging.
    
    Args:
        exception: The RateLimitExceeded exception
        context: Context string for the error message
    """
    st.error(f"⏱️ Rate limit exceeded during {context}. Returning partial data.")
    st.info(
        "💡 **Tips:**\n"
        "- Wait a few minutes before trying again\n"
        "- Try processing fewer items\n"
        "- The improved API automatically handles rate limiting and retries"
    )


def validate_and_get_client(
    input_value: Any,
    validation_func: callable,
    item_type: str
) -> Tuple[Optional[Any], Optional[SpotifyAPIClient]]:
    """
    Validate input and get authenticated client in one step.
    
    Args:
        input_value: Raw input to validate
        validation_func: Function to validate/parse the input
        item_type: Type of item for error messages
        
    Returns:
        Tuple of (validated_id, spotify_client) or (None, None) if validation fails
    """
    validated_id = validation_func(input_value, item_type)
    if not validated_id:
        return None, None
    
    client = get_authenticated_client()
    if not client:
        return None, None
    
    return validated_id, client


def display_no_data_error(
    show_debug_info: bool = True,
    debug_data: Optional[Dict] = None
) -> None:
    """
    Display standardized no data error message.
    
    Args:
        show_debug_info: Whether to show debug information
        debug_data: Optional debug data to display
    """
    st.error("❌ No data was successfully retrieved. This could be due to:")
    st.markdown("""
    - Invalid IDs
    - Severe API rate limiting
    - Network connectivity issues
    - No available releases in the selected market
    - Track data processing issues (check warnings above for details)
    """)
    
    if show_debug_info and debug_data:
        st.subheader("🔍 Debug Information")
        for key, value in debug_data.items():
            if isinstance(value, dict):
                st.write(f"**{key}:**")
                for sub_key, sub_value in value.items():
                    st.write(f"  - {sub_key}: {sub_value}")
            else:
                st.write(f"**{key}:** {value}")