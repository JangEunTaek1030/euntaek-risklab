from __future__ import annotations

import pandas as pd


class DataValidationError(ValueError):
    """Raised when market data fails validation checks."""


def validate_prices(prices: pd.DataFrame) -> None:
    if prices.empty:
        raise DataValidationError("Price dataframe is empty.")
    if prices.isna().any().any():
        missing_count = int(prices.isna().sum().sum())
        raise DataValidationError(f"Price dataframe has {missing_count} missing values.")


def validate_returns(returns: pd.DataFrame) -> None:
    if returns.empty:
        raise DataValidationError("Returns dataframe is empty.")
    if returns.isna().any().any():
        missing_count = int(returns.isna().sum().sum())
        raise DataValidationError(f"Returns dataframe has {missing_count} missing values.")
