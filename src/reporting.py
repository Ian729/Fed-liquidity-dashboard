from __future__ import annotations
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from .util import ensure_dir

plt.rcParams.update({"figure.figsize": (9, 4), "figure.dpi": 140})


def line_chart(series: pd.Series, title: str, outpath: str) -> str:
    ensure_dir(os.path.dirname(outpath))
    fig = plt.figure()
    data = series.dropna()
    if len(data) > 0:
        data.plot()
    else:
        # Handle empty series
        plt.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=plt.gca().transAxes)
    plt.title(title)
    plt.tight_layout()
    fig.savefig(outpath)
    plt.close(fig)
    return outpath


def write_dashboard(output_dir: str, sections: dict[str, str]) -> str:
    ensure_dir(output_dir)
    md_path = os.path.join(output_dir, "dashboard.md")
    with open(md_path, "w", encoding="utf-8") as f:
        from datetime import timezone
        f.write(f"# Daily Macro Liquidity Dashboard\n\nGenerated: {datetime.now(timezone.utc).isoformat()}Z\n")
        for h, content in sections.items():
            f.write(f"\n## {h}\n\n{content}\n")
    return md_path


def md_kv(kv: dict[str, float]) -> str:
    return "\n".join([f"- **{k}**: {v:0.1f}" for k, v in kv.items()])

