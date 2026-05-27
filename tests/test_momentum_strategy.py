import numpy as np
import pandas as pd

from src.strategies.momentum_rotation import MomentumRotationStrategy


def test_momentum_strategy_produces_non_zero_weights_after_lookback() -> None:
    idx = pd.bdate_range("2024-01-01", periods=180)
    returns = pd.DataFrame(
        {
            "SPY": np.full(len(idx), 0.001),
            "QQQ": np.full(len(idx), 0.0008),
            "TLT": np.full(len(idx), -0.0002),
        },
        index=idx,
    )

    strategy = MomentumRotationStrategy(lookback_days=63, top_k=2)
    weights = strategy.generate_weights(returns)

    assert (weights.sum(axis=1) > 0).any()
