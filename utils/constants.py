"""
Constants and configuration values for the Spotify ISRC Finder application.
"""

# API Configuration
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"

# Rate Limiting and Timeouts
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 5
INITIAL_BACKOFF_DELAY = 1.0  # seconds
MAX_BACKOFF_DELAY = 60.0  # seconds
BACKOFF_MULTIPLIER = 2.0
JITTER_RANGE = 1.0  # seconds

# Batch Sizes (Spotify API limits)
TRACKS_BATCH_SIZE = 50  # Maximum tracks per request
ALBUMS_BATCH_SIZE = 20  # Maximum albums per request
PLAYLIST_ITEMS_LIMIT = 100  # Maximum playlist items per page
ARTIST_ALBUMS_LIMIT = 50  # Maximum artist albums per page

# Request Delays
INTER_BATCH_DELAY = 0.1  # seconds between batches
INTER_PAGE_DELAY = 0.1  # seconds between pages
RATE_LIMIT_DELAY = 0.5  # seconds between requests to avoid rate limits

# Thread Pool Configuration
MAX_WORKERS = 2  # Maximum concurrent threads for API requests

# Input Validation
MAX_INPUT_LENGTH = 10000  # Maximum characters in text input
MAX_ITEMS_PER_REQUEST = 1000  # Maximum items to process in one request
SPOTIFY_ID_LENGTH = 22  # Standard Spotify ID length

# Album Types for separate queries
ALBUM_TYPES = ["album", "single", "compilation"]

# Supported Markets
DEFAULT_MARKET = "US"

# Error Messages
ERROR_MESSAGES = {
    "invalid_id": "Invalid Spotify ID format",
    "rate_limit": "Rate limit exceeded. Please try again later.",
    "auth_failed": "Authentication failed. Please check your credentials.",
    "network_error": "Network error. Please check your connection.",
    "invalid_input": "Invalid input detected",
    "input_too_long": f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters",
    "too_many_items": f"Too many items. Maximum allowed: {MAX_ITEMS_PER_REQUEST}",
}

# Success Messages
SUCCESS_MESSAGES = {
    "batch_complete": "Batch processing completed successfully",
    "data_fetched": "Data fetched successfully",
    "validation_passed": "Input validation passed",
}

# File Export
EXCEL_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"