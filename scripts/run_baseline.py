from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.backtest.engine import run_backtest
from src.data.market_data_loader import MarketDataLoader
from src.evaluator.constraints import basic_metric_constraints
from src.evaluator.metrics import (
    annual_return,
    annual_volatility,
    calmar_ratio,
    historical_cvar_95,
    historical_var_95,
    max_drawdown,
    sharpe_ratio,
    sortino_ratio,
)
from src.evaluator.scoring import score_strategy
from src.reporting.charts import save_curve_tables
from src.reporting.summary import save_best_summary, save_leaderboard
from src.strategies.equal_weight import EqualWeightStrategy
from src.strategies.momentum_rotation import MomentumRotationStrategy
from src.strategies.volatility_target import VolatilityTargetStrategy


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_metrics(portfolio_returns: pd.Series, avg_turnover: float, risk_free_rate: float) -> dict[str, float]:
    return {
        "annual_return": annual_return(portfolio_returns),
        "annual_volatility": annual_volatility(portfolio_returns),
        "sharpe_ratio": sharpe_ratio(portfolio_returns, risk_free_rate),
        "sortino_ratio": sortino_ratio(portfolio_returns, risk_free_rate),
        "max_drawdown": max_drawdown(portfolio_returns),
        "calmar_ratio": calmar_ratio(portfolio_returns),
        "historical_var_95": historical_var_95(portfolio_returns),
        "historical_cvar_95": historical_cvar_95(portfolio_returns),
        "average_turnover": avg_turnover,
    }


def main() -> None:
    config = load_yaml(ROOT / "config" / "default.yaml")
    universe = load_yaml(ROOT / "config" / "asset_universe.yaml")

    tickers = universe["assets"]
    loader = MarketDataLoader(ROOT / "data" / "raw", ROOT / "data" / "processed")

    prices = loader.load_prices(tickers, config["start_date"], config["end_date"])
    returns = loader.build_returns(prices)

    strategies = [
        EqualWeightStrategy(),
        MomentumRotationStrategy(**config["strategy_params"]["momentum_rotation"]),
        VolatilityTargetStrategy(**config["strategy_params"]["volatility_target"]),
    ]

    rows: list[dict[str, float | str]] = []
    equity_curves: dict[str, pd.Series] = {}
    drawdown_curves: dict[str, pd.Series] = {}

    for strategy in strategies:
        weights = strategy.generate_weights(returns)
        result = run_backtest(
            asset_returns=returns,
            weights=weights,
            initial_capital=float(config["initial_capital"]),
            transaction_cost_bps=float(config["transaction_cost_bps"]),
        )

        portfolio_returns = result["portfolio_returns"]
        metrics = compute_metrics(portfolio_returns, float(result["average_turnover"]), float(config["risk_free_rate"]))
        score_details = score_strategy(metrics)
        constraints = basic_metric_constraints(metrics)

        row = {"strategy": strategy.name, **metrics, **score_details}
        row.update({f"constraint_{k}": v for k, v in constraints.items()})
        rows.append(row)

        equity_curves[strategy.name] = result["equity_curve"]
        drawdown_curves[strategy.name] = result["drawdown_curve"]

    leaderboard = pd.DataFrame(rows).sort_values("final_score", ascending=False).reset_index(drop=True)

    output_dir = ROOT / "reports"
    save_leaderboard(leaderboard, output_dir)
    save_best_summary(leaderboard.iloc[0], output_dir)
    save_curve_tables(pd.DataFrame(equity_curves), pd.DataFrame(drawdown_curves), output_dir)

    print("Baseline run complete. Reports saved to ./reports")


if __name__ == "__main__":
    main()
