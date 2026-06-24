# Week 4 Workshop

Week 4 now covers four stages of the data factory floor.

- Stage 1: connect to sources and save local datasets
- Stage 2: compute returns, run data checks, and build rolling features
- Stage 3: form and evaluate the first in-sample mean-variance portfolios
- Stage 4: turn the portfolio workflow into a client-facing Streamlit app

## Core Path

1. Review `README.md`, `DATA_GUIDE.md`, and `guidance/week-context.md`.
2. Run `python fins2026/week4/scripts/describe_data.py`.
3. Run `python fins2026/week4/scripts/run_beginner_ecb_api.py`.
4. Explain the ECB request in plain English:
   - the URL is the endpoint
   - the query string controls the request
   - the GET call returns raw data
   - we tidy the response after the fetch
5. Run `python fins2026/week4/scripts/run_beginner_french_rfr.py`.
6. Explain the French risk-free step:
   - it is still part of Stage 1
   - we keep only `RF`
   - we rename it to `rfr`
   - we divide by `100`
   - we save only one final Parquet file
7. Before Tiingo, make sure `TIINGO_API_KEY` is set in the current shell.
8. If an assistant is helping and the key is missing, it should ask for it
   before continuing.
9. Run `python fins2026/week4/scripts/run_beginner_tiingo_small_panel.py`.
10. Run `python fins2026/week4/scripts/run_beginner_tiingo_wide_panel.py`.
11. Explain the Tiingo role:
    - it teaches keyed API access
    - it shows a vendor-style workflow
    - it is not the main downstream Week 4 dataset
12. Optionally run `python fins2026/week4/scripts/run_beginner_tiingo_famous_50.py`.
13. Run `python fins2026/week4/scripts/run_beginner_yahoo_small_panel.py`.
14. Run `python fins2026/week4/scripts/run_beginner_yahoo_famous_50.py`.
15. Explain the Yahoo role:
    - it is the main Week 4 equity dataset
    - Stage 2 and Stage 3 default to Yahoo
16. Explain the source contrast:
    - Tiingo is keyed and vendor-like
    - Yahoo is public and more brittle
    - both save long panels
17. Run `python fins2026/week4/scripts/run_beginner_stage2_returns_wide.py`.
18. Explain the wide return calculation from adjusted prices.
19. Run `python fins2026/week4/scripts/run_beginner_stage2_returns_long.py`.
20. Explain the long `groupby` return calculation and the parity check.
21. Run `python fins2026/week4/scripts/run_beginner_stage2_features_long.py`.
22. Explain the rolling six-month features:
    - average return
    - annualized volatility
    - VaR-95%
    - Sharpe
    - Sortino
23. Run `python fins2026/week4/scripts/make_stage2_return_check_figures.py`.
24. Explain the Stage 2 figure pack:
    - return distribution
    - extreme single-day moves
    - volatility ranking
    - top/bottom 5 cumulative returns on log scale
    - extreme-move count with recession shading
25. Run `python fins2026/week4/scripts/run_beginner_stage3_portfolios.py`.
26. Explain the three in-sample portfolio definitions:
    - equal-weight
    - minimum variance
    - mean-variance tangency portfolio
27. Emphasize the Stage 3 caveat:
    - this is in-sample only
    - out-of-sample work would require re-estimation using past data only
28. Run `python fins2026/week4/scripts/make_stage3_portfolio_figures.py`.
29. Explain the Stage 3 figure pack:
    - portfolio weights
    - growth of `$1`
    - drawdowns
    - in-sample scorecard
    - efficient frontier and tangency line
30. Run `python fins2026/week4/scripts/build_week4_app_fixture.py`.
31. Launch `streamlit run fins2026/week4/app/streamlit_app.py`.
32. Explain the Stage 4 app contract:
    - the app uses a 10-stock Yahoo universe
    - live Yahoo and live Kenneth French are the runtime path
    - committed fixtures are the fallback path
    - the app stays in-sample only
    - the app compares custom, equal-weight, minimum-variance, and mean-variance portfolios

## Common API Errors

- `400`: bad request, usually a bad parameter or date format
- `401`: missing or invalid Tiingo key
- `403`: request blocked even though the key exists
- `404`: wrong endpoint path or wrong ticker/code
- `429`: request limit hit
- `5xx`: provider-side failure

Read the status code first before changing the code.

## Teaching Message

- Stage 1 gets the data in the door.
- Stage 2 checks whether the saved prices are usable for later portfolio work.
- Stage 3 uses the cleaned panel to build the first risky portfolios.
- Stage 4 turns that same in-sample portfolio logic into a client-facing app.
- Yahoo is the main Week 4 equity dataset.
- Tiingo stays in the week because students still need to learn how keyed APIs work.
- Long format is the canonical equity panel.
- Wide format is a derived shape for return and covariance work.
- The Kenneth French `rfr` file is part of the same pipeline, not a separate
  week.
- Outliers should be flagged and investigated before later optimization work.
- Out-of-sample portfolio evaluation is the next step, but it is not coded in
  Week 4 yet.
