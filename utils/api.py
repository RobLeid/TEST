import requests
import time
import random
from typing import List, Dict, Optional, Tuple, Any
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class RateLimitExceeded(Exception):
    """Custom exception for when rate limits are exceeded"""
    pass

def make_request_with_retry(url: str, headers: Dict, params: Dict = None, timeout: int = 30, max_retries: int = 5) -> Optional[Dict]:
    """Improved request function with better 429 handling"""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit - check retry-after header
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    wait_time = min(int(retry_after), 60)  # Cap at 60 seconds
                    st.warning(f"⏱️ Rate limit hit. Waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    # Exponential backoff with jitter
                    wait_time = min((2 ** attempt) + random.uniform(0, 1), 60)
                    st.warning(f"⏱️ Rate limit hit. Waiting {wait_time:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
            elif response.status_code == 401:
                st.error("🔐 Authentication failed. Please check your access token.")
                return None
            elif response.status_code == 404:
                return None
            else:
                if attempt == max_retries - 1:
                    st.warning(f"⚠️ Request failed with status {response.status_code}")
                    return None
                # Wait before retry
                time.sleep(min(2 ** attempt, 10))
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(min(2 ** attempt, 10))
            else:
                st.error("❌ Request timed out after multiple attempts")
                return None
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                st.warning(f"🔗 Connection error, retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(min(2 ** attempt, 10))
            else:
                st.error("❌ Connection failed after multiple attempts")
                return None
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None
    
    raise RateLimitExceeded(f"Max retries ({max_retries}) exceeded")

def fetch_tracks_by_ids_batched(track_ids: List[str], access_token: str, batch_size: int = 50, max_retries: int = 5) -> List[Dict]:
    """Optimized track fetching with better rate limit handling using maximum batch size"""
    headers = {"Authorization": f"Bearer {access_token}"}
    all_tracks = []
    
    # Use maximum batch size (50) to minimize total requests and avoid 429 errors
    batch_size = min(batch_size, 50)  # Spotify API maximum
    
    total_batches = (len(track_ids) + batch_size - 1) // batch_size
    
    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        batch_ids = ",".join(batch)
        
        try:
            st.write(f"📥 Fetching batch {i//batch_size + 1}/{total_batches}: {len(batch)} tracks")
            
            response = make_request_with_retry(
                f"https://api.spotify.com/v1/tracks?ids={batch_ids}",
                headers,
                max_retries=max_retries
            )
            
            if response and "tracks" in response:
                valid_tracks = [track for track in response["tracks"] if track is not None]
                all_tracks.extend(valid_tracks)
                st.success(f"✅ Batch {i//batch_size + 1} complete: {len(valid_tracks)} tracks retrieved")
            else:
                st.warning(f"⚠️ Batch {i//batch_size + 1} returned no data")
                
        except RateLimitExceeded:
            st.error(f"❌ Rate limit exceeded for batch {i//batch_size + 1}. Returning partial data.")
            break
        except Exception as e:
            st.error(f"❌ Error fetching batch {i//batch_size + 1}: {e}")
            continue
        
        # Small delay between batches to be nice to the API
        if i + batch_size < len(track_ids):
            time.sleep(0.1)
    
    st.info(f"📊 Retrieved {len(all_tracks)} tracks total")
    return all_tracks

def fetch_album_details_optimized(album_id: str, access_token: str, max_retries: int = 5) -> Tuple[Optional[Dict], List[Dict], List[Dict]]:
    """Fetch album details with better error handling"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get album metadata
        album_data = make_request_with_retry(
            f"https://api.spotify.com/v1/albums/{album_id}",
            headers,
            max_retries=max_retries
        )
        
        if not album_data:
            return None, [], []
        
        track_items = album_data.get("tracks", {}).get("items", [])
        
        # Extract track IDs for batch fetching
        track_ids = [track["id"] for track in track_items if track.get("id")]
        
        # Fetch full track data using maximum batch size
        full_tracks = fetch_tracks_by_ids_batched(track_ids, access_token, batch_size=50, max_retries=max_retries)
        
        return album_data, track_items, full_tracks
        
    except RateLimitExceeded:
        st.error(f"❌ Rate limit exceeded while fetching album {album_id}")
        return None, [], []
    except Exception as e:
        st.error(f"❌ Error fetching album {album_id}: {e}")
        return None, [], []

def fetch_playlist_metadata_and_tracks_optimized(playlist_id: str, access_token: str, max_retries: int = 5) -> Tuple[Optional[Dict], List[Dict]]:
    """Fetch playlist with better error handling"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get playlist metadata
        playlist_data = make_request_with_retry(
            f"https://api.spotify.com/v1/playlists/{playlist_id}",
            headers,
            max_retries=max_retries
        )
        
        if not playlist_data:
            return None, []
        
        # Get all playlist tracks with pagination
        all_tracks = []
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        page = 1
        
        while url:
            st.write(f"📥 Fetching playlist page {page}...")
            response = make_request_with_retry(url, headers, {"limit": 100}, max_retries=max_retries)
            if not response:
                break
                
            items = response.get("items", [])
            all_tracks.extend(items)
            url = response.get("next")
            page += 1
            
            # Small delay between pages
            if url:
                time.sleep(0.1)
        
        # Extract track IDs for batch fetching of full track data
        track_ids = []
        for item in all_tracks:
            if item.get("track") and item["track"].get("id"):
                track_ids.append(item["track"]["id"])
        
        if track_ids:
            # Fetch full track data using maximum batch size
            full_tracks = fetch_tracks_by_ids_batched(track_ids, access_token, max_retries=max_retries)
            track_map = {track["id"]: track for track in full_tracks if track}
            
            # Update playlist items with full track data
            for item in all_tracks:
                if item.get("track") and item["track"].get("id"):
                    track_id = item["track"]["id"]
                    if track_id in track_map:
                        item["track"] = track_map[track_id]
        
        return playlist_data, all_tracks
        
    except RateLimitExceeded:
        st.error(f"❌ Rate limit exceeded while fetching playlist {playlist_id}")
        return None, []
    except Exception as e:
        st.error(f"❌ Error fetching playlist {playlist_id}: {e}")
        return None, []

def fetch_artist_metadata_and_top_tracks_optimized(artist_id: str, access_token: str, market: str = "US", max_retries: int = 5) -> Tuple[Optional[Dict], List[Dict]]:
    """Fetch artist data with better error handling"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get artist metadata
        artist_data = make_request_with_retry(
            f"https://api.spotify.com/v1/artists/{artist_id}",
            headers,
            max_retries=max_retries
        )
        
        # Get top tracks (already returns full track data)
        top_tracks_data = make_request_with_retry(
            f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks",
            headers,
            params={"market": market},
            max_retries=max_retries
        )
        
        if not artist_data or not top_tracks_data:
            return None, []
        
        return artist_data, top_tracks_data.get("tracks", [])
        
    except RateLimitExceeded:
        st.error(f"❌ Rate limit exceeded while fetching artist {artist_id}")
        return None, []
    except Exception as e:
        st.error(f"❌ Error fetching artist {artist_id}: {e}")
        return None, []

def fetch_artist_albums_optimized(artist_id: str, market: str, access_token: str, max_retries: int = 5) -> List[Dict]:
    """Fetch artist albums with pagination and better error handling"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    all_albums = []
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {
        "market": market,
        "limit": 50,  # Maximum allowed
        "include_groups": "album,single,compilation"
    }
    page = 1
    
    try:
        while url:
            st.write(f"📥 Fetching artist albums page {page}...")
            response = make_request_with_retry(url, headers, params, max_retries=max_retries)
            if not response:
                break
                
            albums = response.get("items", [])
            all_albums.extend(albums)
            url = response.get("next")
            params = None  # Clear params for subsequent requests (they're in the URL)
            page += 1
            
            # Small delay between pages
            if url:
                time.sleep(0.1)
        
        st.info(f"📊 Found {len(all_albums)} albums for artist")
        return all_albums
        
    except RateLimitExceeded:
        st.error(f"❌ Rate limit exceeded while fetching albums for artist {artist_id}")
        return all_albums  # Return partial data
    except Exception as e:
        st.error(f"❌ Error fetching albums for artist {artist_id}: {e}")
        return []

def fetch_multiple_artists_catalogs_super_optimized(
    artist_ids: List[str], 
    market: str, 
    access_token: str, 
    max_retries: int = 5,
    max_workers: int = 2
) -> Dict[str, Any]:
    """
    Optimized multiple artist processing with better rate limit handling
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    results = {}
    
    def process_artist(artist_id: str) -> Tuple[str, Dict]:
        """Process a single artist's catalog"""
        try:
            # Get albums for this artist
            albums = fetch_artist_albums_optimized(artist_id, market, access_token, max_retries)
            
            # Get album details using maximum batch size (20 for albums)
            album_ids = [album["id"] for album in albums]
            album_data = {}
            all_track_ids = []
            
            # Process albums in batches of 20 (Spotify API maximum)
            for i in range(0, len(album_ids), 20):
                batch_ids = album_ids[i:i+20]
                batch_ids_str = ",".join(batch_ids)
                
                st.write(f"📥 Fetching album batch {i//20 + 1} for artist {artist_id}")
                
                response = make_request_with_retry(
                    f"https://api.spotify.com/v1/albums?ids={batch_ids_str}",
                    headers,
                    max_retries=max_retries
                )
                
                if response and "albums" in response:
                    for album in response["albums"]:
                        if album:
                            album_data[album["id"]] = album
                            # Collect all track IDs
                            track_items = album.get("tracks", {}).get("items", [])
                            track_ids = [track["id"] for track in track_items if track.get("id")]
                            all_track_ids.extend(track_ids)
                
                # Small delay between album batches
                time.sleep(0.1)
            
            # Fetch all tracks for this artist using maximum batch size
            all_tracks = fetch_tracks_by_ids_batched(all_track_ids, access_token, batch_size=50, max_retries=max_retries)
            
            return artist_id, {
                "albums": albums,
                "album_data": album_data,
                "tracks": all_tracks,
                "failed_albums": []
            }
            
        except Exception as e:
            st.error(f"❌ Error processing artist {artist_id}: {e}")
            return artist_id, {"albums": [], "album_data": {}, "tracks": [], "failed_albums": []}
    
    # Process artists with limited concurrency to respect rate limits
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_artist = {executor.submit(process_artist, artist_id): artist_id for artist_id in artist_ids}
        
        for future in as_completed(future_to_artist):
            artist_id, result = future.result()
            results[artist_id] = result
    
    return results

# Legacy function names for backward compatibility
def fetch_tracks_by_ids(track_ids: List[str], access_token: str) -> List[Dict]:
    """Legacy wrapper for backward compatibility"""
    return fetch_tracks_by_ids_batched(track_ids, access_token)

def fetch_album_details(album_id: str, access_token: str) -> Tuple[Optional[Dict], List[Dict], List[Dict]]:
    """Legacy wrapper for backward compatibility"""
    return fetch_album_details_optimized(album_id, access_token)

def fetch_playlist_metadata_and_tracks(playlist_id: str, access_token: str) -> Tuple[Optional[Dict], List[Dict]]:
    """Legacy wrapper for backward compatibility"""
    return fetch_playlist_metadata_and_tracks_optimized(playlist_id, access_token)

def fetch_artist_metadata_and_top_tracks(artist_id: str, access_token: str) -> Tuple[Optional[Dict], List[Dict]]:
    """Legacy wrapper for backward compatibility"""
    return fetch_artist_metadata_and_top_tracks_optimized(artist_id, access_token, market="US")

def fetch_artist_albums(artist_id: str, market: str, access_token: str) -> List[Dict]:
    """Legacy wrapper for backward compatibility"""
    return fetch_artist_albums_optimized(artist_id, market, access_token)

def fetch_multiple_artists_catalogs_optimized(artist_ids: List[str], market: str, access_token: str, max_retries: int = 5) -> Dict[str, Any]:
    """Legacy wrapper for backward compatibility"""
    return fetch_multiple_artists_catalogs_super_optimized(artist_ids, market, access_token, max_retries)