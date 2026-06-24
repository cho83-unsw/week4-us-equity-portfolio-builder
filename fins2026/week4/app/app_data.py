"""Cached data loaders for the dff 50-stock portfolio app."""

from __future__ import annotations

import pandas as pd

from fins2026.week4.code.stage4_dff_app import (
    DFF_SAMPLE_PERIODS,
    DFFBundle,
    filter_features_for_period,
    filter_prices_for_period,
    load_dff_bundle,
)


def load_app_bundle() -> tuple[DFFBundle, str, str | None]:
    try:
        bundle = load_dff_bundle()
        return bundle, "Course equity bundle", None
    except Exception as exc:
        raise RuntimeError(
            f"Could not load the 50-stock equity data bundle. "
            f"Check network access to the course data ZIP. Detail: {exc}"
        ) from exc


def apply_sample_period(
    bundle: DFFBundle, sample_period: str
) -> DFFBundle:
    years = DFF_SAMPLE_PERIODS[sample_period]
    return DFFBundle(
        price_panel=filter_prices_for_period(bundle.price_panel, years),
        feature_panel=filter_features_for_period(bundle.feature_panel, years),
        sector_map=bundle.sector_map,
        latest_observation_date=bundle.latest_observation_date,
    )


def source_status_text(
    bundle: DFFBundle,
    *,
    active_source: str,
) -> str:
    latest_price = pd.to_datetime(bundle.price_panel["date"]).max()
    n_tickers = bundle.price_panel["ticker"].nunique()
    return (
        f"{active_source}: {n_tickers} U.S. equities, daily adjusted close "
        f"prices through {latest_price:%Y-%m-%d}, sector labels included."
    )
