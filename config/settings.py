"""
Price Monitor Settings
Load configuration from environment and YAML files.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
TMP_DIR = PROJECT_ROOT / ".tmp"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "prices.db"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Scraping defaults
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
TIMEOUT_MS = int(os.getenv("TIMEOUT_MS", "30000"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Proxy (optional)
PROXY_URL = os.getenv("PROXY_URL", "")

# Schedule
SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "4"))

# Alert threshold
PRICE_CHANGE_THRESHOLD_PERCENT = float(os.getenv("PRICE_CHANGE_THRESHOLD_PERCENT", "0"))


def load_competitors_config() -> dict:
    """Load competitors configuration from YAML."""
    config_path = CONFIG_DIR / "competitors.yaml"
    if not config_path.exists():
        return {"competitors": [], "alerts": {}, "scraping": {}}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
