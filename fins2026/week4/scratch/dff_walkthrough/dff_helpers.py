"""Shared helpers for the Data Factory Floor walkthrough (Week 4, 50-stock equity data).

FT-style figures, a safe CSV/Parquet writer, and the closed-form portfolio maths used in
Stage 3 (equal-weight, minimum-variance, tangency, and the efficient frontier). Kept in one
small module so the numbered stage scripts stay short and read top-to-bottom.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Financial Times palette (matches the rest of the course figures).
FT_CREAM = "#FDF1E6"
FT_MAROON = "#990F3D"
FT_BLUE = "#0F5499"
FT_TEAL = "#2F7F73"
FT_GREY = "#6B625C"
TRADING_DAYS = 252  # US equities trade about 252 days a year.


def apply_ft_style():
    """Set rcParams so the next figure follows a clean FT-style look."""
    plt.rcParams.update({
        "figure.facecolor": FT_CREAM, "axes.facecolor": FT_CREAM,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.edgecolor": "#66605C", "axes.grid": True, "grid.color": "#E2D8CF",
        "axes.axisbelow": True, "font.family": "DejaVu Sans", "font.size": 12,
    })


def ft_header(fig, title, subtitle, source):
    """Write the FT-style title / subtitle / source block onto a figure."""
    fig.text(0.012, 0.96, title, fontsize=15, fontweight="bold", color="#262A33")
    fig.text(0.012, 0.91, subtitle, fontsize=11, color=FT_GREY)
    fig.text(0.012, 0.01, source, fontsize=8, color=FT_GREY)
    fig.subplots_adjust(top=0.86, bottom=0.12)


def save_both(frame, csv_path, parquet_path):
    """Always save the CSV; try Parquet too but do not crash on a minimal install."""
    frame.to_csv(csv_path)
    try:
        frame.to_parquet(parquet_path)
    except Exception as exc:  # e.g. no pyarrow/fastparquet installed
        print(f"  (skipped {Path(parquet_path).name}: {exc}; the CSV is saved and is enough)")


# -----------------------------------------------------------------------------
# Stage 3 portfolio maths (closed form, in-sample, fully invested, short sales allowed)
# -----------------------------------------------------------------------------

def equal_weights(n_assets):
    """The 1/N benchmark: put the same fraction in every asset."""
    return np.ones(n_assets) / n_assets


def minimum_variance_weights(cov):
    """w = Sigma^{-1} 1 / (1' Sigma^{-1} 1). The fully-invested portfolio with the lowest
    variance, ignoring expected returns entirely."""
    ones = np.ones(cov.shape[0])
    inv_ones = np.linalg.solve(cov, ones)
    return inv_ones / (ones @ inv_ones)


def tangency_weights(mean, cov, risk_free=0.0):
    """w = Sigma^{-1}(mu - rf 1) / (1' Sigma^{-1}(mu - rf 1)). The fully-invested portfolio
    with the highest Sharpe ratio (the tangency / mean-variance portfolio)."""
    ones = np.ones(len(mean))
    excess = mean - risk_free * ones
    inv_excess = np.linalg.solve(cov, excess)
    return inv_excess / (ones @ inv_excess)


def efficient_frontier(mean, cov, n_points=250, max_return=None):
    """Return (target daily returns, daily volatilities) tracing the minimum-variance frontier.
    Uses the standard a, b, c constants: a=1'S^{-1}1, b=1'S^{-1}mu, c=mu'S^{-1}mu, and
    sigma^2(m) = (a m^2 - 2 b m + c) / (a c - b^2). By default the curve runs up to the highest
    single-stock return; pass max_return to extend it (e.g. up to the tangency return)."""
    ones = np.ones(len(mean))
    inv_ones = np.linalg.solve(cov, ones)
    inv_mean = np.linalg.solve(cov, mean)
    a = ones @ inv_ones
    b = ones @ inv_mean
    c = mean @ inv_mean
    determinant = a * c - b * b
    gmv_return = b / a  # the global minimum-variance portfolio's expected return
    top = mean.max() if max_return is None else max_return
    targets = np.linspace(gmv_return, top, n_points)
    variances = (a * targets ** 2 - 2 * b * targets + c) / determinant
    return targets, np.sqrt(variances)


def annualized_stats(returns, risk_free=0.0):
    """Annualized return, volatility, and Sharpe ratio for a daily return series."""
    mean_d, std_d = returns.mean(), returns.std()
    ann_return = mean_d * TRADING_DAYS
    ann_vol = std_d * np.sqrt(TRADING_DAYS)
    sharpe = (mean_d - risk_free) / std_d * np.sqrt(TRADING_DAYS) if std_d > 0 else np.nan
    return ann_return, ann_vol, sharpe
