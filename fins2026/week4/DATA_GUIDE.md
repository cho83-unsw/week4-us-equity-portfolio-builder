# Week 4 Data Guide

Week 4 has four data layers:

- Stage 1 source pulls
- Stage 2 return and feature outputs
- Stage 3 in-sample portfolio outputs
- Stage 4 app runtime and fallback inputs

Provider priority:

- Yahoo is the canonical Week 4 equity dataset for Stage 2 and Stage 3
- Tiingo stays in Week 4 to teach keyed API access and vendor-style pulls

## Source Inputs in `data/`

- `tiingo_intro_3.txt`
  - tiny Tiingo warm-up universe
- `tiingo_famous_50_pre2000.txt`
  - larger Tiingo universe for the 50-name pull
- `yahoo_intro_3.txt`
  - tiny Yahoo warm-up universe
- `yahoo_famous_50.txt`
  - larger Yahoo universe for the 50-name pull
- `yahoo_app_10.txt`
  - the 10-stock client-facing app universe

## Stage 1 Outputs in `results/data/`

### ECB API intro

- `results/data/ecb_api_intro/ecb_exchange_rates_raw.csv`
- `results/data/ecb_api_intro/ecb_exchange_rates_tidy.csv`
- `results/data/ecb_api_intro/ecb_exchange_rates_tidy.parquet`

### Kenneth French daily risk-free rate

- `results/data/french_daily_rfr/french_daily_rfr.parquet`

This file contains only:

- `date`
- `rfr`

The source `RF` column is in percent. Week 4 divides by `100`, so `rfr` is a
decimal daily rate.

### Tiingo small panel

- `results/data/tiingo_small_panel/tiingo_eod_panel_long.csv`
- `results/data/tiingo_small_panel/tiingo_eod_panel_long.parquet`
- `results/data/tiingo_small_panel/tiingo_eod_metadata.csv`
- `results/data/tiingo_small_panel/tiingo_eod_coverage_summary.csv`
- `results/data/tiingo_small_panel/tiingo_close_wide.csv`
- `results/data/tiingo_small_panel/tiingo_close_wide.parquet`

### Tiingo 50-ticker panel

- `results/data/tiingo_famous_50/tiingo_eod_panel_long.csv`
- `results/data/tiingo_famous_50/tiingo_eod_panel_long.parquet`
- `results/data/tiingo_famous_50/tiingo_eod_metadata.csv`
- `results/data/tiingo_famous_50/tiingo_eod_coverage_summary.csv`

Interpretation:

- this is the keyed vendor-style extension surface
- it is useful for teaching API authentication
- it is not the main downstream Week 4 dataset

### Yahoo small panel

- `results/data/yahoo_small_panel/yahoo_chart_panel_long.csv`
- `results/data/yahoo_small_panel/yahoo_chart_panel_long.parquet`
- `results/data/yahoo_small_panel/yahoo_chart_metadata.csv`
- `results/data/yahoo_small_panel/yahoo_chart_coverage_summary.csv`
- `results/data/yahoo_small_panel/yahoo_chart_failures.csv` only if some
  tickers fail

### Yahoo 50-ticker panel

- `results/data/yahoo_famous_50/yahoo_chart_panel_long.csv`
- `results/data/yahoo_famous_50/yahoo_chart_panel_long.parquet`
- `results/data/yahoo_famous_50/yahoo_chart_metadata.csv`
- `results/data/yahoo_famous_50/yahoo_chart_coverage_summary.csv`
- `results/data/yahoo_famous_50/yahoo_chart_failures.csv` only if some
  tickers fail
- `results/data/yahoo_famous_50/_ticker_cache/`
  - per-ticker cache used for resume mode

Interpretation:

- this is the canonical Week 4 50-name equity dataset
- Stage 2 and Stage 3 default to Yahoo outputs

## Stage 2 Outputs in `results/data/stage2/<provider>/`

Each provider gets the same final Stage 2 Parquet set:

- `{provider}_adjclose_wide.parquet`
- `{provider}_returns_wide.parquet`
- `{provider}_returns_long.parquet`
- `{provider}_returns_features_long.parquet`

Interpretation:

- adjusted prices are the base input for return construction
- wide returns show the row-wise matrix calculation
- long returns show the `groupby` panel calculation
- the feature-rich long panel is the main Stage 2 output for later weeks
- by default, the canonical Stage 2 path is `results/data/stage2/yahoo/`

## Stage 2 Long-Panel Feature Columns

The feature-rich long panel adds:

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

## Equity Schema Notes

### Tiingo long panel

Key:

- `ticker`
- `date`

Fields:

- `open`
- `high`
- `low`
- `close`
- `volume`
- `adjOpen`
- `adjHigh`
- `adjLow`
- `adjClose`
- `adjVolume`
- `divCash`
- `splitFactor`

Interpretation:

- raw OHLCV is closest to observed market data
- adjusted fields are the better default for return work
- `divCash` and `splitFactor` show when corporate actions matter

### Yahoo long panel

Key:

- `ticker`
- `date`

Fields:

- `open`
- `high`
- `low`
- `close`
- `adjClose`
- `volume`
- `dividend`
- `splitFactor`

Interpretation:

- Yahoo `close` is already split-adjusted
- Yahoo `adjClose` is split-and-dividend-adjusted
- Yahoo is useful for free historical pulls, but it is not raw Tiingo-style
  OHLCV

## Stage 2 Figure Outputs

Week 4 Stage 2 figures live under:

- `results/figures/stage2/tiingo/`
- `results/figures/stage2/yahoo/`

The canonical Stage 2 figure path is:

- `results/figures/stage2/yahoo/`

The canonical Stage 2 figure pack includes:

- pooled return distribution
- largest one-day moves
- volatility ranking
- annualized return ranking
- Sharpe ratio ranking
- top/bottom 5 cumulative-return comparison
- daily count of names with returns above `10%` in absolute value

## Stage 3 Outputs

Stage 3 saves the in-sample portfolio objects under:

- `results/data/stage3/<provider>/`
- `results/tables/stage3/<provider>/`
- `results/figures/stage3/<provider>/`

Canonical Stage 3 files:

- `{provider}_portfolio_weights.parquet`
- `{provider}_portfolio_returns.parquet`
- `{provider}_efficient_frontier.parquet`
- `{provider}_portfolio_metrics.csv`

Interpretation:

- weights are stored in long form with columns `portfolio`, `ticker`, `weight`
- portfolio returns store the daily rebalanced constant-weight return series
- the frontier file stores annualized expected return and volatility points
- the metrics file summarizes annualized return, annualized volatility, Sharpe
  ratio, and max drawdown
- by default, the canonical Stage 3 path is `results/data/stage3/yahoo/`

## Stage 3 Figure Outputs

The FT-style Stage 3 portfolio pack includes:

- portfolio weights
- growth of `$1`
- drawdown comparison
- in-sample portfolio scorecard
- efficient frontier with the tangency line

## Stage 4 App Inputs

The Week 4 app keeps a small committed fallback bundle under:

- `app/fixtures/yahoo_app_10_long.parquet`
- `app/fixtures/french_daily_rfr.parquet`

Interpretation:

- the runtime app universe is narrower than the Week 4 lecture 50-name universe
- the app uses Yahoo as the main runtime source
- the committed fixture is the fallback path for deploy reliability and AppTest

## Rules

- keep committed source inputs in `data/`
- keep downloaded and derived outputs in `results/data/`
- keep the Tiingo key out of tracked files
- use adjusted prices for Stage 2 returns
- do not silently delete outliers during Stage 2
- keep Stage 3 strictly in-sample for this week
- keep Stage 4 strictly in-sample as well
