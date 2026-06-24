# Publication-Grade Streamlit Apps

Use this checklist for every course app, not only the Week 2 example.

## Product Standard

- Start with one clear user question.
- Put data loading, cleaning, feature construction, and modeling in functions
  that can be tested without Streamlit.
- Keep controls in the sidebar and keep the first screen focused on the main
  insight.
- Show a compact data-health strip with source, sample start, sample end,
  observation count, and missing values.
- Use metric cards for current state, changes, percentiles, and model quality.
- Keep metric cards responsive. Use the shared metric helpers so cards wrap
  instead of clipping on narrow or browser-zoomed screens.
- Do not use large `st.metric` values for long text such as model targets,
  formulas, or caveats. Use compact cards, captions, or Method text instead.
- Render equations with `st.latex` or Markdown LaTeX delimiters. Do not show
  source-code-style formulas in client-facing explanation.
- Put controls near the output they affect. Global controls belong in the
  sidebar; forecast-specific controls should live in the forecast/backtest view.
- Include a Method or Caveats view written for a real user, not for a developer.
- Write copy as client-facing product language. Avoid internal phrasing such as
  "This app...", "so the user can...", "state indicator", or "baseline forecast
  target" in visible UI text.
- Every displayed metric needs units or denomination when the number is not
  self-explanatory. Use `%`, `index`, `USD`, `billions`, or similar labels in
  the card label, value, or caption.
- Composite scores need direction, scale, and sample context. State whether
  higher values are better or worse, label z-scores as `(z)`, explain that
  `0` is the selected-sample average, and show a current or recent reading
  alongside any historical sample view.
- Percentiles must be interpreted in words. Prefer "higher than 78% of days in
  the selected sample" over bare labels such as "sample percentile."

## Forecast Target Discipline

- Define one `SeriesSpec` per modeled series before building forecasts.
- The forecast target and the plotted object can differ. For rates, spreads,
  and credit OAS, forecast changes and plot the implied level path. For
  quarterly GDP, forecast annualized quarterly growth and plot the implied real
  GDP level path.
- Do not put context series such as VIX into simple forecast controls unless
  the app uses a model appropriate for volatility or risk-state dynamics.
- Write the target rule in the Method view. Users should know whether they are
  seeing a level forecast, a change forecast converted to levels, or a growth
  forecast converted to levels.
- Treat release lags and data revisions as first-class caveats. GDP, CPI,
  payrolls, and industrial production are not available on the observation date.
- Yield-curve views should say what the latest slope and one-year shift imply:
  upward sloping, flat, inverted, flattening, or steepening. GDP views should
  say whether latest annualized quarterly growth is contractionary, slow,
  moderate, or strong, and connect that to the forecast-implied level change.

## App State

- Make important controls URL-shareable with `st.query_params`.
- Validate query parameters before using them in widgets.
- Use deterministic defaults when a URL parameter is missing or invalid.
- Sync the URL after controls are rendered so graders can copy the exact view
  they are inspecting.

## Performance

- Cache API calls, CSV loads, and expensive transformations with
  `st.cache_data(ttl=86400)`.
- Use `st.cache_resource` only for shared resources such as model objects or
  database connections.
- Streamlit tabs should be lazy when content is expensive. Use
  `st.tabs(..., on_change="rerun")` and render only the tab whose `.open`
  property is true, or use the repo `lazy_tabs` helper.
- Do not put Streamlit UI calls inside cached functions.

## Figures

- Use Plotly for app charts and the shared `fintools.apps` Plotly helpers before
  writing bespoke chart code.
- Time-series charts should have horizontal gridlines, clean legends, unified
  hover, range controls, and sparse date ticks.
- Range controls and legends must not overlap. If a chart has a legend, use a
  bottom range slider instead of range selector buttons.
- U.S. macro time-series should show light gray NBER recession shading.
- Forecast charts must make every legend item visible: observed line, forecast
  line, and uncertainty band.
- Noisy daily composites should show a subdued daily line plus a rolling
  average that matches the current-state metric. Always sort time indexes
  before plotting; diagonal time-series segments usually mean the dates are out
  of order.
- Do not expose raw dataframe column names in chart titles, axes, hover labels,
  legends, or captions.

## Tables And Downloads

- Use app-facing labels: capitalized, no underscores, and clear units.
- Prefer common symbols over internal abbreviations in the UI. For example, use
  `%` or "percentage points" instead of `p.p.` unless the audience expects the
  abbreviation.
- Render tables with typed Streamlit column configuration for dates and numbers.
- Size short presentation tables to their real row count so blank grid rows do
  not appear below the data.
- Do not pass `height=None` to Streamlit display elements; omit the height
  argument unless a real pixel value is needed.
- Center compact dashboard tables when they are used as presentation panels.
- Hide raw indexes unless the index is meaningful and explicitly labeled.
- Provide CSV downloads for the selected sample and key model outputs.

## Deployment And Grading

- Run apps from the repo root with `streamlit run path/to/app/streamlit_app.py`.
- Keep the local terminal open while testing localhost.
- Before hand-in, run `python tools/workflow.py check-app-submission --target ...`.
- Streamlit Community Cloud needs the exact GitHub repo, branch, entrypoint
  path, Python version, and dependencies.
- If the GitHub repo is private, make the Streamlit app public for grading and
  confirm the public URL works in an incognito browser.
- Never commit `.streamlit/secrets.toml`, `.env`, `.venv/`, local absolute
  paths, or private raw data.
