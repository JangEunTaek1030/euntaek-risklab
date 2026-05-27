from __future__ import annotations

import pandas as pd

from src.strategies.base import BaseStrategy


class EqualWeightStrategy(BaseStrategy):
    name = "equal_weight"

    def generate_weights(self, returns: pd.DataFrame) -> pd.DataFrame:
        n_assets = returns.shape[1]
        weights = pd.DataFrame(1.0 / n_assets, index=returns.index, columns=returns.columns)
        return weights
