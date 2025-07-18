import re
import streamlit as st

def parse_spotify_id(user_input, item_type):
    """
    Parses a Spotify ID from a URI, URL, or plain ID.
    
    Args:
        user_input (str): The input string from the user.
        item_type (str): The type of item to parse ('artist', 'album', 'track', 'playlist').
    """
    if not user_input:
        return None
    
    user_input = user_input.strip()
    
    # Handle URI format: spotify:track:4iV5W9uYEdYUVa79Axb7Rh
    if user_input.startswith(f"spotify:{item_type}:"):
        return user_input.split(":")[2]
    
    # Handle URL formats
    url_patterns = [
        rf"spotify\.com/{item_type}/([a-zA-Z0-9]+)",
        rf"open\.spotify\.com/{item_type}/([a-zA-Z0-9]+)"
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, user_input)
        if match:
            return match.group(1)
    
    # Handle plain ID (basic validation)
    if len(user_input) == 22 and re.match(r"^[a-zA-Z0-9]+$", user_input):
        return user_input
    
    st.error(f"❌ Invalid {item_type.capitalize()} input: '{user_input}'. Please enter a valid ID, URI, or URL.")
    st.info(f"""
    **Valid formats:**
    - ID: `4iV5W9uYEdYUVa79Axb7Rh`
    - URI: `spotify:{item_type}:4iV5W9uYEdYUVa79Axb7Rh`
    - URL: `https://open.spotify.com/{item_type}/4iV5W9uYEdYUVa79Axb7Rh`
    """)
    return None

def parse_multi_spotify_ids(user_input, item_type):
    """Parses multiple Spotify IDs from a text area."""
    if not user_input:
        return []
    
    raw_items = [item.strip() for item in user_input.splitlines() if item.strip()]
    valid_ids = []
    invalid_count = 0
    
    for item in raw_items:
        parsed_id = parse_spotify_id(item, item_type)
        if parsed_id:
            valid_ids.append(parsed_id)
        else:
            invalid_count += 1
    
    if valid_ids:
        st.success(f"✅ Found {len(valid_ids)} valid {item_type} IDs")
    
    if invalid_count > 0:
        st.warning(f"⚠️ Skipped {invalid_count} invalid entries")
    
    return valid_ids