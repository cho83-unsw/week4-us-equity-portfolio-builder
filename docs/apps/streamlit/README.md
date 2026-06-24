# Streamlit App Framework

This folder is the shared source of truth for building course apps.
Weekly folders should add only the week-specific data, prompt, and product
brief. General Streamlit rules live here.

## App Goal

Every app should convert analysis into an inspectable product:

- a clear question
- transparent data sources
- reproducible cleaning and modeling code
- interactive figures or controls
- a short interpretation of the main insight
- a public deployment link for grading

## Standard Folder Shape

```text
app/
  streamlit_app.py
  README.md
  tests/test_app_smoke.py
.streamlit/config.toml
.github/workflows/submission-check.yml
SUBMISSION_CHECKLIST.md
data/
guidance/
results/app/
```

Run apps from the repo root:

```bash
streamlit run projects/my_project/app/streamlit_app.py
```

Check submission readiness from the repo root:

```bash
python tools/workflow.py check-app-submission --target projects/my_project
```

Prepare a minimal private-repo bundle for deployment rehearsal:

```bash
python tools/workflow.py prepare-app-repo --source projects/my_project --dest ../my_project_handin --repo my_project_handin
```

Running from the repo root keeps local paths aligned with Streamlit Community
Cloud, which runs apps from the root of the repository.

Local Streamlit apps are live only while the command is still running. Keep the
terminal, PowerShell tab, or PyCharm run pane open while using `localhost`;
closing it stops the local server and the browser will show a
connection-refused page. Do not rely on an AI assistant to leave a detached
background server running after the task finishes. Stop the app with `Ctrl+C`
in the terminal when you are done.

On macOS, Streamlit may mention Watchdog or Xcode Command Line Tools. Treat
that as an optional performance suggestion for faster file watching, not as a
fatal app error.

The course repo includes `.streamlit/config.toml` at the repo root so local
apps run headless and do not stop on Streamlit's first-run email prompt. If a
student deploys a standalone project repo, copy the `.streamlit/config.toml`
file to that repo root.

For final projects, the default workflow is a private student-owned GitHub
repository during development, regular private pushes, and a public Streamlit
Community Cloud app URL at hand-in. The teaching team must also have access to
the GitHub repository by the deadline. See `github-submission.md` and
`finish-deployment.md`.

If you are a student and want the plain-English path from local app to public
hand-in URL, start with `student-quickstart.md`.

If you are auditing an existing app, use `audit-checklist.md` before making
changes. It captures the current Streamlit docs benchmark, app-state gotchas,
deployment checks, and reusable findings format.

## Core Rules

- Keep data loading, transformations, and modeling in functions that can be
  tested without Streamlit.
- Once an app grows beyond a short prototype, keep `streamlit_app.py` as a thin
  entrypoint and split labels/specs, data loading, interpretation/model logic,
  and Streamlit views into focused modules.
- Use `st.cache_data(ttl=86400)` for FRED downloads, CSV loads, and expensive
  transformations.
- Use the reusable `fintools.apps` Streamlit and Plotly helpers for shared
  app patterns: query-parameter state, data-health panels, metric strips, lazy
  tabs, typed tables, downloads, time-axis controls, and NBER recession shading.
- Keep the sidebar for global controls. Put forecast/model/horizon controls in
  the forecast or backtest view so users can see what the control affects.
- For forecast apps, define a `SeriesSpec` before modeling. Do not blindly
  forecast raw levels. Rates, spreads, and credit OAS usually forecast changes
  and then reconstruct an implied level path; GDP-style activity series usually
  forecast growth; context series such as VIX can be displayed without being
  forecast.
- Do not commit `.streamlit/secrets.toml`.
- Do not use local absolute paths such as `C:\Users\...` or `/Users/...`.
- Keep the local `streamlit run ...` terminal open while testing the app.
- Push regularly to a private GitHub repo; do not wait until the deadline to
  create the remote.
- `submission.json` is optional. If you keep one for deployment metadata, do
  not let it contradict the real repo URL, entrypoint, visibility, or
  teaching-team access arrangement.
- Run `check-app-submission` before deploying or handing in the app.
- Use `prepare-app-repo` when creating a clean private GitHub deploy repo from
  the course workspace.
- Submit a public Streamlit URL and a GitHub repo URL the teaching team can
  access.
- Prefer one strong product question over many disconnected charts.
- Keep forecast methods transparent unless the assignment explicitly asks for
  heavier modeling.
- Use app-facing labels in charts and tables; raw dataframe names with
  underscores should not appear in the user interface.
- Use client-facing language in visible UI text. Avoid internal phrasing such
  as "This app...", "so the user can...", and model-development jargon.
- Render finance and forecasting equations with Streamlit math support
  (`st.latex` or Markdown LaTeX delimiters). Avoid code-style formulas in
  client-facing Method or Overview text.
- Include units or denominations on visible metrics and table headers.
- Composite indicators must state direction, units, and comparison window.
  Show a current or recent value, not only a statistic over the selected
  historical sample.
- If a composite indicator is standardized against a user-selected sample,
  name that comparison window in the metric label and explain that changing the
  sample can change the reported z-score or percentile.
- When a current value is a rolling average, compare its percentile with
  historical rolling averages that use the same window. Do not compare a
  21-day average with daily observations unless that mismatch is the point.
- Current market and macro metrics must include the actual latest observation
  date for the series behind the value, especially when daily and quarterly
  FRED series appear together.
- Percentiles should be interpreted in words, for example "higher than 78% of
  days in the selected sample."
- Long time-series apps should have a sample-period control, and forecast
  traces should be visible whenever they appear in the legend.
- Time-series range controls must not overlap legends. If a chart has a legend,
  use a bottom range slider instead of range selector buttons.
- Time-series data must be sorted before plotting. Diagonal segments across a
  chart are usually a date-ordering bug. For noisy daily scores, show a subdued
  daily line plus the rolling average used by the headline metric.
- Important app controls should be shareable through URL query parameters so a
  grader can open the exact same view.
- Streamlit tabs should be lazy for expensive views; default tabs can still run
  hidden content unless state-tracked lazy rendering is used.
- URL-shareable tabs need one stable source of truth. Let the URL set the
  initial tab for a fresh browser session, then let `st.session_state` own tab
  clicks. Do not feed a changing `?view=` value into `st.tabs(default=...)` on
  every rerun, because it can make the first click bounce back.
- Live data apps should degrade to a fixture or fallback view when the API is
  unavailable, and they should show both latest observation dates and source
  refresh status. A cached live load time, fixture snapshot date, and latest
  FRED observation date answer different user questions.
- Metric strips should wrap rather than forcing four or five cards into one
  row; presentation clipping is a product bug.
- Short presentation tables should use compact dynamic heights so they do not
  show empty grid rows below the real data.
- Long text is not a metric value. Use compact KPI cards or explanatory text
  for model targets and formulas.
- Method tabs for deterministic baseline models should include the actual
  model equations, not generic model descriptions.
- Domain tabs must answer what the user can learn. Yield-curve tabs should
  interpret slope, inversion, flattening, and steepening. GDP tabs should
  interpret latest quarterly growth, year-over-year growth,
  forecast-implied level change, release lags, and revision risk.
- App tests should exercise every tab or active view. Default-tab smoke tests
  are not enough because hidden tabs can still contain Streamlit runtime errors.
  Include rendered-content assertions and query parameters for the target view,
  not only `assert not at.exception`.

## References

- `student-quickstart.md`
- `audit-checklist.md`
- `app-structure.md`
- `data-and-caching.md`
- `fred-apps.md`
- `deployment-and-grading.md`
- `github-submission.md`
- `finish-deployment.md`
- `publication-grade-apps.md`
- `prompt.md`
