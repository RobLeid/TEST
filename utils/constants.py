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
MARKETS = [
    "AD","AE","AG","AL","AM","AO","AR","AT","AU","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BN",
    "BO","BR","BS","BT","BW","BY","BZ","CA","CD","CG","CH","CI","CL","CM","CO","CR","CV","CW","CY","CZ",
    "DE","DJ","DK","DM","DO","DZ","EC","EE","EG","ES","ET","FI","FJ","FM","FR","GA","GB","GD","GE","GH",
    "GM","GN","GQ","GR","GT","GW","GY","HK","HN","HR","HT","HU","ID","IE","IL","IN","IQ","IS","IT","JM",
    "JO","JP","KE","KG","KH","KI","KM","KN","KR","KW","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU",
    "LV","LY","MA","MC","MD","ME","MG","MH","MK","ML","MN","MO","MR","MT","MU","MV","MW","MX","MY","MZ",
    "NA","NE","NG","NI","NL","NO","NP","NR","NZ","OM","PA","PE","PG","PH","PK","PL","PR","PS","PT","PW",
    "PY","QA","RO","RS","RW","SA","SB","SC","SE","SG","SI","SK","SL","SM","SN","SR","ST","SV","SZ","TD",
    "TG","TH","TJ","TL","TN","TO","TR","TT","TV","TW","TZ","UA","UG","US","UY","UZ","VC","VE","VN","VU",
    "WS","XK","ZA","ZM","ZW"
]

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