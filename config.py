"""
Configuration file for Web Intelligence Gatherer
Set all constants, defaults, and API configurations here
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Search configuration
TIMEOUT = 10  # Request timeout in seconds
RATE_LIMIT_DELAY = 1.0  # Delay between requests (in seconds)
MAX_RESULTS_DEFAULT = 5  # Default results per source
MAX_RESULTS_LIMIT = 50  # Maximum allowed results per source
REQUEST_RETRIES = 2  # Number of retries on failure

# Available search sources
AVAILABLE_SOURCES = [
    "wikipedia",
    "stackoverflow",
    "github",
    "googlenews",
    "hackernews"
]

DEFAULT_SOURCES = ["wikipedia", "github", "stackoverflow"]

# User agent to avoid blocking
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# API endpoints
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
GITHUB_API = "https://api.github.com/search/repositories"
STACKOVERFLOW_API = "https://api.stackexchange.com/2.3/search"
GOOGLE_NEWS_URL = "https://news.google.com/search"
HACKERNEWS_API = "https://hn.algolia.com/api/v1/search"

# Output formats
OUTPUT_FORMAT_JSON = "json"
OUTPUT_FORMAT_CSV = "csv"
VALID_FORMATS = [OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_CSV]

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Threading
MAX_THREADS = 5  # Maximum concurrent search threads

# Data validation
MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 200

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
