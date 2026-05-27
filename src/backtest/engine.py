from __future__ import annotations

import pandas as pd


def run_backtest(
    asset_returns: pd.DataFrame,
    weights: pd.DataFrame,
    initial_capital: float,
    transaction_cost_bps: float,
) -> dict[str, pd.Series | float]:
    aligned_weights = weights.reindex(asset_returns.index).fillna(0.0)
    shifted_weights = aligned_weights.shift(1).fillna(0.0)

    gross_returns = (shifted_weights * asset_returns).sum(axis=1)
    turnover_series = aligned_weights.diff().abs().sum(axis=1).fillna(0.0)
    transaction_cost = turnover_series * (transaction_cost_bps / 10000.0)
    net_returns = gross_returns - transaction_cost

    equity_curve = initial_capital * (1 + net_returns).cumprod()
    drawdown_curve = equity_curve / equity_curve.cummax() - 1.0

    return {
        "portfolio_returns": net_returns,
        "equity_curve": equity_curve,
        "drawdown_curve": drawdown_curve,
        "average_turnover": float(turnover_series.mean()),
    }
