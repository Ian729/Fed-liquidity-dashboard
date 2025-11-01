from __future__ import annotations
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

# Load .env file with explicit encoding handling
# Handle various encoding issues that may occur on Windows
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    # Manually read the file to handle encoding issues
    encodings = ['utf-8-sig', 'utf-16', 'utf-16-le', 'utf-8', 'latin-1']
    loaded = False
    for encoding in encodings:
        try:
            with open(env_path, 'r', encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            loaded = True
            break
        except (UnicodeDecodeError, UnicodeError, Exception):
            continue
    
    # Fallback to python-dotenv if manual reading fails
    if not loaded:
        try:
            load_dotenv(env_path, encoding='utf-8-sig')
        except Exception:
            try:
                load_dotenv(env_path)
            except Exception:
                pass
else:
    # Try default location
    load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY", "")

def recent_start(days: int) -> str:
    return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")


def normalize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    return (s - s.min()) / (s.max() - s.min()) if s.max() != s.min() else s * 0


def pct_change_annualized(s: pd.Series, periods: int = 252) -> float:
    if len(s) < 2:
        return 0.0
    return ((s.dropna().iloc[-1] / s.dropna().iloc[0]) - 1) * (252 / max(1, len(s.dropna())))


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

