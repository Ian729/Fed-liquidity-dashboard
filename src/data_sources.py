from __future__ import annotations
import io
from datetime import datetime
import pandas as pd
import requests
import yfinance as yf
from .util import FRED_API_KEY

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def fred_series(series_id: str, start_date: str) -> pd.Series:
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
    }
    r = requests.get(FRED_BASE, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()["observations"]
    df = pd.DataFrame(data)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df.index = pd.to_datetime(df["date"])  # daily (business days mostly)
    return df["value"].asfreq("D").interpolate(limit_direction="both")


def yf_series(ticker: str, start_date: str, max_retries: int = 3) -> pd.Series:
    """Download yfinance data with retry logic and alternative tickers."""
    # Alternative ticker mappings for common failures
    alternatives = {
        "DX-Y.NYB": ["^DXY", "DX=F", "DX-Y.NYB"],
        "HG=F": ["HG=F", "HG=F"],
        "CL=F": ["CL=F", "CL=F"],
        "HYG": ["HYG"],
        "IEF": ["IEF"],
    }
    
    ticker_list = alternatives.get(ticker, [ticker])
    
    for attempt_ticker in ticker_list:
        for attempt in range(max_retries):
            try:
                import time
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                df = yf.download(attempt_ticker, start=start_date, auto_adjust=True, progress=False, timeout=10)
                if df.empty:
                    if attempt < max_retries - 1:
                        continue
                    print(f"Warning: No data for {ticker} (tried {attempt_ticker})")
                    return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
                
                if "Close" not in df.columns:
                    if attempt < max_retries - 1:
                        continue
                    print(f"Warning: No 'Close' column for {ticker} (tried {attempt_ticker})")
                    return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
                
                s = df["Close"].copy()
                s.index = pd.to_datetime(s.index)
                if len(s) > 0:
                    return s
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                # Only print error on last attempt of last ticker alternative
                if attempt_ticker == ticker_list[-1] and attempt == max_retries - 1:
                    print(f"Warning: Failed to download {ticker} after {max_retries} attempts (tried: {', '.join(ticker_list)})")
    
    return pd.Series(dtype=float, index=pd.DatetimeIndex([]))

