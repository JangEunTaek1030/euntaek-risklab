from __future__ import annotations

import pandas as pd


def select_top_candidates(results_df: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """Return the highest-scoring candidates by deterministic evaluator score."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if "final_score" not in results_df.columns:
        raise ValueError("results_df must include final_score")
    return results_df.sort_values("final_score", ascending=False).head(top_k).reset_index(drop=True)
