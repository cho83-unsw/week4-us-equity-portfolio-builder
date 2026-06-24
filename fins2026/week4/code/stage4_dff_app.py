"""Data loading and portfolio helpers for the dff 50-stock app."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from fins2026.week4.code.stage3_portfolios import (
    PORTFOLIO_COLUMN_ORDER,
    PORTFOLIO_LABELS,
    SQRT_252,
    TRADING_DAYS_PER_YEAR,
    Stage3Sample,
    build_balanced_stage3_sample,
    build_efficient_frontier,
    drawdown_series,
    summarize_asset_statistics,
)
from fins2026.week4.scratch.dff_walkthrough.data_access import (
    load_equity_prices,
    load_sector_universe,
)
from fintools.portfolio_math import (
    equal_weight_vector,
    minimum_variance_weights,
    tangency_weights,
)


@dataclass(frozen=True)
class DFFBundle:
    price_panel: pd.DataFrame
    feature_panel: pd.DataFrame
    sector_map: pd.DataFrame
    latest_observation_date: pd.Timestamp


DFF_SAMPLE_PERIODS = {"1Y": 1, "2Y": 2, "3Y": 3, "Max": None}


def load_dff_bundle() -> DFFBundle:
    prices = load_equity_prices()
    prices["date"] = pd.to_datetime(prices["date"])
    prices = prices.sort_values(["ticker", "date"]).reset_index(drop=True)

    feature = prices.copy()
    feature["ret"] = feature.groupby("ticker", sort=False)["adjClose"].pct_change(
        fill_method=None
    )
    feature["rfr"] = 0.0

    latest = pd.to_datetime(prices["date"]).max()
    sector_map = load_sector_universe()

    return DFFBundle(
        price_panel=prices,
        feature_panel=feature,
        sector_map=sector_map,
        latest_observation_date=pd.Timestamp(latest),
    )


def filter_prices_for_period(
    prices: pd.DataFrame, years: int | None
) -> pd.DataFrame:
    if years is None:
        return prices
    cutoff = pd.to_datetime(prices["date"]).max() - pd.DateOffset(years=years)
    return prices.loc[pd.to_datetime(prices["date"]) >= cutoff].reset_index(
        drop=True
    )


def filter_features_for_period(
    features: pd.DataFrame, years: int | None
) -> pd.DataFrame:
    if years is None:
        return features
    cutoff = pd.to_datetime(features["date"]).max() - pd.DateOffset(years=years)
    return features.loc[pd.to_datetime(features["date"]) >= cutoff].reset_index(
        drop=True
    )


def build_dff_sample(
    feature_panel: pd.DataFrame, selected_tickers: list[str]
) -> Stage3Sample:
    subset = feature_panel.loc[
        feature_panel["ticker"].isin(selected_tickers)
    ].copy()
    if subset.empty:
        raise ValueError("No data remaining for the selected tickers.")
    return build_balanced_stage3_sample(
        subset,
        provider="dff_50",
        display_name="50-stock equity bundle",
    )


def estimate_dff_weights(sample: Stage3Sample) -> pd.DataFrame:
    returns = sample.returns_wide.to_numpy(dtype=float)
    mean_returns = returns.mean(axis=0)
    covariance = np.cov(returns, rowvar=False, ddof=1)
    avg_daily_rfr = float(sample.rfr.mean())

    eq_weights = equal_weight_vector(sample.n_assets)
    mv_weights, _ = minimum_variance_weights(covariance)
    tan_weights, _ = tangency_weights(mean_returns, covariance, avg_daily_rfr)

    weight_frame = pd.DataFrame(
        {
            "ticker": sample.tickers,
            PORTFOLIO_LABELS["equal_weight"]: eq_weights,
            PORTFOLIO_LABELS["minimum_variance"]: mv_weights,
            PORTFOLIO_LABELS["mean_variance_tangency"]: tan_weights,
        }
    )
    long_weights = (
        weight_frame.melt(
            id_vars="ticker", var_name="portfolio", value_name="weight"
        )
        .sort_values(["portfolio", "ticker"])
        .reset_index(drop=True)
    )
    return long_weights


def compute_dff_portfolio_returns(
    sample: Stage3Sample, weights: pd.DataFrame
) -> pd.DataFrame:
    matrix = weights.pivot(
        index="ticker", columns="portfolio", values="weight"
    )
    matrix = matrix.reindex(index=sample.tickers)
    display_columns = [
        PORTFOLIO_LABELS[key] for key in PORTFOLIO_COLUMN_ORDER
    ]
    matrix = matrix.reindex(columns=display_columns)
    returns_array = sample.returns_wide.to_numpy(dtype=float)
    portfolio_returns = returns_array @ matrix.to_numpy(dtype=float)
    output = pd.DataFrame(
        portfolio_returns,
        index=sample.returns_wide.index,
        columns=display_columns,
    )
    output = output.reset_index().rename(columns={"index": "date"})
    output["rfr"] = sample.rfr.to_numpy(dtype=float)
    return output


def summarize_dff_metrics(portfolio_returns: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    rfr = portfolio_returns["rfr"].astype(float)
    for label in [PORTFOLIO_LABELS[key] for key in PORTFOLIO_COLUMN_ORDER]:
        returns = portfolio_returns[label].astype(float)
        excess = returns - rfr
        annualized_return = float(returns.mean() * TRADING_DAYS_PER_YEAR)
        annualized_vol = float(returns.std(ddof=1) * SQRT_252)
        sharpe = (
            float(SQRT_252 * excess.mean() / excess.std(ddof=1))
            if not np.isclose(float(excess.std(ddof=1)), 0.0)
            else np.nan
        )
        max_dd = float(drawdown_series(returns).min())
        rows.append(
            {
                "portfolio": label,
                "annualized_return_pct": annualized_return * 100.0,
                "annualized_volatility_pct": annualized_vol * 100.0,
                "sharpe_ratio": sharpe,
                "max_drawdown_pct": max_dd * 100.0,
            }
        )
    return pd.DataFrame(rows)


build_dff_frontier = build_efficient_frontier

__all__ = [
    "DFF_SAMPLE_PERIODS",
    "DFFBundle",
    "build_dff_frontier",
    "build_dff_sample",
    "compute_dff_portfolio_returns",
    "estimate_dff_weights",
    "filter_features_for_period",
    "filter_prices_for_period",
    "load_dff_bundle",
    "summarize_asset_statistics",
    "summarize_dff_metrics",
]
