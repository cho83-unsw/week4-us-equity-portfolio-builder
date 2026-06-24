"""Data Factory Floor, Stage 2: Feature Engineering.

From clean prices we build the numbers an analyst actually judges a stock on: returns,
volatility, the Sharpe ratio, and how stocks move together. With 50 stocks we cannot read
every number, so we rank them and show the top and bottom 10, and we group the 50 into their
10 sectors. The whole point is to learn how to evaluate risk and return across many assets.

Run 01_stage1_etl.py first. Then run this file whole, or one numbered stage at a time.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dff_helpers import (FT_BLUE, FT_GREY, FT_MAROON, TRADING_DAYS, annualized_stats,
                         apply_ft_style, ft_header, save_both)

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    guess = Path.cwd() / "fins2026" / "week4" / "scratch" / "dff_walkthrough"
    BASE_DIR = guess if guess.is_dir() else Path.cwd()
OUTPUT_DIR = BASE_DIR / "output"
FIGURE_DIR = OUTPUT_DIR / "figures"
TABLE_DIR = OUTPUT_DIR / "tables"
for folder in (FIGURE_DIR, TABLE_DIR):
    folder.mkdir(parents=True, exist_ok=True)
print(f"Saving outputs to: {OUTPUT_DIR}")


# -----------------------------------------------------------------------------
# 1. Load the clean prices and compute simple daily returns
# -----------------------------------------------------------------------------

wide = pd.read_csv(OUTPUT_DIR / "adjclose_wide.csv", index_col=0, parse_dates=True)
sector_map = pd.read_csv(OUTPUT_DIR / "sector_map.csv").set_index("ticker")["sector"]

# The simple daily return is the percentage change in the adjusted close:
#   ret_t = (P_t - P_{t-1}) / P_{t-1}
returns = wide.pct_change().dropna(how="all")

print("\nStage 2.1: returns")
print(f"Return matrix: {returns.shape[0]:,} days x {returns.shape[1]} stocks")
save_both(returns, OUTPUT_DIR / "returns_wide.csv", OUTPUT_DIR / "returns_wide.parquet")


# -----------------------------------------------------------------------------
# 2. Descriptive statistics and an outlier check
# -----------------------------------------------------------------------------

pooled = returns.stack()
print("\nStage 2.2: descriptive statistics (pooled daily returns, all stocks)")
print(f"Mean: {pooled.mean() * 100:.3f}%   Std: {pooled.std() * 100:.3f}%")
print(f"Min: {pooled.min() * 100:.1f}%   Max: {pooled.max() * 100:.1f}%   Excess kurtosis: {pooled.kurt():.1f}")

# An outlier check: count days where a stock moved more than 10% or 20%. We flag them but do
# not delete them -- in 2020 many were real (the Covid crash), not data errors.
moves_10 = int((returns.abs() > 0.10).sum().sum())
moves_20 = int((returns.abs() > 0.20).sum().sum())
print(f"Daily moves above 10%: {moves_10}   above 20%: {moves_20} (flagged, not deleted)")


# -----------------------------------------------------------------------------
# 3. Risk and return per stock; rank and show the top and bottom 10
# -----------------------------------------------------------------------------

# For each stock we annualize three numbers: return (mean x 252), volatility (std x sqrt 252),
# and the Sharpe ratio (return per unit of volatility). With 50 stocks we rank and show the
# ends of the list.
per_stock = pd.DataFrame(
    {ticker: annualized_stats(returns[ticker].dropna()) for ticker in returns.columns},
    index=["ann_return", "ann_vol", "sharpe"],
).T
per_stock["sector"] = sector_map
per_stock = per_stock.sort_values("sharpe", ascending=False)
per_stock.round(4).to_csv(TABLE_DIR / "per_stock_stats.csv")

print("\nStage 2.3: top and bottom 10 stocks by Sharpe ratio")
show = per_stock.copy()
show["ann_return"] = (show["ann_return"] * 100).round(1)
show["ann_vol"] = (show["ann_vol"] * 100).round(1)
show["sharpe"] = show["sharpe"].round(2)
print("TOP 10\n" + show.head(10).to_string())
print("\nBOTTOM 10\n" + show.tail(10).to_string())


def ranked_bar(series, title, subtitle, xlabel, filename, fmt="{:.2f}"):
    """Horizontal bar chart of the top 10 and bottom 10 of a 50-stock series."""
    ordered = series.sort_values()
    ends = pd.concat([ordered.head(10), ordered.tail(10)])
    colors = [FT_MAROON if v < 0 else FT_BLUE for v in ends.values]
    apply_ft_style()
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(range(len(ends)), ends.values, color=colors)
    ax.set_yticks(range(len(ends)))
    ax.set_yticklabels(ends.index, fontsize=9)
    ax.axvline(0.0, color="#66605C", linewidth=0.8)
    for i, v in enumerate(ends.values):
        ax.annotate(fmt.format(v), xy=(v, i), xytext=(4 if v >= 0 else -4, 0),
                    textcoords="offset points", va="center",
                    ha="left" if v >= 0 else "right", fontsize=8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(xlabel)
    ft_header(fig, title, subtitle, "Source: course equity bundle | daily adjusted close, 2020-2023")
    fig.savefig(FIGURE_DIR / filename, dpi=150)
    plt.close()
    plt.rcParams.update(plt.rcParamsDefault)


ranked_bar(per_stock["sharpe"], "Sharpe ratio: best and worst 10 of 50",
           "Annualized Sharpe ratio per stock (risk-free = 0)", "Sharpe ratio",
           "stage2_01_sharpe_top_bottom.png")
ranked_bar(per_stock["ann_vol"] * 100, "Volatility: calmest and wildest 10 of 50",
           "Annualized volatility per stock", "Annualized volatility (%)",
           "stage2_02_vol_top_bottom.png", fmt="{:.0f}%")


# -----------------------------------------------------------------------------
# 4. Risk and return across sectors
# -----------------------------------------------------------------------------

# We group the 50 stocks into their 10 sectors and average each annualized number. This asks
# a portfolio question: which kinds of business paid you for the risk you took?
by_sector = per_stock.groupby("sector")[["ann_return", "ann_vol", "sharpe"]].mean().sort_values("sharpe")
by_sector.round(4).to_csv(TABLE_DIR / "by_sector_stats.csv")
print("\nStage 2.4: risk and return by sector (average across the 5 stocks)")
print((by_sector.assign(ann_return=lambda d: (d.ann_return * 100).round(1),
                        ann_vol=lambda d: (d.ann_vol * 100).round(1),
                        sharpe=lambda d: d.sharpe.round(2))).to_string())

apply_ft_style()
fig, ax = plt.subplots(figsize=(10, 6))
colors = [FT_MAROON if v < 0 else FT_BLUE for v in by_sector["sharpe"].values]
ax.barh(range(len(by_sector)), by_sector["sharpe"].values, color=colors)
ax.set_yticks(range(len(by_sector)))
ax.set_yticklabels(by_sector.index, fontsize=10)
ax.axvline(0.0, color="#66605C", linewidth=0.8)
for i, v in enumerate(by_sector["sharpe"].values):
    ax.annotate(f"{v:.2f}", xy=(v, i), xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                va="center", ha="left" if v >= 0 else "right", fontsize=9)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Average annualized Sharpe ratio")
ft_header(fig, "Sharpe ratio by sector", "Average across the 5 stocks in each sector (risk-free = 0)",
          "Source: course equity bundle | daily adjusted close, 2020-2023")
fig.savefig(FIGURE_DIR / "stage2_03_sector_sharpe.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 5. Growth of $1 by sector
# -----------------------------------------------------------------------------

# An equal-weight basket of the 5 stocks in each sector, then the growth of $1 invested in
# each basket. This shows the whole path, not just the end point.
sector_returns = returns.T.groupby(sector_map).mean().T  # average return across each sector's stocks
sector_growth = (1.0 + sector_returns).cumprod()

apply_ft_style()
fig, ax = plt.subplots(figsize=(10, 6))
ordered_sectors = sector_growth.iloc[-1].sort_values(ascending=False).index
palette = plt.cm.tab10(np.linspace(0, 1, len(ordered_sectors)))
for color, sector in zip(palette, ordered_sectors):
    ax.plot(sector_growth.index, sector_growth[sector], color=color, linewidth=1.5, label=sector)
ax.axhline(1.0, color="#66605C", linewidth=0.8)
ax.grid(axis="x", visible=False)
ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=2)
ax.set_ylabel("Value of $1")
ft_header(fig, "Growth of $1 by sector", "Equal-weight basket of the 5 stocks in each sector",
          "Source: course equity bundle | daily adjusted close, 2020-2023")
fig.savefig(FIGURE_DIR / "stage2_04_sector_growth.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)
sector_growth.round(4).to_csv(TABLE_DIR / "sector_growth.csv")


# -----------------------------------------------------------------------------
# 6. Correlation: how the stocks move together
# -----------------------------------------------------------------------------

# Correlation measures how two stocks' returns move together, from -1 (opposite) through 0
# (unrelated) to +1 (in lock-step). It is the covariance divided by the two volatilities:
#   corr(i, j) = cov(r_i, r_j) / (sigma_i sigma_j)
# Low correlations are what makes diversification work: combining stocks that do not all move
# together lowers the risk of the whole portfolio. We order the 50 stocks by sector so the
# blocks of related companies are visible.
ordered_tickers = sector_map.sort_values().index
corr = returns[ordered_tickers].corr()
corr.round(4).to_csv(TABLE_DIR / "correlation_matrix.csv")
print(f"\nStage 2.6: correlation")
upper = corr.where(np.triu(np.ones(corr.shape, dtype=bool), k=1))
print(f"Average pairwise correlation: {upper.stack().mean():.2f}")

apply_ft_style()
fig, ax = plt.subplots(figsize=(9, 8))
image = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(ordered_tickers)))
ax.set_xticklabels(ordered_tickers, rotation=90, fontsize=5)
ax.set_yticks(range(len(ordered_tickers)))
ax.set_yticklabels(ordered_tickers, fontsize=5)
ax.grid(False)
fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Correlation")
fig.text(0.012, 0.97, "Return correlation across the 50 stocks", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.005, "Source: course equity bundle | daily returns 2020-2023, ordered by sector",
         fontsize=8, color=FT_GREY)
fig.subplots_adjust(top=0.93, bottom=0.10)
fig.savefig(FIGURE_DIR / "stage2_05_correlation.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)

print("\nSaved Stage 2 figures (stage2_01 ... stage2_05) and tables.")
