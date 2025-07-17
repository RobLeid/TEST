def ms_to_min_sec(ms):
    """Converts milliseconds to a mm:ss format string."""
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{seconds:02d}"

def process_track_data(tracks):
    """Processes raw track JSON data into a simplified format for a DataFrame."""
    simplified_data = []
    for t in tracks:
        if t:
            simplified_data.append({
                "Track Artist(s)": ", ".join([artist["name"] for artist in t["artists"]]),
                "Track Name": t["name"],
                "ISRC": t.get("external_ids", {}).get("isrc", "N/A"),
                "Duration": ms_to_min_sec(t["duration_ms"]),
                "Explicit": "Yes" if t["explicit"] else "No",
                "Spotify URL": t["external_urls"]["spotify"]
            })
    return simplified_data

def process_album_track_data(album_data, track_items, full_tracks):
    """Processes album and track JSON data for a DataFrame."""
    upc = album_data.get("external_ids", {}).get("upc", "N/A")
    label = album_data.get("label", "N/A")
    p_line = "N/A"
    for c in album_data.get("copyrights", []):
        if c.get("type") == "P":
            p_line = c.get("text", "N/A")
            break
    
    simplified_data = []
    # Enforce a 1-to-1 match and the specified column order
    for meta, full in zip(track_items, full_tracks):
        simplified_data.append({
            "Album Artist(s)": ", ".join([artist["name"] for artist in album_data.get("artists", [])]),
            "Album Name": album_data.get("name", "Unknown Album"),
            "UPC": upc,
            "Release Date": album_data.get("release_date", "N/A"),
            "Release Type": album_data.get("album_type", "N/A").capitalize(),
            "Label": label,
            "℗ Line": p_line,
            "Album Spotify URL": album_data.get("external_urls", {}).get("spotify", "N/A"),
            "Disc Number": meta.get("disc_number", "N/A"),
            "Track Number": meta.get("track_number", "N/A"),
            "Track Artist(s)": ", ".join([artist["name"] for artist in full.get("artists", [])]),
            "Track Name": full.get("name", meta.get("name")),
            "ISRC": full.get("external_ids", {}).get("isrc", "N/A"),
            "Explicit": "Yes" if full.get("explicit") else "No",
            "Duration": ms_to_min_sec(full.get("duration_ms", 0)),
            "Track Spotify URL": full.get("external_urls", {}).get("spotify", "N/A")
        })
    return simplified_data

def process_artist_album_data(album_data, track_items, full_tracks):
    """Processes album and track data specifically for artist catalogs, using the standardized format."""
    upc = album_data.get("external_ids", {}).get("upc", "N/A")
    label = album_data.get("label", "N/A")
    p_line = "N/A"
    for c in album_data.get("copyrights", []):
        if c.get("type") == "P":
            p_line = c.get("text", "N/A")
            break
            
    tracks = []
    for meta, full in zip(track_items, full_tracks):
        tracks.append({
            "Album Artist(s)": ", ".join([a["name"] for a in album_data.get("artists", [])]),
            "Album Name": album_data.get("name", "Unknown Album"),
            "UPC": upc,
            "Release Date": album_data.get("release_date", "N/A"),
            "Release Type": album_data.get("album_type", "N/A").capitalize(),
            "Label": label,
            "℗ Line": p_line,
            "Album Spotify URL": album_data.get("external_urls", {}).get("spotify", "N/A"),
            "Disc Number": meta.get("disc_number", "N/A"),
            "Track Number": meta.get("track_number", "N/A"),
            "Track Artist(s)": ", ".join([a["name"] for a in full.get("artists", [])]),
            "Track Name": full.get("name", meta.get("name")),
            "ISRC": full.get("external_ids", {}).get("isrc", "N/A"),
            "Explicit": "Yes" if full.get("explicit") else "No",
            "Duration": ms_to_min_sec(full.get("duration_ms", 0)),
            "Track Spotify URL": full.get("external_urls", {}).get("spotify", "N/A")
        })
    
    return tracks