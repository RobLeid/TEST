import re
import streamlit as st

def parse_spotify_id(user_input, item_type):
    """
    Parses a Spotify ID from a URI, URL, or plain ID.
    
    Args:
        user_input (str): The input string from the user.
        item_type (str): The type of item to parse ('artist', 'album', 'track', 'playlist').
    """
    user_input = user_input.strip()
    
    # Handle URI
    if user_input.startswith(f"spotify:{item_type}:"):
        return user_input.split(":")[2]
    
    # Handle URL
    url_pattern = rf"spotify\.com/{item_type}/([a-zA-Z0-9]+)"
    match = re.search(url_pattern, user_input)
    if match:
        return match.group(1)
    
    # Handle plain ID
    if len(user_input) == 22 and re.match(r"^[a-zA-Z0-9]+$", user_input):
        return user_input
    
    st.error(f"Invalid {item_type.capitalize()} input: '{user_input}'. Please enter a valid ID, URI, or URL.")
    return None

def parse_multi_spotify_ids(user_input, item_type):
    """Parses multiple Spotify IDs from a text area."""
    raw_items = [item.strip() for item in user_input.splitlines() if item.strip()]
    return [parse_spotify_id(item, item_type) for item in raw_items if parse_spotify_id(item, item_type)]