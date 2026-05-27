from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_curve_tables(equity_curves: pd.DataFrame, drawdown_curves: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    equity_curves.to_csv(output_dir / "equity_curves.csv")
    drawdown_curves.to_csv(output_dir / "drawdown_curves.csv")
