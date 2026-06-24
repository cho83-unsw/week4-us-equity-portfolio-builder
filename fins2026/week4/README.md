# Week 4: APIs, Returns, and Portfolio Construction

Week 4 introduces the first four stages of the data factory floor.

- Stage 1: connect to outside sources and save clean local datasets
- Stage 2: turn those saved prices into returns, data checks, and rolling
  features
- Stage 3: use those cleaned return panels for in-sample portfolio
  construction and evaluation
- Stage 4: turn the portfolio workflow into a client-facing Streamlit app

The point is to build the market-data input layer, validate it, use it to form
the first mean-variance portfolios, and then package that logic into a simple
client-facing app.

## Week Aim

Students should leave Week 4 able to:

1. explain what an API is and how a request is formed
2. pull market data from free and authenticated sources
3. save equity prices in long panel form and reshape them to wide form
4. compute simple daily returns from adjusted prices in both wide and long
   data
5. merge the daily risk-free rate into the same panel
6. build rolling return, volatility, VaR, Sharpe, and Sortino features
7. produce FT-style figures that check for outliers, suspicious moves, and
   volatility structure
8. form equal-weight, minimum-variance, and mean-variance portfolios
9. interpret their in-sample weights, frontier position, and cumulative
   performance
10. explain how the same in-sample portfolio workflow can be exposed in a
    client-facing app

## Stage 1: Source Connection

Week 4 uses four Stage 1 inputs:

- ECB exchange rates as the simplest free API example
- Kenneth French daily `RF` as a clean risk-free input
- Tiingo as the keyed vendor-style API teaching example
- Yahoo Finance as the main equity dataset for later Week 4 work

Stage 1 scripts:

```text
python fins2026/week4/scripts/run_beginner_ecb_api.py
python fins2026/week4/scripts/run_beginner_french_rfr.py
python fins2026/week4/scripts/run_beginner_tiingo_small_panel.py
python fins2026/week4/scripts/run_beginner_tiingo_wide_panel.py
python fins2026/week4/scripts/run_beginner_tiingo_famous_50.py
python fins2026/week4/scripts/run_beginner_yahoo_small_panel.py
python fins2026/week4/scripts/run_beginner_yahoo_famous_50.py
```

Important Week 4 source rules:

- keep the Tiingo key in `TIINGO_API_KEY`, never in tracked files
- Yahoo is queried through the direct chart endpoint, not `yfinance`
- save downloaded data under `results/data/`, not `data/`
- the Kenneth French daily risk-free pull writes only one final Parquet file
- Yahoo 50 is the canonical equity panel for Stage 2 and Stage 3
- Tiingo remains available for teaching authentication and vendor-style API use

## Stage 2: Returns and Data Checks

Stage 2 starts from the saved Stage 1 long panels.

The default teaching path is Yahoo. Tiingo remains supported, but it is the
secondary keyed source rather than the main downstream dataset.

Stage 2 scripts:

```text
python fins2026/week4/scripts/run_beginner_stage2_returns_wide.py
python fins2026/week4/scripts/run_beginner_stage2_returns_long.py
python fins2026/week4/scripts/run_beginner_stage2_features_long.py
python fins2026/week4/scripts/make_stage2_return_check_figures.py
```

All four Stage 2 scripts now default to `--provider yahoo`.

Stage 2 teaching contract:

- use adjusted prices:
  - Tiingo: `adjClose`
  - Yahoo: `adjClose`
- compute simple daily returns, not log returns
- show the wide calculation and the long `groupby` calculation
- verify that the two return paths match
- merge the Kenneth French `rfr` series by `date`
- forward-fill `rfr` after the latest available French date so the panel runs
  to the latest equity date

### Rolling Six-Month Features

Stage 2 adds these long-panel columns:

- `ret`
- `abs_ret`
- `rfr`
- `excess_ret`
- `is_large_move_10pct`
- `is_large_move_20pct`
- `rolling_6m_avg_ret`
- `rolling_6m_vol`
- `rolling_6m_var_95`
- `rolling_6m_sharpe`
- `rolling_6m_sortino`

Definitions:

- six months = `126` trading days
- `rolling_6m_avg_ret` stays in daily return units
- `rolling_6m_vol` is annualized with `sqrt(252)`
- `rolling_6m_var_95` is the trailing historical 5th percentile of daily
  returns
- `rolling_6m_sharpe` and `rolling_6m_sortino` use excess returns and are
  annualized with `sqrt(252)`

Stage 2 flags suspicious moves but does not delete or winsorize them
automatically.

## Stage 2 Figure Pack

The FT-style Stage 2 figure pack is the first data-quality narrative layer.

It includes:

1. pooled daily return distribution
2. largest absolute one-day moves
3. annualized volatility ranking by ticker
4. annualized return ranking by ticker
5. Sharpe ratio ranking by ticker
6. growth of `$1` for the top and bottom five volatility names
7. daily count of names with absolute returns above `10%`

Important presentation rules:

- use simple adjusted-price returns
- use log scale for the cumulative-return comparison
- shade NBER recessions on long time-series views
- keep titles short and put detail in the caption context

## Stage 3: In-Sample Mean-Variance Portfolios

Stage 3 uses the cleaned Stage 2 return panel to form three risky portfolios:

1. equal-weight `1/N`
2. minimum variance
3. mean-variance, defined here as the tangency or max-Sharpe portfolio

Default lecture surface:

- provider: Yahoo 50
- sample: the full balanced in-sample daily return panel
- constraints: fully invested, with short sales allowed

Stage 3 scripts:

```text
python fins2026/week4/scripts/run_beginner_stage3_portfolios.py
python fins2026/week4/scripts/make_stage3_portfolio_figures.py
```

Stage 3 teaching contract:

- estimation is strictly in-sample
- expected returns use sample daily means
- covariance uses the sample daily covariance matrix
- the tangency portfolio uses the average daily `rfr` from the in-sample window
- portfolio returns are daily rebalanced constant-weight returns
- out-of-sample re-estimation is discussed conceptually only

### Stage 3 Figure Pack

The FT-style Stage 3 figure pack includes:

1. portfolio weights
2. growth of `$1`
3. portfolio drawdowns
4. in-sample scorecard
5. efficient frontier with the tangency line

These figures are designed to explain:

- how the optimized portfolios differ from the naive benchmark
- where short positions appear
- how the three portfolios trade off return and risk in-sample
- how the tangency portfolio sits on the frontier

## Stage 4: Client-Facing App

Stage 4 narrows the Week 4 equity universe to 10 recognizable stocks and turns
the in-sample portfolio workflow into a deployable Streamlit product.

Stage 4 app surface:

- runtime source: live Yahoo prices plus live Kenneth French `rfr`
- fallback: committed app fixture under `app/fixtures/`
- default scope: in-sample only
- optimization modes:
  - long-only
  - unconstrained
- portfolio set:
  - custom
  - equal-weight
  - minimum variance
  - mean-variance

Stage 4 commands:

```text
python fins2026/week4/scripts/build_week4_app_fixture.py
streamlit run fins2026/week4/app/streamlit_app.py
```

The app uses the committed 10-stock universe in `data/yahoo_app_10.txt`.

## Recommended Teaching Flow

1. run the ECB free API example
2. run the Kenneth French daily risk-free download
3. run the Tiingo small pull
4. explain API keys and authenticated requests with Tiingo
5. optionally run the Tiingo 50-ticker pull
6. run the Yahoo small pull
7. run the Yahoo 50-ticker pull
8. compute wide adjusted-price returns on Yahoo
9. compute long `groupby` returns on Yahoo and verify parity
10. add the rolling Stage 2 features on Yahoo
11. export the FT-style Stage 2 check figures on Yahoo
12. build the in-sample Stage 3 portfolios on Yahoo
13. export the FT-style Stage 3 portfolio figures on Yahoo
14. refresh the Week 4 app fixture
15. launch the Week 4 Streamlit app

## Run The Week

From the repo root:

```text
python fins2026/week4/scripts/describe_data.py
python fins2026/week4/scripts/run_week.py
python fins2026/week4/scripts/run_beginner_ecb_api.py
python fins2026/week4/scripts/run_beginner_french_rfr.py
python fins2026/week4/scripts/run_beginner_tiingo_small_panel.py
python fins2026/week4/scripts/run_beginner_tiingo_wide_panel.py
python fins2026/week4/scripts/run_beginner_yahoo_small_panel.py
python fins2026/week4/scripts/run_beginner_yahoo_famous_50.py
python fins2026/week4/scripts/run_beginner_tiingo_famous_50.py
python fins2026/week4/scripts/run_beginner_stage2_returns_wide.py
python fins2026/week4/scripts/run_beginner_stage2_returns_long.py
python fins2026/week4/scripts/run_beginner_stage2_features_long.py
python fins2026/week4/scripts/make_stage2_return_check_figures.py
python fins2026/week4/scripts/run_beginner_stage3_portfolios.py
python fins2026/week4/scripts/make_stage3_portfolio_figures.py
python fins2026/week4/scripts/build_week4_app_fixture.py
streamlit run fins2026/week4/app/streamlit_app.py
```

Set the Tiingo key before Tiingo scripts:

```powershell
$env:TIINGO_API_KEY = "your-token-here"
```

```bash
export TIINGO_API_KEY="your-token-here"
```

## Data and Output Contract

- `data/` holds only committed source inputs such as ticker lists
- `results/data/` holds downloaded and derived data outputs
- `results/data/french_daily_rfr/french_daily_rfr.parquet` is the canonical
  daily risk-free file
- `results/data/stage2/<provider>/` holds the Stage 2 Parquet outputs
- `results/figures/stage2/<provider>/` holds the FT-style Stage 2 figures
- `results/data/stage3/<provider>/` holds the Stage 3 portfolio outputs
- `results/tables/stage3/<provider>/` holds the Stage 3 portfolio metrics
- `results/figures/stage3/<provider>/` holds the FT-style Stage 3 figures
- `app/fixtures/` holds the committed Week 4 app fallback bundle
- long panel data is the canonical equity shape
- wide price and return tables are derived Stage 2 objects

Canonical Stage 2 Parquet files per provider:

- `{provider}_adjclose_wide.parquet`
- `{provider}_returns_wide.parquet`
- `{provider}_returns_long.parquet`
- `{provider}_returns_features_long.parquet`

Canonical Stage 3 output files per provider:

- `{provider}_portfolio_weights.parquet`
- `{provider}_portfolio_returns.parquet`
- `{provider}_efficient_frontier.parquet`
- `{provider}_portfolio_metrics.csv`

## Working Rules

- keep API keys out of source files and out of git
- if `TIINGO_API_KEY` is missing, stop and ask for it before any Tiingo pull
- diagnose HTTP status codes before rewriting code:
  - `400`: bad request
  - `401`: missing or invalid key
  - `403`: not allowed
  - `404`: wrong endpoint or ticker
  - `429`: too many requests
  - `5xx`: provider-side failure
- for Stage 2, use adjusted prices and simple daily returns
- do not silently delete outliers during the teaching pipeline
- for Stage 3, stay strictly in-sample unless the user explicitly asks to move
  into rolling or out-of-sample portfolio evaluation
- for Stage 4, keep Yahoo as the runtime source and Tiingo as the API-teaching
  branch
- refresh `guidance/` after major Week 4 changes
