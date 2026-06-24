# Week Context

## Week Identity
- Week folder: `fins2026/week4`
- Title: Week 4: APIs, Returns, and Portfolio Construction
- README summary: Week 4 introduces the first four stages of the data factory floor.

## Core Guides

- `fins2026/week4/README.md`: Week 4: APIs, Returns, and Portfolio Construction. Week 4 introduces the first four stages of the data factory floor.
- `fins2026/week4/WORKSHOP.md`: Week 4 Workshop. Week 4 now covers four stages of the data factory floor.
- `fins2026/week4/DATA_GUIDE.md`: Week 4 Data Guide. Week 4 has four data layers:
- `fins2026/week4/SUBMISSION_CHECKLIST.md`: Week 4 Submission Checklist. `README.md` explains the week purpose and canonical commands; `WORKSHOP.md` reflects the actual workshop flow; `DATA_GUIDE.md` and `data/README.md` describe the inputs accurately

## Prompt Files

- `fins2026/week4/prompts/assistant_starter.md`: Week 4 Assistant Starter Prompt. Week 4 is the first four stages of the data factory floor.
- `fins2026/week4/prompts/README.md`: Week 4 Prompts. Keep reusable prompts here when the week benefits from repeated AI-assisted figure, app, report, or data-analysis tasks.

## Current Scripts

- `fins2026/week4/scripts/_bootstrap.py`: Small helper for Week 4 scripts that need repo-root imports.
- `fins2026/week4/scripts/build_week4_app_fixture.py`: Build the committed Week 4 app fallback fixture.
- `fins2026/week4/scripts/describe_data.py`: Summarize the current data files for this week.
- `fins2026/week4/scripts/make_stage2_return_check_figures.py`: Build FT-style Stage 2 return-diagnostic figures for Week 4.
- `fins2026/week4/scripts/make_stage3_portfolio_figures.py`: Export Week 4 Stage 3 FT-style portfolio figures.
- `fins2026/week4/scripts/run_beginner_ecb_api.py`: Run the Week 4 free-API walkthrough with the ECB.
- `fins2026/week4/scripts/run_beginner_french_rfr.py`: Download the Week 4 daily risk-free rate from Kenneth French.
- `fins2026/week4/scripts/run_beginner_stage2_features_long.py`: Add rolling Stage 2 features to the Week 4 long return panel.
- `fins2026/week4/scripts/run_beginner_stage2_returns_long.py`: Build long daily returns for Week 4 Stage 2 and verify parity with wide returns.
- `fins2026/week4/scripts/run_beginner_stage2_returns_wide.py`: Build wide adjusted-price and return tables for Week 4 Stage 2.
- `fins2026/week4/scripts/run_beginner_stage3_portfolios.py`: Build Week 4 Stage 3 in-sample portfolios and efficient-frontier outputs.
- `fins2026/week4/scripts/run_beginner_tiingo_famous_50.py`: Run the full 50-ticker Tiingo panel pull and save the long parquet output.
- `fins2026/week4/scripts/run_beginner_tiingo_small_panel.py`: Run the first authenticated Tiingo pull on a tiny ticker set.
- `fins2026/week4/scripts/run_beginner_tiingo_wide_panel.py`: Convert a saved Tiingo long panel into a wide close-price table.
- `fins2026/week4/scripts/run_beginner_yahoo_famous_50.py`: Run the 50-ticker Yahoo Finance panel pull.
- `fins2026/week4/scripts/run_beginner_yahoo_small_panel.py`: Run the first Yahoo Finance chart-history pull on a tiny ticker set.
- `fins2026/week4/scripts/run_week.py`: Print the canonical Week 4 workflow.

## Standard Working Rules

- `data/` is for committed source inputs.
- `results/data/` is for generated, downloaded, cleaned, or merged datasets.
- `scratch/` is for disposable experiments, not the final path.
- Promote reused week-local logic into `code/` and cross-week logic into `fintools/`.

## Current Paths

- Source data: `fins2026/week4/data`
- Generated outputs: `fins2026/week4/results`
- Current context files: `fins2026/week4/guidance`
