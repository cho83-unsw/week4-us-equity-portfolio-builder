"""Configuration constants for the dff 50-stock portfolio app."""

from __future__ import annotations

from fins2026.week4.code.stage3_portfolios import PORTFOLIO_LABELS

APP_TITLE = "50-Stock U.S. Equity Portfolio Comparison"
APP_SUBTITLE = (
    "Compare three standard portfolio strategies across a diversified 50-stock "
    "U.S. equity universe using in-sample historical data."
)
PRODUCT_QUESTION = (
    "How would three different portfolio strategies—equal-weight, "
    "minimum-variance, and mean-variance—have performed with 50 U.S. stocks?"
)

VIEW_OPTIONS = [
    "Overview",
    "Portfolio Weights",
    "Historical Performance",
    "Efficient Frontier",
    "Data",
    "Methodology",
]
DEFAULT_VIEW = "Overview"

SAMPLE_PERIOD_OPTIONS = {"1Y": 1, "2Y": 2, "3Y": 3, "Max": None}
DEFAULT_SAMPLE_PERIOD = "3Y"

PORTFOLIO_KEYS = ["equal_weight", "minimum_variance", "mean_variance_tangency"]
PORTFOLIO_LABELS_MAP = {
    "equal_weight": PORTFOLIO_LABELS["equal_weight"],
    "minimum_variance": PORTFOLIO_LABELS["minimum_variance"],
    "mean_variance_tangency": PORTFOLIO_LABELS["mean_variance_tangency"],
}
PORTFOLIO_DISPLAY_ORDER = [PORTFOLIO_LABELS[key] for key in PORTFOLIO_KEYS]

PORTFOLIO_COLORS = {
    PORTFOLIO_LABELS["equal_weight"]: "#7A746B",
    PORTFOLIO_LABELS["minimum_variance"]: "#4E8B84",
    PORTFOLIO_LABELS["mean_variance_tangency"]: "#8E3B46",
}

METHOD_NOTES = {
    "in_sample": (
        "All three portfolios use the same historical data to estimate expected returns "
        "and covariances, then to evaluate performance. This is in-sample only: the "
        "mean-variance portfolio's Sharpe ratio is inflated because it exploits the same "
        "sample it is measured on."
    ),
}
