from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUTPUT_PATH = RAW_DIR / "prices.csv"

FILES = {
    "SPY": "spy_us_d.csv",
    "QQQ": "qqq_us_d.csv",
    "TLT": "tlt_us_d.csv",
    "IEF": "ief_us_d.csv",
    "GLD": "gld_us_d.csv",
    "EEM": "eem_us_d.csv",
    "VNQ": "vnq_us_d.csv",
}

START_DATE = "2018-01-01"
END_DATE = "2025-12-31"

prices = {}

for ticker, filename in FILES.items():
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing file for {ticker}: {path}")

    print(f"Reading {ticker}: {path}")

    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if "Date" not in df.columns or "Close" not in df.columns:
        raise ValueError(
            f"{filename} must contain Date and Close columns. "
            f"Found columns: {df.columns.tolist()}"
        )

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    prices[ticker] = df["Close"]

prices_df = pd.DataFrame(prices)

# Match the project config period
prices_df = prices_df.loc[START_DATE:END_DATE]

# Fill small gaps and keep only complete rows
prices_df = prices_df.ffill().dropna()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
prices_df.to_csv(OUTPUT_PATH)

print()
print(f"Saved merged prices to {OUTPUT_PATH}")
print("Preview:")
print(prices_df.head())
print(prices_df.tail())
print(f"Shape: {prices_df.shape}")
