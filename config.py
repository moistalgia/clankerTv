"""
Configuration settings for ClankerTV Discord Bot
===============================================

Contains all configuration constants and settings.
Uses environment variables for sensitive data in production.
"""

import os
from typing import List, Dict, Any

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, environment variables must be set system-wide
    pass

# ========================================
# DISCORD CONFIGURATION
# ========================================

# Use environment variables for sensitive data, with fallbacks for development
TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_TOKEN_HERE")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))  # Replace with your guild ID
ANNOUNCE_CHANNEL_ID = os.getenv("ANNOUNCE_CHANNEL_ID", "clanker-commands")
STREAM_CHANNEL_ID = int(os.getenv("STREAM_CHANNEL_ID", "0"))  # Replace with your voice channel ID
NOTIFY_USER_ID = int(os.getenv("NOTIFY_USER_ID", "0"))  # Replace with your user ID

# Bot command prefix
COMMAND_PREFIX = "!"

# ========================================
# PLEX MEDIA SERVER CONFIGURATION
# ========================================

PLEX_URL = os.getenv("PLEX_URL", "http://localhost:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN", "YOUR_PLEX_TOKEN_HERE")
PLEX_CLIENT_NAME = os.getenv("PLEX_CLIENT_NAME", "Plex (Windows)")
PLEX_LIBRARY = os.getenv("PLEX_LIBRARY", "Movies")

# ========================================
# QBITTORRENT CONFIGURATION
# ========================================

QB_HOST = os.getenv("QB_HOST", "localhost:8080")
QB_USER = os.getenv("QB_USER", "admin")
QB_PASS = os.getenv("QB_PASS", "YOUR_QB_PASSWORD_HERE")

# Default download path for torrents
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", r"C:\Downloads\Movies")

# ========================================
# OPENAI CONFIGURATION
# ========================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# AI Model settings
AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.9"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "300"))

# ========================================
# SUBTITLES CONFIGURATION
# ========================================

PREFERRED_LANG = os.getenv("PREFERRED_LANG", "en")

# ========================================
# BOT PERSONALITY CONFIGURATION
# ========================================

# Bot personality trigger words
BOT_SLURS: List[str] = ["inorganic", "clanker", "cog", "meatless"]

# Default AI personality sliders (0-10 scale)
DEFAULT_SLIDERS: Dict[str, int] = {
    "creepiness": 10,
    "humor": 5,
    "violence": 5,
    "mystery": 10,
}

# ========================================
# TASK INTERVALS
# ========================================

SPONTANEOUS_MESSAGE_INTERVAL = int(os.getenv("SPONTANEOUS_MESSAGE_INTERVAL", "300"))  # 5 minutes in seconds
PLAYBACK_CHECK_INTERVAL = int(os.getenv("PLAYBACK_CHECK_INTERVAL", "5"))  # 5 seconds
STATS_UPDATE_INTERVAL = int(os.getenv("STATS_UPDATE_INTERVAL", "30"))  # 30 seconds

# ========================================
# DATA PERSISTENCE
# ========================================

DATA_DIR = "data"
USER_STATS_FILE = f"{DATA_DIR}/user_stats.json"
WATCH_HISTORY_FILE = f"{DATA_DIR}/watch_history.json"
MOVIE_RATINGS_FILE = f"{DATA_DIR}/movie_ratings.json"
USER_BADGES_FILE = f"{DATA_DIR}/user_badges.json"

# ========================================
# LOGGING CONFIGURATION
# ========================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "clanker.log")

# ========================================
# VALIDATION
# ========================================

def validate_config():
    """Validate that required configuration values are set."""
    required_vars = [
        ("DISCORD_TOKEN", TOKEN),
        ("GUILD_ID", GUILD_ID),
        ("OPENAI_API_KEY", OPENAI_API_KEY),
    ]
    
    missing = []
    for var_name, value in required_vars:
        if not value or str(value).startswith("YOUR_") or value == 0:
            missing.append(var_name)
    
    if missing:
        raise ValueError(
            f"Missing required configuration values: {', '.join(missing)}\n"
            f"Please set these environment variables or update your .env file."
        )

# Validate config on import (can be disabled for testing)
if os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    validate_config()