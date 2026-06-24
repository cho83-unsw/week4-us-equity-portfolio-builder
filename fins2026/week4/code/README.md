# Week 4 Week-Local Code

Use this folder for week-local reusable helpers. If the logic becomes useful
across multiple weeks, move it into `fintools/`.

Current Week 4 modules:

- `api_intro_ecb.py`: helpers for the free ECB API introduction
- `risk_free_rate_french.py`: helpers for the Kenneth French daily risk-free
  download and final Parquet output
- `equity_api_tiingo.py`: helpers for authenticated Tiingo pulls, long panels,
  coverage summaries, and wide reshapes
- `equity_api_yahoo.py`: helpers for Yahoo chart-endpoint pulls, per-ticker
  cache/retry behavior, and normalized long-panel outputs
- `stage2_equity_returns.py`: helpers for adjusted-price pivots, wide and long
  return construction, risk-free merges, and rolling six-month feature columns
- `stage2_return_figures.py`: helpers for the FT-style Stage 2 diagnostic
  figure pack
- `stage3_portfolios.py`: helpers for balanced in-sample return matrices,
  mean-variance weights, efficient-frontier construction, and portfolio
  metrics
- `stage3_portfolio_figures.py`: helpers for the FT-style Stage 3 portfolio
  figure pack
- `stage4_app.py`: helpers for the 10-stock client-facing app, including live
  Yahoo/French loading, fallback fixtures, custom-weight normalization, long-only
  optimization, and app-specific portfolio comparison outputs

