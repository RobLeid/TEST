def ms_to_min_sec(ms):
    """Converts milliseconds to a mm:ss format string."""
    if ms is None or ms < 0:
        return "0:00"
    
    try:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"
    except (TypeError, ValueError):
        return "0:00"

def safe_get(data, key, default="N/A"):
    """Safely get a value from a dictionary"""
    if not isinstance(data, dict):
        return default
    return data.get(key, default)

def get_artist_names(artists):
    """Extract artist names from artists array"""
    if not artists or not isinstance(artists, list):
        return "Unknown Artist"
    
    try:
        names = []
        for artist in artists:
            if isinstance(artist, dict) and "name" in artist:
                names.append(artist["name"])
        return ", ".join(names) if names else "Unknown Artist"
    except:
        return "Unknown Artist"

def process_track_data(tracks):
    """Processes raw track JSON data into a simplified format for a DataFrame."""
    if not tracks:
        return []
    
    simplified_data = []
    
    for track in tracks:
        if not track or not isinstance(track, dict):
            continue
        
        try:
            simplified_data.append({
                "Track Artist(s)": get_artist_names(track.get("artists", [])),
                "Track Name": safe_get(track, "name", "Unknown Track"),
                "ISRC": safe_get(track.get("external_ids", {}), "isrc", "N/A"),
                "Duration": ms_to_min_sec(track.get("duration_ms", 0)),
                "Explicit": "Yes" if track.get("explicit", False) else "No",
                "Spotify URL": safe_get(track.get("external_urls", {}), "spotify", "N/A")
            })
        except Exception as e:
            # Skip tracks that can't be processed but log the error
            import streamlit as st
            st.warning(f"Skipped track due to processing error: {str(e)}")
            continue
    
    return simplified_data

def process_album_track_data(album_data, track_items, full_tracks):
    """Processes album and track JSON data for a DataFrame."""
    if not album_data or not isinstance(album_data, dict):
        return []
    
    # Extract album metadata
    album_artists = get_artist_names(album_data.get("artists", []))
    album_name = safe_get(album_data, "name", "Unknown Album")
    upc = safe_get(album_data.get("external_ids", {}), "upc", "N/A")
    release_date = safe_get(album_data, "release_date", "N/A")
    release_type = safe_get(album_data, "album_type", "N/A").capitalize()
    label = safe_get(album_data, "label", "N/A")
    album_url = safe_get(album_data.get("external_urls", {}), "spotify", "N/A")
    
    # Extract P-line (phonogram copyright)
    p_line = "N/A"
    copyrights = album_data.get("copyrights", [])
    if isinstance(copyrights, list):
        for copyright_info in copyrights:
            if isinstance(copyright_info, dict) and copyright_info.get("type") == "P":
                p_line = copyright_info.get("text", "N/A")
                break
    
    simplified_data = []
    
    # Process tracks (ensure we have matching track_items and full_tracks)
    for i, (track_item, full_track) in enumerate(zip(track_items, full_tracks)):
        if not full_track or not isinstance(full_track, dict):
            continue
        
        try:
            simplified_data.append({
                "Album Artist(s)": album_artists,
                "Album Name": album_name,
                "UPC": upc,
                "Release Date": release_date,
                "Release Type": release_type,
                "Label": label,
                "℗ Line": p_line,
                "Album Spotify URL": album_url,
                "Disc Number": track_item.get("disc_number", 1) if track_item else 1,
                "Track Number": track_item.get("track_number", i + 1) if track_item else i + 1,
                "Track Artist(s)": get_artist_names(full_track.get("artists", [])),
                "Track Name": safe_get(full_track, "name", "Unknown Track"),
                "ISRC": safe_get(full_track.get("external_ids", {}), "isrc", "N/A"),
                "Explicit": "Yes" if full_track.get("explicit", False) else "No",
                "Duration": ms_to_min_sec(full_track.get("duration_ms", 0)),
                "Track Spotify URL": safe_get(full_track.get("external_urls", {}), "spotify", "N/A")
            })
        except Exception:
            # Skip tracks that can't be processed
            continue
    
    return simplified_data

def process_artist_album_data(album_data, track_items, full_tracks):
    """Processes album and track data specifically for artist catalogs."""
    # Use the same processing as regular albums
    return process_album_track_data(album_data, track_items, full_tracks)