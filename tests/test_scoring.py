from src.evaluator.scoring import score_strategy


def test_scoring_has_components_and_final_score() -> None:
    sample_metrics = {
        "annual_return": 0.10,
        "sharpe_ratio": 1.2,
        "calmar_ratio": 0.9,
        "max_drawdown": -0.15,
        "historical_cvar_95": -0.02,
        "average_turnover": 0.12,
    }
    scored = score_strategy(sample_metrics)
    assert "final_score" in scored
    assert "sharpe_score" in scored
    assert "drawdown_penalty" in scored
