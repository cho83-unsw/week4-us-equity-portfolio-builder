"""SpaceX IPO, part 2: build a data narrative from the hourly SPCX price.

This script reads the cleaned hourly file that part 1 (01_spacex_prices_returns.py)
saved, then teaches four basic ideas every market analyst uses:

  1. simple returns         -- the percentage change from one bar to the next
  2. cumulative return      -- the growth of $1 invested at the first bar
  3. volatility             -- how much the returns bounce around (annualized)
  4. the Sharpe ratio       -- return earned per unit of risk taken

Run part 1 first so the input file exists. Then run this file with the green Play
button, or send one numbered stage at a time to the Python Console.

PyCharm shortcut note:
Settings -> Keymap -> Search for -> Execute Selection in Python Console
Change it to the shortcut you want, then run this file one numbered stage at a time.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Same absolute-path setup as part 1, so outputs never nest, on Mac or Windows.
THIS_SCRIPT_FOLDER = Path("fins2026") / "week4" / "scratch" / "spacex_ipo"
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:  # no __file__ when running a highlighted selection in the console
    guess = Path.cwd() / THIS_SCRIPT_FOLDER
    BASE_DIR = guess if guess.is_dir() else Path.cwd()
OUTPUT_DIR = BASE_DIR / "output"
FIGURE_DIR = OUTPUT_DIR / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
print(f"Reading from and saving to: {OUTPUT_DIR}")


# -----------------------------------------------------------------------------
# 1. Read the cleaned hourly data from part 1
# -----------------------------------------------------------------------------

SPCX_CSV = OUTPUT_DIR / "spcx_hourly.csv"
if not SPCX_CSV.is_file():
    raise SystemExit("Could not find spcx_hourly.csv. Run 01_spacex_prices_returns.py first.")

spcx = pd.read_csv(SPCX_CSV, parse_dates=["datetime"]).set_index("datetime")
price = spcx["close"]

print(f"Loaded {len(spcx):,} hourly bars")
print(f"First bar: {price.index.min():%d %b %H:%M} ET,  last bar: {price.index.max():%d %b %H:%M} ET")

# We also load the five-minute file (saved by part 1). Stages 6 and 7 use it, because the
# return distribution and the first-day path both need many more observations than the ~34
# hourly bars give us.
SPCX_5M_CSV = OUTPUT_DIR / "spcx_5min.csv"
have_5min = SPCX_5M_CSV.is_file()
if have_5min:
    spcx_5m = pd.read_csv(SPCX_5M_CSV, parse_dates=["datetime"]).set_index("datetime")
    print(f"Loaded {len(spcx_5m):,} five-minute bars")
else:
    print("No five-minute file found; skipping stages 6 and 7. Re-run part 1 to create it.")


# -----------------------------------------------------------------------------
# 2. Simple returns
# -----------------------------------------------------------------------------

# A simple return is the fractional change in price from one bar to the next:
#   r_t = (P_t - P_{t-1}) / P_{t-1}
# We keep it as a fraction here (0.01 = 1%) so the maths in the next stages is clean.
returns = price.pct_change().dropna()

print("\nStage 2: simple hourly returns")
print(f"Number of return bars: {len(returns):,}")
print(f"Average hourly return: {returns.mean() * 100:.3f}%")
print(f"Best bar: {returns.max() * 100:.2f}%,  worst bar: {returns.min() * 100:.2f}%")


# -----------------------------------------------------------------------------
# 3. Cumulative return: the growth of $1
# -----------------------------------------------------------------------------

# If you had invested $1 at the $135 offer price and stayed invested, its value at each
# later bar is just the price divided by that first price. We plot the dollar value, which
# is always positive and easy to read: $1.20 means a 20% gain so far. The line starts at
# $1.00 at the offer and jumps with the IPO pop on the first bar. This equals the running
# product of (1 + return) -- dividing by the first price is the same thing, written shorter.
growth_of_one = price / price.iloc[0]
total_return = growth_of_one.iloc[-1] - 1.0

print("\nStage 3: growth of $1")
print(f"$1 at the $135 offer price is worth ${growth_of_one.iloc[-1]:.3f} at the last bar")
print(f"Total return over the window: {total_return * 100:.2f}%")

FT_MAROON = "#990F3D"


def apply_ft_style():
    """Set a few rcParams so the next figure follows a clean FT-style look."""
    plt.rcParams.update({
        "figure.facecolor": "#FDF1E6", "axes.facecolor": "#FDF1E6",
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": "#66605C", "axes.grid": True, "grid.color": "#E2D8CF",
        "axes.axisbelow": True, "font.family": "DejaVu Sans", "font.size": 12,
    })


def day_boundary_ticks(index):
    """Return (positions, labels) marking the first bar of each trading day. We plot the
    bars in sequence (0, 1, 2, ...) so nights and weekends do not appear as price moves."""
    positions, labels, last_day = [], [], None
    for i, timestamp in enumerate(index):
        if timestamp.date() != last_day:
            positions.append(i)
            labels.append(timestamp.strftime("%d %b"))
            last_day = timestamp.date()
    return positions, labels


apply_ft_style()
tick_positions, tick_labels = day_boundary_ticks(growth_of_one.index)
# Drop the offer-price tick at position 0 so its "11 Jun" label does not collide with "12 Jun".
if tick_positions and tick_positions[0] == 0:
    tick_positions, tick_labels = tick_positions[1:], tick_labels[1:]
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(range(len(growth_of_one)), growth_of_one.values, color=FT_MAROON, linewidth=1.8)
ax.axhline(1.0, color="#66605C", linewidth=0.8)  # the starting value of $1
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels)
ax.grid(axis="x", visible=False)
ax.annotate(f"  ${growth_of_one.iloc[-1]:.2f}", xy=(len(growth_of_one) - 1, growth_of_one.iloc[-1]),
            color=FT_MAROON, fontweight="bold", va="center")
fig.text(0.012, 0.96, "Growth of $1 invested in SpaceX", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, r"Value of \$1 invested at the \$135 offer price", fontsize=11, color="#6B625C")
fig.text(0.012, 0.01, "Source: Yahoo Finance | from the first SPCX bar onward", fontsize=8, color="#6B625C")
ax.set_xlabel("")
ax.set_ylabel("US dollars")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "04_spcx_growth_of_one_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 4. Volatility, and the annualization idea
# -----------------------------------------------------------------------------

# Volatility is the standard deviation of returns: a bigger number means the price bounces
# around more. The raw number is "per hour", which is hard to compare across assets, so we
# scale it to a yearly figure. We count how many bars fall on an average trading day, then
# assume 252 trading days in a year. Volatility scales with the square root of the number
# of periods, so the annualization factor is sqrt(bars per day x 252).
bars_per_day = len(returns) / returns.index.normalize().nunique()
periods_per_year = bars_per_day * 252
ann_factor = np.sqrt(periods_per_year)

vol_per_bar = returns.std()
vol_annual = vol_per_bar * ann_factor

print("\nStage 4: volatility")
print(f"Bars per trading day (average): {bars_per_day:.1f}")
print(f"Volatility per bar: {vol_per_bar * 100:.3f}%")
print(f"Annualized volatility: {vol_annual * 100:.1f}%")


# -----------------------------------------------------------------------------
# 5. The Sharpe ratio
# -----------------------------------------------------------------------------

# The Sharpe ratio is the average return earned per unit of risk (volatility) taken:
#   Sharpe = (average return - risk-free rate) / volatility
# It lets us compare a calm asset and a wild one on the same footing. We annualize it the
# same way: multiply the per-bar mean by the number of periods, and the per-bar volatility
# by the square root of that number.
#
# Over this very short window we set the risk-free rate to zero. For daily or longer
# horizons you would subtract the actual risk-free rate (for example the Kenneth French
# daily series used elsewhere in Week 4) before dividing.
mean_per_bar = returns.mean()
sharpe_annual = (mean_per_bar * periods_per_year) / vol_annual

print("\nStage 5: Sharpe ratio")
print(f"Annualized Sharpe ratio (risk-free = 0): {sharpe_annual:.2f}")


# -----------------------------------------------------------------------------
# 6. The first trading day, minute by minute
# -----------------------------------------------------------------------------

# The hourly chart in part 1 only had a few bars on debut day. The five-minute data shows
# the first day in much more detail: the IPO opened well above the $135 offer price and
# swung around through the session. We plot 12 June on its own.
OFFER_PRICE = 135.0
if have_5min:
    first_day = spcx_5m.loc[spcx_5m.index.normalize() == spcx_5m.index.normalize().min(), "close"]

    apply_ft_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(len(first_day)), first_day.values, color=FT_MAROON, linewidth=1.8)
    ax.axhline(OFFER_PRICE, color="#0F5499", linewidth=1.2, linestyle="--")
    ax.annotate("  $135 offer price", xy=(0, OFFER_PRICE), color="#0F5499", fontsize=10, va="bottom")
    ax.annotate(f"  first bar ${first_day.iloc[0]:,.0f}", xy=(0, first_day.iloc[0]),
                color=FT_MAROON, fontsize=10, va="center")
    ax.annotate(f"  close ${first_day.iloc[-1]:,.0f}", xy=(len(first_day) - 1, first_day.iloc[-1]),
                color=FT_MAROON, fontweight="bold", va="center")
    ax.grid(axis="x", visible=False)
    fig.text(0.012, 0.96, "SpaceX on its first trading day", fontsize=15, fontweight="bold", color="#262A33")
    fig.text(0.012, 0.91, f"SPCX, five-minute close on {first_day.index[0]:%d %B %Y}", fontsize=11, color="#6B625C")
    fig.text(0.012, 0.01, "Source: Yahoo Finance | five-minute bars, regular trading hours", fontsize=8, color="#6B625C")
    ax.set_xlabel("Five-minute bars through the day")
    ax.set_ylabel("US dollars")
    fig.subplots_adjust(top=0.86, bottom=0.10)
    fig.savefig(FIGURE_DIR / "05_spcx_first_day_ft.png", dpi=150)
    plt.show()
    plt.close()
    plt.rcParams.update(plt.rcParamsDefault)
    print("\nStage 6: first trading day")
    print(f"Debut-day five-minute bars: {len(first_day)}")
    print(f"First bar ${first_day.iloc[0]:.2f}, high ${first_day.max():.2f}, close ${first_day.iloc[-1]:.2f}")


# -----------------------------------------------------------------------------
# 7. The shape of returns: heavy tails (leptokurtosis)
# -----------------------------------------------------------------------------

# A well-known fact about stock returns is that they are NOT normally distributed. Compared
# with a bell curve, real returns have a taller peak and "heavier tails": extreme moves
# (both up and down) happen far more often than a normal distribution predicts. This shape
# is called leptokurtosis. We measure it with excess kurtosis, where a normal distribution
# scores 0 and a positive number means heavier tails.
#
# We need many observations to see the shape, so we use the five-minute returns (a few
# hundred) rather than the ~33 hourly returns (too few to judge the tails).
if have_5min:
    r5 = spcx_5m["return"].dropna()
    excess_kurtosis = r5.kurt()  # pandas .kurt() is excess kurtosis (normal = 0)

    apply_ft_style()
    fig, ax = plt.subplots(figsize=(10, 6))
    counts, bins, _ = ax.hist(r5 * 100, bins=40, density=True, color="#0F5499", alpha=0.7)
    # Overlay the normal bell curve with the same mean and standard deviation. Where the
    # blue bars rise above the line near zero and poke out past it in the tails, that is the
    # heavy-tailed, tall-peaked shape the stylized fact describes.
    grid = np.linspace(bins[0], bins[-1], 200)
    mu, sigma = (r5 * 100).mean(), (r5 * 100).std()
    normal_pdf = np.exp(-0.5 * ((grid - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    ax.plot(grid, normal_pdf, color=FT_MAROON, linewidth=2.0)
    ax.annotate("normal curve\n(same mean and SD)", xy=(grid[-1] * 0.6, normal_pdf.max() * 0.7),
                color=FT_MAROON, fontsize=10)
    ax.grid(axis="x", visible=False)
    fig.text(0.012, 0.96, "SpaceX returns have heavy tails", fontsize=15, fontweight="bold", color="#262A33")
    fig.text(0.012, 0.91, f"Five-minute returns vs a normal curve | excess kurtosis = {excess_kurtosis:.1f}",
             fontsize=11, color="#6B625C")
    fig.text(0.012, 0.01, "Source: Yahoo Finance | a normal distribution would have excess kurtosis 0",
             fontsize=8, color="#6B625C")
    ax.set_xlabel("Five-minute return (per cent)")
    ax.set_ylabel("Density")
    fig.subplots_adjust(top=0.86, bottom=0.10)
    fig.savefig(FIGURE_DIR / "06_spcx_return_distribution_ft.png", dpi=150)
    plt.show()
    plt.close()
    plt.rcParams.update(plt.rcParamsDefault)
    print("\nStage 7: return distribution")
    print(f"Excess kurtosis of five-minute returns: {excess_kurtosis:.2f} (normal = 0; positive = heavy tails)")


# -----------------------------------------------------------------------------
# 8. The Sharpe ratio collapsed as the rally reversed
# -----------------------------------------------------------------------------

# The single Sharpe number above hides the story. We recompute it day by day: at the end of
# each trading day we use every return from the first traded bar up to that point. The early
# rally pushed the Sharpe sky-high; the 22 June selloff dragged it below zero. We measure
# from the first traded price (not the offer) so the collapse into negative territory shows.
traded_price = price[price.index >= pd.Timestamp("2026-06-12")]  # drop the synthetic offer-price row
traded_ret = traded_price.pct_change().dropna()
day_ends = sorted(set(traded_ret.index.normalize()))
sharpe_values = []
for day in day_ends:
    window = traded_ret[traded_ret.index < day + pd.Timedelta(days=1)]
    bars_per_day_d = len(window) / window.index.normalize().nunique()
    n_per_year = bars_per_day_d * 252
    sharpe_values.append(window.mean() * n_per_year / (window.std() * np.sqrt(n_per_year)))
sharpe_by_day = pd.Series(sharpe_values, index=[d.strftime("%d %b") for d in day_ends])

print("\nStage 8: annualized Sharpe by day (from the first traded price)")
print(sharpe_by_day.round(2).to_string())

apply_ft_style()
positions = range(len(sharpe_by_day))
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(positions, sharpe_by_day.values, color=FT_MAROON, linewidth=1.8, marker="o", markersize=7)
ax.axhline(0.0, color="#66605C", linewidth=1.0)  # above zero is good, below zero loses money
ax.fill_between(list(positions), sharpe_by_day.values, 0.0,
                where=(sharpe_by_day.values < 0), color=FT_MAROON, alpha=0.15)
ax.set_xticks(list(positions))
ax.set_xticklabels(sharpe_by_day.index)
ax.grid(axis="x", visible=False)
peak_i = int(np.argmax(sharpe_by_day.values))
ax.annotate(f"peak {sharpe_by_day.max():.1f}", xy=(peak_i, sharpe_by_day.max()),
            xytext=(0, 9), textcoords="offset points", ha="center", color="#262A33", fontweight="bold", fontsize=10)
ax.annotate(f"{sharpe_by_day.iloc[-1]:.1f}", xy=(len(sharpe_by_day) - 1, sharpe_by_day.iloc[-1]),
            xytext=(8, -2), textcoords="offset points", color=FT_MAROON, fontweight="bold", fontsize=10)
fig.text(0.012, 0.96, "SpaceX's Sharpe ratio collapsed", fontsize=15, fontweight="bold", color="#262A33")
fig.text(0.012, 0.91, "Annualized Sharpe from the first traded price, through each day's close (risk-free = 0)",
         fontsize=11, color="#6B625C")
fig.text(0.012, 0.01, "Source: Yahoo Finance | the first day uses only a few hours, so read it as indicative",
         fontsize=8, color="#6B625C")
ax.set_xlabel("")
ax.set_ylabel("Annualized Sharpe ratio")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(FIGURE_DIR / "11_spcx_sharpe_collapse_ft.png", dpi=150)
plt.show()
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 9. A small scorecard
# -----------------------------------------------------------------------------

scorecard = pd.Series({
    "First price ($)": price.iloc[0],
    "Last price ($)": price.iloc[-1],
    "Total return (%)": total_return * 100,
    "Average hourly return (%)": mean_per_bar * 100,
    "Annualized volatility (%)": vol_annual * 100,
    "Annualized Sharpe ratio": sharpe_annual,
})

print("\nSpaceX hourly scorecard")
print(scorecard.round(2).to_string())

SCORECARD_CSV = OUTPUT_DIR / "spcx_scorecard.csv"
scorecard.round(4).to_csv(SCORECARD_CSV, header=["value"])
print(f"\nSaved scorecard: {SCORECARD_CSV}")
print("Saved figure:", FIGURE_DIR / "04_spcx_growth_of_one_ft.png")
