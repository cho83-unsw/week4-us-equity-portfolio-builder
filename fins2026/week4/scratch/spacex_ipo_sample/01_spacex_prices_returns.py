"""SpaceX IPO, part 1: download the hourly SPCX price, plot it, and compute returns.

SpaceX (ticker SPCX) was the largest stock-market debut in history. It priced at
$135 per share on 11 June 2026 and began trading on the Nasdaq on 12 June 2026.
This script downloads the HOURLY price of SPCX from Yahoo Finance, plots it,
marks the $135 offer price, then computes hourly returns and plots those too.

This is the first of two scripts. Part 2 (02_spacex_data_narrative.py) reads the
file this script saves and builds the data narrative: cumulative growth of $1,
volatility, and the Sharpe ratio.

We use HOURLY bars (not daily) because SPCX has only a handful of trading days so
far, and the interesting story happens inside the trading day: the IPO "pop" from
the $135 offer price to the first public trade near $150, the intraday high near
$176, and the $160.95 first-day close.

PyCharm shortcut note:
Settings -> Keymap -> Search for -> Execute Selection in Python Console
Change it to the shortcut you want, then run this file one numbered stage at a time.
"""

from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests
import numpy as np

# Where to save outputs. This works two ways: running the whole file (the green Play
# button defines __file__) and sending a highlighted block to the Python Console (no
# __file__, so we fall back to the working directory and step into this script's folder
# when we can find it). Both are absolute paths, so neither nests, on Mac or Windows.
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
# 1. Download the hourly SpaceX price from Yahoo Finance
# -----------------------------------------------------------------------------

TICKER = "SPCX"
INTERVAL = "1h"        # hourly bars. Try "5m" for finer five-minute detail.
RANGE = "1mo"          # last month covers the whole trading history so far.
OFFER_PRICE = 135.0    # the IPO offer price, set on 11 June 2026.
OFFER_DATETIME = pd.Timestamp("2026-06-11 16:00")  # priced after the close on 11 June.

# Yahoo Finance serves prices from a web address called the chart API. We send a normal
# browser User-Agent so Yahoo does not reject us, and we try a second address if the
# first one fails.
YAHOO_ENDPOINTS = [
    "https://query2.finance.yahoo.com/v8/finance/chart/{ticker}",
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
]


def download_yahoo_intraday(ticker, interval, range_):
    """Download one ticker's intraday close prices from Yahoo and return time/close."""
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

    # Yahoo timestamps are in UTC seconds. Every SPCX bar so far is in June 2026, which is
    # entirely US Eastern Daylight Time (UTC-4), so we shift by a fixed four hours to read
    # the prices on a New York clock. A fixed offset avoids needing a timezone database,
    # which is not always installed on a minimal Python setup on Windows.
    times = pd.to_datetime(item["timestamp"], unit="s") + timedelta(hours=-4)
    close = item["indicators"]["quote"][0]["close"]
    return pd.DataFrame({"datetime": times, "close": close})


spcx = download_yahoo_intraday(TICKER, INTERVAL, RANGE)

print(f"Downloaded {TICKER}: {len(spcx):,} hourly bars")
print("\nFirst rows")
print(spcx.head())
print("\nLast rows")
print(spcx.tail())


# -----------------------------------------------------------------------------
# 2. Clean the data
# -----------------------------------------------------------------------------

# Each bar has one timestamp (the New York hour it traded) and one close price. We make
# the price numeric, drop empty bars, remove duplicates, sort by time, and use the time
# as the index so the plots have a proper time axis.
spcx["datetime"] = pd.to_datetime(spcx["datetime"])
spcx["close"] = pd.to_numeric(spcx["close"], errors="coerce")
spcx = spcx.dropna().drop_duplicates(subset="datetime").sort_values("datetime")
spcx = spcx.set_index("datetime")

# Add the $135 IPO offer price as the very first point, P_0. SpaceX priced at $135 on the
# evening of 11 June, before any public trading began. Including it means the first return
# bar captures the IPO "pop": the jump from the offer price to the first hourly price the
# next day. Read that first bar as the offer-to-market jump, not a normal hourly move --
# most buyers could only get $135 if they were allocated shares in the IPO itself.
offer_row = pd.DataFrame({"close": [OFFER_PRICE]}, index=[OFFER_DATETIME])
offer_row.index.name = "datetime"
spcx = pd.concat([offer_row, spcx])

print("\nStage 2 checks")
print(f"Bars: {len(spcx):,}")
print(f"First bar: {spcx.index.min():%Y-%m-%d %H:%M} ET,  last bar: {spcx.index.max():%Y-%m-%d %H:%M} ET")
print(f"Trading days covered: {spcx.index.normalize().nunique()}")
print(f"Lowest price: ${spcx['close'].min():,.2f},  highest price: ${spcx['close'].max():,.2f}")

price = spcx["close"]


# -----------------------------------------------------------------------------
# 3. Plot the price: a plain plot, then a Financial Times (FT) style plot
# -----------------------------------------------------------------------------

# First the plain default plot. It works, but it is busy and has no clear reference point.
plt.rcParams.update(plt.rcParamsDefault)  # start from the plain defaults

plt.figure(figsize=(10, 6))
price.plot(ax=plt.gca())
plt.title("SpaceX hourly price (SPCX)")
plt.xlabel("Date and time (ET)")
plt.ylabel("US dollars")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "01_spcx_price_plain.png", dpi=150)
plt.show()
plt.close()


def apply_ft_style():
    """Set a few rcParams so the next figure follows a clean FT-style look."""
    plt.rcParams.update({
        "figure.facecolor": "#FDF1E6", "axes.facecolor": "#FDF1E6",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": "#66605C", "axes.grid": True, "grid.color": "#E2D8CF",
        "axes.axisbelow": True, "font.family": "DejaVu Sans", "font.size": 12,
    })


def day_boundary_ticks(index):
    """Return (positions, labels) marking the first bar of each trading day, for use on a
    sequential x-axis. Plotting hourly bars in sequence (0, 1, 2, ...) instead of against
    the clock stops the chart drawing nights and weekends as straight diagonal lines, which
    would wrongly look like the price moved while the market was closed."""
    positions, labels, last_day = [], [], None
    for i, timestamp in enumerate(index):
        if timestamp.date() != last_day:
            positions.append(i)
            labels.append(timestamp.strftime("%d %b"))
            last_day = timestamp.date()
    return positions, labels


FT_MAROON = "#990F3D"  # the Financial Times signature colour

apply_ft_style()
bar_positions = range(len(price))
tick_positions, tick_labels = day_boundary_ticks(price.index)
# Drop the offer-price tick at position 0; otherwise its "11 Jun" label collides with the
# "12 Jun" label one bar to its right. The offer point is already marked by the dashed line.
if tick_positions and tick_positions[0] == 0:
    tick_positions, tick_labels = tick_positions[1:], tick_labels[1:]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(bar_positions, price.values, color=FT_MAROON, linewidth=1.8)
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels)
ax.grid(axis="x", visible=False)
# Draw the $135 offer price as a flat reference line. The gap between this line and the
# first traded price is the IPO "pop".
ax.axhline(OFFER_PRICE, color="#0F5499", linewidth=1.2, linestyle="--")
ax.annotate("  $135 offer price", xy=(0, OFFER_PRICE),
            color="#0F5499", fontsize=10, va="bottom")
# Label the latest value directly on the line instead of using a legend.
ax.annotate(f"  ${price.iloc[-1]:,.2f}", xy=(len(price) - 1, price.iloc[-1]),
            color=FT_MAROON, fontweight="bold", va="center")
fig.text(0.012, 0.96, "SpaceX after its record IPO", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, "SPCX, hourly close on the Nasdaq", fontsize=11, color="#6B625C")
fig.text(0.012, 0.01,
         f"Source: Yahoo Finance | {price.index.min():%d %b %H:%M} to {price.index.max():%d %b %H:%M} ET",
         fontsize=8, color="#6B625C")
ax.set_xlabel("")
ax.set_ylabel("")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "02_spcx_price_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 4. Compute hourly returns and plot them
# -----------------------------------------------------------------------------

# The hourly return is the percentage change in the price from one bar to the next. This
# is the series we study in part 2. Note that the return from the last bar of one day to
# the first bar of the next day spans the overnight gap, not a single hour of trading.
spcx["return"] = spcx["close"].pct_change() * 100
hourly_return = spcx["return"].dropna()

print("\nStage 4 checks")
print(f"Average hourly return: {hourly_return.mean():.3f}%")
print(f"Largest up bar: {hourly_return.max():.2f}%,  largest down bar: {hourly_return.min():.2f}%")

apply_ft_style()
ret_tick_positions, ret_tick_labels = day_boundary_ticks(hourly_return.index)
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(range(len(hourly_return)), hourly_return.values,
       width=0.8, color=np.where(hourly_return.values >= 0, "#0F5499", FT_MAROON))
ax.axhline(0.0, color="#66605C", linewidth=0.8)  # the flat level returns vary around
ax.set_xticks(ret_tick_positions)
ax.set_xticklabels(ret_tick_labels)
ax.grid(axis="x", visible=False)
fig.text(0.012, 0.96, "SpaceX hourly returns", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, "Percentage change in SPCX from one bar to the next", fontsize=11, color="#6B625C")
fig.text(0.012, 0.01, "Source: Yahoo Finance | blue = up bar, maroon = down bar", fontsize=8, color="#6B625C")
ax.set_xlabel("")
ax.set_ylabel("Per cent")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "03_spcx_returns_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 5. Save the cleaned data for the narrative script
# -----------------------------------------------------------------------------

def save_both(frame, csv_path, parquet_path):
    """Always save the CSV. Try the Parquet file too, but do not stop if the Parquet
    engine is missing on a minimal Python install -- the CSV is enough for part 2."""
    frame.to_csv(csv_path)
    try:
        frame.to_parquet(parquet_path)
    except Exception as exc:  # e.g. no pyarrow/fastparquet installed
        print(f"  (skipped {parquet_path.name}: {exc}; the CSV is saved and is enough)")


SPCX_CSV = OUTPUT_DIR / "spcx_hourly.csv"
SPCX_PARQUET = OUTPUT_DIR / "spcx_hourly.parquet"
save_both(spcx[["close", "return"]], SPCX_CSV, SPCX_PARQUET)

print("\nSaved cleaned SpaceX data")
print(SPCX_CSV)
print(SPCX_PARQUET)


# -----------------------------------------------------------------------------
# 6. Also save five-minute data for the distribution and first-day figures
# -----------------------------------------------------------------------------

# Five-minute bars give many more observations than hourly bars. Part 2 uses them for two
# things that need a lot of data points: the shape of the return distribution, and a close
# look at the first trading day. We do not add the $135 offer price here -- this file is
# the raw traded five-minute series, so the distribution reflects real trading only.
spcx_5m = download_yahoo_intraday(TICKER, "5m", RANGE)
spcx_5m["datetime"] = pd.to_datetime(spcx_5m["datetime"])
spcx_5m["close"] = pd.to_numeric(spcx_5m["close"], errors="coerce")
spcx_5m = spcx_5m.dropna().drop_duplicates(subset="datetime").sort_values("datetime").set_index("datetime")
spcx_5m["return"] = spcx_5m["close"].pct_change()

SPCX_5M_CSV = OUTPUT_DIR / "spcx_5min.csv"
SPCX_5M_PARQUET = OUTPUT_DIR / "spcx_5min.parquet"
save_both(spcx_5m[["close", "return"]], SPCX_5M_CSV, SPCX_5M_PARQUET)
print(f"\nSaved {len(spcx_5m):,} five-minute bars")
print(SPCX_5M_CSV)

print("\nSaved figures")
print(FIGURE_DIR / "01_spcx_price_plain.png")
print(FIGURE_DIR / "02_spcx_price_ft.png")
print(FIGURE_DIR / "03_spcx_returns_ft.png")
