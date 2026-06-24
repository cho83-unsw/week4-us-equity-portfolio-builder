"""Data Factory Floor, Stage 1: Extract, Transform, Load (ETL).

We read the project's 50-stock equity dataset, check it, format it, and save clean tables
the later stages read. The dataset is 50 large US companies across 10 sectors, daily prices
from 2020 to 2023, downloaded once from the course data bundle by data_access.py.

This is the first of three scripts:
  01_stage1_etl.py        (this file: read, check, reshape, save)
  02_stage2_features.py   (returns, risk, Sharpe, by sector, correlation)
  03_stage3_portfolios.py (combine the 50 stocks into optimal portfolios)

PyCharm shortcut note:
Settings -> Keymap -> Search for -> Execute Selection in Python Console
Change it to the shortcut you want, then run this file one numbered stage at a time.
"""

from pathlib import Path

import pandas as pd

import data_access
from dff_helpers import save_both

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:  # no __file__ when running a highlighted selection in the console
    guess = Path.cwd() / "fins2026" / "week4" / "scratch" / "dff_walkthrough"
    BASE_DIR = guess if guess.is_dir() else Path.cwd()
OUTPUT_DIR = BASE_DIR / "output"
TABLE_DIR = OUTPUT_DIR / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)
print(f"Saving outputs to: {OUTPUT_DIR}")


# -----------------------------------------------------------------------------
# 1. Extract: load the equity data from the course bundle
# -----------------------------------------------------------------------------

# data_access downloads one public ZIP once, caches it, and reads the parquet file. We never
# commit the data; this single call gets it on any machine.
equity = data_access.load_equity_prices()

print("\nStage 1.1: extracted the raw equity panel")
print(f"Rows: {len(equity):,}")
print("Columns:", list(equity.columns))
print(equity.head(3).to_string())


# -----------------------------------------------------------------------------
# 2. Transform: check and format the data
# -----------------------------------------------------------------------------

# A market data table can carry quiet errors: wrong types, missing rows, duplicates, or
# impossible prices. We check for each one before trusting the data.
equity["date"] = pd.to_datetime(equity["date"])
for column in ["open", "high", "low", "close", "adjClose", "volume"]:
    equity[column] = pd.to_numeric(equity[column], errors="coerce")

n_missing = int(equity[["adjClose"]].isna().sum().iloc[0])
n_duplicate = int(equity.duplicated(subset=["ticker", "date"]).sum())
n_nonpositive = int((equity["adjClose"] <= 0).sum())

print("\nStage 1.2: data-quality checks")
print(f"Tickers: {equity['ticker'].nunique()}  |  Sectors: {equity['sector'].nunique()}")
print(f"Date range: {equity['date'].min():%Y-%m-%d} to {equity['date'].max():%Y-%m-%d}")
print(f"Missing adjClose: {n_missing}  |  Duplicate ticker-date rows: {n_duplicate}  |  Non-positive prices: {n_nonpositive}")

equity = equity.dropna(subset=["adjClose"]).drop_duplicates(subset=["ticker", "date"])
equity = equity.sort_values(["ticker", "date"]).reset_index(drop=True)

# A ticker -> sector lookup we will reuse in Stage 2.
sector_map = equity[["ticker", "sector"]].drop_duplicates().sort_values(["sector", "ticker"]).reset_index(drop=True)
print("\nSectors (5 stocks each):")
print(sector_map.groupby("sector")["ticker"].apply(lambda s: ", ".join(s)).to_string())


# -----------------------------------------------------------------------------
# 3. Long vs wide: two shapes for the same data
# -----------------------------------------------------------------------------

# The data arrives in LONG form: one row per ticker per day. This is tidy and flexible, and
# it is the right shape for adding a sector column or filtering. For returns and correlations
# we want WIDE form: one row per day, one column per ticker. We pivot to get it.
long_panel = equity[["date", "ticker", "adjClose", "sector"]].copy()
wide_adjclose = equity.pivot(index="date", columns="ticker", values="adjClose").sort_index()

print("\nStage 1.3: long vs wide")
print(f"Long panel: {long_panel.shape[0]:,} rows x {long_panel.shape[1]} columns (one row per ticker-day)")
print(long_panel.head(3).to_string(index=False))
print(f"\nWide adjClose: {wide_adjclose.shape[0]:,} rows x {wide_adjclose.shape[1]} columns (one row per day)")
print(wide_adjclose.iloc[:3, :5].round(2).to_string())


# -----------------------------------------------------------------------------
# 4. Load: save the clean tables for Stage 2
# -----------------------------------------------------------------------------

save_both(wide_adjclose, OUTPUT_DIR / "adjclose_wide.csv", OUTPUT_DIR / "adjclose_wide.parquet")
save_both(long_panel.set_index("date"), OUTPUT_DIR / "equity_long.csv", OUTPUT_DIR / "equity_long.parquet")
sector_map.to_csv(OUTPUT_DIR / "sector_map.csv", index=False)

inventory = pd.DataFrame({
    "item": ["stocks", "sectors", "first date", "last date", "trading days", "rows (long)"],
    "value": [equity["ticker"].nunique(), equity["sector"].nunique(),
              f"{equity['date'].min():%Y-%m-%d}", f"{equity['date'].max():%Y-%m-%d}",
              wide_adjclose.shape[0], len(equity)],
})
inventory.to_csv(TABLE_DIR / "stage1_inventory.csv", index=False)

print("\nSaved clean tables:")
print(OUTPUT_DIR / "adjclose_wide.parquet")
print(OUTPUT_DIR / "equity_long.parquet")
print(OUTPUT_DIR / "sector_map.csv")
