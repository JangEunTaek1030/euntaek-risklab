from __future__ import annotations

import numpy as np
import pandas as pd

from src.strategies.base import BaseStrategy


class VolatilityTargetStrategy(BaseStrategy):
    name = "volatility_target"

    def __init__(self, target_annual_vol: float = 0.12, max_leverage: float = 1.5) -> None:
        self.target_annual_vol = target_annual_vol
        self.max_leverage = max_leverage

    def generate_weights(self, returns: pd.DataFrame) -> pd.DataFrame:
        base_weights = pd.DataFrame(1.0 / returns.shape[1], index=returns.index, columns=returns.columns)
        base_portfolio_returns = (returns * base_weights).sum(axis=1)
        rolling_vol = base_portfolio_returns.rolling(21).std() * np.sqrt(252)

        leverage = (self.target_annual_vol / rolling_vol).clip(upper=self.max_leverage)
        leverage = leverage.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        scaled_weights = base_weights.mul(leverage, axis=0)
        return scaled_weights.fillna(0.0)
