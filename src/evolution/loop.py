from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

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
from src.evolution.candidate import StrategyCandidate
from src.evolution.generator import SearchSpace, generate_initial_population
from src.evolution.mutation import mutate_candidate
from src.evolution.selection import select_top_candidates
from src.strategies.momentum_rotation import MomentumRotationStrategy
from src.strategies.volatility_target import VolatilityTargetStrategy

ROOT = Path(__file__).resolve().parents[2]
REPORT_FILENAMES = {
    "leaderboard": "evolution_leaderboard.csv",
    "experiment_log": "evolution_experiment_log.csv",
    "summary": "best_evolved_strategy_summary.md",
}


def load_yaml(path: Path) -> dict[str, Any]:
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


def _candidate_to_strategy(candidate: StrategyCandidate) -> MomentumRotationStrategy | VolatilityTargetStrategy:
    if candidate.strategy_family == "momentum_rotation":
        return MomentumRotationStrategy(**candidate.params)
    if candidate.strategy_family == "volatility_target":
        return VolatilityTargetStrategy(**candidate.params)
    raise ValueError(f"Unsupported strategy family: {candidate.strategy_family}")


def _candidate_lookup(candidates: list[StrategyCandidate]) -> dict[str, StrategyCandidate]:
    return {candidate.candidate_id: candidate for candidate in candidates}


def _evaluate_candidate(
    candidate: StrategyCandidate,
    returns: pd.DataFrame,
    default_config: dict[str, Any],
) -> dict[str, Any]:
    strategy = _candidate_to_strategy(candidate)
    weights = strategy.generate_weights(returns)
    result = run_backtest(
        asset_returns=returns,
        weights=weights,
        initial_capital=float(default_config["initial_capital"]),
        transaction_cost_bps=float(default_config["transaction_cost_bps"]),
    )

    portfolio_returns = result["portfolio_returns"]
    metrics = compute_metrics(
        portfolio_returns,
        float(result["average_turnover"]),
        float(default_config["risk_free_rate"]),
    )
    score_details = score_strategy(metrics, default_config.get("evaluator_weights"))
    constraints = basic_metric_constraints(metrics)

    row: dict[str, Any] = {
        "candidate_id": candidate.candidate_id,
        "round_id": candidate.round_id,
        "strategy_family": candidate.strategy_family,
        "params": json.dumps(candidate.params, sort_keys=True),
        "parent_id": candidate.parent_id,
        "mutation_note": candidate.mutation_note,
    }
    row.update(metrics)
    row.update(score_details)
    row.update({f"constraint_{name}": value for name, value in constraints.items()})
    return row


def _build_next_generation(
    survivors: list[StrategyCandidate],
    search_space: SearchSpace,
    population_size: int,
    mutation_rate: float,
    round_id: int,
    random_state: random.Random,
) -> list[StrategyCandidate]:
    next_generation: list[StrategyCandidate] = []
    for idx in range(population_size):
        parent = random_state.choice(survivors)
        next_generation.append(
            mutate_candidate(
                candidate=parent,
                search_space=search_space,
                mutation_rate=mutation_rate,
                new_candidate_id=f"cand_r{round_id:02d}_{idx:03d}",
                round_id=round_id,
                random_state=random_state,
            )
        )
    return next_generation


def _save_best_summary(best_row: pd.Series, output_dir: Path) -> None:
    content = (
        "# Best Evolved Strategy Summary\n\n"
        "This report is for educational and research purposes only. It is not investment advice. "
        "The system does not predict prices; it ranks deterministic strategy configurations using "
        "backtested risk metrics and an explicit evaluator score.\n\n"
        f"- Best Candidate ID: **{best_row['candidate_id']}**\n"
        f"- Strategy Family: **{best_row['strategy_family']}**\n"
        f"- Parameters: `{best_row['params']}`\n"
        f"- Final Score: **{best_row['final_score']:.4f}**\n"
        f"- Annual Return: {best_row['annual_return']:.4f}\n"
        f"- Annual Volatility: {best_row['annual_volatility']:.4f}\n"
        f"- Sharpe Ratio: {best_row['sharpe_ratio']:.4f}\n"
        f"- Calmar Ratio: {best_row['calmar_ratio']:.4f}\n"
        f"- Max Drawdown: {best_row['max_drawdown']:.4f}\n"
        f"- Historical CVaR 95: {best_row['historical_cvar_95']:.4f}\n"
        f"- Average Turnover: {best_row['average_turnover']:.4f}\n\n"
        "## Why the evaluator selected it\n\n"
        "This candidate had the highest final score after combining reward components "
        "(Sharpe, Calmar, and annual return) with explicit penalties for drawdown, "
        "tail risk, and turnover. The selection is fully reproducible from the saved "
        "configuration and experiment log.\n\n"
        "## Disclaimer\n\n"
        "This project is an educational portfolio risk-control lab. It is not a trading system, "
        "does not forecast asset prices, and should not be used as investment advice.\n"
    )
    (output_dir / REPORT_FILENAMES["summary"]).write_text(content, encoding="utf-8")


def run_evolution_loop(
    root: Path = ROOT,
    default_config_path: Path | None = None,
    evolution_config_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run deterministic evaluator-driven strategy evolution and write Stage 2 reports."""
    default_config_path = default_config_path or root / "config" / "default.yaml"
    evolution_config_path = evolution_config_path or root / "config" / "evolution.yaml"
    output_dir = output_dir or root / "reports"

    default_config = load_yaml(default_config_path)
    evolution_config = load_yaml(evolution_config_path)
    universe = load_yaml(root / "config" / "asset_universe.yaml")

    random_seed = int(evolution_config["random_seed"])
    n_rounds = int(evolution_config["n_rounds"])
    population_size = int(evolution_config["population_size"])
    top_k_survivors = int(evolution_config["top_k_survivors"])
    mutation_rate = float(evolution_config["mutation_rate"])
    search_space: SearchSpace = evolution_config["search_space"]

    if n_rounds <= 0:
        raise ValueError("n_rounds must be positive")
    if top_k_survivors > population_size:
        raise ValueError("top_k_survivors cannot exceed population_size")

    loader = MarketDataLoader(root / "data" / "raw", root / "data" / "processed")
    prices = loader.load_prices(universe["assets"], default_config["start_date"], default_config["end_date"])
    returns = loader.build_returns(prices)

    random_state = random.Random(random_seed)
    population = generate_initial_population(search_space, population_size, random_seed)
    experiment_rows: list[dict[str, Any]] = []

    for round_id in range(n_rounds):
        round_rows = [_evaluate_candidate(candidate, returns, default_config) for candidate in population]
        experiment_rows.extend(round_rows)

        if round_id == n_rounds - 1:
            continue

        round_results = pd.DataFrame(round_rows)
        survivor_rows = select_top_candidates(round_results, top_k_survivors)
        current_candidates = _candidate_lookup(population)
        survivors = [current_candidates[candidate_id] for candidate_id in survivor_rows["candidate_id"]]
        population = _build_next_generation(
            survivors=survivors,
            search_space=search_space,
            population_size=population_size,
            mutation_rate=mutation_rate,
            round_id=round_id + 1,
            random_state=random_state,
        )

    experiment_log = pd.DataFrame(experiment_rows)
    leaderboard = experiment_log.sort_values("final_score", ascending=False).reset_index(drop=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    leaderboard.to_csv(output_dir / REPORT_FILENAMES["leaderboard"], index=False)
    experiment_log.to_csv(output_dir / REPORT_FILENAMES["experiment_log"], index=False)
    best_row = leaderboard.iloc[0]
    _save_best_summary(best_row, output_dir)

    return {
        "leaderboard": leaderboard,
        "experiment_log": experiment_log,
        "best": best_row,
        "report_paths": {
            "leaderboard": output_dir / REPORT_FILENAMES["leaderboard"],
            "experiment_log": output_dir / REPORT_FILENAMES["experiment_log"],
            "summary": output_dir / REPORT_FILENAMES["summary"],
        },
    }
