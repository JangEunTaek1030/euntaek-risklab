import pandas as pd

from src.reporting.ai_memo import REQUIRED_MEMO_SECTIONS, build_memo_prompt


def _sample_leaderboard() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "cand_r01_001",
                "strategy_family": "volatility_target",
                "params": '{"target_annual_vol": 0.1, "max_leverage": 1.5}',
                "final_score": 0.81,
                "annual_return": 0.09,
                "annual_volatility": 0.11,
                "sharpe_ratio": 0.72,
                "max_drawdown": -0.18,
                "historical_cvar_95": -0.025,
                "average_turnover": 0.04,
            }
        ]
    )


def _sample_experiment_log() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "round_id": 0,
                "candidate_id": "cand_r00_000",
                "strategy_family": "momentum_rotation",
                "params": '{"lookback_days": 63, "top_k": 3}',
                "final_score": 0.53,
                "annual_return": 0.07,
                "annual_volatility": 0.13,
                "sharpe_ratio": 0.45,
                "sortino_ratio": 0.61,
                "calmar_ratio": 0.31,
                "max_drawdown": -0.22,
                "historical_var_95": -0.018,
                "historical_cvar_95": -0.029,
                "average_turnover": 0.06,
            },
            {
                "round_id": 1,
                "candidate_id": "cand_r01_001",
                "strategy_family": "volatility_target",
                "params": '{"target_annual_vol": 0.1, "max_leverage": 1.5}',
                "final_score": 0.81,
                "annual_return": 0.09,
                "annual_volatility": 0.11,
                "sharpe_ratio": 0.72,
                "sortino_ratio": 0.95,
                "calmar_ratio": 0.50,
                "max_drawdown": -0.18,
                "historical_var_95": -0.015,
                "historical_cvar_95": -0.025,
                "average_turnover": 0.04,
            },
        ]
    )


def test_build_memo_prompt_includes_required_sections() -> None:
    prompt = build_memo_prompt(
        leaderboard=_sample_leaderboard(),
        experiment_log=_sample_experiment_log(),
        best_summary="# Best Evolved Strategy Summary\nDeterministic evaluator selected cand_r01_001.",
    )

    for section in REQUIRED_MEMO_SECTIONS:
        assert section in prompt


def test_build_memo_prompt_includes_disclaimer() -> None:
    prompt = build_memo_prompt(
        leaderboard=_sample_leaderboard(),
        experiment_log=_sample_experiment_log(),
        best_summary="# Best Evolved Strategy Summary\nEducational and research purposes only.",
    )

    assert "educational" in prompt.lower()
    assert "not investment advice" in prompt.lower()


def test_build_memo_prompt_rejects_prediction_and_advice_claims() -> None:
    prompt = build_memo_prompt(
        leaderboard=_sample_leaderboard(),
        experiment_log=_sample_experiment_log(),
        best_summary="# Best Evolved Strategy Summary\nDeterministic risk metrics only.",
    ).lower()

    assert "do not claim that the system predicts prices" in prompt
    assert "do not present the memo as investment advice" in prompt
    assert "deterministic evaluator selected" in prompt
    assert "trading signals" in prompt
