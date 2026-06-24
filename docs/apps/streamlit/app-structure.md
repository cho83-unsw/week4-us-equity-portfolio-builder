# Streamlit App Structure

Use a small app architecture:

1. Page configuration and app title.
2. Cached data loading.
3. Pure data transformations.
4. Pure modeling or insight functions.
5. UI controls in the sidebar.
6. Main view with metric cards, a data-health strip, lazy tabs, charts, and
   interpretation.

Keep `streamlit_app.py` readable. If a function grows beyond one screen, move
it into `code/` or `fintools/` and test it separately.

The Streamlit config belongs at the repository root as `.streamlit/config.toml`.
In this repo that config disables usage telemetry, runs local apps headless,
and avoids the first-run email prompt.

Final-project app scaffolds should also include `SUBMISSION_CHECKLIST.md` at
the project root. If you want a machine-readable metadata file such as
`submission.json`, keep it optional and keep it out of code comments. The app
repo should also carry `.github/workflows/submission-check.yml` so every push runs
`python tools/workflow.py check-app-submission --target ... --run-tests`.

Nested app entrypoints must make the repository root importable before importing
repo-local packages. Put the repo-root `sys.path` bootstrap before imports from
`fintools` or project-local packages. This avoids Streamlit Cloud
`ModuleNotFoundError` failures when the app file is below the repo root.

## UI Baseline

- Use a short app title and one-sentence caption.
- Put controls in the sidebar.
- Keep only global controls in the sidebar. Put chart, model, and horizon
  controls in the tab or panel they affect.
- Use metric cards for the main state of the data.
- Do not use large metric values for long text. Model targets, formulas, and
  caveats belong in compact cards, captions, or Method text.
- Use `st.latex` or Markdown LaTeX delimiters for mathematical equations.
  Method tabs should read like finance documentation, not source-code notes.
- For scorecards or composite indicators, show the current or recent state,
  not only a full-sample statistic. Define the unit, direction, and comparison
  window in the card help text.
- Add a data-health strip near the top of the app: active source, sample start,
  sample end, observations, and missing values.
- Persist important controls with URL query parameters so the current view can
  be shared with a grader or collaborator.
- For long time-series apps, include a segmented sample-period control. The
  selected period should control the chart, metrics, forecast, backtest, and
  displayed data unless the app explicitly labels it as chart-only zoom.
- Use tabs for natural product sections such as `Forecast`, `Data`, `Backtest`,
  and `Method`. For expensive views, use lazy tabs through `st.tabs(...,
  on_change="rerun")` plus each tab's `.open` property, or use the repo
  `lazy_tabs` helper.
- When tabs are URL-shareable, do not treat the URL and the tab widget as equal
  sources of truth after the first render. Use the URL to seed the initial tab,
  then keep navigation in `st.session_state`; otherwise reruns can briefly
  switch tabs and then bounce back to the old URL state.
- Add a one-sentence explanation at the top of each tab so users understand the
  view before reading the chart.
- Headings should name the decision or section, not the implementation. Use
  labels such as `Market Overview`, `Current Stress`, or `Forecast Results`;
  avoid vague headings such as `What This Shows`.
- Use client-facing language in visible text. Do not write "This app...",
  "the user can...", "state indicator", or other implementation-facing phrases
  in the product UI.
- Show loading or error states when data is unavailable.
- Keep charts full width and avoid tiny subplots inside apps.
- Make every visible dataframe presentation-safe: convert date indexes into a
  `Date` column, capitalize labels, and remove underscores from column names.
- Include units or denominations on visible metrics and table headers whenever
  values are not obvious.
- Use `st.column_config` through the repo table helpers so date and numeric
  columns render with app-facing formats.
- Size short presentation tables to their actual row count. Blank grid rows in
  an Overview or KPI table make the app look unfinished.
- Never pass optional Streamlit layout arguments with `None` values. Omit the
  argument unless a real value is intended.
- Provide CSV downloads for the selected data sample and important model
  outputs.
- Forecast charts must make every legend item visible. If the forecast horizon
  is short relative to the history, connect the forecast to the final observed
  point, draw the band behind it, and use a sample-period control or focused
  view so the forecast is inspectable.
- Forecast apps must declare the target transform before modeling. Use
  `SeriesSpec` plus `forecast_series_spec` for baseline apps so users can see
  whether the model forecasts levels, changes, growth, or no forecast.
- U.S. macro time-series should include light gray NBER recession shading.
- Time-series charts should use unified hover and range controls. If a chart
  has a legend, use a range slider instead of range selector buttons so the
  controls cannot overlap legend labels.
- Before plotting a time series, sort the date index and check that it is
  monotonic. Lines crossing the chart diagonally are usually an ordering bug,
  not a design choice.
- For noisy daily scores, pair the daily line with the rolling average used in
  the headline metric so the chart matches the dashboard number.
- If the headline metric is a rolling average, compare its percentile with
  historical rolling averages that use the same window.
- Write the `Method` tab for an outside user. Explain data, model, backtest,
  and uncertainty in product language; do not expose implementation-module
  names as the main explanation. When baseline models are deterministic and
  known, include the concrete equations.
- Analysis tabs need a direct interpretation. For example, a yield-curve tab
  should explain whether the curve is upward sloping, flat, inverted,
  flattening, or steepening; a GDP tab should explain latest annualized
  quarterly growth, year-over-year growth, forecast-implied level change,
  release lags, and revision risk.

## What To Avoid

- long blocks of explanatory text before the app does anything
- raw dataframe column names in visible labels
- hidden dependencies on generated local files
- apps that work only on the author's machine
- forecasts without target-transform language, a backtest, or uncertainty
  language
