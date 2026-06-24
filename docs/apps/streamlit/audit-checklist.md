# Streamlit App Audit Checklist

Use this checklist when reviewing any coursework Streamlit app. Benchmark the
app against the current Streamlit docs, the course app standards, and the
specific product question the app claims to answer.

## Official Docs To Recheck

- Stateful tabs and lazy rendering:
  <https://docs.streamlit.io/develop/api-reference/layout/st.tabs>
- Session state:
  <https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state>
- Query parameters:
  <https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params>
- Caching:
  <https://docs.streamlit.io/develop/concepts/architecture/caching>
- Forms:
  <https://docs.streamlit.io/develop/concepts/architecture/forms>
- Fragments:
  <https://docs.streamlit.io/develop/concepts/architecture/fragments>
- App testing:
  <https://docs.streamlit.io/develop/concepts/app-testing>
- Dataframes and column configuration:
  <https://docs.streamlit.io/develop/api-reference/data/st.dataframe>
- Configuration and theming:
  <https://docs.streamlit.io/develop/api-reference/configuration>
- Secrets:
  <https://docs.streamlit.io/develop/concepts/connections/secrets-management>
- Community Cloud deployment:
  <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>

## Audit Output

Write findings in this order:

1. Blocking defects that can break the app, deployment, or user navigation.
2. Product clarity defects that make the app hard to interpret.
3. Streamlit execution/state/performance issues.
4. Testing, deployment, and maintainability gaps.
5. Nice-to-have polish.

For each finding, include:

- severity: `Blocker`, `High`, `Medium`, or `Low`
- affected file or UI area
- observed behavior or code pattern
- why it matters
- concrete fix
- whether the fix belongs in the app, shared helpers, docs, or tests

## App Shell And Deployment

- Run from the repository root and verify the app entrypoint path matches the
  deployment instructions.
- Check `st.set_page_config` or the shared `configure_page` helper is called
  before visible Streamlit elements.
- Verify `.streamlit/config.toml` is present at the deployed repo root. An app
  subfolder config is useful only if the app is run from that subfolder.
- Confirm `requirements.txt` pins Streamlit tightly enough for the APIs used.
  If the app uses stateful tabs, require a Streamlit version that supports
  `st.tabs(..., key=..., on_change="rerun")`.
- Verify secrets are not committed and that any secret-dependent path uses
  `st.secrets` or the deployment platform's secrets UI.
- Run `python tools/workflow.py check-app-submission --target ...` before
  treating the app as hand-in ready.

## State, Query Params, And Navigation

- Treat URL query parameters as serialized input, not trusted state. Validate
  every value before using it in a widget default.
- For URL-shareable tabs, let the URL set the initial tab only once per browser
  session; after that, let `st.session_state` own tab clicks.
- Do not feed a changing `?view=` value into `st.tabs(default=...)` on every
  rerun. This can cause first-click tab bounce.
- Use `lazy_tabs` for expensive tab views so hidden charts and models are not
  recomputed unnecessarily.
- Check every widget has a stable key when its state matters across reruns.
- Avoid mutating widget state after the widget has already been created.

## Execution, Caching, Forms, And Fragments

- Cache data downloads and expensive deterministic transforms with
  `st.cache_data`. Use a `ttl` for live data and API calls.
- Use `st.cache_resource` only for shared thread-safe resources such as clients
  or model objects.
- Keep cached functions free of visible UI side effects unless the behavior is
  intentional and tested.
- Use `st.form` to batch groups of controls when users should change several
  values before rerunning a heavy chart or model.
- Use `st.fragment` for self-contained controls or live-updating panels that
  should rerun independently of the full app.
- Do not use caching and fragments on the same function.
- Show `st.spinner`, `st.status`, or concise status text around live data or
  expensive model paths when delays are visible.

## Product Clarity

- The first viewport must answer: what is this product, what data is active,
  what is the latest state, and what should the user do next?
- Every tab must answer a user question, not merely hold a chart.
- Metric labels must include units, date context, and comparison window when
  those details affect interpretation.
- Composite indicators must state direction, units, baseline, rolling window,
  latest observation date, and percentile interpretation.
- Forecast apps must explain the target transform, displayed forecast object,
  uncertainty, and backtest metric.
- Method tabs should use `st.latex` or Markdown LaTeX for equations, not
  code-style formulas.
- Client-facing copy should avoid implementation phrasing such as "this app",
  "so the user can", "fixture mode" without explanation, or raw column names.

## Data Display And Visuals

- Use `st.dataframe` with `column_config`, typed dates, typed numbers, and
  hidden indexes where appropriate.
- Short tables should use compact dynamic heights and should not show blank
  grid rows.
- Downloads should match the visible sample and use clear filenames.
- Plotly charts should use unified hover, readable legends, explicit units,
  recession shading for U.S. macro series where useful, and range controls that
  do not overlap legends.
- Time-series indexes must be sorted before plotting.
- Avoid long metric-card values for formulas, caveats, or target descriptions.

## Testing

- Test pure data/model functions without Streamlit.
- Add `AppTest` smoke tests for every tab or active view where the runtime
  supports reliable temp cleanup.
- In app tests, set `query_params` and `session_state` to exercise shared URLs,
  tab navigation, and non-default widget states.
- Check app text for client-facing labels and absence of raw dataframe names,
  local absolute paths, secrets, and developer-only comments.
- Run Ruff and `git diff --check`.
- For deployed apps, inspect the public URL in an incognito browser.

## Maintenance

- Split very large `streamlit_app.py` files once helper sections become hard to
  scan. Keep data loading, modeling, insight functions, and UI rendering in
  testable boundaries.
- Promote repeated app patterns into `fintools.apps` rather than copying them
  across weeks.
- After fixing a recurring issue, update this checklist, the workflow doc, and
  the relevant assistant skill adapter.
