# Weekly Overlay

This folder is `fins2026/week4`.

## Week Identity

- Week 4 covers the first four stages of the data factory floor.
- Stage 1: source connection, authentication, and local dataset creation.
- Stage 2: return construction, data checks, and rolling features.
- Stage 3: in-sample portfolio construction and evaluation from the cleaned
  Stage 2 outputs.
- Stage 4: the Week 4 client-facing Streamlit app built on a 10-stock Yahoo
  runtime universe.

Default mental model:

- ECB teaches the simplest free API request
- Kenneth French adds the daily risk-free series
- Tiingo teaches a keyed vendor-style equity workflow
- Yahoo is the main equity dataset for the rest of the week
- Stage 2 converts those saved prices into usable return panels
- Stage 3 turns those cleaned return panels into mean-variance portfolios
- Stage 4 packages the Week 4 logic into a client-facing portfolio app

## Working Rules

- Keep week-specific work inside this folder.
- Use `data/` for committed source inputs only.
- Use `results/data/` for generated datasets.
- Use `results/figures/` for exported Week 4 figures.
- Before any Tiingo step, check whether `TIINGO_API_KEY` is already set in the
  current shell. If it is missing, ask the student for it first.
- Never write the Tiingo key into tracked files, prompts, docs, or logs.
- Diagnose HTTP status codes before changing code:
  - `400`: bad request
  - `401`: missing or invalid key
  - `403`: not allowed
  - `404`: wrong endpoint or ticker
  - `429`: rate or quota limit
  - `5xx`: provider-side failure
- Use Tiingo historical windows through `/tiingo/daily/{ticker}/prices`.
- Use Yahoo historical pulls through `https://query2.finance.yahoo.com/v8/finance/chart/{ticker}`.
- Do not introduce `yfinance` unless the user explicitly asks for it.
- Keep the canonical equity output in long panel form with key `ticker, date`.
- Treat wide price and return tables as derived Stage 2 objects.
- Week 4 defaults should treat Yahoo as the canonical downstream provider for:
  - Stage 2 return construction
  - Stage 2 figures
  - Stage 3 portfolios
- Week 4 Stage 4 should treat Yahoo as the live runtime source and the committed
  app fixture as the fallback source.
- Keep Tiingo available as the authentication and vendor-style API teaching path.
- For Stage 2, use adjusted prices and simple daily returns.
- Merge the Kenneth French `rfr` series by `date` and forward-fill after the
  last available French date so the equity panel reaches the latest market
  observations.
- Stage 2 should flag suspicious returns, not silently winsorize or drop them.
- Stage 3 defaults to Yahoo 50, uses the full balanced in-sample window, and
  allows short sales.
- Stage 3 portfolios are:
  - Equal-weight
  - Minimum variance
  - Mean-variance, defined here as the tangency or max-Sharpe portfolio
- Stage 4 app scope:
  - 10-stock Yahoo universe
  - custom, equal-weight, minimum-variance, and mean-variance portfolios
  - long-only and unconstrained optimization modes
  - in-sample historical comparison only
- Do not introduce rolling re-estimation or out-of-sample portfolio code
  unless the user explicitly asks for it.
- Keep reusable week-local logic in `code/`.
- Regenerate `guidance/*.md` after week docs, scripts, or data contracts change.

## Useful Commands

- `python fins2026/week4/scripts/describe_data.py`
- `python fins2026/week4/scripts/run_week.py`
- `python fins2026/week4/scripts/run_beginner_stage2_returns_wide.py`
- `python fins2026/week4/scripts/run_beginner_stage2_returns_long.py`
- `python fins2026/week4/scripts/run_beginner_stage2_features_long.py`
- `python fins2026/week4/scripts/make_stage2_return_check_figures.py`
- `python fins2026/week4/scripts/run_beginner_stage3_portfolios.py`
- `python fins2026/week4/scripts/make_stage3_portfolio_figures.py`
- `python fins2026/week4/scripts/build_week4_app_fixture.py`
- `streamlit run fins2026/week4/app/streamlit_app.py`
- `python tools/workflow.py build-week-context --target fins2026/week4`
