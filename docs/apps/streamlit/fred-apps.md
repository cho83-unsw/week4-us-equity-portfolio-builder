# FRED App Pattern

FRED graph CSV URLs are useful for course apps because they do not require an
API key.

Build the URL with:

```python
from fintools.apps import fred_graph_url

url = fred_graph_url(["UNRATE", "CPIAUCSL", "INDPRO"])
```

Then clean with `clean_fred_graph_csv`.

When pulling several FRED series, use `read_fred_graph_csv` from
`fintools.apps` rather than calling `pd.read_csv` on a long URL directly. The
helper batches multi-series downloads and avoids brittle decode failures seen
on some large `fredgraph.csv` requests.

## Forecasting Rules

- Forecast the economically meaningful target, not whatever column happens to
  be in the dataframe.
- Declare the target with `SeriesSpec` and use `forecast_series_spec` so the
  app can explain what is being modeled and what is being plotted.
- Treasury rates, yield spreads, and credit OAS should normally forecast
  changes. Plot the historical level plus the implied level path:
  `level[t+h] = level[t] + cumulative_forecast_change[t+h]`.
- Quarterly real GDP should normally forecast annualized quarterly growth.
  Convert it back to a level path with quarterly compounding.
- VIX is volatility context in the Week 2 app, not a forecast target.
  Do not add VIX to simple baseline forecast selectors unless the product has a
  real volatility-modeling rationale.
- Use Streamlit math rendering for FRED formulas and model equations. Prefer
  `st.latex` or Markdown LaTeX delimiters over code-style formula strings in
  the visible app.
- CBOE VIX is quoted in percent terms, as annualized expected S&P 500
  volatility. Label VIX values with `%`, not `index`.
- If VIX, high-yield OAS, and yield-curve slope are combined into a stress
  score, label the score as a z-score and explain direction: higher values
  mean more market stress; `0` is the selected-sample average.
- Show a current stress measure, such as the latest 21-trading-day average,
  when the app has a sample-period control. A five-year or twenty-year sample
  describes the comparison window, not the current condition by itself.
- If the current stress score is standardized against the selected sample,
  label the comparison window directly, for example `Current stress vs 5Y
  (z)`, and explain that the value can change when the sample period changes.
- Interpret stress-score percentiles in words and compare like with like. If
  the current score is a 21-trading-day average, compare it with historical
  21-trading-day averages in the selected sample.
- Every current FRED metric must show the actual latest observation date for
  that series. Do not imply that daily market data and quarterly macro data
  share the same date.
- Yield-curve views should interpret latest slope, inversion, flattening, or
  steepening instead of only plotting Treasury maturities.
- GDP views should interpret the latest annualized quarterly growth rate,
  year-over-year growth, and forecast-implied level change, and should remind
  users that GDP is lagged and revised.
- CPI should usually become year-over-year inflation.
- Industrial production and payrolls should usually become growth rates.
- Respect release lags. GDP, inflation, payrolls, and industrial production are
  observed only after publication and are later revised; serious real-time apps
  need vintage-aware data.
- Always show a backtest or a simple error summary.
- Forecast bands are approximate; describe them as uncertainty bands, not
  confidence guarantees.
- Daily FRED forecasts can be visually tiny when plotted against decades of
  history. Use an analysis sample-period control, a visible forecast connection
  from the final observed point, and a clearly labeled horizon unit.
- U.S. macro time-series should include light gray NBER recession shading.
- Long FRED histories should use Plotly range controls and unified hover labels
  so the app remains useful at full sample and zoomed-in views. Prefer a range
  slider when the chart also has a legend.
- If live FRED fails, show a concise warning and fall back to a small frozen
  fixture instead of crashing.

## Good Macro App Sections

- Latest conditions
- Historical chart
- Forecast and uncertainty band
- Backtest
- Method and caveats
