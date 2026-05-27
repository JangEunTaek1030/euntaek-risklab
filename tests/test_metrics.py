import pandas as pd

from src.evaluator import metrics


def test_metrics_outputs_numeric() -> None:
    returns = pd.Series([0.01, -0.005, 0.002, 0.004, -0.003])
    outputs = [
        metrics.annual_return(returns),
        metrics.annual_volatility(returns),
        metrics.sharpe_ratio(returns, risk_free_rate=0.01),
        metrics.sortino_ratio(returns, risk_free_rate=0.01),
        metrics.max_drawdown(returns),
        metrics.calmar_ratio(returns),
        metrics.historical_var_95(returns),
        metrics.historical_cvar_95(returns),
    ]
    assert all(isinstance(x, float) for x in outputs)
