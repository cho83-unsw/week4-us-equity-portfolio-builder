# Submission Checklist

Before hand-in, confirm each item below.

## Public app

- [ ] Public Streamlit Community Cloud URL:
      ___________________________________________________________________

## GitHub repo

- [ ] Accessible GitHub repo URL (private, shared with teaching team):
      ___________________________________________________________________
- [ ] Branch: `_____________`
- [ ] Entrypoint: `fins2026/week4/app/streamlit_app.py`
- [ ] Final commit hash: `_____________`

## Pre-submission check

Run from the repo root:

```bash
python tools/workflow.py check-app-submission \
    --target fins2026/week4 \
    --entrypoint fins2026/week4/app/streamlit_app.py
```

Record any blocking issues here:

___________________________________________________________________

___________________________________________________________________

## Verification

- [ ] App runs locally with `streamlit run fins2026/week4/app/streamlit_app.py`
- [ ] All tabs render without Streamlit or Python errors
- [ ] Stock universe selector includes all 50 stocks
- [ ] Portfolio weights, growth of $1, scorecard, and efficient frontier display
      correctly for the selected stock subset
- [ ] CSV downloads produce valid files
- [ ] Sample-period controls update the charts and tables
- [ ] No local absolute paths committed
- [ ] No secrets committed
