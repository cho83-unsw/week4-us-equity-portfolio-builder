# dff 50-Stock Equity Portfolio App

Compare three standard portfolio strategies — equal-weight, minimum-variance,
and mean-variance — across a diversified 50-stock U.S. equity universe.

Data comes from the course data bundle (`load_equity_prices()`), which covers
50 large U.S. companies across 10 sectors with daily adjusted close prices from
2020 to 2023. All results are **in-sample only**.

## Product question

How would three different portfolio strategies have performed with 50 U.S. stocks?

## Run locally

From the repo root:

```bash
streamlit run fins2026/week4/app/streamlit_app.py
```

The app loads the 50-stock equity dataset from the course data bundle (hosted
ZIP, fetched once and cached). No API keys needed.

## App structure

- `app_config.py`: labels, options, and display constants
- `app_data.py`: cached data loading from the dff data bundle
- `app_insights.py`: Plotly figures, metric cards, and formatting helpers
- `app_views.py`: Streamlit layout, sidebar controls, tabs, and downloads
- `streamlit_app.py`: repo-root bootstrap and `main()` entrypoint

The data and portfolio logic lives in `code/stage4_dff_app.py`, which wraps the
dff walkthrough `data_access` module and the shared `stage3_portfolios` helpers.

## Tabs

1. **Overview**: portfolio comparison with weights chart, growth chart, and
   scorecard table.
2. **Portfolio Weights**: inspect individual portfolio allocations.
3. **Historical Performance**: growth of $1, drawdowns, and full scorecard with
   CSV downloads.
4. **Efficient Frontier**: risk-return frontier with portfolio markers.
5. **Data**: browse and download the underlying price, return, and weight tables.
6. **Methodology**: model equations and in-sample caveats.

## Controls

- **Sample window**: select a 1Y, 2Y, 3Y, or Max trailing window.
- **Stock universe**: choose which stocks to include (all 50 selected by default).

## Deployment

Before deployment, run from the repo root:

```bash
python tools/workflow.py check-app-submission --target fins2026/week4 --entrypoint fins2026/week4/app/streamlit_app.py
```

To prepare a clean private deploy repo:

```bash
python tools/workflow.py prepare-app-repo --source fins2026/week4 --dest ../dff-50-stock-portfolio --repo dff-50-stock-portfolio --entrypoint fins2026/week4/app/streamlit_app.py
```
