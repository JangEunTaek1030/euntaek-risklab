from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

from src.data.data_validator import validate_prices, validate_returns


class MarketDataLoader:
    def __init__(self, raw_path: Path, processed_path: Path) -> None:
        self.raw_path = raw_path
        self.processed_path = processed_path
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def load_prices(self, tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        prices_file = self.raw_path / "prices.csv"
        if prices_file.exists():
            prices = pd.read_csv(prices_file, index_col=0, parse_dates=True)
        else:
            downloaded = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
            )
            if "Close" in downloaded.columns:
                prices = downloaded["Close"].copy()
            else:
                prices = downloaded.copy()
            if isinstance(prices, pd.Series):
                prices = prices.to_frame(name=tickers[0])
            prices = prices.dropna(how="all")
            prices.to_csv(prices_file)

        prices = prices.sort_index().ffill().dropna(how="any")
        validate_prices(prices)
        return prices

    def build_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        returns = prices.pct_change().dropna(how="any")
        validate_returns(returns)
        returns_file = self.processed_path / "returns.csv"
        returns.to_csv(returns_file)
        return returns
