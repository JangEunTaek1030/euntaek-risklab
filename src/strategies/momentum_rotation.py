from __future__ import annotations

import numpy as np
import pandas as pd

from src.strategies.base import BaseStrategy


class MomentumRotationStrategy(BaseStrategy):
    name = "momentum_rotation"

    def __init__(self, lookback_days: int = 126, top_k: int = 3) -> None:
        self.lookback_days = lookback_days
        self.top_k = top_k

    def generate_weights(self, returns: pd.DataFrame) -> pd.DataFrame:
        momentum = (1 + returns).rolling(self.lookback_days).apply(np.prod, raw=True) - 1
        rebalance_dates = returns.groupby(returns.index.to_period("M")).tail(1).index

        weights = pd.DataFrame(0.0, index=returns.index, columns=returns.columns)
        current_weights = pd.Series(0.0, index=returns.columns)

        for date in returns.index:
            if date in rebalance_dates and date in momentum.index:
                scores = momentum.loc[date].dropna().sort_values(ascending=False)
                top_assets = scores.head(self.top_k).index
                current_weights = pd.Series(0.0, index=returns.columns)
                if len(top_assets) > 0:
                    current_weights.loc[top_assets] = 1.0 / len(top_assets)
            weights.loc[date] = current_weights.values

        return weights.fillna(0.0)
