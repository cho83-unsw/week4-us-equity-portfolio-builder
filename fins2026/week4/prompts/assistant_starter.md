# Week 4 Assistant Starter Prompt

Week 4 is the first four stages of the data factory floor.

Stage 1:

- connect to outside sources
- authenticate when needed
- pull raw data
- save clean local datasets

Stage 2:

- compute simple daily returns from adjusted prices
- compare wide and long return construction
- merge the daily risk-free rate
- build rolling six-month features
- export FT-style data-check figures

Stage 3:

- form the first in-sample mean-variance portfolios
- compare equal-weight, minimum-variance, and mean-variance tangency weights
- evaluate in-sample cumulative returns, drawdowns, Sharpe ratios, and the
  efficient frontier

Stage 4:

- turn the Week 4 portfolio workflow into a client-facing Streamlit app
- keep Yahoo as the runtime equity source
- keep the app in-sample only
- let users compare custom, equal-weight, minimum-variance, and mean-variance portfolios

Provider priority:

- Yahoo is the main Week 4 equity dataset
- Tiingo stays in the week to teach keyed API access and vendor-style workflows
- unless the user explicitly asks otherwise, default Stage 2, Stage 3, and Stage 4 work
  to Yahoo

Do not jump ahead to out-of-sample portfolio evaluation or forecasting unless
the user explicitly asks to move beyond the Week 4 scope.

Before any Tiingo step:

- stop and ask for `TIINGO_API_KEY` if it is not already set in the current
  shell
- help the student set it for the current shell only
- never write it into tracked files, prompts, docs, or logs

Week 4 source rules:

- Tiingo history uses `GET /tiingo/daily/{ticker}/prices`
- Yahoo history uses `GET https://query2.finance.yahoo.com/v8/finance/chart/{ticker}`
- Yahoo is queried directly, not through `yfinance`
- Kenneth French daily `RF` is renamed to `rfr` and divided by `100`
- the French step saves only one final Parquet file

Week 4 Stage 2 rules:

- use adjusted prices for return construction
- compute simple daily returns, not log returns
- verify wide-return and long-return parity
- keep long format as the main panel
- treat wide tables as derived objects
- merge `rfr` by date and forward-fill the tail
- flag outliers, do not silently delete them

Rolling Stage 2 features:

- `rolling_6m_avg_ret`
- `rolling_6m_vol`
- `rolling_6m_var_95`
- `rolling_6m_sharpe`
- `rolling_6m_sortino`

with a `126`-trading-day window.

Common API errors:

- `400`: bad request
- `401`: missing or invalid key
- `403`: not allowed
- `404`: wrong endpoint or ticker
- `429`: too many requests
- `5xx`: provider-side failure

Diagnose the status code first. Do not treat key and quota errors as parsing
bugs.

Default Week 4 flow:

1. ECB API
2. Kenneth French `rfr`
3. Tiingo small pull
4. explain keyed API access with Tiingo
5. optionally run the Tiingo 50-name pull
6. Yahoo small pull
7. Yahoo 50-name pull
8. Stage 2 wide returns on Yahoo
9. Stage 2 long returns on Yahoo
10. Stage 2 rolling features on Yahoo
11. Stage 2 FT-style check figures on Yahoo
12. Stage 3 in-sample portfolios on Yahoo
13. Stage 3 FT-style portfolio figures on Yahoo
14. refresh the Week 4 app fixture
15. build or launch the Week 4 Streamlit app
