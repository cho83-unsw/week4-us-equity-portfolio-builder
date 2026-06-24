"""SpaceX IPO, part 3: compare SpaceX against other stocks.

A +37% gain sounds huge, but was it special, or did every technology stock rise that
week? To answer that we need a benchmark. This script downloads hourly prices for SpaceX
and three comparisons over the same window and lines them up:

  - TSLA  Tesla            (Elon Musk's other big company)
  - NVDA  Nvidia           (the best-known AI chip stock)
  - QQQ   Nasdaq-100 ETF   (a fund that tracks the 100 largest Nasdaq companies, our
                            stand-in for "the technology market" as a whole)

It then builds four figures: the growth of $1 in each, a risk-return scatter, a Sharpe
ratio bar chart, and a total-return bar chart.

To compare fairly we line every stock up from the first hour SpaceX actually traded and
give each one $1 at that moment. SpaceX starts here at its first traded price, not the
$135 offer price, because no benchmark has an "offer price" to start from.

PyCharm shortcut note:
Settings -> Keymap -> Search for -> Execute Selection in Python Console
Change it to the shortcut you want, then run this file one numbered stage at a time.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

THIS_SCRIPT_FOLDER = Path("fins2026") / "week4" / "scratch" / "spacex_ipo"
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:  # no __file__ when running a highlighted selection in the console
    guess = Path.cwd() / THIS_SCRIPT_FOLDER
    BASE_DIR = guess if guess.is_dir() else Path.cwd()
OUTPUT_DIR = BASE_DIR / "output"
FIGURE_DIR = OUTPUT_DIR / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
print(f"Saving outputs to: {OUTPUT_DIR}")


# -----------------------------------------------------------------------------
# 1. Download hourly prices for SpaceX and the three benchmarks
# -----------------------------------------------------------------------------

# Each stock has a name and a colour. SpaceX is maroon and drawn thick so it stands out;
# the benchmarks are muted so the eye goes to SpaceX first.
STOCKS = {
    "SPCX": {"name": "SpaceX", "color": "#990F3D", "width": 2.4},
    "TSLA": {"name": "Tesla", "color": "#0F5499", "width": 1.4},
    "NVDA": {"name": "Nvidia", "color": "#276749", "width": 1.4},
    "QQQ": {"name": "Nasdaq-100 (QQQ)", "color": "#9C8B7A", "width": 1.4},
}
INTERVAL = "1h"
RANGE = "1mo"

YAHOO_ENDPOINTS = [
    "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}",
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
]


def download_yahoo_intraday(ticker, interval, range_):
    """Download one ticker's intraday close prices from Yahoo and return a time/close frame."""
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    params = {"interval": interval, "range": range_, "includePrePost": "false"}
    payload = None
    for endpoint in YAHOO_ENDPOINTS:
        try:
            response = session.get(endpoint.format(ticker=ticker), params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            break
        except requests.RequestException:
            continue
    if payload is None:
        raise SystemExit("Could not reach Yahoo Finance. Check your internet connection.")
    item = payload["chart"]["result"][0]
    if "timestamp" not in item:
        raise SystemExit(f"Yahoo returned no price bars for {ticker}. Is the ticker correct?")
    from datetime import timedelta
    times = pd.to_datetime(item["timestamp"], unit="s") + timedelta(hours=-4)  # UTC -> New York (EDT)
    close = item["indicators"]["quote"][0]["close"]
    return pd.Series(pd.to_numeric(close, errors="coerce"), index=times, name=ticker)


series = []
for ticker in STOCKS:
    one = download_yahoo_intraday(ticker, INTERVAL, RANGE).dropna()
    one = one[~one.index.duplicated()].sort_index()
    series.append(one)
    print(f"Downloaded {ticker}: {len(one):,} hourly bars")

# Line the four price series up on the hours they all share, then keep only the window that
# starts when SpaceX began trading. An inner join drops any hour a stock did not trade.
prices = pd.concat(series, axis=1, join="inner").dropna()
spcx_start = series[0].index.min()  # SpaceX's first traded bar
prices = prices.loc[prices.index >= spcx_start]
print(f"\nAligned window: {prices.index.min():%d %b %H:%M} to {prices.index.max():%d %b %H:%M} ET, {len(prices)} shared bars")


# -----------------------------------------------------------------------------
# 2. Growth of $1 in each stock
# -----------------------------------------------------------------------------

# Give each stock $1 at the first shared bar by dividing every price by its own first price.
# Now the lines start together at $1, so differences in height are differences in return.
growth = prices / prices.iloc[0]


def apply_ft_style():
    """Set a few rcParams so the next figure follows a clean FT-style look."""
    plt.rcParams.update({
        "figure.facecolor": "#FDF1E6", "axes.facecolor": "#FDF1E6",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": "#66605C", "axes.grid": True, "grid.color": "#E2D8CF",
        "axes.axisbelow": True, "font.family": "DejaVu Sans", "font.size": 12,
    })


def day_boundary_ticks(index):
    """Return (positions, labels) marking the first bar of each trading day, so plotting in
    sequence does not draw nights and weekends as straight diagonal price moves."""
    positions, labels, last_day = [], [], None
    for i, timestamp in enumerate(index):
        if timestamp.date() != last_day:
            positions.append(i)
            labels.append(timestamp.strftime("%d %b"))
            last_day = timestamp.date()
    return positions, labels


apply_ft_style()
tick_positions, tick_labels = day_boundary_ticks(growth.index)
fig, ax = plt.subplots(figsize=(10, 6))
for ticker, meta in STOCKS.items():
    ax.plot(range(len(growth)), growth[ticker].values,
            color=meta["color"], linewidth=meta["width"], label=meta["name"])
ax.axhline(1.0, color="#66605C", linewidth=0.8)
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels)
ax.grid(axis="x", visible=False)
ax.legend(loc="upper left", frameon=False, fontsize=11)
fig.text(0.012, 0.96, "Growth of $1 since SpaceX began trading", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, "Value of $1 invested in each stock at SpaceX's first hourly bar", fontsize=11, color="#6B625C")
fig.text(0.012, 0.01, "Source: Yahoo Finance | hourly close, regular trading hours", fontsize=8, color="#6B625C")
ax.set_xlabel("")
ax.set_ylabel("US dollars")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "07_compare_growth_of_one_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 3. Per-stock metrics: return, volatility, and Sharpe ratio
# -----------------------------------------------------------------------------

# We reuse the ideas from part 2 for every stock at once. Returns are bar-to-bar changes;
# volatility is their standard deviation; the Sharpe ratio is return per unit of risk. We
# annualize using the number of bars in an average trading day times 252 days.
returns = prices.pct_change().dropna()
bars_per_day = len(returns) / returns.index.normalize().nunique()
periods_per_year = bars_per_day * 252
ann_factor = np.sqrt(periods_per_year)

metrics = pd.DataFrame({
    "total_return_pct": (growth.iloc[-1] - 1.0) * 100,
    "vol_per_bar_pct": returns.std() * 100,
    "ann_return_pct": returns.mean() * periods_per_year * 100,
    "ann_vol_pct": returns.std() * ann_factor * 100,
})
metrics["sharpe"] = (returns.mean() * periods_per_year) / (returns.std() * ann_factor)
metrics["name"] = [STOCKS[t]["name"] for t in metrics.index]

print("\nComparison metrics (annualized figures are illustrative -- the window is only days long)")
print(metrics.round(2).to_string())


# -----------------------------------------------------------------------------
# 4. Risk-return scatter
# -----------------------------------------------------------------------------

# Each stock is one dot: risk (the typical size of an hourly move) across, reward (the total
# return over the window) up. Higher and to the left is better. SpaceX sits far to the right
# -- the biggest gain, but also by far the biggest swings. Tesla is a useful contrast: more
# risk than the Nasdaq-100 but a smaller gain, so more risk did not buy more reward here.
# Small per-bar offsets keep the labels from overlapping where two dots sit close together.
label_offsets = {  # (dx, dy) in points, and horizontal alignment
    "SPCX": (-12, 0, "right"),
    "TSLA": (12, 0, "left"),
    "NVDA": (12, -14, "left"),
    "QQQ": (12, 14, "left"),
}
apply_ft_style()
fig, ax = plt.subplots(figsize=(10, 6))
for ticker, row in metrics.iterrows():
    color = STOCKS[ticker]["color"]
    dx, dy, ha = label_offsets[ticker]
    ax.scatter(row["vol_per_bar_pct"], row["total_return_pct"], s=170, color=color, zorder=3)
    ax.annotate(row["name"], xy=(row["vol_per_bar_pct"], row["total_return_pct"]),
                xytext=(dx, dy), textcoords="offset points",
                color=color, fontsize=11, fontweight="bold", va="center", ha=ha)
ax.axhline(0.0, color="#66605C", linewidth=0.8)
ax.margins(x=0.22, y=0.22)
ax.grid(axis="x", visible=False)
fig.text(0.012, 0.96, "Risk and return since the SpaceX debut", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, "Total return vs the typical size of an hourly move", fontsize=11, color="#6B625C")
fig.text(0.012, 0.01, "Source: Yahoo Finance | window starts at SpaceX's first hourly bar", fontsize=8, color="#6B625C")
ax.set_xlabel("Hourly volatility (per cent)")
ax.set_ylabel("Total return over the window (per cent)")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "08_compare_risk_return_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 5. Sharpe ratio and total-return bar charts
# -----------------------------------------------------------------------------

def bar_figure(values, title, subtitle, ylabel, filename):
    """Draw one labelled bar chart, SpaceX in maroon and the benchmarks muted."""
    apply_ft_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [STOCKS[t]["color"] for t in values.index]
    names = [STOCKS[t]["name"] for t in values.index]
    bars = ax.bar(range(len(values)), values.values, color=colors, width=0.6)
    ax.axhline(0.0, color="#66605C", linewidth=0.8)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(names)
    ax.grid(axis="x", visible=False)
    for rect, value in zip(bars, values.values):
        ax.annotate(f"{value:.2f}", xy=(rect.get_x() + rect.get_width() / 2, value),
                    ha="center", va="bottom" if value >= 0 else "top", fontsize=11, fontweight="bold")
    fig.text(0.012, 0.96, title, fontsize=15, fontweight="bold", color="#262A33")
    fig.text(0.012, 0.91, subtitle, fontsize=11, color="#6B625C")
    fig.text(0.012, 0.01, "Source: Yahoo Finance | window starts at SpaceX's first hourly bar", fontsize=8, color="#6B625C")
    ax.set_ylabel(ylabel)
    fig.subplots_adjust(top=0.86, bottom=0.10)
    fig.savefig(FIGURE_DIR / filename, dpi=150)
    plt.show()
    plt.close()
    plt.rcParams.update(plt.rcParamsDefault)


bar_figure(metrics["sharpe"], "Sharpe ratio: return per unit of risk",
           "Annualized Sharpe ratio since the SpaceX debut (risk-free = 0)", "Sharpe ratio",
           "09_compare_sharpe_ft.png")
bar_figure(metrics["total_return_pct"], "Who won the week?",
           "Total return since SpaceX's first hourly bar", "Total return (per cent)",
           "10_compare_total_return_ft.png")


# -----------------------------------------------------------------------------
# 6. Save the comparison table
# -----------------------------------------------------------------------------

METRICS_CSV = OUTPUT_DIR / "comparison_metrics.csv"
metrics.round(4).to_csv(METRICS_CSV)
print(f"\nSaved comparison table: {METRICS_CSV}")
print("Saved figures: 07_compare_growth_of_one_ft.png, 08_compare_risk_return_ft.png,")
print("               09_compare_sharpe_ft.png, 10_compare_total_return_ft.png")
