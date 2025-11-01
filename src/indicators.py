from __future__ import annotations
import pandas as pd
import numpy as np
from .util import normalize_series


def compute_liquidity_score(walcl: pd.Series, reserves: pd.Series, w_walcl=0.45, w_res=0.55) -> float:
    walcl_n = normalize_series(walcl).iloc[-90:].mean()
    res_n = normalize_series(reserves).iloc[-90:].mean()
    score = 100 * (w_walcl * walcl_n + w_res * res_n)
    return float(np.clip(score, 0, 100))


def compute_risk_score(hyg: pd.Series, ief: pd.Series, dxy: pd.Series, w_spread=0.6, w_dxy=0.4) -> float:
    spread = hyg.pct_change(20, fill_method=None) - ief.pct_change(20, fill_method=None)
    spread_n = normalize_series(spread).iloc[-60:].mean()
    dxy_n = 1 - normalize_series(dxy).iloc[-60:].mean()  # 弱美元→风险偏好↑
    score = 100 * (w_spread * spread_n + w_dxy * dxy_n)
    return float(np.clip(score, 0, 100))


def compute_macro_weakness_score(dgs2: pd.Series, dgs10: pd.Series, copper: pd.Series, wti: pd.Series,
                                 w_curve=0.6, w_cw=0.4) -> float:
    curve = dgs10 - dgs2  # 倒挂→宏观疲弱↑
    curve_n = 1 - normalize_series(curve).iloc[-90:].mean()
    cw_ratio = (copper / wti).replace([np.inf, -np.inf], np.nan)
    cw_n = 1 - normalize_series(cw_ratio).iloc[-90:].mean()
    score = 100 * (w_curve * curve_n + w_cw * cw_n)
    return float(np.clip(score, 0, 100))

