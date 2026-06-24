# Streamlit App Prompt

Use this with an AI assistant when you have a dataframe, script, or analysis
and want to build a course app.

```text
I want to turn this analysis into a Streamlit app.

Use the repo Streamlit rules in docs/apps/streamlit/ and the build-app
workflow in docs/ai/workflows/build-app.md.

Build a polished app with:
- one clear product question
- cached data loading
- sidebar controls
- forecast/model/horizon controls placed beside the chart or tab they affect
- metric cards
- a data-health strip with source, sample span, observation count, and missingness
- URL-shareable state for important controls with validated query parameters
- interactive Plotly figures
- sample-period controls for long time series
- lazy tabs or an active-view control so hidden expensive views do not rerun
- a data tab
- a method/caveats tab
- typed Streamlit tables with clean date and numeric formatting
- CSV downloads for selected data and important model outputs
- tests or at least a smoke test
- a README with local run and Streamlit Community Cloud deployment details
- a SUBMISSION_CHECKLIST.md with public app URL, accessible GitHub repo URL,
  branch, entrypoint, and final commit hash fields
- instructions to run `python tools/workflow.py check-app-submission --target ...`
  before hand-in
- repo-root import-path bootstrap before importing repo-local packages when the
  app entrypoint is nested below the repo root

Assume local PyCharm development, regular pushes to a private student-owned
GitHub repo, and a public Streamlit app URL for grading. Keep data
transformations and model logic in pure functions that can be tested without
Streamlit. Do not use local absolute paths. Do not commit secrets.

Forecasting standards:
- define `SeriesSpec` metadata before forecasting any series
- decide explicitly whether each series is a level, change, growth rate, or not
  forecastable
- for rates, yield spreads, and credit OAS, forecast changes and plot implied
  levels unless there is a better domain-specific reason
- for GDP-style fundamentals, forecast growth and plot implied levels
- do not forecast VIX-style stress indicators with simple baseline models by
  default

Presentation standards:
- never show raw dataframe column names such as `absolute_error` to users
- never use large metric values for long model-target names, formulas, or caveats
- render equations with `st.latex` or Markdown LaTeX delimiters; do not expose
  code-style formulas in finance or forecasting explanations
- write visible UI copy as client-facing product language; avoid phrases like
  "This app..." and "so the user can..."
- include units or denominations on every visible metric and table header
- for composite indicators, state whether higher values are better or worse,
  label z-scores as `(z)`, explain the comparison window, and show a current
  or recent reading
- interpret percentiles in words instead of showing a bare percentile label
- compare rolling-average percentiles with historical rolling averages that use
  the same window
- format data tables with capitalized labels and date columns
- size short presentation tables so they do not show blank rows below the data
- test every tab or active view, not only the default view
- for URL-shareable tabs, use URL state only to initialize the first tab in a
  browser session, then use `st.session_state` for tab clicks so navigation does
  not require a double click
- make forecast and uncertainty traces visible when they appear in the legend
- use the shared `fintools.apps` helpers for query state, lazy tabs, data-health
  panels, metric strips, typed tables, downloads, and Plotly app figures
- use unified hover, horizontal gridlines, range controls, and NBER recession
  shading for U.S. macro time-series figures
- use a range slider instead of range selector buttons when a chart also has a
  legend
- sort time-series indexes before plotting and use a rolling average for noisy
  daily composites when it matches the headline metric
- fall back to fixture data when a live API fails
- write the Method tab as user-facing product documentation with equations for
  deterministic baseline models, not developer notes
- make each domain tab answer a client question: yield-curve tabs interpret
  slope, inversion, flattening, or steepening; GDP tabs interpret latest
  quarterly growth, year-over-year growth, forecast-implied level change,
  release lags, and revision risk
```
