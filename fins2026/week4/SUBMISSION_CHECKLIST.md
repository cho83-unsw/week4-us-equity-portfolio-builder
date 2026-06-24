# Week 4 Submission Checklist

- `README.md` explains the week purpose and canonical commands.
- `WORKSHOP.md` reflects the actual workshop flow.
- `DATA_GUIDE.md` and `data/README.md` describe the inputs accurately.
- `data/` contains only committed source inputs such as ticker-universe files.
- Canonical scripts live in `scripts/`, not `scratch/`.
- The Week 4 ladder is clear:
  - ECB free API intro
  - Kenneth French daily risk-free download
  - Tiingo small authenticated pull
  - long-to-wide reshape
  - full 50-ticker Tiingo pull
  - Yahoo small pull
  - Yahoo 50-ticker pull
  - Stage 4 app fixture refresh
  - Stage 4 Streamlit app
- Generated outputs live under `results/` and are reproducible.
- No API key is committed in source files, tracked outputs, or docs.
- `guidance/*.md` has been refreshed with `python tools/workflow.py build-week-context --target fins2026/week4`.
- Any app work is isolated under `app/`.
- The Week 4 app runs locally with `streamlit run fins2026/week4/app/streamlit_app.py`.
- The Week 4 app fallback fixture is refreshable with
  `python fins2026/week4/scripts/build_week4_app_fixture.py`.
- Before deployment, the Week 4 app passes
  `python tools/workflow.py check-app-submission --target fins2026/week4 --entrypoint fins2026/week4/app/streamlit_app.py`.

