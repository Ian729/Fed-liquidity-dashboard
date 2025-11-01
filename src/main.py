from __future__ import annotations
import os
import yaml
import pandas as pd
from datetime import datetime, timezone
from .data_sources import fred_series, yf_series
from .indicators import compute_liquidity_score, compute_risk_score, compute_macro_weakness_score
from .reporting import write_dashboard, line_chart, md_kv
from .util import recent_start, ensure_dir

ROOT = os.path.dirname(os.path.dirname(__file__))


def load_config():
    with open(os.path.join(ROOT, "config.yaml"), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    start_date = recent_start(cfg.get("start_days_ago", 1200))
    out_dir = os.path.join(ROOT, cfg.get("output_dir", "outputs"))
    charts_dir = os.path.join(out_dir, "charts")

    # --- Fetch data ---
    fred_ids = cfg["series"]["fred"]
    yfs = cfg["series"]["yfinance"]

    WALCL = fred_series(fred_ids["WALCL"], start_date)
    WRESBAL = fred_series(fred_ids["WRESBAL"], start_date)
    DGS2 = fred_series(fred_ids["DGS2"], start_date)
    DGS10 = fred_series(fred_ids["DGS10"], start_date)

    DXY = yf_series(yfs["DXY"], start_date)
    HYG = yf_series(yfs["HYG"], start_date)
    IEF = yf_series(yfs["IEF"], start_date)
    COPPER = yf_series(yfs["COPPER"], start_date)
    WTI = yf_series(yfs["WTI"], start_date)

    # Align indices (daily)
    all_series = [WALCL, WRESBAL, DGS2, DGS10, DXY, HYG, IEF, COPPER, WTI]
    valid_starts = [s.index.min() for s in all_series if not s.empty]
    if not valid_starts:
        raise ValueError("All data series are empty. Check your API keys and data sources.")
    idx = pd.date_range(start=min(valid_starts),
                        end=datetime.now(timezone.utc).date(), freq="D")
    series = lambda s: s.reindex(idx).interpolate(limit_direction="both")

    WALCL, WRESBAL, DGS2, DGS10 = map(series, [WALCL, WRESBAL, DGS2, DGS10])
    DXY, HYG, IEF, COPPER, WTI = map(series, [DXY, HYG, IEF, COPPER, WTI])

    # --- Scores ---
    liq = compute_liquidity_score(WALCL, WRESBAL,
                                  cfg["scoring"]["liquidity"]["walcl_weight"],
                                  cfg["scoring"]["liquidity"]["reserves_weight"])

    risk = compute_risk_score(HYG, IEF, DXY,
                              cfg["scoring"]["risk"]["hyg_ief_weight"],
                              cfg["scoring"]["risk"]["dxy_weight"])

    macro = compute_macro_weakness_score(DGS2, DGS10, COPPER, WTI,
                                         cfg["scoring"]["macro_weakness"]["curve_weight"],
                                         cfg["scoring"]["macro_weakness"]["copper_wti_weight"])

    # --- Charts ---
    ensure_dir(charts_dir)
    charts = {
        "Fed Total Assets (WALCL)": line_chart(WALCL, "Fed Total Assets (WALCL)", os.path.join(charts_dir, "walcl.png")),
        "Reserve Balances (WRESBAL)": line_chart(WRESBAL, "Reserve Balances (WRESBAL)", os.path.join(charts_dir, "wresbal.png")),
        "UST 2Y vs 10Y": line_chart(DGS10 - DGS2, "UST 10Y-2Y (Curve)", os.path.join(charts_dir, "curve.png")),
        "DXY": line_chart(DXY, "DXY (Dollar Index)", os.path.join(charts_dir, "dxy.png")),
        "HYG-IEF Spread (20D Δ)": line_chart((HYG.pct_change(20, fill_method=None) - IEF.pct_change(20, fill_method=None)),
                                            "HYG-IEF 20D Spread", os.path.join(charts_dir, "spread.png")),
        "Copper/WTI": line_chart(COPPER / WTI, "Copper / WTI", os.path.join(charts_dir, "copper_wti.png")),
    }

    sections = {
        "Headline Scores": md_kv({
            "LiquidityScore": liq,
            "RiskScore": risk,
            "MacroWeaknessScore": macro,
        }) + "\n\n> 0–100 越高表示该维度越强（弱美元、信用利差收窄→RiskScore上升；曲线倒挂更深→MacroWeakness上升）。",
        "Key Charts": "\n" + "\n".join([f"![]({p})" for p in charts.values()]),
        "Notes": (
            "- WALCL/WRESBAL 趋势可与市场风格切换对照\n"
            "- DXY 走弱常配合风险资产走强；反之亦然\n"
            "- 10Y-2Y 倒挂加深往往对应宏观警示\n"
        )
    }

    md_path = write_dashboard(out_dir, sections)
    print(f"Successfully wrote dashboard: {md_path}")


if __name__ == "__main__":
    main()

