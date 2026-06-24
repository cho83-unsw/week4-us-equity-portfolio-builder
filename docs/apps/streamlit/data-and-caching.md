# Data And Caching

Streamlit reruns the script after interactions. Treat every data load and
expensive transformation as something that may rerun many times.

Use:

```python
@st.cache_data(ttl=86400)
def load_data() -> pd.DataFrame:
    ...
```

Rules:

- Cache dataframes and API results with `st.cache_data`.
- Use a TTL for API calls so the app eventually refreshes.
- Validate required columns before plotting.
- Keep cached functions free of Streamlit UI calls.
- Return copies or fresh dataframes when mutating downstream.
- Show a clear `st.error` if data is missing or malformed.
- Do not strand the user on a dead error screen when a live API fails. Prefer a
  small fixture or cached fallback, plus a concise warning that live data was
  unavailable.
- Keep UI labels separate from internal data names. Prepare display dataframes
  with app-facing column labels before calling `st.dataframe`.
- Use typed Streamlit column configuration for user-facing tables. Dates should
  render as dates, numeric columns should use consistent formats, and raw
  indexes should be hidden unless deliberately shown.
- Expose CSV downloads for the exact filtered sample and model outputs that the
  user is viewing.
- Cache data and model results, but do not cache Streamlit widgets or render
  calls.
- For long or expensive apps, avoid doing hidden work in default tabs. Use
  state-tracked lazy tabs or a single active-view control.

For final projects, include small fallback data or a fixture when a live API can
fail. A public app should still render a useful diagnostic instead of crashing.

On native Windows, Streamlit's `AppTest` can leave locked temporary folders in
some host environments. Keep pure data/model tests as the required Windows
check, and use `AppTest` smoke tests where the runtime handles temp cleanup
cleanly.
