from __future__ import annotations

from pathlib import Path

import pandas as pd


def save_leaderboard(leaderboard: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    leaderboard.to_csv(output_dir / "leaderboard.csv", index=False)


def save_best_summary(best_row: pd.Series, output_dir: Path) -> None:
    content = (
        "# Best Strategy Summary\n\n"
        "This report is for educational and research purposes only. "
        "It is not investment advice.\n\n"
        f"- Strategy: **{best_row['strategy']}**\n"
        f"- Final Score: **{best_row['final_score']:.4f}**\n"
        f"- Annual Return: {best_row['annual_return']:.4f}\n"
        f"- Annual Volatility: {best_row['annual_volatility']:.4f}\n"
        f"- Sharpe Ratio: {best_row['sharpe_ratio']:.4f}\n"
        f"- Max Drawdown: {best_row['max_drawdown']:.4f}\n"
    )
    (output_dir / "best_strategy_summary.md").write_text(content, encoding="utf-8")
