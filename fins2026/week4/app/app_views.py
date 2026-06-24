"""Streamlit layout and controls for the dff 50-stock portfolio app."""

from __future__ import annotations

import pandas as pd

from fins2026.week4.app.app_config import (
    APP_SUBTITLE,
    APP_TITLE,
    DEFAULT_SAMPLE_PERIOD,
    DEFAULT_VIEW,
    METHOD_NOTES,
    PORTFOLIO_DISPLAY_ORDER,
    SAMPLE_PERIOD_OPTIONS,
    VIEW_OPTIONS,
)
from fins2026.week4.app.app_data import (
    apply_sample_period,
    load_app_bundle,
    source_status_text,
)
from fins2026.week4.app.app_insights import (
    compact_table_height,
    cumulative_growth_figure,
    drawdown_figure,
    efficient_frontier_figure,
    portfolio_metric_table,
    portfolio_weight_figure,
    top_portfolio_metrics,
)
from fins2026.week4.code.stage4_dff_app import (
    build_dff_frontier,
    build_dff_sample,
    compute_dff_portfolio_returns,
    estimate_dff_weights,
    summarize_asset_statistics,
    summarize_dff_metrics,
)
from fintools.apps import (
    active_tab_label,
    configure_page,
    lazy_tabs,
    query_choice,
    render_csv_download,
    render_data_health,
    render_display_table,
    render_metric_strip,
    sync_query_params,
    tab_is_open,
)


def _ticker_label(
    ticker: str, sector_map: pd.DataFrame
) -> str:
    row = sector_map.loc[sector_map["ticker"] == ticker]
    sector = row["sector"].iloc[0] if not row.empty else ""
    return f"{ticker} ({sector})" if sector else ticker


def _ticker_labels(
    tickers: list[str], sector_map: pd.DataFrame
) -> dict[str, str]:
    return {t: _ticker_label(t, sector_map) for t in tickers}


def _initialize_state(st) -> None:
    st.session_state.setdefault(
        "dff_sample_period",
        query_choice("sample", list(SAMPLE_PERIOD_OPTIONS), default=DEFAULT_SAMPLE_PERIOD),
    )
    st.session_state.setdefault("dff_initialized", False)


def _render_sidebar_controls(
    st, all_tickers: list[str], sector_map: pd.DataFrame
) -> tuple[str, list[str]]:
    labels = _ticker_labels(all_tickers, sector_map)
    with st.sidebar:
        st.header("Controls")
        sample_period = (
            st.segmented_control(
                "Sample window",
                list(SAMPLE_PERIOD_OPTIONS),
                key="dff_sample_period",
            )
            or st.session_state["dff_sample_period"]
        )

        selected_labels = st.multiselect(
            "Stock universe",
            options=[labels[t] for t in all_tickers],
            default=[labels[t] for t in all_tickers],
            key="dff_selected_tickers",
        )
        selected_tickers = [
            t for t in all_tickers if labels[t] in selected_labels
        ]
        if not selected_tickers:
            selected_tickers = all_tickers[:1]

    return sample_period, selected_tickers


def _weight_matrix_table(weights: pd.DataFrame) -> pd.DataFrame:
    matrix = weights.pivot(
        index="ticker", columns="portfolio", values="weight"
    ).mul(100.0)
    matrix = matrix.dropna(how="all").reset_index().rename(
        columns={"ticker": "Ticker"}
    )
    return matrix


def main() -> None:
    st = configure_page(APP_TITLE)
    _initialize_state(st)

    bundle, active_source, warning = load_app_bundle()

    all_tickers = sorted(bundle.sector_map["ticker"].tolist())
    sample_period, selected_tickers = _render_sidebar_controls(
        st, all_tickers, bundle.sector_map
    )

    sampled_bundle = apply_sample_period(bundle, sample_period)

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    if warning:
        st.warning(warning)
    st.caption(source_status_text(sampled_bundle, active_source=active_source))

    render_data_health(
        sampled_bundle.price_panel.loc[
            sampled_bundle.price_panel["ticker"].isin(selected_tickers)
        ],
        source=active_source,
        date_column="date",
        value_columns=["adjClose"],
    )

    if len(selected_tickers) < 2:
        st.info(
            "Select at least two stocks to build optimized portfolios "
            "and draw the efficient frontier."
        )
        return

    sample = build_dff_sample(sampled_bundle.feature_panel, selected_tickers)
    weights = estimate_dff_weights(sample)
    portfolio_returns = compute_dff_portfolio_returns(sample, weights)
    metrics = summarize_dff_metrics(portfolio_returns)
    frontier = build_dff_frontier(sample, weights)
    asset_stats = summarize_asset_statistics(sample)

    render_metric_strip(
        top_portfolio_metrics(
            metrics,
            sample=sample,
            n_selected=len(selected_tickers),
        ),
        columns=3,
    )

    view_default = query_choice("view", VIEW_OPTIONS, default=DEFAULT_VIEW)
    tabs = lazy_tabs(VIEW_OPTIONS, default=view_default, key="dff_app_view")
    active_view = active_tab_label(VIEW_OPTIONS, tabs, default=view_default)
    (
        tab_overview,
        tab_weights,
        tab_history,
        tab_frontier,
        tab_data,
        tab_method,
    ) = tabs

    if tab_is_open(tab_overview, fallback=active_view == "Overview"):
        with tab_overview:
            st.subheader("Portfolio comparison")
            st.markdown(
                f"Using **{len(selected_tickers)} stocks** over the balanced "
                f"in-sample window from **{sample.start_date:%Y-%m-%d}** to "
                f"**{sample.end_date:%Y-%m-%d}** ({sample.sample_days:,} trading days)."
            )

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    portfolio_weight_figure(
                        weights, portfolio_label=PORTFOLIO_DISPLAY_ORDER[2]
                    ),
                    width="stretch",
                )
            with col2:
                st.plotly_chart(
                    cumulative_growth_figure(portfolio_returns, sample=sample),
                    width="stretch",
                )

            metric_table = portfolio_metric_table(metrics)
            render_display_table(
                metric_table,
                reset_index=False,
                height=compact_table_height(metric_table),
            )

    if tab_is_open(tab_weights, fallback=active_view == "Portfolio Weights"):
        with tab_weights:
            st.subheader("Portfolio weights")
            weight_focus = st.radio(
                "Inspect weights for",
                PORTFOLIO_DISPLAY_ORDER,
                index=2,
                horizontal=True,
                key="dff_weight_focus",
            )
            st.plotly_chart(
                portfolio_weight_figure(weights, portfolio_label=weight_focus),
                width="stretch",
            )
            weight_table = _weight_matrix_table(weights)
            render_display_table(
                weight_table,
                reset_index=False,
                height=compact_table_height(weight_table, max_height=640),
            )

    if tab_is_open(tab_history, fallback=active_view == "Historical Performance"):
        with tab_history:
            st.subheader("Historical in-sample performance")
            st.plotly_chart(
                cumulative_growth_figure(portfolio_returns, sample=sample),
                width="stretch",
            )
            st.plotly_chart(
                drawdown_figure(portfolio_returns, sample=sample),
                width="stretch",
            )
            metric_table = portfolio_metric_table(metrics)
            render_display_table(
                metric_table,
                reset_index=False,
                height=compact_table_height(metric_table),
            )
            download_cols = st.columns(2)
            with download_cols[0]:
                render_csv_download(
                    portfolio_returns,
                    label="Download portfolio return panel",
                    file_name="dff_portfolio_returns.csv",
                    key="download_dff_portfolio_returns",
                )
            with download_cols[1]:
                render_csv_download(
                    metrics,
                    label="Download portfolio metrics",
                    file_name="dff_portfolio_metrics.csv",
                    key="download_dff_portfolio_metrics",
                )

    if tab_is_open(tab_frontier, fallback=active_view == "Efficient Frontier"):
        with tab_frontier:
            st.subheader("Efficient frontier")
            st.markdown(
                "The curve and points below are estimated in-sample only, "
                "using the selected historical window. Each grey dot is one "
                "stock; the curve traces the best risk-return combinations "
                "available from the selected opportunity set."
            )
            st.plotly_chart(
                efficient_frontier_figure(
                    frontier,
                    asset_stats,
                    metrics,
                    sample=sample,
                ),
                width="stretch",
            )

    if tab_is_open(tab_data, fallback=active_view == "Data"):
        with tab_data:
            st.subheader("Data and downloads")
            table_choice = st.segmented_control(
                "Table",
                [
                    "Price panel",
                    "Feature panel",
                    "Balanced returns",
                    "Portfolio returns",
                    "Weights",
                ],
                key="dff_data_choice",
            )
            table_choice = table_choice or "Price panel"
            if table_choice == "Price panel":
                frame = sampled_bundle.price_panel.loc[
                    sampled_bundle.price_panel["ticker"].isin(selected_tickers)
                ].copy()
            elif table_choice == "Feature panel":
                frame = sampled_bundle.feature_panel.loc[
                    sampled_bundle.feature_panel["ticker"].isin(selected_tickers)
                ].copy()
            elif table_choice == "Balanced returns":
                frame = sample.returns_wide.reset_index()
                frame = frame.rename(columns={"index": "date"})
            elif table_choice == "Portfolio returns":
                frame = portfolio_returns.copy()
            else:
                frame = _weight_matrix_table(weights)
            render_display_table(
                frame.tail(300), reset_index=False, height=520
            )
            render_csv_download(
                frame,
                label="Download displayed table",
                file_name="dff_displayed_table.csv",
                key=f"download_dff_{table_choice.lower().replace(' ', '_')}",
            )

    if tab_is_open(tab_method, fallback=active_view == "Methodology"):
        with tab_method:
            st.subheader("Methodology")
            st.markdown(
                "- **Data source**: 50 U.S. equities across 10 sectors, daily "
                "adjusted close prices from the course data bundle (2020-2023).\n"
                "- **Returns**: simple daily returns computed from adjusted close prices.\n"
                "- **Risk-free rate**: set to 0% for this comparison, following the "
                "course dff walkthrough convention.\n"
                f"- {METHOD_NOTES['in_sample']}\n"
                "- **Optimization**: unconstrained (short sales allowed), fully invested, "
                "closed-form solution using the sample covariance matrix."
            )
            st.markdown("**Equal-weight portfolio**")
            st.latex(r"w_i = \frac{1}{N} \quad \text{for each asset } i")
            st.markdown("**Minimum-variance portfolio**")
            st.latex(
                r"w_{mv} = \frac{\Sigma^{-1}\mathbf{1}}"
                r"{\mathbf{1}^\top\Sigma^{-1}\mathbf{1}}"
            )
            st.markdown("**Mean-variance (tangency) portfolio**")
            st.latex(
                r"w_{tan} = \frac{\Sigma^{-1}(\mu - r_f\mathbf{1})}"
                r"{\mathbf{1}^\top\Sigma^{-1}(\mu - r_f\mathbf{1})}"
            )
            st.info(
                "Out-of-sample re-estimation is covered in Week 5 of the course. "
                "These results are in-sample learning tools, not live trading recommendations."
            )

    sync_query_params(
        view=active_view,
        sample=sample_period,
    )
