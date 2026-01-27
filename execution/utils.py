"""
Shared utilities for execution scripts.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"
DIRECTIVES_DIR = PROJECT_ROOT / "directives"
EXECUTION_DIR = PROJECT_ROOT / "execution"


def ensure_tmp_dir():
    """Ensure .tmp directory exists."""
    TMP_DIR.mkdir(exist_ok=True)


def save_json(data: dict, filename: str) -> Path:
    """Save data to .tmp as JSON."""
    ensure_tmp_dir()
    filepath = TMP_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def load_json(filename: str) -> dict:
    """Load JSON from .tmp directory."""
    filepath = TMP_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_env(key: str, required: bool = True) -> str:
    """Get environment variable with optional requirement check."""
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value or ""
