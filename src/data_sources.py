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


def yf_series(ticker: str, start_date: str) -> pd.Series:
    try:
        df = yf.download(ticker, start=start_date, auto_adjust=True, progress=False)
        if df.empty:
            print(f"Warning: No data for {ticker}")
            return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
        if "Close" not in df.columns:
            print(f"Warning: No 'Close' column for {ticker}")
            return pd.Series(dtype=float, index=pd.DatetimeIndex([]))
        s = df["Close"].copy()
        s.index = pd.to_datetime(s.index)
        return s
    except Exception as e:
        print(f"Error downloading {ticker}: {e}")
        return pd.Series(dtype=float, index=pd.DatetimeIndex([]))

