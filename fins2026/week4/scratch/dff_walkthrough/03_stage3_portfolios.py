"""Data Factory Floor, Stage 3: Model Design --- combining 50 stocks into a portfolio.

The big question: we have 50 individual stocks, each with its own return and risk. How do we
combine them into ONE good portfolio? We solve for the portfolio WEIGHTS --- the fraction of
money in each stock. That weight vector is the key output of the model.

We build three portfolios:
  - equal-weight (1/N): the simple benchmark, 1/50 in every stock.
  - minimum-variance: the weights that make the portfolio's risk as low as possible.
  - mean-variance (tangency): the weights with the highest Sharpe ratio.

IMPORTANT: these weights are IN-SAMPLE. We use the same 2020-2023 data to choose the weights
AND to measure how they did, so the results flatter the optimised portfolios. Week 5 covers
honest out-of-sample testing. Here we learn what the model solves and what it produces.

Run 01 and 02 first. Then run this file whole, or one numbered stage at a time.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dff_helpers import (FT_BLUE, FT_GREY, FT_MAROON, FT_TEAL, TRADING_DAYS, annualized_stats,
                         apply_ft_style, efficient_frontier, equal_weights, ft_header,
                         minimum_variance_weights, save_both, tangency_weights)

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
RISK_FREE = 0.0  # we set the daily risk-free rate to zero to keep the example simple.

# Portfolio colours, shared across the figures.
COLORS = {"Equal-weight": "#6F6A61", "Minimum-variance": FT_TEAL, "Mean-variance (tangency)": FT_MAROON}


# -----------------------------------------------------------------------------
# 1. The inputs: average return and the covariance matrix
# -----------------------------------------------------------------------------

# The optimiser needs two inputs, both estimated from the in-sample daily returns:
#   mu     = the average daily return of each stock           (a 50-vector)
#   Sigma  = the covariance matrix of the stock returns       (a 50 x 50 matrix)
# The covariance matrix carries both each stock's variance (its risk) and every pair's
# co-movement (how they diversify each other).
returns = pd.read_csv(OUTPUT_DIR / "returns_wide.csv", index_col=0, parse_dates=True).dropna()
tickers = list(returns.columns)
mean_vector = returns.mean().to_numpy()
covariance = np.cov(returns.to_numpy(), rowvar=False, ddof=1)

print("Stage 3.1: inputs")
print(f"Sample: {returns.index.min():%Y-%m-%d} to {returns.index.max():%Y-%m-%d}, "
      f"{len(returns):,} days x {len(tickers)} stocks")
print(f"mu is a {mean_vector.shape[0]}-vector; Sigma is a {covariance.shape[0]} x {covariance.shape[1]} matrix")


# -----------------------------------------------------------------------------
# 2. Solve for the weights (the key model output)
# -----------------------------------------------------------------------------

# Each portfolio is one line of linear algebra. Every weight vector sums to 1 (fully invested);
# short positions (negative weights) are allowed.
weights = pd.DataFrame({
    "Equal-weight": equal_weights(len(tickers)),
    "Minimum-variance": minimum_variance_weights(covariance),
    "Mean-variance (tangency)": tangency_weights(mean_vector, covariance, RISK_FREE),
}, index=tickers)
weights.round(5).to_csv(TABLE_DIR / "portfolio_weights.csv")

print("\nStage 3.2: weights solved (each column sums to 1)")
print(weights.sum().round(3).to_string())
print("\nTangency portfolio: 5 largest long and 5 largest short positions")
tan = weights["Mean-variance (tangency)"].sort_values()
print("  largest shorts:", ", ".join(f"{t} {w*100:.0f}%" for t, w in tan.head(5).items()))
print("  largest longs: ", ", ".join(f"{t} {w*100:.0f}%" for t, w in tan.tail(5).items()))


# -----------------------------------------------------------------------------
# 3. What would we have earned? In-sample portfolio performance
# -----------------------------------------------------------------------------

# Apply the weights to the daily stock returns to get each portfolio's daily return, then the
# growth of $1 and the usual scorecard. (In-sample: the same data chose the weights.)
portfolio_returns = returns @ weights
growth = (1.0 + portfolio_returns).cumprod()

scorecard = pd.DataFrame(
    {name: annualized_stats(portfolio_returns[name], RISK_FREE) for name in weights.columns},
    index=["ann_return", "ann_vol", "sharpe"],
).T
scorecard["max_drawdown"] = (growth / growth.cummax() - 1.0).min()
scorecard.round(4).to_csv(TABLE_DIR / "portfolio_scorecard.csv")

print("\nStage 3.3: in-sample portfolio scorecard")
print((scorecard.assign(ann_return=lambda d: (d.ann_return * 100).round(1),
                        ann_vol=lambda d: (d.ann_vol * 100).round(1),
                        sharpe=lambda d: d.sharpe.round(2),
                        max_drawdown=lambda d: (d.max_drawdown * 100).round(1))).to_string())
save_both(growth, OUTPUT_DIR / "portfolio_growth.csv", OUTPUT_DIR / "portfolio_growth.parquet")


# -----------------------------------------------------------------------------
# 4. Figure: the tangency weights (the model output, made visible)
# -----------------------------------------------------------------------------

apply_ft_style()
ends = pd.concat([tan.head(10), tan.tail(10)]) * 100
colors = [FT_MAROON if w < 0 else FT_BLUE for w in ends.values]
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(range(len(ends)), ends.values, color=colors)
ax.set_yticks(range(len(ends)))
ax.set_yticklabels(ends.index, fontsize=9)
ax.axvline(0.0, color="#66605C", linewidth=0.8)
ax.grid(axis="y", visible=False)
ax.set_xlabel("Weight (%)")
ft_header(fig, "The max-Sharpe portfolio's biggest bets",
          "Tangency weights: 10 largest long (blue) and 10 largest short (maroon). Equal-weight is 2% in each.",
          "Source: course equity bundle | in-sample 2020-2023")
fig.savefig(FIGURE_DIR / "stage3_01_tangency_weights.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 5. Figure: growth of $1 for the three portfolios
# -----------------------------------------------------------------------------

apply_ft_style()
fig, ax = plt.subplots(figsize=(10, 6))
for name in weights.columns:
    ax.plot(growth.index, growth[name], color=COLORS[name], linewidth=1.8, label=name)
ax.axhline(1.0, color="#66605C", linewidth=0.8)
ax.grid(axis="x", visible=False)
ax.legend(loc="upper left", frameon=False, fontsize=10)
ax.set_ylabel("Value of $1")
ft_header(fig, "Growth of $1: three portfolios", "In-sample, daily rebalanced, fully invested",
          "Source: course equity bundle | in-sample 2020-2023, weights chosen on the same data")
fig.savefig(FIGURE_DIR / "stage3_02_growth.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)


# -----------------------------------------------------------------------------
# 6. Figure: the efficient frontier with the three portfolios
# -----------------------------------------------------------------------------

# The frontier is the best possible risk-return trade-off: for each level of risk, the highest
# return a portfolio of these 50 stocks can reach. The tangency portfolio is the point on the
# frontier that the straight line from the risk-free rate just touches --- the highest Sharpe.
# Extend the frontier curve up to the tangency portfolio's return so the tangency point sits
# on the curve where the capital allocation line touches it (the textbook picture).
tan_daily_return = portfolio_returns["Mean-variance (tangency)"].mean()
target_d, vol_d = efficient_frontier(mean_vector, covariance, max_return=tan_daily_return * 1.04)
frontier_x = vol_d * np.sqrt(TRADING_DAYS) * 100
frontier_y = target_d * TRADING_DAYS * 100

asset_x = returns.std().to_numpy() * np.sqrt(TRADING_DAYS) * 100
asset_y = mean_vector * TRADING_DAYS * 100

apply_ft_style()
fig, ax = plt.subplots(figsize=(10, 6.5))
ax.scatter(asset_x, asset_y, s=18, color=FT_GREY, alpha=0.6, label="individual stocks")
ax.plot(frontier_x, frontier_y, color="#262A33", linewidth=1.8, label="efficient frontier")
markers = {"Equal-weight": "s", "Minimum-variance": "D", "Mean-variance (tangency)": "^"}
for name in weights.columns:
    ax.scatter(scorecard.loc[name, "ann_vol"] * 100, scorecard.loc[name, "ann_return"] * 100,
               s=170, marker=markers[name], color=COLORS[name], edgecolor="white", zorder=5, label=name)
# Capital allocation line from the risk-free rate (0, 0) through the tangency portfolio.
tan_x = scorecard.loc["Mean-variance (tangency)", "ann_vol"] * 100
tan_y = scorecard.loc["Mean-variance (tangency)", "ann_return"] * 100
cal_x = np.array([0, asset_x.max() * 1.05])
ax.plot(cal_x, tan_y / tan_x * cal_x, color=FT_MAROON, linewidth=1.0, linestyle="--", label="capital allocation line")
ax.grid(axis="x", visible=False)
ax.legend(loc="lower right", frameon=False, fontsize=9)
ax.set_xlabel("Annualized volatility (%)")
ax.set_ylabel("Annualized return (%)")
ax.set_ylim(0, max(frontier_y.max(), asset_y.max()) * 1.1)
ft_header(fig, "The efficient frontier", "Each grey dot is one stock; the curve is the best risk-return trade-off",
          "Source: course equity bundle | in-sample 2020-2023, risk-free rate 0")
fig.savefig(FIGURE_DIR / "stage3_03_frontier.png", dpi=150)
plt.close()
plt.rcParams.update(plt.rcParamsDefault)

print("\nSaved Stage 3 figures (stage3_01 ... stage3_03) and tables.")
print(f"Tangency in-sample Sharpe: {scorecard.loc['Mean-variance (tangency)', 'sharpe']:.2f} "
      f"(spectacular BECAUSE it is in-sample -- Week 5 shows the honest test)")
