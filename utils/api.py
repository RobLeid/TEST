import requests
import time
import streamlit as st

def make_api_call(method, url, headers=None, params=None, data=None):
    """
    Centralized function to make API calls with rate limiting handling.
    Retries the request after 30 seconds if a 429 error is received.
    """
    if method.upper() not in ['GET', 'POST']:
        raise ValueError("Method must be 'GET' or 'POST'")

    while True:
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            else:
                response = requests.post(url, headers=headers, data=data)

            if response.status_code == 429:
                st.info("Rate limit hit (429 error). Waiting for 30 seconds...", icon="⏳")
                time.sleep(30)
                continue
            
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred during the API call: {e}")
            return None

def paginate_api_call(base_url, headers, limit=50, params=None):
    """
    Handles pagination for API endpoints.
    Fetches all items by repeatedly calling the 'next' URL.
    """
    all_items = []
    current_url = base_url
    current_params = params.copy() if params else {}

    while current_url:
        response = make_api_call('GET', current_url, headers=headers, params=current_params)
        if response is None:
            break
        
        data = response.json()
        
        # Check for different item keys
        items = data.get("items") or data.get("tracks")
        if not items:
            break

        all_items.extend(items)
        
        # Spotify API has different pagination patterns
        current_url = data.get("next")
        current_params = {} # The 'next' URL already contains the offset and limit
        if not current_url and len(items) < limit:
            break

    return all_items

def fetch_tracks_by_ids(track_ids, access_token):
    """Fetches track data for a list of track IDs."""
    headers = {"Authorization": f"Bearer {access_token}"}
    tracks = []
    id_chunks = [track_ids[i:i + 50] for i in range(0, len(track_ids), 50)]
    for chunk in id_chunks:
        ids_param = ",".join(chunk)
        response = make_api_call('GET', f"https://api.spotify.com/v1/tracks?ids={ids_param}", headers=headers)
        if response and "tracks" in response.json():
            tracks.extend(response.json()["tracks"])
    return tracks

def fetch_artist_albums(artist_id, market, access_token):
    """Fetches all albums for a given artist, handling pagination."""
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {"limit": 50, "market": market, "include_groups": "album,single,compilation"}
    albums = paginate_api_call(base_url, headers, params=params)
    seen_ids = set()
    unique_albums = []
    for album in albums:
        if album["id"] not in seen_ids:
            seen_ids.add(album["id"])
            unique_albums.append(album)
    return unique_albums

def fetch_album_details(album_id, access_token):
    """Fetches all tracks for a given album, handling pagination."""
    headers = {"Authorization": f"Bearer {access_token}"}
    album_data = make_api_call('GET', f"https://api.spotify.com/v1/albums/{album_id}", headers=headers)
    if not album_data:
        return None
    album_data = album_data.json()
    base_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    track_items = paginate_api_call(base_url, headers, limit=50)
    track_ids = [t["id"] for t in track_items]
    full_tracks = fetch_tracks_by_ids(track_ids, access_token)
    return album_data, track_items, full_tracks

def fetch_artist_metadata_and_top_tracks(artist_id, access_token, market="US"):
    """Fetches artist metadata and their top tracks."""
    headers = {"Authorization": f"Bearer {access_token}"}
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    top_tracks_url = f"{artist_url}/top-tracks?market={market}"
    artist_response = make_api_call('GET', artist_url, headers=headers)
    top_tracks_response = make_api_call('GET', top_tracks_url, headers=headers)
    if not artist_response or not top_tracks_response:
        return None, None, []
    artist_data = artist_response.json()
    top_tracks_data = top_tracks_response.json().get("tracks", [])
    return artist_data, top_tracks_data

def fetch_playlist_metadata_and_tracks(playlist_id, access_token):
    """Fetches playlist metadata and all tracks, handling pagination."""
    headers = {"Authorization": f"Bearer {access_token}"}
    base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    meta_response = make_api_call('GET', base_url, headers=headers)
    if not meta_response:
        return None, None
    meta_data = meta_response.json()
    tracks = paginate_api_call(f"{base_url}/tracks", headers, limit=100)
    return meta_data, tracks