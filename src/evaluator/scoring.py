from __future__ import annotations

from dataclasses import dataclass

DEFAULT_WEIGHTS: dict[str, float] = {
    "sharpe_score": 0.30,
    "calmar_score": 0.20,
    "return_score": 0.15,
    "drawdown_penalty": 0.20,
    "cvar_penalty": 0.10,
    "turnover_penalty": 0.05,
}


@dataclass
class ScoreDetails:
    sharpe_score: float
    calmar_score: float
    return_score: float
    drawdown_penalty: float
    cvar_penalty: float
    turnover_penalty: float
    final_score: float


def score_strategy(metrics: dict[str, float], weights: dict[str, float] | None = None) -> dict[str, float]:
    applied_weights = {**DEFAULT_WEIGHTS, **(weights or {})}

    sharpe_score = metrics["sharpe_ratio"]
    calmar_score = metrics["calmar_ratio"]
    return_score = metrics["annual_return"]
    drawdown_penalty = abs(metrics["max_drawdown"])
    cvar_penalty = abs(metrics["historical_cvar_95"])
    turnover_penalty = metrics["average_turnover"]

    final_score = (
        applied_weights["sharpe_score"] * sharpe_score
        + applied_weights["calmar_score"] * calmar_score
        + applied_weights["return_score"] * return_score
        - applied_weights["drawdown_penalty"] * drawdown_penalty
        - applied_weights["cvar_penalty"] * cvar_penalty
        - applied_weights["turnover_penalty"] * turnover_penalty
    )

    details = ScoreDetails(
        sharpe_score=sharpe_score,
        calmar_score=calmar_score,
        return_score=return_score,
        drawdown_penalty=drawdown_penalty,
        cvar_penalty=cvar_penalty,
        turnover_penalty=turnover_penalty,
        final_score=final_score,
    )
    return details.__dict__
