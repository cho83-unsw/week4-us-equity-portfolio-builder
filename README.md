# Streamlit App Deploy Bundle

This repository is a minimal deployable app bundle prepared from the course repo.

## Local Check

Run from the repository root:

```bash
python tools/workflow.py check-app-submission --target fins2026/week4 --entrypoint fins2026/week4/app/streamlit_app.py
```

## Local Run

```bash
streamlit run fins2026/week4/app/streamlit_app.py
```

Keep the terminal open while using `localhost`.

## GitHub Actions

This bundle includes `.github/workflows/submission-check.yml`. Every push runs
the same deployment readiness gate used locally by `check-app-submission`.

## Streamlit Community Cloud

- Branch: `main`
- Main file path: `fins2026/week4/app/streamlit_app.py`
- Python version: `3.13`
- Secrets: none unless the app explicitly uses `st.secrets`

Make the deployed Streamlit app public for grading. The GitHub repo may remain
private if the teaching team has access.
