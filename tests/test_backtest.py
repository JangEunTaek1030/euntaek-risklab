import pandas as pd

from src.backtest.engine import run_backtest


def test_backtest_outputs_non_empty_series() -> None:
    idx = pd.date_range("2024-01-01", periods=5, freq="B")
    asset_returns = pd.DataFrame(
        {
            "SPY": [0.001, -0.002, 0.003, 0.002, -0.001],
            "QQQ": [0.002, -0.001, 0.001, 0.003, -0.002],
        },
        index=idx,
    )
    weights = pd.DataFrame(0.5, index=idx, columns=asset_returns.columns)

    result = run_backtest(asset_returns, weights, initial_capital=1000, transaction_cost_bps=5)
    assert not result["portfolio_returns"].empty
    assert not result["equity_curve"].empty
