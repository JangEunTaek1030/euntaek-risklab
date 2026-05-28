from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_MEMO_SECTIONS = [
    "Executive Summary",
    "Best Strategy Configuration",
    "Why the Evaluator Selected It",
    "Risk-Adjusted Performance Review",
    "Drawdown and Tail Risk Discussion",
    "Turnover and Implementation Considerations",
    "Limitations",
    "Next Steps for Productization",
    "Disclaimer: educational only, not investment advice",
]

DEFAULT_TOP_ROWS = 10


def load_evolution_results(
    leaderboard_path: Path | str,
    experiment_log_path: Path | str,
    best_summary_path: Path | str,
) -> dict[str, Any]:
    """Load deterministic Stage 2 reports that will be used as memo inputs."""
    leaderboard_file = Path(leaderboard_path)
    experiment_log_file = Path(experiment_log_path)
    best_summary_file = Path(best_summary_path)

    return {
        "leaderboard": pd.read_csv(leaderboard_file),
        "experiment_log": pd.read_csv(experiment_log_file),
        "best_summary": best_summary_file.read_text(encoding="utf-8"),
        "source_paths": {
            "leaderboard": leaderboard_file,
            "experiment_log": experiment_log_file,
            "best_summary": best_summary_file,
        },
    }

def _safe_markdown_table(frame: pd.DataFrame, max_rows: int = DEFAULT_TOP_ROWS) -> str:
    if frame.empty:
        return "No rows available."

    display = frame.head(max_rows).copy()
    display.columns = [str(column) for column in display.columns]
    display = display.astype(str)

    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in display.to_numpy()]

    return "\n".join([header, separator, *rows])


def _format_metric_summary(experiment_log: pd.DataFrame) -> str:
    if experiment_log.empty:
        return "No experiment log rows were available."

    fields = [
        "final_score",
        "annual_return",
        "annual_volatility",
        "sharpe_ratio",
        "sortino_ratio",
        "calmar_ratio",
        "max_drawdown",
        "historical_var_95",
        "historical_cvar_95",
        "average_turnover",
    ]
    available_fields = [field for field in fields if field in experiment_log.columns]
    if not available_fields:
        return "No standard metric columns were available in the experiment log."

    summary = experiment_log[available_fields].describe().loc[
        ["mean", "std", "min", "max"]
    ]
    return _safe_markdown_table(summary.reset_index(names="stat"), max_rows=len(summary))


def _format_round_summary(experiment_log: pd.DataFrame) -> str:
    required_columns = {"round_id", "candidate_id", "final_score"}
    if experiment_log.empty or not required_columns.issubset(experiment_log.columns):
        return "Round-level winner data is unavailable."

    top_by_round = (
        experiment_log.sort_values(["round_id", "final_score"], ascending=[True, False])
        .groupby("round_id", as_index=False)
        .head(1)
    )
    columns = [
        column
        for column in [
            "round_id",
            "candidate_id",
            "strategy_family",
            "params",
            "final_score",
            "sharpe_ratio",
            "max_drawdown",
            "historical_cvar_95",
            "average_turnover",
        ]
        if column in top_by_round.columns
    ]
    return _safe_markdown_table(top_by_round[columns], max_rows=len(top_by_round))


def build_memo_prompt(
    leaderboard: pd.DataFrame,
    experiment_log: pd.DataFrame,
    best_summary: str,
    top_n: int = DEFAULT_TOP_ROWS,
) -> str:
    """Build a constrained prompt from deterministic Stage 2 report artifacts only."""
    sections = "\n".join(f"- {section}" for section in REQUIRED_MEMO_SECTIONS)
    top_leaderboard = _safe_markdown_table(leaderboard, max_rows=top_n)
    metric_summary = _format_metric_summary(experiment_log)
    round_summary = _format_round_summary(experiment_log)
    candidate_count = len(experiment_log)
    best_candidate = "unavailable"
    if not leaderboard.empty and "candidate_id" in leaderboard.columns:
        best_candidate = str(leaderboard.iloc[0]["candidate_id"])

    return f"""You are writing an institutional-style portfolio risk memo for Euntaek RiskLab.

Use only the deterministic Stage 2 artifacts supplied below. Do not add external market data, do not infer unstated live prices, and do not invent performance numbers. Strategy quality has already been determined by deterministic backtests, explicit risk metrics, constraints, and the evaluator score. Your role is only to explain the saved results clearly.

Important guardrails:
- Do not claim that the system predicts prices.
- Do not describe the output as trading signals.
- Do not present the memo as investment advice.
- Do not say the LLM selected the strategy; the deterministic evaluator selected it.
- State that this is educational and research oriented.

Required memo sections:
{sections}

Deterministic report context:
- Best candidate from leaderboard: {best_candidate}
- Candidates evaluated in experiment log: {candidate_count}

Saved best evolved strategy summary:
{best_summary.strip()}

Top {top_n} rows from saved evolution leaderboard:
{top_leaderboard}

Experiment-log metric distribution from saved deterministic report:
{metric_summary}

Top candidate by evolution round from saved experiment log:
{round_summary}

Write the memo in Markdown. Use a sober institutional risk-review tone. Keep conclusions tied to the deterministic evaluator outputs. Include the exact disclaimer section requested above.
"""


def generate_ai_risk_memo(
    leaderboard_path: Path | str,
    experiment_log_path: Path | str,
    best_summary_path: Path | str,
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    model: str = "deepseek-chat",
    output_path: Path | str | None = None,
    temperature: float = 0.2,
) -> str:
    """Generate an AI-written memo using only saved deterministic Stage 2 reports."""
    results = load_evolution_results(leaderboard_path, experiment_log_path, best_summary_path)
    prompt = build_memo_prompt(
        leaderboard=results["leaderboard"],
        experiment_log=results["experiment_log"],
        best_summary=results["best_summary"],
    )

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a risk-reporting assistant. You explain deterministic "
                    "backtest results and never provide investment advice."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    content = response.choices[0].message.content or ""
    if "not investment advice" not in content.lower():
        content = (
            content.rstrip()
            + "\n\n## Disclaimer: educational only, not investment advice"
            + "\n\nThis memo is for educational and research purposes only. "
            + "It is not investment advice."
        )

    if output_path is not None:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")

    return content
