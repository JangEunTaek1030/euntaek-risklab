from __future__ import annotations

import importlib
from pathlib import Path

import pandas as pd


def test_streamlit_app_imports_without_optional_ui_dependencies() -> None:
    module = importlib.import_module("app.streamlit_app")

    assert module.ROOT.exists()


def test_load_optional_csv_reports_clear_missing_guidance(tmp_path: Path) -> None:
    from app.streamlit_app import load_optional_csv

    data, warning = load_optional_csv("leaderboard.csv", reports_dir=tmp_path)

    assert data is None
    assert warning == "Missing reports/leaderboard.csv. Run `python scripts/run_baseline.py` to generate it."


def test_load_optional_csv_reads_existing_report(tmp_path: Path) -> None:
    from app.streamlit_app import load_optional_csv

    report_path = tmp_path / "leaderboard.csv"
    pd.DataFrame([{"strategy": "Equal Weight", "final_score": 1.0}]).to_csv(report_path, index=False)

    data, warning = load_optional_csv("leaderboard.csv", reports_dir=tmp_path)

    assert warning is None
    assert data is not None
    assert data.loc[0, "strategy"] == "Equal Weight"
