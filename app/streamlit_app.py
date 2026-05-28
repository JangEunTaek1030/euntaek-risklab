from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

REPORT_GUIDANCE = {
    "leaderboard.csv": "python scripts/run_baseline.py",
    "equity_curves.csv": "python scripts/run_baseline.py",
    "drawdown_curves.csv": "python scripts/run_baseline.py",
    "best_strategy_summary.md": "python scripts/run_baseline.py",
    "evolution_leaderboard.csv": "python scripts/run_evolution.py",
    "evolution_experiment_log.csv": "python scripts/run_evolution.py",
    "best_evolved_strategy_summary.md": "python scripts/run_evolution.py",
    "ai_institutional_risk_memo.md": "python scripts/generate_ai_memo.py",
}

BASELINE_METRICS = [
    "final_score",
    "annual_return",
    "annual_volatility",
    "sharpe_ratio",
    "max_drawdown",
    "historical_cvar_95",
    "average_turnover",
]

EVOLUTION_COLUMNS = ["candidate_id", "strategy_family", "params", "final_score"]


def report_path(filename: str, reports_dir: Path = REPORTS_DIR) -> Path:
    """Return the expected path for a report artifact."""
    return reports_dir / filename


def load_optional_csv(filename: str, reports_dir: Path = REPORTS_DIR) -> tuple[pd.DataFrame | None, str | None]:
    """Load a report CSV when present; otherwise return a clear operator warning."""
    path = report_path(filename, reports_dir)
    if not path.exists():
        command = REPORT_GUIDANCE.get(filename, "python scripts/run_baseline.py")
        return None, f"Missing reports/{filename}. Run `{command}` to generate it."
    return pd.read_csv(path), None


def load_optional_markdown(filename: str, reports_dir: Path = REPORTS_DIR) -> tuple[str | None, str | None]:
    """Load a report Markdown file when present; otherwise return a clear operator warning."""
    path = report_path(filename, reports_dir)
    if not path.exists():
        command = REPORT_GUIDANCE.get(filename, "python scripts/run_baseline.py")
        return None, f"Missing reports/{filename}. Run `{command}` to generate it."
    return path.read_text(encoding="utf-8"), None


def available_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    """Keep requested columns that exist in a DataFrame, preserving order."""
    return [column for column in columns if column in df.columns]


def sort_by_score(df: pd.DataFrame) -> pd.DataFrame:
    """Sort report rows by final_score when that evaluator column is available."""
    if "final_score" not in df.columns:
        return df
    return df.sort_values("final_score", ascending=False).reset_index(drop=True)


def _warn_missing(st, warning: str | None) -> bool:
    if warning:
        st.warning(warning)
        return True
    return False


def _format_best_label(row: pd.Series, name_columns: Iterable[str]) -> str:
    for column in name_columns:
        if column in row and pd.notna(row[column]):
            return str(row[column])
    return "Top ranked row"


def _metric_value(row: pd.Series, column: str) -> float | str:
    value = row[column]
    if isinstance(value, float):
        return f"{value:.4f}"
    return value


def render_header(st) -> None:
    st.title("Euntaek RiskLab")
    st.subheader("Evaluator-driven AI lab for quantitative portfolio risk control")
    st.info(
        "Educational and research purpose only. This product prototype is not investment advice, "
        "does not forecast prices, and does not provide trading recommendations."
    )


def render_workflow_overview(st) -> None:
    st.header("Workflow Overview")
    col1, col2, col3 = st.columns(3)
    col1.markdown("### Stage 1\n**Deterministic Risk Evaluation**\n\nBacktest strategies and score explicit risk metrics.")
    col2.markdown("### Stage 2\n**Agentic Strategy Evolution**\n\nGenerate, evaluate, select, and mutate candidate configurations.")
    col3.markdown("### Stage 3\n**AI Risk Memo**\n\nSummarize completed deterministic reports for institutional-style review.")


def render_baseline_leaderboard(st) -> None:
    st.header("Baseline Strategy Leaderboard")
    leaderboard, warning = load_optional_csv("leaderboard.csv")
    if _warn_missing(st, warning):
        return

    assert leaderboard is not None
    leaderboard = sort_by_score(leaderboard)
    if leaderboard.empty:
        st.warning("reports/leaderboard.csv is empty. Re-run `python scripts/run_baseline.py`.")
        return

    best = leaderboard.iloc[0]
    st.success(f"Best baseline strategy: {_format_best_label(best, ['strategy'])}")

    metric_columns = available_columns(leaderboard, BASELINE_METRICS)
    metric_containers = st.columns(min(len(metric_columns), 4) or 1)
    for index, column in enumerate(metric_columns):
        metric_containers[index % len(metric_containers)].metric(column, _metric_value(best, column))

    st.dataframe(leaderboard, use_container_width=True)

    baseline_summary, summary_warning = load_optional_markdown("best_strategy_summary.md")
    if summary_warning:
        st.warning(summary_warning)
    elif baseline_summary:
        with st.expander("Baseline best strategy summary"):
            st.markdown(baseline_summary)


def render_evolution_leaderboard(st) -> None:
    st.header("Evolution Leaderboard")
    st.caption("Candidates are ranked only by deterministic evaluator score, not by an LLM.")
    leaderboard, warning = load_optional_csv("evolution_leaderboard.csv")
    if _warn_missing(st, warning):
        return

    assert leaderboard is not None
    leaderboard = sort_by_score(leaderboard)
    if leaderboard.empty:
        st.warning("reports/evolution_leaderboard.csv is empty. Re-run `python scripts/run_evolution.py`.")
        return

    best = leaderboard.iloc[0]
    st.success(f"Best evolved candidate: {_format_best_label(best, ['candidate_id'])}")
    display_columns = available_columns(leaderboard, EVOLUTION_COLUMNS)
    st.dataframe(leaderboard[display_columns] if display_columns else leaderboard, use_container_width=True)


def render_evolution_progress(st) -> None:
    st.header("Evolution Progress")
    experiment_log, warning = load_optional_csv("evolution_experiment_log.csv")
    if _warn_missing(st, warning):
        return

    assert experiment_log is not None
    required_columns = {"round_id", "final_score"}
    if experiment_log.empty or not required_columns.issubset(experiment_log.columns):
        st.warning("Evolution progress requires round_id and final_score columns. Re-run `python scripts/run_evolution.py`.")
        return

    progress = (
        experiment_log.groupby("round_id")
        .agg(best_final_score=("final_score", "max"), candidate_count=("final_score", "size"))
        .reset_index()
        .sort_values("round_id")
    )

    chart_data = progress.set_index("round_id")
    st.subheader("Best final_score by round")
    st.line_chart(chart_data["best_final_score"])
    st.subheader("Candidate count by round")
    st.bar_chart(chart_data["candidate_count"])

    top_rows = experiment_log.loc[experiment_log.groupby("round_id")["final_score"].idxmax()].sort_values("round_id")
    top_columns = available_columns(top_rows, ["round_id", "candidate_id", "strategy_family", "params", "final_score"])
    st.subheader("Top candidate per round")
    st.dataframe(top_rows[top_columns] if top_columns else top_rows, use_container_width=True)


def _prepare_curve_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    date_column = df.columns[0]
    prepared = df.copy()
    prepared[date_column] = pd.to_datetime(prepared[date_column], errors="coerce")
    prepared = prepared.dropna(subset=[date_column]).set_index(date_column)
    prepared.index.name = "date"
    return prepared


def render_risk_curves(st) -> None:
    st.header("Risk Curves")
    equity_curves, equity_warning = load_optional_csv("equity_curves.csv")
    drawdown_curves, drawdown_warning = load_optional_csv("drawdown_curves.csv")

    missing = False
    missing = _warn_missing(st, equity_warning) or missing
    missing = _warn_missing(st, drawdown_warning) or missing
    if missing:
        return

    assert equity_curves is not None and drawdown_curves is not None
    if equity_curves.empty or drawdown_curves.empty:
        st.warning("Risk curve reports are empty. Re-run `python scripts/run_baseline.py`.")
        return

    st.subheader("Equity curves")
    st.line_chart(_prepare_curve_dataframe(equity_curves))
    st.subheader("Drawdown curves")
    st.line_chart(_prepare_curve_dataframe(drawdown_curves))


def render_markdown_report(st, filename: str, title: str, note: str | None = None) -> None:
    st.header(title)
    if note:
        st.caption(note)
    content, warning = load_optional_markdown(filename)
    if _warn_missing(st, warning):
        return
    assert content is not None
    st.markdown(content)


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Euntaek RiskLab", layout="wide")
    render_header(st)
    render_workflow_overview(st)
    render_baseline_leaderboard(st)
    render_evolution_leaderboard(st)
    render_evolution_progress(st)
    render_risk_curves(st)
    render_markdown_report(st, "best_evolved_strategy_summary.md", "Best Strategy Summary")
    render_markdown_report(
        st,
        "ai_institutional_risk_memo.md",
        "AI Institutional Risk Memo",
        "Generated only after deterministic evaluation is complete; the evaluator decides strategy quality.",
    )


if __name__ == "__main__":
    main()
