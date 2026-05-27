from __future__ import annotations


def basic_metric_constraints(metrics: dict[str, float]) -> dict[str, bool]:
    return {
        "finite_sharpe": abs(metrics.get("sharpe_ratio", 0.0)) < 1000,
        "drawdown_within_bounds": -1.0 <= metrics.get("max_drawdown", -1.0) <= 0.0,
        "non_negative_turnover": metrics.get("average_turnover", 0.0) >= 0.0,
    }
