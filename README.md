# Fed Liquidity & Rates Monitor

Automated dashboard tracking the Fed balance sheet, reserves, UST curve, USD, credit spreads, and commodities. It computes three headline scores to frame risk-taking vs. caution.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # paste your FRED key
python -m src.main
```
Outputs land in `outputs/`.

## Scores (0–100)
- **LiquidityScore**: ↑ when WALCL & WRESBAL trend up
- **RiskScore**: ↑ when HYG>IEF (spread up) & USD weakens
- **MacroWeaknessScore**: ↑ when curve inversion deepens & Copper/WTI deteriorates

> These are heuristic composites meant for monitoring, not signals.

## Customize
- Edit `config.yaml` weights and tickers
- Swap DXY ticker to `^DXY` if `DX-Y.NYB` is unavailable in your region

## Caveats
- FRED daily series often contain gaps → we interpolate to daily
- yfinance data is subject to vendor changes
- This is **not** investment advice
