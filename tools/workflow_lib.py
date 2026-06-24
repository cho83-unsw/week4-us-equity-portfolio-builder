"""Deterministic helpers for shared repo workflows."""

from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
}
SECTION_RE = re.compile(r"\\(section|subsection|subsubsection)\{([^}]*)\}")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
MARKER_RE = re.compile(r"^\s*%%\s*(BEGIN|END)\s+([A-Za-z0-9_-]+)\s*$")
BIB_ENTRY_RE = re.compile(r"@\w+\{([^,]+),")
SUPPORTED_PYTHON = (3, 13)
MACOS_PIP_RUNTIME_FAILURE_MARKERS = (
    "pyexpat",
    "xml.parsers.expat",
    "libexpat",
    "xml_setalloctrackeractivationthreshold",
)
WEEK_FOLDER_RE = re.compile(r"^week(?:10|[1-9])$")
TEXT_EXTENSIONS = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
BUNDLE_EXCLUDED_DIRS = {
    ".git",
    ".maintainers",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "_raw",
    "_refresh",
    "results",
    "venv",
}
BUNDLE_EXCLUDED_SUFFIXES = {
    ".aux",
    ".bbl",
    ".blg",
    ".docx",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".pdf",
    ".png",
    ".pyc",
    ".pyo",
    ".synctex.gz",
}
SUBMISSION_PLACEHOLDER_RE = re.compile(r"TODO|<[^>]+>")
SUBMISSION_ACCESS_MODES = {
    "private_collaborators",
    "public_repo",
    "course_org_repo",
}
INTERNAL_WORKFLOWS = {"audit-week", "prepare-public-repo"}
PUBLIC_ROOT_SURFACE_FILES = (
    Path("AGENTS.md"),
    Path("README.md"),
    Path("QUICKSTART.md"),
    Path("CLAUDE.md"),
    Path("GEMINI.md"),
    Path("QWEN.md"),
)
PUBLIC_SURFACE_DIRS = (
    Path("docs") / "ai",
    Path(".agents") / "skills",
    Path(".claude") / "skills",
    Path(".gemini") / "commands",
    Path(".qwen") / "skills",
    Path("fins2026"),
)
PUBLIC_SURFACE_SUFFIXES = {".md", ".toml", ".yaml", ".yml"}
PUBLIC_PRIVACY_BLOCKED_PATHS = (
    Path("docs") / "ai" / "maintainers",
    Path("docs") / "ai" / "workflows" / "maintain-week.md",
    Path(".agents") / "skills" / "maintain-week",
    Path(".claude") / "skills" / "maintain-week",
    Path(".gemini") / "commands" / "maintain-week.toml",
    Path(".qwen") / "skills" / "maintain-week",
)
PUBLIC_PRIVACY_BLOCKED_MARKERS = (
    "audit-week",
    "docs/ai/maintainers/",
    "maintain-week",
    "maintainer",
    ".maintainers/",
)
PUBLISHED_WEEK_NAMES = tuple(f"week{index}" for index in range(0, 6))
UNRELEASED_WEEK_NAMES = tuple(f"week{index}" for index in range(6, 11))
PUBLIC_RELEASE_ALLOWED_TOP_LEVELS = frozenset(
    {
        ".agents",
        ".claude",
        ".codex",
        ".editorconfig",
        ".gemini",
        ".gitattributes",
        ".github",
        ".gitignore",
        ".python-version",
        ".qwen",
        ".streamlit",
        ".vscode",
        "AGENTS.md",
        "boilerplate",
        "CLAUDE.md",
        "docs",
        "fins2026",
        "fintools",
        "GEMINI.md",
        "LICENSE",
        "projects",
        "pyproject.toml",
        "QUICKSTART.md",
        "QWEN.md",
        "README.md",
        "requirements-dev.txt",
        "requirements-plotly.txt",
        "requirements.txt",
        "tests",
        "tools",
    }
)
PUBLIC_RELEASE_REQUIRED_ROOT_FILES = (
    Path("AGENTS.md"),
    Path("README.md"),
    Path("QUICKSTART.md"),
    Path("CLAUDE.md"),
    Path("GEMINI.md"),
    Path("QWEN.md"),
    Path("LICENSE"),
    Path("pyproject.toml"),
    Path("requirements.txt"),
    Path("requirements-dev.txt"),
    Path("requirements-plotly.txt"),
    Path(".python-version"),
    Path(".gitignore"),
)
PUBLIC_RELEASE_REQUIRED_WEEK_DIRS = tuple(
    Path("fins2026") / week_name for week_name in PUBLISHED_WEEK_NAMES
)
PUBLIC_RELEASE_BLOCKED_PATHS = (
    Path(".maintainers"),
    *(Path("fins2026") / week_name for week_name in UNRELEASED_WEEK_NAMES),
    *PUBLIC_PRIVACY_BLOCKED_PATHS,
    Path("docs") / "apps" / "streamlit" / "validation-rehearsal.md",
    Path("docs") / "apps" / "streamlit" / "roadmap.md",
)
DEFAULT_WEEK_AUDIT_SPECS: dict[str, dict[str, object]] = {
    "week1": {
        "week_id": "week1",
        "title": "Week 1: Structured Data Foundations",
        "required_files": [
            "README.md",
            "WORKSHOP.md",
            "DATA_GUIDE.md",
            "ASSIGNMENT.md",
            "PRACTICE_GUIDE.md",
            "SUBMISSION_CHECKLIST.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "QWEN.md",
            "prompts/README.md",
            "prompts/assistant_starter.md",
            "prompts/workshop_walkthrough.md",
            "prompts/practice1_coach.md",
            "guidance/week-context.md",
            "guidance/data-context.md",
            "guidance/output-context.md",
            "scripts/01_load_panel.py",
            "scripts/02_save_formats.py",
            "scripts/03_duckdb_query.py",
            "scripts/04_panel_slices.py",
            "scripts/05_end_to_end.py",
            "scripts/06_coke_pepsi_practice.py",
            "scripts/run_week.py",
            "scripts/describe_data.py",
            "data/README.md",
            "data/week1_workshop_panel.csv",
            "data/week1_workshop_panel.parquet",
            "data/week1_assignment_data.txt",
            "scratch/README.md",
            "tests/test_week_smoke.py",
        ],
        "results_dirs": [
            "results/data",
            "results/figures",
            "results/tables",
            "results/app",
        ],
        "script_files": [
            "scripts/01_load_panel.py",
            "scripts/02_save_formats.py",
            "scripts/03_duckdb_query.py",
            "scripts/04_panel_slices.py",
            "scripts/05_end_to_end.py",
            "scripts/06_coke_pepsi_practice.py",
            "scripts/run_week.py",
            "scripts/describe_data.py",
        ],
        "banned_markers": [
            "_solutions",
            "PORTED FROM",
            "do not edit here",
            "maintainer",
        ],
        "required_substrings": {
            "AGENTS.md": [
                "README.md",
                "WORKSHOP.md",
                "DATA_GUIDE.md",
                "ASSIGNMENT.md",
                "PRACTICE_GUIDE.md",
                "guidance/week-context.md",
                "guidance/data-context.md",
                "guidance/output-context.md",
            ],
            "CLAUDE.md": [
                "guidance/output-context.md",
                "prompts/workshop_walkthrough.md",
                "prompts/practice1_coach.md",
            ],
            "GEMINI.md": [
                "guidance/output-context.md",
                "prompts/workshop_walkthrough.md",
                "prompts/practice1_coach.md",
            ],
            "QWEN.md": [
                "guidance/output-context.md",
                "prompts/workshop_walkthrough.md",
                "prompts/practice1_coach.md",
            ],
            "prompts/assistant_starter.md": [
                "guidance/output-context.md",
                "results/data/",
                "results/figures/",
            ],
            "prompts/workshop_walkthrough.md": [
                "guidance/output-context.md",
                "scripts/01_load_panel.py",
                "scripts/05_end_to_end.py",
            ],
            "prompts/practice1_coach.md": [
                "guidance/output-context.md",
                "scripts/06_coke_pepsi_practice.py",
            ],
            "guidance/week-context.md": [
                "## Prompt Files",
                "prompts/assistant_starter.md",
                "prompts/workshop_walkthrough.md",
                "prompts/practice1_coach.md",
            ],
        },
        "tabular_checks": [
            {
                "label": "Workshop raw CSV",
                "path": "data/week1_workshop_panel.csv",
                "format": "csv",
                "parse_dates": ["Date"],
                "dayfirst": True,
                "shape": [26159, 6],
                "duplicate_keys": ["Date", "Ticker"],
                "duplicate_count": 3,
                "date_column": "Date",
                "date_min": "2000-01-03",
                "date_max": "2025-12-31",
            },
            {
                "label": "Workshop clean parquet",
                "path": "data/week1_workshop_panel.parquet",
                "format": "parquet",
                "shape": [26156, 6],
                "duplicate_keys": ["Date", "Ticker"],
                "duplicate_count": 0,
                "date_column": "Date",
                "date_min": "2000-01-03",
                "date_max": "2025-12-31",
                "group_count_column": "Ticker",
                "group_counts": {
                    "AAPL": 6539,
                    "MSFT": 6539,
                    "NVDA": 6539,
                    "ORCL": 6539,
                },
            },
            {
                "label": "Practice raw TSV",
                "path": "data/week1_assignment_data.txt",
                "format": "tsv",
                "shape": [13078, 10],
                "date_from_column": "DlyCalDt",
                "date_from_format": "%Y%m%d",
                "date_new_column": "Date",
                "duplicate_keys": ["Date", "Ticker"],
                "duplicate_count": 0,
                "null_cells": 0,
                "date_column": "Date",
                "date_min": "2000-01-03",
                "date_max": "2025-12-31",
                "group_count_column": "Ticker",
                "group_counts": {"KO": 6539, "PEP": 6539},
            },
        ],
        "cross_section_checks": [
            {
                "label": "Workshop crash-day cross-section",
                "path": "data/week1_workshop_panel.parquet",
                "format": "parquet",
                "date_column": "Date",
                "filter_date": "2020-03-16",
                "row_count": 4,
            },
            {
                "label": "Practice crash-day cross-section",
                "path": "data/week1_assignment_data.txt",
                "format": "tsv",
                "date_from_column": "DlyCalDt",
                "date_from_format": "%Y%m%d",
                "date_new_column": "Date",
                "date_column": "Date",
                "filter_date": "2020-03-16",
                "row_count": 2,
                "key_column": "Ticker",
                "value_column": "DlyRet",
                "expected_values": {"KO": -0.066227, "PEP": -0.112672},
                "abs_tolerance": 0.000001,
            },
        ],
        "growth_checks": [
            {
                "label": "Practice growth of one dollar",
                "path": "data/week1_assignment_data.txt",
                "format": "tsv",
                "date_from_column": "DlyCalDt",
                "date_from_format": "%Y%m%d",
                "date_new_column": "Date",
                "index_column": "Date",
                "columns_column": "Ticker",
                "values_column": "DlyRet",
                "expected_final_values": {"KO": 4.93, "PEP": 7.90},
                "abs_tolerance": 0.03,
                "ratio_numerator": "PEP",
                "ratio_denominator": "KO",
                "expected_ratio": 1.60,
                "ratio_abs_tolerance": 0.03,
            }
        ],
    },
    "week2": {
        "week_id": "week2",
        "title": "Week 2: FT-Style Plotting, Narrative, And A First Streamlit App",
        "required_files": [
            "README.md",
            "WORKSHOP.md",
            "DATA_GUIDE.md",
            "FIGURE_GALLERY.md",
            "AGENTS.md",
            "prompts/README.md",
            "prompts/assistant_starter.md",
            "prompts/figure_correction_prompt.md",
            "prompts/ft_figure_prompt.md",
            "prompts/australia_macro_prompt.md",
            "data/README.md",
            "data/australia_macro_stage1_long.csv",
            "guidance/week-context.md",
            "guidance/data-context.md",
            "guidance/output-context.md",
            "scripts/describe_data.py",
            "scripts/describe_week2_data.py",
            "scripts/run_week.py",
            "scripts/make_all_week2_figures.py",
            "scripts/pull_fred_market_data.py",
            "scripts/make_fred_market_figures.py",
            "scripts/pull_australia_macro_data.py",
            "scripts/make_australia_macro_figures.py",
            "code/market_panel.py",
            "code/market_window.py",
            "code/australia_macro_specs.py",
            "code/australia_macro_panel.py",
        ],
        "results_dirs": [
            "results/data",
            "results/figures",
            "results/tables",
            "results/app",
        ],
        "script_files": [
            "scripts/describe_data.py",
            "scripts/describe_week2_data.py",
            "scripts/run_week.py",
            "scripts/make_all_week2_figures.py",
            "scripts/pull_fred_market_data.py",
            "scripts/make_fred_market_figures.py",
            "scripts/pull_australia_macro_data.py",
            "scripts/make_australia_macro_figures.py",
        ],
        "banned_markers": [
            "_solutions",
            "PORTED FROM",
            "do not edit here",
            "maintainer",
        ],
        "required_substrings": {
            "README.md": [
                "results/figures/market_macro_story/",
                "results/figures/australia_macro_story/",
                "pull_australia_macro_data.py",
                "make_australia_macro_figures.py",
                "2025-12-31",
                "2026-03-31",
            ],
            "DATA_GUIDE.md": [
                "australia_macro_stage1_long.csv",
                "australia_macro_reference_panel.csv",
                "reference_date",
                "observable_month_end",
            ],
            "AGENTS.md": [
                "results/figures/australia_macro_story/",
                "2025-12-31",
                "2026-03-31",
                "reference_date",
                "observable_month_end",
            ],
            "prompts/assistant_starter.md": [
                "results/figures/australia_macro_story/",
                "2025-12-31",
                "2026-03-31",
            ],
            "guidance/week-context.md": [
                "## Timing And Alignment Notes",
                "2025-12-31",
                "2026-03-31",
            ],
        },
        "tabular_checks": [
            {
                "label": "Australia Stage 1 fixture",
                "path": "data/australia_macro_stage1_long.csv",
                "format": "csv",
                "parse_dates": ["reference_date"],
                "shape": [2855, 17],
                "date_column": "reference_date",
                "date_min": "2000-01-31",
                "date_max": "2025-12-31",
            }
        ],
    },
    "week3": {
        "week_id": "week3",
        "title": "Week 3: Dual Macro App Lab",
        "required_files": [
            "README.md",
            "WORKSHOP.md",
            "DATA_GUIDE.md",
            "BEGINNER_FORECASTING.md",
            "US_BEGINNER_FORECASTING.md",
            "APP_LAB.md",
            "APP_AUDIT.md",
            "SUBMISSION_CHECKLIST.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "QWEN.md",
            "prompts/README.md",
            "prompts/assistant_starter.md",
            "data/README.md",
            "data/australia_macro_stage1_long.csv",
            "data/benchmark_leaderboard_fixture.csv",
            "guidance/week-context.md",
            "guidance/data-context.md",
            "guidance/output-context.md",
            "code/README.md",
            "code/beginner_forecasting.py",
            "code/forecast_pipeline.py",
            "app/README.md",
            "app/streamlit_app.py",
            "app/tests/test_app_smoke.py",
            "us_app/README.md",
            "us_app/streamlit_app.py",
            "us_app/tests/test_app_smoke.py",
            "scripts/build_forecast_inputs.py",
            "scripts/describe_data.py",
            "scripts/describe_forecast_data.py",
            "scripts/make_beginner_forecast_story_figures.py",
            "scripts/make_beginner_forecasting_series.py",
            "scripts/make_us_beginner_forecast_story_figures.py",
            "scripts/make_us_beginner_forecasting_series.py",
            "scripts/run_beginner_ar_forecast.py",
            "scripts/run_beginner_arma_forecast.py",
            "scripts/run_beginner_armax_forecast.py",
            "scripts/run_beginner_arx_forecast.py",
            "scripts/run_beginner_enet_forecast.py",
            "scripts/run_beginner_ensemble_forecast.py",
            "scripts/run_beginner_model_horse_race.py",
            "scripts/run_beginner_naive_forecast.py",
            "scripts/run_beginner_ols_forecast.py",
            "scripts/run_beginner_unit_root_check.py",
            "scripts/run_forecast_benchmarks.py",
            "scripts/run_us_beginner_ar_forecast.py",
            "scripts/run_us_beginner_arma_forecast.py",
            "scripts/run_us_beginner_arx_forecast.py",
            "scripts/run_us_beginner_model_horse_race.py",
            "scripts/run_us_beginner_naive_forecast.py",
            "scripts/run_us_beginner_unit_root_check.py",
            "scripts/run_week.py",
            "scratch/README.md",
            "tests/test_beginner_forecasting.py",
            "tests/test_week_smoke.py",
        ],
        "results_dirs": [
            "results/data",
            "results/figures",
            "results/tables",
            "results/app",
        ],
        "script_files": [
            "scripts/build_forecast_inputs.py",
            "scripts/describe_data.py",
            "scripts/describe_forecast_data.py",
            "scripts/make_beginner_forecast_story_figures.py",
            "scripts/make_beginner_forecasting_series.py",
            "scripts/make_us_beginner_forecast_story_figures.py",
            "scripts/make_us_beginner_forecasting_series.py",
            "scripts/run_beginner_ar_forecast.py",
            "scripts/run_beginner_arma_forecast.py",
            "scripts/run_beginner_armax_forecast.py",
            "scripts/run_beginner_arx_forecast.py",
            "scripts/run_beginner_enet_forecast.py",
            "scripts/run_beginner_ensemble_forecast.py",
            "scripts/run_beginner_model_horse_race.py",
            "scripts/run_beginner_naive_forecast.py",
            "scripts/run_beginner_ols_forecast.py",
            "scripts/run_beginner_unit_root_check.py",
            "scripts/run_forecast_benchmarks.py",
            "scripts/run_us_beginner_ar_forecast.py",
            "scripts/run_us_beginner_arma_forecast.py",
            "scripts/run_us_beginner_arx_forecast.py",
            "scripts/run_us_beginner_model_horse_race.py",
            "scripts/run_us_beginner_naive_forecast.py",
            "scripts/run_us_beginner_unit_root_check.py",
            "scripts/run_week.py",
        ],
        "banned_markers": [
            "_solutions",
            "PORTED FROM",
            "do not edit here",
            "maintainer",
        ],
        "required_substrings": {
            "README.md": [
                "2019-12-31",
                "2020-01-31",
                "app/streamlit_app.py",
                "us_app/streamlit_app.py",
                "data/australia_macro_stage1_long.csv",
            ],
            "AGENTS.md": [
                "Australia macro forecast app",
                "U.S. macro app",
                "run_forecast_benchmarks.py --use-fixture",
                "streamlit run fins2026/week3/us_app/streamlit_app.py",
            ],
            "prompts/assistant_starter.md": [
                "BEGINNER_FORECASTING.md",
                "US_BEGINNER_FORECASTING.md",
                "results/data/",
                "results/figures/",
                "results/tables/",
            ],
            "guidance/week-context.md": [
                "## Timing And Alignment Notes",
                "observable panel",
                "run_forecast_benchmarks.py",
                "run_us_beginner_model_horse_race.py",
            ],
        },
        "tabular_checks": [
            {
                "label": "Australia Stage 1 fixture",
                "path": "data/australia_macro_stage1_long.csv",
                "format": "csv",
                "shape": [2855, 17],
                "duplicate_keys": ["series_id", "reference_date"],
                "duplicate_count": 0,
                "null_cells": 2435,
                "date_column": "reference_date",
                "date_min": "2000-01-31",
                "date_max": "2025-12-31",
            },
            {
                "label": "Australia benchmark leaderboard fixture",
                "path": "data/benchmark_leaderboard_fixture.csv",
                "format": "csv",
                "shape": [48, 12],
                "duplicate_keys": ["series", "target", "model"],
                "duplicate_count": 0,
                "null_cells": 48,
            },
        ],
    },
    "week4": {
        "week_id": "week4",
        "title": "Week 4: APIs, Returns, and Portfolio Construction",
        "required_files": [
            "README.md",
            "WORKSHOP.md",
            "DATA_GUIDE.md",
            "SUBMISSION_CHECKLIST.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "QWEN.md",
            "prompts/README.md",
            "prompts/assistant_starter.md",
            "data/README.md",
            "data/tiingo_famous_50_pre2000.txt",
            "data/tiingo_intro_3.txt",
            "data/yahoo_app_10.txt",
            "data/yahoo_famous_50.txt",
            "data/yahoo_intro_3.txt",
            "guidance/week-context.md",
            "guidance/data-context.md",
            "guidance/output-context.md",
            "code/README.md",
            "code/api_intro_ecb.py",
            "code/equity_api_tiingo.py",
            "code/equity_api_yahoo.py",
            "code/risk_free_rate_french.py",
            "code/stage2_equity_returns.py",
            "code/stage2_return_figures.py",
            "code/stage3_portfolio_figures.py",
            "code/stage3_portfolios.py",
            "code/stage4_app.py",
            "app/README.md",
            "app/streamlit_app.py",
            "app/tests/test_app_smoke.py",
            "app/fixtures/README.md",
            "app/fixtures/french_daily_rfr.parquet",
            "app/fixtures/yahoo_app_10_long.parquet",
            "scripts/_bootstrap.py",
            "scripts/build_week4_app_fixture.py",
            "scripts/describe_data.py",
            "scripts/make_stage2_return_check_figures.py",
            "scripts/make_stage3_portfolio_figures.py",
            "scripts/run_beginner_ecb_api.py",
            "scripts/run_beginner_french_rfr.py",
            "scripts/run_beginner_stage2_features_long.py",
            "scripts/run_beginner_stage2_returns_long.py",
            "scripts/run_beginner_stage2_returns_wide.py",
            "scripts/run_beginner_stage3_portfolios.py",
            "scripts/run_beginner_tiingo_famous_50.py",
            "scripts/run_beginner_tiingo_small_panel.py",
            "scripts/run_beginner_tiingo_wide_panel.py",
            "scripts/run_beginner_yahoo_famous_50.py",
            "scripts/run_beginner_yahoo_small_panel.py",
            "scripts/run_week.py",
            "scratch/README.md",
            "tests/test_api_intro.py",
            "tests/test_stage4_app.py",
            "tests/test_week_smoke.py",
        ],
        "results_dirs": [
            "results/data",
            "results/figures",
            "results/tables",
            "results/app",
        ],
        "script_files": [
            "scripts/_bootstrap.py",
            "scripts/build_week4_app_fixture.py",
            "scripts/describe_data.py",
            "scripts/make_stage2_return_check_figures.py",
            "scripts/make_stage3_portfolio_figures.py",
            "scripts/run_beginner_ecb_api.py",
            "scripts/run_beginner_french_rfr.py",
            "scripts/run_beginner_stage2_features_long.py",
            "scripts/run_beginner_stage2_returns_long.py",
            "scripts/run_beginner_stage2_returns_wide.py",
            "scripts/run_beginner_stage3_portfolios.py",
            "scripts/run_beginner_tiingo_famous_50.py",
            "scripts/run_beginner_tiingo_small_panel.py",
            "scripts/run_beginner_tiingo_wide_panel.py",
            "scripts/run_beginner_yahoo_famous_50.py",
            "scripts/run_beginner_yahoo_small_panel.py",
            "scripts/run_week.py",
        ],
        "banned_markers": [
            "_solutions",
            "PORTED FROM",
            "do not edit here",
            "maintainer",
        ],
        "required_substrings": {
            "README.md": [
                "TIINGO_API_KEY",
                "direct chart endpoint",
                "126",
                "sqrt(252)",
            ],
            "AGENTS.md": [
                "TIINGO_API_KEY",
                "Week 4 Stage 4 should treat Yahoo as the live runtime source",
                "run_beginner_stage3_portfolios.py",
            ],
            "prompts/assistant_starter.md": [
                "TIINGO_API_KEY",
                "query2.finance.yahoo.com",
                "`126`-trading-day window",
                "Diagnose the status code first.",
            ],
            "guidance/week-context.md": [
                "## Current Scripts",
                "run_beginner_tiingo_famous_50.py",
                "run_beginner_stage3_portfolios.py",
                "build_week4_app_fixture.py",
            ],
        },
        "tabular_checks": [
            {
                "label": "French risk-free fixture",
                "path": "app/fixtures/french_daily_rfr.parquet",
                "format": "parquet",
                "shape": [26212, 2],
                "duplicate_keys": ["date"],
                "duplicate_count": 0,
                "null_cells": 0,
                "date_column": "date",
                "date_min": "1926-07-01",
                "date_max": "2026-03-31",
            },
            {
                "label": "Yahoo app fixture",
                "path": "app/fixtures/yahoo_app_10_long.parquet",
                "format": "parquet",
                "shape": [66330, 10],
                "duplicate_keys": ["ticker", "date"],
                "duplicate_count": 0,
                "null_cells": 0,
                "date_column": "date",
                "date_min": "2000-01-03",
                "date_max": "2026-05-18",
                "group_count_column": "ticker",
                "group_counts": {
                    "AAPL": 6633,
                    "AMZN": 6633,
                    "JNJ": 6633,
                    "JPM": 6633,
                    "KO": 6633,
                    "MSFT": 6633,
                    "NVDA": 6633,
                    "PG": 6633,
                    "WMT": 6633,
                    "XOM": 6633,
                },
            },
        ],
    },
    "week5": {
        "week_id": "week5",
        "title": "Week 5: Crypto Data, Diagnostics, and OOS Portfolios",
        "required_files": [
            "README.md",
            "WORKSHOP.md",
            "DATA_GUIDE.md",
            "SUBMISSION_CHECKLIST.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md",
            "QWEN.md",
            "prompts/README.md",
            "prompts/assistant_starter.md",
            "data/README.md",
            "data/yahoo_crypto_20_since_2019.txt",
            "data/yahoo_crypto_intro_5.txt",
            "guidance/week-context.md",
            "guidance/data-context.md",
            "guidance/output-context.md",
            "code/README.md",
            "code/crypto_api_yahoo.py",
            "code/risk_free_rate_french.py",
            "code/stage2_crypto_figures.py",
            "code/stage2_crypto_returns.py",
            "code/stage3_oos_portfolios.py",
            "code/stage3_portfolio_figures.py",
            "code/stage4_app.py",
            "app/README.md",
            "app/streamlit_app.py",
            "app/tests/test_app_smoke.py",
            "app/fixtures/README.md",
            "app/fixtures/week5_app_features_long.parquet",
            "scripts/_bootstrap.py",
            "scripts/build_week5_app_fixture.py",
            "scripts/describe_data.py",
            "scripts/make_stage2_crypto_figures.py",
            "scripts/make_stage3_portfolio_figures.py",
            "scripts/run_beginner_french_rfr.py",
            "scripts/run_beginner_stage2_features_long.py",
            "scripts/run_beginner_stage2_returns_long.py",
            "scripts/run_beginner_stage2_returns_wide.py",
            "scripts/run_beginner_stage3_oos_weights.py",
            "scripts/run_beginner_yahoo_crypto_20_since_2019.py",
            "scripts/run_beginner_yahoo_crypto_intro_5.py",
            "scripts/run_week.py",
            "results/data/stage3/.gitkeep",
            "results/tables/stage3/.gitkeep",
            "scratch/README.md",
            "tests/test_stage1_stage2_crypto.py",
            "tests/test_stage3_oos_portfolios.py",
            "tests/test_stage3_portfolio_figures.py",
            "tests/test_stage4_app.py",
            "tests/test_week_smoke.py",
        ],
        "results_dirs": [
            "results/data",
            "results/data/stage3",
            "results/figures",
            "results/tables",
            "results/tables/stage3",
            "results/app",
        ],
        "script_files": [
            "scripts/_bootstrap.py",
            "scripts/build_week5_app_fixture.py",
            "scripts/describe_data.py",
            "scripts/make_stage2_crypto_figures.py",
            "scripts/make_stage3_portfolio_figures.py",
            "scripts/run_beginner_french_rfr.py",
            "scripts/run_beginner_stage2_features_long.py",
            "scripts/run_beginner_stage2_returns_long.py",
            "scripts/run_beginner_stage2_returns_wide.py",
            "scripts/run_beginner_stage3_oos_weights.py",
            "scripts/run_beginner_yahoo_crypto_20_since_2019.py",
            "scripts/run_beginner_yahoo_crypto_intro_5.py",
            "scripts/run_week.py",
        ],
        "banned_markers": [
            "_solutions",
            "PORTED FROM",
            "do not edit here",
            "maintainer",
        ],
        "required_substrings": {
            "README.md": [
                "24/7",
                "180",
                "sqrt(365)",
                "drop all-null placeholder OHLCV rows before coverage checks",
            ],
            "AGENTS.md": [
                "365",
                "180",
                "long_only",
                "prepare-app-repo --source fins2026/week5",
            ],
            "prompts/assistant_starter.md": [
                "365",
                "`180`-day window",
                "mean-CVaR tangency",
                "point-in-time views",
            ],
            "guidance/week-context.md": [
                "## Timing And Alignment Notes",
                "return_date",
                "factsheet",
                "BTC/ETH exposure",
            ],
        },
        "tabular_checks": [
            {
                "label": "Week 5 app feature fixture",
                "path": "app/fixtures/week5_app_features_long.parquet",
                "format": "parquet",
                "shape": [53920, 21],
                "duplicate_keys": ["ticker", "date"],
                "duplicate_count": 0,
                "null_cells": 18060,
                "date_column": "date",
                "date_min": "2019-01-01",
                "date_max": "2026-05-20",
                "group_count_column": "ticker",
                "group_counts": {
                    "ADA-USD": 2696,
                    "BCH-USD": 2696,
                    "BNB-USD": 2696,
                    "BTC-USD": 2696,
                    "DASH-USD": 2696,
                    "DOGE-USD": 2696,
                    "EOS-USD": 2696,
                    "ETC-USD": 2696,
                    "ETH-USD": 2696,
                    "LINK-USD": 2696,
                    "LTC-USD": 2696,
                    "MKR-USD": 2696,
                    "NEO-USD": 2696,
                    "TRX-USD": 2696,
                    "VET-USD": 2696,
                    "XLM-USD": 2696,
                    "XMR-USD": 2696,
                    "XRP-USD": 2696,
                    "XTZ-USD": 2696,
                    "ZEC-USD": 2696,
                },
            }
        ],
    },
}


class WorkflowError(RuntimeError):
    """Raised when a workflow cannot complete cleanly."""


@dataclass
class CommandReport:
    """Report for a subprocess command."""

    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class VenvLockHolder:
    """Process that appears to be using the repo virtual environment."""

    pid: int
    name: str
    command_line: str


@dataclass
class SectionEntry:
    """One parsed LaTeX section."""

    level: str
    title: str
    line_no: int


@dataclass
class MarkerEntry:
    """One parsed BEGIN/END marker."""

    kind: str
    key: str
    line_no: int


@dataclass
class MarkerSpan:
    """A matched BEGIN/END pair."""

    key: str
    start_line: int
    end_line: int
    body_lines: int


@dataclass
class BibEntry:
    """One parsed BibTeX entry."""

    key: str
    line_no: int


def repo_root() -> Path:
    """Return the repo root."""

    return Path(__file__).resolve().parents[1]


def current_workdir() -> Path:
    """Return the current working directory."""

    return Path.cwd().resolve()


def print_lines(lines: Iterable[str]) -> None:
    """Print one line at a time."""

    for line in lines:
        print(line)


def ensure_within_repo(path: Path, root: Path) -> Path:
    """Ensure a path stays within the repo root."""

    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:  # pragma: no cover - defensive
        raise WorkflowError(f"path is outside the repo: {resolved}") from exc
    return resolved


def read_text(path: Path) -> str:
    """Read UTF-8 text."""

    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 text, creating parents when needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sanitize_bundle_requirements_dev(text: str) -> str:
    """Remove repo-local editable installs from deploy-bundle dev requirements."""

    editable_repo_re = re.compile(r"^(?:-e|--editable)\s+\./?\s*(?:#.*)?$")
    lines = [line for line in text.splitlines() if not editable_repo_re.match(line.strip())]
    return "\n".join(lines).rstrip() + "\n"


def resolve_path(cwd: Path, target_path: Path) -> Path:
    """Resolve an absolute or cwd-relative path."""

    if target_path.is_absolute():
        return target_path.resolve()
    return (cwd / target_path).resolve()


def run_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 120,
) -> CommandReport:
    """Run a subprocess and capture its output."""

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=merged_env,
        check=False,
    )
    return CommandReport(
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def format_command(command: list[str]) -> str:
    """Render a command for user-facing output."""

    if platform.system() == "Windows":
        return subprocess.list2cmdline(command)
    return shlex.join(command)


def system_python_install_hint() -> str:
    """Return the correct Python 3.13 install hint for the current OS."""

    system = platform.system()
    if system == "Windows":
        return "winget install Python.Python.3.13"
    if system == "Darwin":
        return "brew install python@3.13"
    return "sudo apt install python3.13 python3.13-venv"


def venv_python_path(root: Path) -> Path:
    """Return the interpreter path inside .venv."""

    if platform.system() == "Windows":
        return root / ".venv" / "Scripts" / "python.exe"
    return root / ".venv" / "bin" / "python"


def path_is_within(path: Path, parent: Path) -> bool:
    """Return whether path resolves inside parent."""

    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def parse_python_version(text: str) -> tuple[int, int, int] | None:
    """Parse a Python version from command output."""

    match = re.search(r"Python\s+(\d+)\.(\d+)\.(\d+)", text)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def command_python_version(command: list[str]) -> tuple[int, int, int] | None:
    """Return the Python version reported by a command prefix."""

    if not shutil.which(command[0]):
        return None
    try:
        proc = subprocess.run(
            [*command, "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return parse_python_version(f"{proc.stdout}\n{proc.stderr}")


def python_313_candidates() -> list[tuple[list[str], str]]:
    """Return platform-appropriate Python 3.13 command candidates."""

    system = platform.system()
    if system == "Windows":
        return [
            (["py", "-3.13"], "Windows Python launcher (py -3.13)"),
            (["python"], "python on PATH"),
            (["python3.13"], "python3.13 on PATH"),
        ]
    return [
        (["python3.13"], "python3.13 on PATH"),
        (["python3"], "python3 on PATH"),
        (["python"], "python on PATH"),
    ]


def find_python_313_command() -> tuple[list[str], str] | None:
    """Find a Python command prefix that resolves to Python 3.13."""

    for command, description in python_313_candidates():
        version = command_python_version(command)
        if version and version[:2] == SUPPORTED_PYTHON:
            return command, description
    return None


def looks_like_macos_pip_runtime_failure(text: str) -> bool:
    """Return whether pip failed with the known macOS pyexpat/libexpat issue."""

    lowered = text.lower()
    return any(marker in lowered for marker in MACOS_PIP_RUNTIME_FAILURE_MARKERS)


def macos_pip_failure_guidance(output: str) -> list[str]:
    """Return student-facing guidance for a macOS Python pip startup failure."""

    lines = [
        "Python 3.13 was found, but pip could not start.",
        output.strip(),
    ]
    if looks_like_macos_pip_runtime_failure(output):
        lines.extend(
            [
                "This looks like the macOS Homebrew Python pyexpat/libexpat issue.",
                "Do not keep rerunning bootstrap; it will fail before the course .venv exists.",
                "Install Python 3.13 from https://www.python.org/downloads/macos/ or ask for help.",
                "Then close and reopen Terminal or PyCharm and verify: python3.13 -m pip --version",
            ]
        )
    else:
        lines.extend(
            [
                "Fix Python 3.13 pip first, then rerun onboarding.",
                "Try closing and reopening Terminal or PyCharm. If pip still fails, "
                "use the Python.org macOS installer or ask for help.",
            ]
        )
    return [line for line in lines if line]


def macos_pip_preflight(root: Path) -> tuple[int, list[str]]:
    """Verify macOS Python can start pip before rebuilding .venv."""

    if platform.system() != "Darwin":
        return 0, []
    report = run_command(
        [sys.executable, "-m", "pip", "--version"],
        cwd=root,
        env=onboarding_temp_env(root),
        timeout=30,
    )
    lines = [f"Ran: {format_command(report.command)}"]
    if report.returncode == 0:
        detail = report.stdout.strip() or "pip startup passed"
        lines.append(f"Python 3.13 pip ready: {detail}")
        return 0, lines
    output = "\n".join(part for part in [report.stdout.strip(), report.stderr.strip()] if part)
    lines.extend(macos_pip_failure_guidance(output))
    return report.returncode or 1, lines


def bootstrap_command_hint() -> str:
    """Return the OS-specific bootstrap command."""

    system = platform.system()
    if system == "Windows":
        return r"powershell -ExecutionPolicy Bypass -File tools/bootstrap_windows.ps1"
    if system == "Darwin":
        return "bash tools/bootstrap_macos.sh"
    return "python3.13 -m venv .venv"


def ripgrep_install_hint(system: str | None = None) -> str:
    """Return the OS-specific advisory ripgrep install command."""

    system = system or platform.system()
    if system == "Windows":
        return "winget install --id BurntSushi.ripgrep.MSVC -e"
    if system == "Darwin":
        return "brew install ripgrep"
    return "install ripgrep with your OS package manager"


def ripgrep_restart_hint(system: str | None = None) -> str:
    """Return a short PATH refresh hint after installing ripgrep."""

    system = system or platform.system()
    if system == "Windows":
        return "If rg was just installed, close and reopen PowerShell or PyCharm."
    if system == "Darwin":
        return "If rg was just installed, close and reopen Terminal or PyCharm."
    return "If rg was just installed, close and reopen your terminal."


def ripgrep_warning_lines(detail: str, system: str | None = None) -> list[str]:
    """Return student-friendly advisory text for a missing or broken rg."""

    return [
        f"[WARN] ripgrep - {detail}",
        "AI assistants can still work, but repo search will be slower.",
        f"Suggested install: {ripgrep_install_hint(system)}",
        ripgrep_restart_hint(system),
    ]


def verify_ripgrep(root: Path) -> tuple[bool, list[str]]:
    """Verify that ripgrep is available and can see repo context files."""

    path = shutil.which("rg")
    if not path:
        return False, ripgrep_warning_lines("rg was not found on PATH.")

    version_report = run_command(["rg", "--version"], cwd=root, timeout=10)
    if version_report.returncode != 0:
        detail = version_report.stderr.strip() or version_report.stdout.strip()
        return False, ripgrep_warning_lines(f"`rg --version` failed. {detail}".strip())

    files_report = run_command(["rg", "--files", "-g", "AGENTS.md"], cwd=root, timeout=10)
    if files_report.returncode != 0 or "AGENTS.md" not in files_report.stdout:
        detail = files_report.stderr.strip() or files_report.stdout.strip()
        return False, ripgrep_warning_lines(
            "`rg --files -g AGENTS.md` did not find the repo context file."
            f" {detail}".strip()
        )

    first_line = version_report.stdout.splitlines()[0] if version_report.stdout else path
    return True, [f"[OK] ripgrep ({first_line})"]


def ripgrep_install_command(system: str | None = None) -> list[str] | None:
    """Return a best-effort install command for ripgrep, if supported."""

    system = system or platform.system()
    if system == "Windows":
        return [
            "winget",
            "install",
            "--id",
            "BurntSushi.ripgrep.MSVC",
            "-e",
            "--source",
            "winget",
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
    if system == "Darwin":
        return ["brew", "install", "ripgrep"]
    return None


def ripgrep_package_manager(system: str | None = None) -> str | None:
    """Return the package-manager executable for ripgrep install."""

    system = system or platform.system()
    if system == "Windows":
        return "winget"
    if system == "Darwin":
        return "brew"
    return None


def ripgrep_advisory(root: Path, *, install: bool) -> list[str]:
    """Check and optionally install ripgrep without blocking onboarding."""

    lines = ["AI workflow search tool:"]
    ok, check_lines = verify_ripgrep(root)
    lines.extend(check_lines)
    if ok or not install:
        return lines

    system = platform.system()
    package_manager = ripgrep_package_manager(system)
    install_command = ripgrep_install_command(system)
    if not package_manager or not install_command:
        lines.append("Automatic ripgrep install is not configured for this OS.")
        return lines
    if not shutil.which(package_manager):
        lines.append(
            f"{package_manager} was not found, so ripgrep was not installed automatically."
        )
        return lines

    install_report = run_command(install_command, cwd=root, timeout=300)
    lines.append(f"Ran: {format_command(install_report.command)}")
    if install_report.returncode != 0:
        lines.append("Could not install ripgrep automatically; continuing setup.")
        detail = install_report.stderr.strip() or install_report.stdout.strip()
        if detail:
            lines.append(detail)
        return lines

    ok_after_install, verify_lines = verify_ripgrep(root)
    if ok_after_install:
        lines.extend(verify_lines)
    else:
        lines.append("ripgrep install finished, but this shell cannot run rg yet.")
        lines.append(ripgrep_restart_hint(system))
        lines.extend(verify_lines)
    return lines


def onboarding_temp_env(root: Path) -> dict[str, str]:
    """Use a repo-local temp directory during bootstrap-like commands."""

    temp_root = root / ".tmp-bootstrap" / f"workflow-{os.getpid()}"
    temp_root.mkdir(parents=True, exist_ok=True)
    pip_env = {"PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_INPUT": "1"}
    if platform.system() == "Windows":
        return {**pip_env, "TEMP": str(temp_root), "TMP": str(temp_root)}
    return {**pip_env, "TMPDIR": str(temp_root), "TEMP": str(temp_root), "TMP": str(temp_root)}


def shorten_command_line(command_line: str, *, limit: int = 180) -> str:
    """Return a compact one-line process command for setup diagnostics."""

    compact = " ".join(command_line.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def windows_venv_lock_holders(root: Path) -> tuple[list[VenvLockHolder], str | None]:
    """Return Windows processes whose command line references the repo .venv."""

    if platform.system() != "Windows":
        return [], None
    venv_root = root / ".venv"
    if not venv_root.exists():
        return [], None

    script = "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"$skipPid = {os.getpid()}",
            "$venv = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) '.venv'))",
            "$needle = $venv.ToLowerInvariant()",
            "$matches = Get-CimInstance Win32_Process | Where-Object {",
            "  $_.ProcessId -ne $skipPid -and",
            "  $_.CommandLine -and",
            "  $_.CommandLine.ToLowerInvariant().Contains($needle)",
            "} | Select-Object ProcessId, Name, CommandLine",
            "$matches | ConvertTo-Json -Compress",
        ]
    )
    report = run_command(
        ["powershell", "-NoProfile", "-Command", script],
        cwd=root,
        timeout=20,
    )
    if report.returncode != 0:
        detail = report.stderr.strip() or report.stdout.strip() or "process query failed"
        return [], detail
    raw = report.stdout.strip()
    if not raw:
        return [], None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [], f"could not parse process query output: {exc}"
    rows = parsed if isinstance(parsed, list) else [parsed]
    holders: list[VenvLockHolder] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            pid = int(row.get("ProcessId", 0))
        except (TypeError, ValueError):
            pid = 0
        holders.append(
            VenvLockHolder(
                pid=pid,
                name=str(row.get("Name") or "process"),
                command_line=shorten_command_line(str(row.get("CommandLine") or "")),
            )
        )
    return holders, None


def append_venv_lock_guidance(
    lines: list[str],
    *,
    holders: list[VenvLockHolder] | None = None,
    probe_error: str | None = None,
) -> None:
    """Append student-facing guidance for Windows .venv lock failures."""

    lines.append("Windows setup cannot safely repair .venv while it may be in use.")
    if holders:
        lines.append("The repo virtual environment is currently used by:")
        for holder in holders:
            label = f"PID {holder.pid}: {holder.name}" if holder.pid else holder.name
            lines.append(f"- {label}")
            if holder.command_line:
                lines.append(f"  {holder.command_line}")
    if probe_error:
        lines.append(f"Could not confirm whether .venv is free: {probe_error}")
    lines.append(
        "Close PyCharm Python Console tabs, notebooks, Streamlit apps, and terminals"
        " using .venv, then rerun setup."
    )


def ensure_windows_venv_unlocked(root: Path, lines: list[str]) -> bool:
    """Fail closed before mutating a Windows .venv that may be locked."""

    if platform.system() != "Windows":
        return True
    holders, probe_error = windows_venv_lock_holders(root)
    if holders or probe_error:
        append_venv_lock_guidance(lines, holders=holders, probe_error=probe_error)
        return False
    return True


def looks_like_windows_venv_damage(text: str) -> bool:
    """Return whether command output resembles an interrupted Windows venv repair."""

    lowered = text.lower()
    return any(
        marker in lowered
        for marker in [
            "access is denied",
            "being used by another process",
            ".pyd",
            "dll load failed",
            "no record file was found",
            "partially initialized module",
        ]
    )


def append_windows_repair_hint(lines: list[str], output: str) -> None:
    """Append extra guidance for common Windows partial-environment failures."""

    if platform.system() != "Windows" or not looks_like_windows_venv_damage(output):
        return
    lines.append(
        "This looks like a Windows .venv lock or partial rebuild. Close PyCharm"
        " Python Console tabs, notebooks, Streamlit apps, and terminals using .venv."
    )
    lines.append("Then rerun: python tools/workflow.py onboard --rebuild")


def onboard(
    root: Path,
    cwd: Path,
    *,
    check_only: bool = False,
    rebuild: bool = False,
) -> tuple[int, list[str]]:
    """Run the onboarding workflow deterministically."""

    lines: list[str] = []
    system = platform.system()
    lines.append(f"Detected OS: {system}")
    lines.append(f"Repo root: {root}")
    if cwd != root:
        lines.append(f"Current shell directory: {cwd}")
        lines.append("Running setup commands from the repo root.")
    if system == "Windows" and "onedrive" in str(root).lower():
        lines.append(
            "Note: this repo is inside a OneDrive-synced folder. If pip reports"
            " 'Access is denied' or 'file in use', pause OneDrive sync or move"
            r" the repo to a non-synced path such as C:\fins-agent."
        )

    version = sys.version_info
    if (version.major, version.minor) != SUPPORTED_PYTHON:
        python_313 = find_python_313_command()
        if python_313:
            command, description = python_313
            lines.append(
                f"Current interpreter is {version.major}.{version.minor}.{version.micro};"
                f" re-running with {description}."
            )
            relaunch_args = ["tools/workflow.py", "onboard"]
            if check_only:
                relaunch_args.append("--check")
            if rebuild:
                relaunch_args.append("--rebuild")
            relaunch = run_command(
                [*command, *relaunch_args],
                cwd=root,
                timeout=1800,
            )
            if relaunch.stdout.strip():
                lines.extend(relaunch.stdout.rstrip().splitlines())
            if relaunch.returncode != 0 and relaunch.stderr.strip():
                lines.append(relaunch.stderr.strip())
            return relaunch.returncode, lines
        lines.append(
            "Python 3.13 is required before the repo onboarding helper can run."
        )
        lines.append(f"Current interpreter: {version.major}.{version.minor}.{version.micro}")
        lines.append(f"Install it with: {system_python_install_hint()}")
        lines.append(f"Then run from the repo root: {bootstrap_command_hint()}")
        return 1, lines

    lines.append(f"Python 3.13 detected at: {sys.executable}")
    lines.extend(ripgrep_advisory(root, install=not check_only))

    venv_root = root / ".venv"
    venv_python = venv_python_path(root)
    current_executable = Path(sys.executable)
    running_inside_repo_venv = path_is_within(current_executable, venv_root)
    if running_inside_repo_venv:
        lines.append(
            "Using the existing repo .venv because this command is already"
            " running inside it."
        )

    preflight_passed = False
    if venv_python.exists() and not rebuild:
        setup_probe = run_command(
            [str(venv_python), "tools/setup_student.py"],
            cwd=root,
        )
        lines.append(f"Ran: {format_command(setup_probe.command)}")
        if setup_probe.stdout.strip():
            lines.extend(setup_probe.stdout.rstrip().splitlines())
        if setup_probe.returncode != 0 and setup_probe.stderr.strip():
            lines.append(setup_probe.stderr.strip())
        if setup_probe.returncode == 0:
            lines.append("Existing repo .venv passed setup checks; skipping package reinstall.")
            return 0, lines

        lines.append("Existing repo .venv needs repair.")
        append_windows_repair_hint(
            lines,
            f"{setup_probe.stdout}\n{setup_probe.stderr}",
        )
        if check_only:
            lines.append("Check-only mode requested; not changing .venv.")
            return setup_probe.returncode, lines
        preflight_passed = ensure_windows_venv_unlocked(root, lines)
        if not preflight_passed:
            return 1, lines

    elif check_only:
        lines.append(f"Expected repo interpreter was not found: {venv_python}")
        lines.append("Check-only mode requested; not creating .venv.")
        return 1, lines

    if rebuild:
        lines.append("Rebuild mode requested; .venv will be recreated.")

    pip_preflight_status, pip_preflight_lines = macos_pip_preflight(root)
    lines.extend(pip_preflight_lines)
    if pip_preflight_status != 0:
        return pip_preflight_status, lines

    should_create_venv = rebuild or not venv_python.exists()
    if should_create_venv:
        if venv_root.exists() and not preflight_passed:
            preflight_passed = ensure_windows_venv_unlocked(root, lines)
            if not preflight_passed:
                return 1, lines
        venv_command = [sys.executable, "-m", "venv"]
        if rebuild or venv_root.exists():
            venv_command.append("--clear")
        venv_command.append(".venv")
        venv_report = run_command(
            venv_command,
            cwd=root,
            env=onboarding_temp_env(root),
            timeout=300,
        )
        lines.append(f"Ran: {format_command(venv_report.command)}")
        if venv_report.returncode != 0:
            lines.append("Failed to create .venv.")
            if venv_report.stderr.strip():
                lines.append(venv_report.stderr.strip())
            append_windows_repair_hint(
                lines,
                f"{venv_report.stdout}\n{venv_report.stderr}",
            )
            lines.append("See docs/setup/troubleshooting.md and docs/setup/ai-troubleshooting.md.")
            return venv_report.returncode, lines

    if not venv_python.exists():
        lines.append(f"Expected interpreter was not created: {venv_python}")
        lines.append(f"Try the OS bootstrap script: {bootstrap_command_hint()}")
        return 1, lines

    env = onboarding_temp_env(root)
    pip_upgrade_report = run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "--disable-pip-version-check",
            "--no-input",
        ],
        cwd=root,
        env=env,
        timeout=300,
    )
    lines.append(f"Ran: {format_command(pip_upgrade_report.command)}")
    if pip_upgrade_report.returncode != 0:
        lines.append("pip upgrade failed.")
        if pip_upgrade_report.stderr.strip():
            lines.append(pip_upgrade_report.stderr.strip())
        append_windows_repair_hint(
            lines,
            f"{pip_upgrade_report.stdout}\n{pip_upgrade_report.stderr}",
        )
        lines.append("See docs/setup/troubleshooting.md and docs/setup/ai-troubleshooting.md.")
        return pip_upgrade_report.returncode, lines

    install_report = run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-input",
            "-r",
            "requirements.txt",
            "-r",
            "requirements-dev.txt",
        ],
        cwd=root,
        env=env,
        timeout=600,
    )
    lines.append(f"Ran: {format_command(install_report.command)}")
    if install_report.returncode != 0:
        lines.append("Package install failed.")
        if install_report.stderr.strip():
            lines.append(install_report.stderr.strip())
        append_windows_repair_hint(
            lines,
            f"{install_report.stdout}\n{install_report.stderr}",
        )
        lines.append("See docs/setup/troubleshooting.md and docs/setup/ai-troubleshooting.md.")
        return install_report.returncode, lines

    setup_report = run_command(
        [str(venv_python), "tools/setup_student.py"],
        cwd=root,
        env=env,
    )
    lines.append(f"Ran: {format_command(setup_report.command)}")
    if setup_report.stdout.strip():
        lines.extend(setup_report.stdout.rstrip().splitlines())
    if setup_report.returncode != 0 and setup_report.stderr.strip():
        lines.append(setup_report.stderr.strip())
    return setup_report.returncode, lines


def validate_project_name(name: str) -> None:
    """Validate a project folder name."""

    if not re.fullmatch(r"[a-z][a-z0-9_]{1,49}", name):
        raise WorkflowError(
            "project name must start with a lowercase letter and then use lowercase letters,"
            " digits, or underscores only"
        )
    if name.lower() in WINDOWS_RESERVED_NAMES:
        raise WorkflowError(f"project name cannot use a Windows reserved device name: {name}")


def project_file_texts(
    name: str,
    *,
    description: str,
    datasets: str,
    notes: str,
    with_app: bool = False,
) -> dict[Path, str]:
    """Return the default project file contents."""

    project_title = name.replace("_", " ").title()
    description_text = description or "Add the project purpose here."
    dataset_text = datasets or "Add expected datasets or APIs here."
    notes_text = notes or "Add project notes, constraints, or milestones here."
    files: dict[Path, str] = {
        Path("README.md"): "\n".join(
            [
                f"# {project_title}",
                "",
                description_text,
                "",
                "## Structure",
                "",
                "- `report/` - Word report source files",
                "- `code/` - reusable project code",
                "- `scripts/` - exploratory scripts",
                "- `app/` - Streamlit app source files" if with_app else "",
                "- `data/` - raw or intermediate project data",
                "- `guidance/` - context and planning notes",
                "- `results/figures/` - output figures",
                "- `results/app/` - app screenshots and local app outputs" if with_app else "",
                "- `results/tables/` - output tables",
                "",
                "## Next Steps",
                "",
                (
                    '- Run `python ../../tools/workflow.py setup-paper --target . --title "..."`'
                    " from this folder to create the Word report scaffold"
                ),
                "- Run `python scripts/make_figures.py` to create starter validation figures.",
                (
                    "- Run `streamlit run app/streamlit_app.py` from the repo root"
                    " to launch the project app."
                    if with_app
                    else ""
                ),
                (
                    "- Build project context with `python ../../tools/workflow.py"
                    ' build-context report/report.docx` once a draft exists'
                ),
                "",
            ]
        )
        + "\n",
        Path("AGENTS.md"): "\n".join(
            [
                "# Project Guide",
                "",
                f"This project lives under `projects/{name}/`.",
                "",
                "## Scope",
                "",
                f"- Project name: `{name}`",
                f"- Description: {description_text}",
                f"- Expected datasets: {dataset_text}",
                f"- Notes: {notes_text}",
                "",
                "## Working Rules",
                "",
                "- Keep reusable code in `code/`.",
                "- Keep one-off exploration in `scripts/`.",
                "- Save report source in `report/` as a Word `.docx` file.",
                "- Keep Streamlit app code in `app/`." if with_app else "",
                "- Save figures in `results/figures/` and tables in `results/tables/`.",
                (
                    "- Submit the public Streamlit app URL, accessible GitHub repo URL,"
                    " branch, app entrypoint path, and final commit hash."
                    if with_app
                    else ""
                ),
                "- Use `fintools.figures` and `FigureContext` for report-ready plots.",
                (
                    '- Use `python ../../tools/workflow.py setup-paper --target . --title "..."`'
                    " to start the Word report."
                ),
                "",
            ]
        )
        + "\n",
        Path("CLAUDE.md"): "\n".join(
            [
                "## Project Overlay",
                "",
                "Read `AGENTS.md` in this project folder first.",
                "Use the repo workflows and keep edits inside this project unless asked otherwise.",
                "",
            ]
        )
        + "\n",
        Path("GEMINI.md"): "\n".join(
            [
                "# Gemini Project Overlay",
                "",
                "@AGENTS.md",
                "",
                (
                    "Use the repo workflows from this project folder and keep edits"
                    " local to this project."
                ),
                "",
            ]
        )
        + "\n",
        Path("QWEN.md"): "\n".join(
            [
                "# Qwen Project Overlay",
                "",
                "Read `AGENTS.md` in this project folder first.",
                "Use project-local files and results unless asked to work elsewhere.",
                "",
            ]
        )
        + "\n",
        Path(".gitignore"): "\n".join(
            [
                "*.aux",
                "*.bbl",
                "*.blg",
                "*.fdb_latexmk",
                "*.fls",
                "*.log",
                "*.out",
                "*.pdf",
                "*.synctex.gz",
                "results/figures/*.png",
                "results/figures/*.pdf",
                "results/figures/*.caption.md",
                "results/figures/*.docx",
                "results/figures/_checks/",
                "results/tables/*.csv",
                "",
            ]
        ),
        Path("scripts/make_figures.py"): "\n".join(
            [
                '"""Starter figure script for this project."""',
                "",
                "from __future__ import annotations",
                "",
                "from pathlib import Path",
                "",
                "import matplotlib",
                'matplotlib.use("Agg", force=False)',
                "import matplotlib.pyplot as plt",
                "",
                "from fintools.datasets import load_validation_dataset",
                "from fintools.figures import (",
                "    FigureContext,",
                "    correlation_heatmap,",
                "    cumulative_returns_plot,",
                "    export_word_figure,",
                "    mean_return_bar_plot,",
                ")",
                "",
                'OUTPUT_DIR = Path("results/figures")',
                "",
                "",
                "def sample_label(index) -> str:",
                '    """Return a compact sample-period label."""',
                "",
                '    return f"{index.min():%Y-%m-%d} to {index.max():%Y-%m-%d}"',
                "",
                "",
                "def main() -> None:",
                '    """Build starter figures from public validation fixtures."""',
                "",
                "    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)",
                "",
                '    ff3 = load_validation_dataset("ff3_monthly")',
                "    context = FigureContext(",
                '        title="Cumulative Market Excess Return",',
                "        note=(",
                '            "Starter figure from monthly Fama/French market excess returns. "',
                '            "Gray bands denote NBER recessions."',
                "        ),",
                "        source=ff3.source,",
                "        sample=sample_label(ff3.data.index),",
                '        units="Cumulative return",',
                "    )",
                "    fig, _ = cumulative_returns_plot(",
                "        ff3.data,",
                '        "Mkt-RF",',
                "        returns_are_percent=True,",
                "        title=context.title,",
                '        profile="word_a4",',
                "    )",
                '    export_word_figure(fig, OUTPUT_DIR, "market_cumulative", context=context)',
                "    plt.close(fig)",
                "",
                '    industries = load_validation_dataset("ff_industry_10_monthly")',
                "    context = FigureContext(",
                '        title="Mean Industry Returns With Standard Errors",',
                "        note=(",
                '            "Mean monthly returns across 10 industry portfolios. "',
                '            "Error bars are standard errors of the monthly mean."',
                "        ),",
                "        source=industries.source,",
                "        sample=sample_label(industries.data.index),",
                '        units="Mean monthly return (%)",',
                "    )",
                "    fig, _, _ = mean_return_bar_plot(",
                "        industries.data,",
                "        industries.data.columns,",
                "        title=context.title,",
                '        profile="word_a4",',
                "    )",
                '    export_word_figure(fig, OUTPUT_DIR, "industry_mean_returns", context=context)',
                "    plt.close(fig)",
                "",
                "    context = FigureContext(",
                '        title="Industry Return Correlations",',
                '        note="Starter heatmap across monthly 10-industry portfolio returns.",',
                "        source=industries.source,",
                "        sample=sample_label(industries.data.index),",
                '        units="Correlation",',
                "    )",
                "    fig, _ = correlation_heatmap(",
                "        industries.data,",
                "        title=context.title,",
                '        profile="word_a4",',
                "    )",
                '    export_word_figure(fig, OUTPUT_DIR, "industry_correlations", context=context)',
                "    plt.close(fig)",
                "",
                '    print(f"Wrote figures to {OUTPUT_DIR.resolve()}")',
                "",
                "",
                'if __name__ == "__main__":',
                "    main()",
                "",
            ]
        ),
    }
    if with_app:
        files.update(app_file_texts(name=name, title=project_title, description=description_text))
    return files


def app_file_texts(
    *,
    name: str,
    title: str,
    description: str,
    entrypoint_path: str | None = None,
) -> dict[Path, str]:
    """Return starter Streamlit app scaffold files for a project."""

    entrypoint = entrypoint_path or f"projects/{name}/app/streamlit_app.py"
    readiness_target = (
        entrypoint.removesuffix("/app/streamlit_app.py")
        if entrypoint.endswith("/app/streamlit_app.py")
        else "."
    )
    return {
        Path("app/README.md"): "\n".join(
            [
                f"# {title} Streamlit App",
                "",
                description,
                "",
                "Run locally from the repo root:",
                "",
                "```bash",
                f"streamlit run {entrypoint}",
                "```",
                "",
                "Deploy on Streamlit Community Cloud with:",
                "",
                "- Repository: your student-owned GitHub repo",
                "- Branch: `main`",
                f"- Entrypoint: `{entrypoint}`",
                "- Python version: match the course repo where possible",
                "",
                "During development, keep the GitHub repo private and push regularly.",
                "At hand-in, submit a public Streamlit app URL and a GitHub repo URL",
                "that the teaching team can access.",
                "",
                "Do not commit `.streamlit/secrets.toml`.",
                "",
            ]
        )
        + "\n",
        Path("SUBMISSION_CHECKLIST.md"): "\n".join(
            [
                f"# {title} Deployment Checklist",
                "",
                "Use this file near hand-in. Keep the project repository private while",
                "developing, but push regularly so the work is backed up and versioned.",
                "",
                "## Required Deployment Fields",
                "",
                "- Public Streamlit app URL: TODO",
                "- GitHub repository URL accessible to the teaching team: TODO",
                "- Branch: `main`",
                f"- App entrypoint: `{entrypoint}`",
                "- Final commit hash: TODO",
                "",
                "## Before Hand-In",
                "",
                "- [ ] Run",
                "  `python tools/workflow.py check-app-submission"
                f" --target {readiness_target} --entrypoint {entrypoint}`",
                "  from the repo root and resolve any blocking issues.",
                "- [ ] The latest code is committed and pushed to GitHub.",
                "- [ ] The app runs locally from the repo root with",
                f"  `streamlit run {entrypoint}`.",
                "- [ ] The Streamlit Community Cloud app loads in an incognito browser.",
                "- [ ] The Streamlit app is public for grading.",
                "- [ ] The teaching team can access the GitHub repository.",
                "- [ ] The README explains the data, insight, local run command, and",
                "  deployment path.",
                "- [ ] No secrets, `.streamlit/secrets.toml`, `.env`, `.venv/`, local",
                "  absolute paths, or private raw data are committed.",
                "",
                "A `localhost` URL is not a valid submission. It only works on the",
                "student's own computer while the local Streamlit process is running.",
                "",
            ]
        ),
        Path(".streamlit/config.toml"): "\n".join(
            [
                "[browser]",
                "gatherUsageStats = false",
                "",
                "[server]",
                "headless = true",
                "",
                "[theme]",
                'base = "light"',
                'primaryColor = "#A51C30"',
                'backgroundColor = "#FFFFFF"',
                'secondaryBackgroundColor = "#F4F2EE"',
                'textColor = "#262A33"',
                'font = "sans serif"',
                "",
            ]
        ),
        Path("app/streamlit_app.py"): "\n".join(
            [
                '"""Starter Streamlit app for this project."""',
                "",
                "from __future__ import annotations",
                "",
                "import sys",
                "from pathlib import Path",
                "",
                "import pandas as pd",
                "import streamlit as st",
                "",
                "REPO_ROOT = next(",
                "    (",
                "        parent",
                "        for parent in Path(__file__).resolve().parents",
                "        if (parent / 'fintools').is_dir()",
                "    ),",
                "    Path(__file__).resolve().parents[2],",
                ")",
                "if str(REPO_ROOT) not in sys.path:",
                "    sys.path.insert(0, str(REPO_ROOT))",
                "",
                "from fintools.apps import (  # noqa: E402",
                "    MetricCard,",
                "    SeriesSpec,",
                "    active_tab_label,",
                "    configure_page,",
                "    forecast_series_spec,",
                "    lazy_tabs,",
                "    query_choice,",
                "    query_int,",
                "    render_csv_download,",
                "    render_data_health,",
                "    render_display_table,",
                "    render_metric_strip,",
                "    rolling_backtest_spec,",
                "    sync_query_params,",
                "    tab_is_open,",
                "    target_forecast_figure,",
                "    target_name,",
                ")",
                "",
                f'APP_TITLE = "{title}"',
                'DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "app_sample.csv"',
                'SAMPLE_PERIODS = {"Full": None, "5Y": 5, "3Y": 3, "1Y": 1}',
                'MODEL_LABELS = {"drift": "Drift", "naive": "Naive", "ar1": "AR(1)"}',
                'VIEW_OPTIONS = ["Forecast", "Data", "Method"]',
                'BACKTEST_LABELS = {',
                '    "actual": "Actual",',
                '    "forecast": "Forecast",',
                '    "error": "Error",',
                '    "absolute_error": "Absolute error",',
                "}",
                "",
                "",
                "@st.cache_data(ttl=86400)",
                "def load_data() -> pd.DataFrame:",
                '    """Load project data or a deterministic fallback sample."""',
                "",
                "    if DATA_PATH.exists():",
                '        return pd.read_csv(DATA_PATH, parse_dates=["date"])',
                '    dates = pd.date_range("2018-01-31", periods=72, freq="ME")',
                "    values = 100 + pd.Series(range(len(dates))).mul(0.35).to_numpy()",
                "    seasonal = pd.Series(range(len(dates))).mod(12).mul(0.08).to_numpy()",
                "    return pd.DataFrame(",
                '        {"date": dates, "indicator": values + seasonal, "segment": "Sample"}',
                "    )",
                "",
                "",
                "def apply_sample_period(frame: pd.DataFrame, sample_period: str) -> pd.DataFrame:",
                '    """Restrict the app data to the selected analysis sample."""',
                "",
                "    years = SAMPLE_PERIODS[sample_period]",
                "    if years is None:",
                "        return frame.copy()",
                '    cutoff = frame["date"].max() - pd.DateOffset(years=years)',
                '    return frame.loc[frame["date"] >= cutoff].copy()',
                "",
                "",
                "def main() -> None:",
                "    configure_page(APP_TITLE)",
                "    st.title(APP_TITLE)",
                '    st.caption("A starter app for an interactive forecast product.")',
                "",
                "    data = load_data()",
                "    value_columns = [",
                "        c",
                "        for c in data.columns",
                "        if c != 'date' and pd.api.types.is_numeric_dtype(data[c])",
                "    ]",
                "    if not value_columns:",
                '        st.error("The app needs at least one numeric column to forecast.")',
                "        return",
                "",
                "    indicator_default = query_choice(",
                '        "indicator", value_columns, default=value_columns[0]',
                "    )",
                '    model_default = query_choice("model", list(MODEL_LABELS), default="drift")',
                '    horizon_default = query_int("horizon", default=12, minimum=3, maximum=24)',
                '    sample_default = query_choice("sample", list(SAMPLE_PERIODS), default="Full")',
                '    view_default = query_choice("view", VIEW_OPTIONS, default="Forecast")',
                "",
                '    st.subheader("Forecast settings")',
                "    control_cols = st.columns([1.25, 1.0, 1.0])",
                "    with control_cols[0]:",
                "        value = st.selectbox(",
                '            "Indicator",',
                "            value_columns,",
                "            index=value_columns.index(indicator_default),",
                "        )",
                "    with control_cols[1]:",
                "        model = st.selectbox(",
                '            "Forecast model",',
                "            list(MODEL_LABELS),",
                "            index=list(MODEL_LABELS).index(model_default),",
                "            format_func=lambda item: MODEL_LABELS[item],",
                "        )",
                "    with control_cols[2]:",
                '        horizon = st.slider("Forecast horizon", 3, 24, horizon_default)',
                "",
                "    sample_period = st.segmented_control(",
                '        "Sample period",',
                "        options=list(SAMPLE_PERIODS),",
                "        default=sample_default,",
                "        help=",
                '        "The selected period controls the chart, forecast, backtest, "',
                '        "metrics, and table.",',
                "    )",
                '    sample_period = sample_period or "Full"',
                "",
                '    frame = apply_sample_period(data, sample_period).dropna(',
                '        subset=["date", value]',
                '    ).sort_values("date")',
                '    series = frame.set_index("date")[value]',
                "    spec = SeriesSpec(",
                "        series_id=value,",
                "        label=value.replace('_', ' ').title(),",
                '        units="Value",',
                '        target="change",',
                "        target_label=f\"Change in {value.replace('_', ' ').title()}\",",
                '        target_units="Value change",',
                "    )",
                "    forecast = forecast_series_spec(series, spec, horizon=horizon, model=model)",
                "    backtest = rolling_backtest_spec(series, spec, model=model, horizon=1)",
                "",
                "    mae = (",
                "        f\"{backtest['absolute_level_error'].mean():,.2f}\"",
                "        if not backtest.empty",
                "        else \"n/a\"",
                "    )",
                "    render_metric_strip(",
                "        [",
                '            MetricCard("Observations", f"{len(series):,}"),',
                '            MetricCard("Latest value", f"{series.iloc[-1]:,.2f}"),',
                '            MetricCard("Backtest MAE", mae),',
                "        ]",
                "    )",
                "    render_data_health(",
                "        frame,",
                '        source="Project data",',
                '        date_column="date",',
                "        value_columns=[value],",
                "    )",
                "",
                "    tabs = lazy_tabs(VIEW_OPTIONS, default=view_default, key=\"main_view\")",
                "    active_view = active_tab_label(VIEW_OPTIONS, tabs, default=view_default)",
                "    tab_forecast, tab_data, tab_method = tabs",
                "    if tab_is_open(tab_forecast, fallback=active_view == \"Forecast\"):",
                "        with tab_forecast:",
                "            st.plotly_chart(",
                "                target_forecast_figure(forecast, indicator_name=spec.label),",
                "                width=\"stretch\",",
                "                config={\"displaylogo\": False, \"scrollZoom\": False},",
                "            )",
                "    if tab_is_open(tab_data, fallback=active_view == \"Data\"):",
                "        with tab_data:",
                "            display = render_display_table(frame)",
                "            render_csv_download(",
                "                display,",
                "                label=\"Download selected sample CSV\",",
                "                file_name=\"selected_sample.csv\",",
                "                key=\"download_sample\",",
                "            )",
                "    if tab_is_open(tab_method, fallback=active_view == \"Method\"):",
                "        with tab_method:",
                "            st.markdown(",
                '            f"The app forecasts **{target_name(spec)}** over the "',
                '            f"**{sample_period}** sample "',
                '            f"using a transparent **{MODEL_LABELS[model]}** baseline. "',
                '            "The chart converts the forecast target back into an "',
                '            "implied level path. "',
                '            "The backtest reports recent one-step-ahead errors, and the "',
                '            "shaded forecast band is an approximate uncertainty guide rather "',
                '            "than a guarantee."',
                "            )",
                "    sync_query_params(",
                "        indicator=value,",
                "        model=model,",
                "        horizon=horizon,",
                "        sample=sample_period,",
                "        view=active_view,",
                "    )",
                "",
                "",
                'if __name__ == "__main__":',
                "    main()",
                "",
            ]
        ),
        Path("app/tests/test_app_smoke.py"): "\n".join(
            [
                '"""Smoke test for the project Streamlit app."""',
                "",
                "from __future__ import annotations",
                "",
                "import platform",
                "import shutil",
                "import tempfile",
                "from pathlib import Path",
                "",
                "import pytest",
                "",
                "",
                "def test_streamlit_app_smoke(monkeypatch) -> None:",
                "    if platform.system() == 'Windows':",
                "        pytest.skip(",
                "            'Streamlit AppTest can leave locked temp files on native Windows.'",
                "        )",
                "",
                "    project_root = Path(__file__).resolve().parents[2]",
                "    temp_root = project_root / '.tmp-streamlit-app-test'",
                "    temp_root.mkdir(exist_ok=True)",
                "    monkeypatch.setenv('TMP', str(temp_root))",
                "    monkeypatch.setenv('TEMP', str(temp_root))",
                "    tempfile.tempdir = str(temp_root)",
                "",
                "    pytest.importorskip('streamlit.testing.v1')",
                "    from streamlit.testing.v1 import AppTest",
                "",
                "    app_path = Path(__file__).resolve().parents[1] / 'streamlit_app.py'",
                "    at = AppTest.from_file(app_path, default_timeout=10)",
                "    at.run()",
                "    assert not at.exception",
                "    shutil.rmtree(temp_root, ignore_errors=True)",
                "",
            ]
        ),
    }


def submission_repo_url_hint(repo: str = "") -> str:
    """Return the default repo URL placeholder for submission metadata."""

    clean_repo = repo.strip()
    if clean_repo and "/" in clean_repo:
        return f"https://github.com/{clean_repo.removesuffix('.git')}.git"
    if clean_repo:
        return f"https://github.com/<owner>/{clean_repo}.git"
    return "https://github.com/<owner>/<repo>.git"


def submission_json_text(*, target: str, entrypoint: str, repo: str = "") -> str:
    """Return optional machine-readable Streamlit deployment metadata."""

    payload = {
        "repo_url": submission_repo_url_hint(repo),
        "branch": "main",
        "target": target,
        "entrypoint": entrypoint,
        "public_app_url": "https://<your-app-name>.streamlit.app",
        "repo_visibility": "private",
        "teaching_team_access": {
            "mode": "private_collaborators",
            "github_usernames": [
                "TODO_INSTRUCTOR_GITHUB_USERNAME",
                "TODO_MARKER_GITHUB_USERNAME",
            ],
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def submission_check_workflow_text(*, target: str, entrypoint: str) -> str:
    """Return the reusable GitHub Actions workflow for deployment checks."""

    return "\n".join(
        [
            "name: Streamlit Deployment Check",
            "",
            "on:",
            "  push:",
            "  workflow_dispatch:",
            "",
            "permissions:",
            "  contents: read",
            "",
            "jobs:",
            "  submission-check:",
            "    runs-on: ubuntu-latest",
            "    steps:",
            "      - name: Check out repository",
            "        uses: actions/checkout@v4",
            "",
            "      - name: Set up Python 3.13",
            "        uses: actions/setup-python@v5",
            "        with:",
            '          python-version: "3.13"',
            "          cache: pip",
            "",
            "      - name: Install dependencies",
            "        shell: bash",
            "        run: |",
            "          python -m pip install --upgrade pip",
            "          python -m pip install -r requirements.txt",
            "          if [ -f requirements-dev.txt ]; then",
            "            python -m pip install -r requirements-dev.txt",
            "          fi",
            "",
            "      - name: Run deployment readiness check",
            "        shell: bash",
            "        run: |",
            "          python tools/workflow.py check-app-submission \\",
            f"            --target {target} \\",
            f"            --entrypoint {entrypoint} \\",
            "            --run-tests",
            "",
        ]
    )


def create_project(
    root: Path,
    *,
    name: str,
    description: str = "",
    datasets: str = "",
    notes: str = "",
    with_app: bool = False,
) -> tuple[Path, list[str]]:
    """Create a new project scaffold."""

    validate_project_name(name)
    project_root = ensure_within_repo(root / "projects" / name, root)
    if project_root.exists():
        raise WorkflowError(f"project already exists: {project_root}")

    directories = [
        project_root / "report",
        project_root / "code",
        project_root / "scripts",
        project_root / "data",
        project_root / "guidance",
        project_root / "results" / "figures",
        project_root / "results" / "tables",
    ]
    if with_app:
        directories.extend([project_root / "app", project_root / "results" / "app"])
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=False)

    for relative, text in project_file_texts(
        name,
        description=description,
        datasets=datasets,
        notes=notes,
        with_app=with_app,
    ).items():
        write_text(project_root / relative, text)

    lines = [
        f"Created project scaffold: {project_root.relative_to(root)}",
        "Created directories:",
    ]
    lines.extend(f"- {path.relative_to(root)}" for path in directories)
    if with_app:
        lines.append("Included Streamlit app scaffold in app/streamlit_app.py")
    lines.append("Next step: run setup-paper in the project root to create report/report.docx.")
    return project_root, lines


def discover_week_root(start: Path, root: Path) -> Path | None:
    """Return the containing weekly root if inside fins2026/weekN/."""

    for candidate in [start, *start.parents]:
        if candidate == root:
            break
        if candidate.parent == root / "fins2026" and WEEK_FOLDER_RE.fullmatch(candidate.name):
            return candidate
    return None


def resolve_week_target(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
) -> Path:
    """Resolve a fins2026/weekN target directory."""

    candidate = ensure_within_repo(resolve_path(cwd, Path(target)), root) if target else cwd
    week_root = discover_week_root(candidate, root)
    if week_root is None:
        raise WorkflowError("could not infer the week folder; use --target fins2026/weekN")
    return week_root


def week_number(week_root: Path) -> int:
    """Return the integer week number from a week root."""

    return int(week_root.name.removeprefix("week"))


def week_heading(week_root: Path, *, title: str = "") -> str:
    """Return a display heading for a weekly scaffold."""

    base = f"Week {week_number(week_root)}"
    clean_title = title.strip()
    return f"{base}: {clean_title}" if clean_title else base


def week_title_slug(week_root: Path, *, title: str = "") -> str:
    """Return a stable week label for docs and prompts."""

    return week_heading(week_root, title=title).replace("#", "").strip()


def scaffold_extra_doc_lines(week_root: Path) -> list[str]:
    """Return optional references to extra week-specific markdown guides."""

    standard_docs = {
        "AGENTS.md",
        "CLAUDE.md",
        "DATA_GUIDE.md",
        "GEMINI.md",
        "QWEN.md",
        "README.md",
        "SUBMISSION_CHECKLIST.md",
        "WORKSHOP.md",
    }
    extras = sorted(
        path.name
        for path in week_root.glob("*.md")
        if path.name not in standard_docs and path.is_file()
    )
    if not extras:
        return []
    lines = ["", "## Existing Week-Specific Guides", ""]
    lines.extend(f"- `{name}`" for name in extras)
    return lines


def week_file_texts(
    root: Path,
    week_root: Path,
    *,
    title: str = "",
) -> dict[Path, str]:
    """Return starter file contents for a weekly scaffold."""

    heading = week_heading(week_root, title=title)
    week_label = week_title_slug(week_root, title=title)
    week_rel = week_root.relative_to(root).as_posix()
    script_path = f"{week_rel}/scripts/run_week.py"
    describe_path = f"{week_rel}/scripts/describe_data.py"
    extra_doc_lines = scaffold_extra_doc_lines(week_root)
    standard_layout_lines = [
        "- `data/` - committed source inputs for this week",
        "- `code/` - week-local reusable logic",
        "- `scripts/` - official rerunnable week scripts",
        "- `scratch/` - disposable exploration and play-around code",
        "- `results/data/` - generated, cleaned, or downloaded datasets",
        "- `results/figures/` - exported figures and proof packs",
        "- `results/tables/` - exported tables",
        "- `results/app/` - local app logs or screenshots when relevant",
        "- `guidance/` - generated week context for students and AI tools",
        "- `prompts/` - reusable prompts for this week",
        "- `app/` - app-specific notes and tests if the week grows into an app",
        "- `tests/` - local week-specific smoke checks",
    ]
    return {
        Path("README.md"): "\n".join(
            [
                f"# {heading}",
                "",
                "This week uses the standard course scaffold. Put source inputs in `data/`,",
                "keep canonical week scripts in `scripts/`, store scratch work in `scratch/`,",
                "and write generated outputs under `results/`.",
                "",
                "## Run First",
                "",
                "From the repo root:",
                "",
                "```bash",
                f"python {describe_path}",
                f"python {script_path}",
                f"python tools/workflow.py build-week-context --target {week_rel}",
                "```",
                "",
                "## Structure",
                "",
                *standard_layout_lines,
                "",
                "## Working Rules",
                "",
                "- Treat `data/` as source-of-truth inputs, not a dump for generated files.",
                "- Save anything rebuilt, merged, downloaded, or model-produced in",
                "  `results/data/`.",
                "- Promote code from `scratch/` into `scripts/`, `code/`, or `fintools/`",
                "  once it matters.",
                "- Keep the week rerunnable from the repo root.",
                "",
                "## Next Steps",
                "",
                "- Fill in `WORKSHOP.md` with the workshop agenda and checkpoints.",
                "- Update `DATA_GUIDE.md` and `data/README.md` once the week's inputs are known.",
                "- Extend `scripts/run_week.py` into the canonical week pipeline.",
                "- Refresh `guidance/` with `python tools/workflow.py "
                f"build-week-context --target {week_rel}`",
                "  after the week content changes.",
                "",
            ]
        )
        + "\n",
        Path("AGENTS.md"): "\n".join(
            [
                "# Weekly Overlay",
                "",
                f"This folder is `{week_rel}`.",
                "",
                "## Working Rules",
                "",
                "- Keep week-specific work inside this folder.",
                "- Use `data/` for committed source inputs only.",
                "- Use `results/data/` for generated or refreshed datasets.",
                "- Keep canonical rerunnable scripts in `scripts/`.",
                "- Use `scratch/` for disposable experiments, not the final path.",
                "- Promote reusable week-local logic into `code/`.",
                "- Move anything reused across weeks into `fintools/`.",
                "- Regenerate `guidance/*.md` after the week docs, scripts, or data change.",
                "",
                "## Useful Commands",
                "",
                f"- `python {describe_path}`",
                f"- `python {script_path}`",
                f"- `python tools/workflow.py build-week-context --target {week_rel}`",
                f"- `python tools/workflow.py build-app --target {week_rel}` when this week",
                "  grows into an app",
                "",
            ]
        )
        + "\n",
        Path("CLAUDE.md"): "\n".join(
            [
                "## Weekly Overlay",
                "",
                "Read `AGENTS.md` in this week folder first.",
                "Keep edits inside this week unless a shared utility belongs in `fintools/`.",
                "",
            ]
        )
        + "\n",
        Path("GEMINI.md"): "\n".join(
            [
                "# Gemini Weekly Overlay",
                "",
                "@AGENTS.md",
                "",
                "Keep week-specific edits local to this folder unless the logic should move to",
                "`fintools/`.",
                "",
            ]
        )
        + "\n",
        Path("QWEN.md"): "\n".join(
            [
                "# Qwen Weekly Overlay",
                "",
                "Read `AGENTS.md` in this week folder first.",
                "Treat this folder as the default write scope for week-specific work.",
                "",
            ]
        )
        + "\n",
        Path("WORKSHOP.md"): "\n".join(
            [
                f"# {week_label} Workshop",
                "",
                "Use this file as the workshop run sheet. Keep the flow concrete enough that a",
                "student can move from data inspection to code, then from code to outputs.",
                "",
                "## Suggested Flow",
                "",
                "1. Review `README.md`, `DATA_GUIDE.md`, and `guidance/week-context.md`.",
                "2. Inspect the current inputs with `scripts/describe_data.py`.",
                "3. Run or extend `scripts/run_week.py`.",
                "4. Save generated datasets, figures, and tables under `results/`.",
                "5. Refresh `guidance/` when the week's materials change.",
                *extra_doc_lines,
                "",
            ]
        )
        + "\n",
        Path("DATA_GUIDE.md"): "\n".join(
            [
                f"# {week_label} Data Guide",
                "",
                "Document the source inputs in `data/`, the meaning of each dataset, and any",
                "transformations that produce derived outputs in `results/data/`.",
                "",
                "## Rules",
                "",
                "- Keep committed source data in `data/`.",
                "- Keep generated, merged, cleaned, or downloaded datasets in `results/data/`.",
                "- Update `data/README.md` with file-level notes and column definitions.",
                "",
            ]
        )
        + "\n",
        Path("SUBMISSION_CHECKLIST.md"): "\n".join(
            [
                f"# {week_label} Submission Checklist",
                "",
                "- `README.md` explains the week purpose and canonical commands.",
                "- `WORKSHOP.md` reflects the actual workshop flow.",
                "- `DATA_GUIDE.md` and `data/README.md` describe the inputs accurately.",
                "- Canonical scripts live in `scripts/`, not `scratch/`.",
                "- Generated outputs live under `results/` and are reproducible.",
                "- `guidance/*.md` has been refreshed with `python tools/workflow.py "
                f"build-week-context --target {week_rel}`.",
                "- Any app work is isolated under `app/`.",
                "",
            ]
        )
        + "\n",
        Path("app/README.md"): "\n".join(
            [
                f"# {week_label} App Notes",
                "",
                "This folder is part of the standard weekly scaffold. Leave it as notes plus",
                "tests until the week needs a real app scaffold.",
                "",
                "If this week grows into a Streamlit app, run:",
                "",
                "```bash",
                f"python tools/workflow.py build-app --target {week_rel}",
                "```",
                "",
            ]
        )
        + "\n",
        Path("code/README.md"): "\n".join(
            [
                f"# {week_label} Week-Local Code",
                "",
                "Use this folder for week-local reusable helpers. If the logic becomes useful",
                "across multiple weeks, move it into `fintools/`.",
                "",
            ]
        )
        + "\n",
        Path("data/README.md"): "\n".join(
            [
                f"# {week_label} Data",
                "",
                "Store committed source inputs for this week here. Describe each file, its",
                "source, key columns, and any important caveats.",
                "",
            ]
        )
        + "\n",
        Path("prompts/README.md"): "\n".join(
            [
                f"# {week_label} Prompts",
                "",
                "Keep reusable prompts here when the week benefits from repeated AI-assisted",
                "figure, app, report, or data-analysis tasks.",
                "",
            ]
        )
        + "\n",
        Path("prompts/assistant_starter.md"): "\n".join(
            [
                f"# {week_label} Assistant Starter Prompt",
                "",
                "Use the current week scaffold and follow these rules:",
                "",
                "- treat `data/` as source inputs",
                "- write generated datasets to `results/data/`",
                "- write generated figures to `results/figures/`",
                "- keep exploratory code in `scratch/` unless it becomes canonical",
                "- promote reusable logic into `code/` or `fintools/`",
                "- refresh context with `guidance/week-context.md`, `guidance/data-context.md`,",
                "  and `guidance/output-context.md` before a major rewrite",
                "",
            ]
        )
        + "\n",
        Path("scratch/README.md"): "\n".join(
            [
                f"# {week_label} Scratch Space",
                "",
                "Use this folder for disposable experiments, debugging snippets, and play-around",
                "code. Anything worth keeping should be promoted into `scripts/`, `code/`, or",
                "`fintools/`.",
                "",
            ]
        )
        + "\n",
        Path("scripts/run_week.py"): "\n".join(
            [
                '"""Starter entrypoint for the weekly scaffold."""',
                "",
                "from __future__ import annotations",
                "",
                "from pathlib import Path",
                "",
                "from describe_data import describe_week_data",
                "",
                "WEEK_ROOT = Path(__file__).resolve().parents[1]",
                "RESULTS_DIRS = [",
                "    WEEK_ROOT / 'results' / 'data',",
                "    WEEK_ROOT / 'results' / 'figures',",
                "    WEEK_ROOT / 'results' / 'tables',",
                "    WEEK_ROOT / 'results' / 'app',",
                "]",
                "",
                "",
                "def main() -> None:",
                '    """Print the week inventory and confirm standard output paths."""',
                "",
                "    for directory in RESULTS_DIRS:",
                "        directory.mkdir(parents=True, exist_ok=True)",
                f"    print('{week_label}')",
                "    print()",
                "    print(describe_week_data())",
                "    print()",
                "    print('Next steps:')",
                "    print('- add committed source inputs under data/')",
                "    print('- extend scripts/run_week.py into the canonical week pipeline')",
                "    print('- keep disposable exploration under scratch/')",
                "    print(",
                "        '- save generated outputs under results/data, results/figures, '",
                "        'and results/tables'",
                "    )",
                "    print(",
                "        '- refresh guidance/ with the build-week-context workflow after '",
                "        'changes'",
                "    )",
                "",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        )
        + "\n",
        Path("scripts/describe_data.py"): "\n".join(
            [
                '"""Summarize the current data files for this week."""',
                "",
                "from __future__ import annotations",
                "",
                "from pathlib import Path",
                "",
                "WEEK_ROOT = Path(__file__).resolve().parents[1]",
                "DATA_DIR = WEEK_ROOT / 'data'",
                "RESULTS_DATA_DIR = WEEK_ROOT / 'results' / 'data'",
                "",
                "",
                "def visible_files(directory: Path) -> list[Path]:",
                '    """Return non-placeholder files inside a directory tree."""',
                "",
                "    if not directory.exists():",
                "        return []",
                "    return sorted(",
                "        path",
                "        for path in directory.rglob('*')",
                "        if path.is_file() and path.name != '.gitkeep'",
                "    )",
                "",
                "",
                "def describe_directory(label: str, directory: Path) -> list[str]:",
                '    """Return a short inventory for one week data directory."""',
                "",
                "    files = visible_files(directory)",
                "    lines = [f'{label}: {directory.relative_to(WEEK_ROOT).as_posix()}']",
                "    if not files:",
                "        lines.append('- no files yet')",
                "        return lines",
                "    for path in files:",
                "        rel = path.relative_to(WEEK_ROOT).as_posix()",
                "        lines.append(f'- {rel} ({path.stat().st_size} bytes)')",
                "    return lines",
                "",
                "",
                "def describe_week_data() -> str:",
                '    """Return a plain-text summary of source and generated datasets."""',
                "",
                "    lines = ['Week data inventory', '']",
                "    lines.extend(describe_directory('Source data', DATA_DIR))",
                "    lines.append('')",
                "    lines.extend(describe_directory('Generated data', RESULTS_DATA_DIR))",
                "    return '\\n'.join(lines)",
                "",
                "",
                "def main() -> None:",
                "    print(describe_week_data())",
                "",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        )
        + "\n",
        Path("tests/test_week_smoke.py"): "\n".join(
            [
                '"""Local smoke test for the standard weekly scaffold."""',
                "",
                "from __future__ import annotations",
                "",
                "from pathlib import Path",
                "",
                "",
                "def test_week_scaffold_smoke() -> None:",
                "    week_root = Path(__file__).resolve().parents[1]",
                "    for relative in [",
                "        'README.md',",
                "        'WORKSHOP.md',",
                "        'DATA_GUIDE.md',",
                "        'SUBMISSION_CHECKLIST.md',",
                "        'AGENTS.md',",
                "        'guidance/week-context.md',",
                "        'guidance/data-context.md',",
                "        'guidance/output-context.md',",
                "        'scripts/run_week.py',",
                "        'scripts/describe_data.py',",
                "        'data/README.md',",
                "        'scratch/README.md',",
                "    ]:",
                "        assert (week_root / relative).exists(), relative",
                "",
            ]
        )
        + "\n",
        Path("app/tests/.gitkeep"): "",
        Path("results/app/.gitkeep"): "",
        Path("results/data/.gitkeep"): "",
        Path("results/figures/.gitkeep"): "",
        Path("results/tables/.gitkeep"): "",
    }


def format_file_size(size_bytes: int) -> str:
    """Render a file size using compact binary units."""

    value = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{int(size_bytes)} B"


def visible_tree_files(directory: Path) -> list[Path]:
    """Return non-placeholder files below a directory."""

    if not directory.exists():
        return []
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.name != ".gitkeep" and "__pycache__" not in path.parts
    )


def tracked_file_set(root: Path) -> set[str] | None:
    """Return tracked repo-relative files, or None when git is unavailable."""

    top_level = git_report(root, ["rev-parse", "--show-toplevel"])
    if top_level.returncode != 0:
        return None
    if Path(top_level.stdout.strip()).resolve() != root.resolve():
        return None
    report = git_report(root, ["ls-files"])
    if report.returncode != 0:
        return None
    return {line.strip() for line in report.stdout.splitlines() if line.strip()}


def summarize_markdown_file(path: Path) -> tuple[str, str]:
    """Return a short title and summary for a markdown file."""

    context = extract_md_context(path)
    return str(context["title"]), str(context["abstract"] or "No summary written yet.")


def summarize_python_file(path: Path) -> str:
    """Return a short one-line summary for a Python script."""

    text = read_text(path)
    lines = text.splitlines()
    if not lines:
        return "No module docstring yet."
    cleaned = lines[0].strip().strip('"').strip("'").strip()
    return cleaned if cleaned else "No module docstring yet."


def column_summary(frame) -> str:
    """Return a compact column summary for a pandas DataFrame."""

    pairs = [f"`{name}` ({dtype})" for name, dtype in frame.dtypes.items()]
    if len(pairs) <= 8:
        return ", ".join(pairs)
    return ", ".join([*pairs[:8], f"... and {len(pairs) - 8} more"])


def describe_tabular_file(path: Path) -> list[str]:
    """Return a schema summary for a tabular file."""

    suffix = path.suffix.lower()
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional in narrow environments
        raise WorkflowError("tabular context generation requires pandas") from exc

    if suffix == ".txt":
        text_lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
        entries = [line for line in text_lines if line and not line.startswith("#")]
        separators = (",", "\t", ";", "|")
        if entries and all(
            not any(separator in line for separator in separators) and len(line.split()) == 1
            for line in entries
        ):
            preview_items = ", ".join(f"`{item}`" for item in entries[:5])
            if len(entries) > 5:
                preview_items = f"{preview_items}, ... and {len(entries) - 5} more"
            return [
                f"- Type: `{suffix or 'no extension'}`",
                "- Format: plain-text one-item-per-line list",
                f"- Entries: {len(entries)}",
                f"- Preview: {preview_items}",
            ]

    if suffix == ".csv":
        frame = pd.read_csv(path)
    elif suffix in {".tsv", ".txt"}:
        try:
            frame = pd.read_csv(path, sep=None, engine="python")
        except Exception:
            return [
                f"- Type: `{suffix or 'no extension'}`",
                "- Schema preview: could not infer a tabular layout",
            ]
    elif suffix == ".xlsx":
        frame = pd.read_excel(path)
    elif suffix == ".parquet":
        frame = pd.read_parquet(path)
    else:
        return [f"- Type: `{suffix or 'no extension'}`", "- Schema preview: not applicable"]
    return [
        f"- Shape: {frame.shape[0]} rows x {frame.shape[1]} columns",
        f"- Columns: {column_summary(frame)}" if frame.shape[1] else "- Columns: none",
    ]


def data_context_section_lines(
    root: Path,
    directory: Path,
    *,
    label: str,
    tracked_relpaths: set[str] | None = None,
) -> list[str]:
    """Return a markdown section for a week data directory."""

    rel_dir = directory.relative_to(root).as_posix()
    lines = [f"## {label}", "", f"- Folder: `{rel_dir}`"]
    visible = visible_tree_files(directory)
    if tracked_relpaths is None:
        files = visible
    else:
        files = [
            path for path in visible if path.relative_to(root).as_posix() in tracked_relpaths
        ]
    if not files:
        if tracked_relpaths is not None and visible:
            lines.extend(["- Status: generated locally and not committed by default", ""])
        else:
            lines.extend(["- Status: no files yet", ""])
        return lines
    lines.extend([f"- Files: {len(files)}", ""])
    for path in files:
        rel_path = path.relative_to(root).as_posix()
        lines.append(f"### `{rel_path}`")
        lines.append(f"- Size: {format_file_size(path.stat().st_size)}")
        if path.suffix.lower() in {".csv", ".tsv", ".txt", ".xlsx", ".parquet"}:
            lines.extend(describe_tabular_file(path))
        else:
            lines.append(f"- Type: `{path.suffix.lower() or 'no extension'}`")
        lines.append("")
    return lines


def output_context_section_lines(
    root: Path,
    directory: Path,
    *,
    label: str,
    tracked_relpaths: set[str] | None = None,
) -> list[str]:
    """Return a markdown section for a week output directory."""

    rel_dir = directory.relative_to(root).as_posix()
    visible = visible_tree_files(directory)
    if tracked_relpaths is None:
        files = visible
    else:
        files = [
            path for path in visible if path.relative_to(root).as_posix() in tracked_relpaths
        ]
    lines = [f"## {label}", "", f"- Folder: `{rel_dir}`"]
    if not files:
        if tracked_relpaths is not None and visible:
            lines.extend(["- Status: generated locally and not committed by default", ""])
        else:
            lines.extend(["- Status: nothing generated yet", ""])
        return lines
    suffix_counts: dict[str, int] = {}
    for path in files:
        suffix = path.suffix.lower() or "[no extension]"
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
    lines.append(f"- Files: {len(files)}")
    lines.append(
        "- Types: "
        + ", ".join(f"`{suffix}` x{count}" for suffix, count in sorted(suffix_counts.items()))
    )
    lines.append("")
    preview = files[:10]
    for path in preview:
        rel_path = path.relative_to(root).as_posix()
        lines.append(f"- `{rel_path}` ({format_file_size(path.stat().st_size)})")
    if len(files) > len(preview):
        lines.append(f"- ... and {len(files) - len(preview)} more files")
    lines.append("")
    return lines


def read_toml_file(path: Path) -> dict[str, object]:
    """Read a TOML file into a Python dictionary."""

    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_week_audit_spec(
    root: Path,
    cwd: Path,
    week_root: Path,
    *,
    spec: str | None,
) -> tuple[str, dict[str, object]]:
    """Load a week-audit spec from an explicit path or built-in defaults."""

    if spec:
        spec_path = ensure_within_repo(resolve_path(cwd, Path(spec)), root)
        if not spec_path.exists():
            raise WorkflowError(
                "could not find the requested week spec; use --spec with a valid repo path: "
                f"{spec_path.relative_to(root)}"
            )
        return spec_path.relative_to(root).as_posix(), read_toml_file(spec_path)

    spec_data = DEFAULT_WEEK_AUDIT_SPECS.get(week_root.name)
    if spec_data is None:
        raise WorkflowError(
            "could not find a built-in week spec; use --spec with a repo-local TOML file"
        )
    return f"built-in:{week_root.name}", copy.deepcopy(spec_data)


def public_repo_surface_files(root: Path) -> list[Path]:
    """Return public-facing repo files that should stay free of internal guidance."""

    files = {
        root / relative
        for relative in PUBLIC_ROOT_SURFACE_FILES
        if (root / relative).exists()
    }
    for relative in PUBLIC_SURFACE_DIRS:
        surface_root = root / relative
        if not surface_root.exists():
            continue
        for path in surface_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in PUBLIC_SURFACE_SUFFIXES:
                files.add(path)
    return sorted(files)


def path_has_public_material(path: Path) -> bool:
    """Return True when a blocked path still contains file content."""

    if not path.exists():
        return False
    if path.is_file():
        return True
    return any(child.is_file() for child in path.rglob("*"))


def audit_public_repo_privacy(root: Path) -> tuple[int, list[str]]:
    """Check public repo surfaces for internal-only workflow leakage."""

    blockers: list[str] = []
    lines = ["Public repo privacy audit:"]

    blocked_paths_found = 0
    for relative in PUBLIC_PRIVACY_BLOCKED_PATHS:
        if path_has_public_material(root / relative):
            blockers.append(f"internal-only path is still committed: {relative.as_posix()}")
            blocked_paths_found += 1
    if not blocked_paths_found:
        lines.append(f"[OK] No blocked internal paths found: {len(PUBLIC_PRIVACY_BLOCKED_PATHS)}")

    files = public_repo_surface_files(root)
    marker_hits = 0
    blocked_markers = [marker.lower() for marker in PUBLIC_PRIVACY_BLOCKED_MARKERS]
    for path in files:
        lowered = read_text(path).lower()
        rel_path = path.relative_to(root).as_posix()
        for marker in blocked_markers:
            if marker in lowered:
                blockers.append(f"blocked marker `{marker}` found in {rel_path}")
                marker_hits += 1
    if not marker_hits:
        lines.append(f"[OK] Public text privacy scan passed: {len(files)} files")

    if blockers:
        lines.extend(
            ["", "Public repo privacy audit failed:", *[f"- {blocker}" for blocker in blockers]]
        )
        return 1, lines

    lines.extend(["", "Public repo privacy audit passed."])
    return 0, lines


def audit_public_release_tree(root: Path) -> tuple[int, list[str]]:
    """Check a prepared public-release tree for blocked paths and missing basics."""

    blockers: list[str] = []
    lines = ["Public release tree audit:"]

    unexpected_entries = sorted(
        child.name
        for child in root.iterdir()
        if child.name != ".git" and child.name not in PUBLIC_RELEASE_ALLOWED_TOP_LEVELS
    )
    if unexpected_entries:
        blockers.extend(
            f"unexpected top-level entry in public release: {entry}"
            for entry in unexpected_entries
        )
    else:
        lines.append(
            f"[OK] Top-level public surface limited to approved entries: "
            f"{len(PUBLIC_RELEASE_ALLOWED_TOP_LEVELS)}"
        )

    missing_root_files = [
        relative.as_posix()
        for relative in PUBLIC_RELEASE_REQUIRED_ROOT_FILES
        if not (root / relative).exists()
    ]
    if missing_root_files:
        blockers.extend(f"missing required public root file: {path}" for path in missing_root_files)
    else:
        lines.append(
            "[OK] Required public root files present: "
            f"{len(PUBLIC_RELEASE_REQUIRED_ROOT_FILES)}"
        )

    missing_week_dirs = [
        relative.as_posix()
        for relative in PUBLIC_RELEASE_REQUIRED_WEEK_DIRS
        if not (root / relative).exists()
    ]
    if missing_week_dirs:
        blockers.extend(
            f"missing required published week folder: {path}" for path in missing_week_dirs
        )
    else:
        lines.append(
            f"[OK] Published week folders present: {len(PUBLIC_RELEASE_REQUIRED_WEEK_DIRS)}"
        )

    blocked_paths_found = 0
    for relative in PUBLIC_RELEASE_BLOCKED_PATHS:
        if path_has_public_material(root / relative):
            blockers.append(f"blocked path present in public release: {relative.as_posix()}")
            blocked_paths_found += 1
    if not blocked_paths_found:
        lines.append(f"[OK] Blocked release paths absent: {len(PUBLIC_RELEASE_BLOCKED_PATHS)}")

    privacy_status, privacy_lines = audit_public_repo_privacy(root)
    if privacy_status != 0:
        blockers.extend(
            line.removeprefix("- ").strip()
            for line in privacy_lines
            if line.startswith("- ")
        )
    else:
        lines.append("[OK] Public text privacy scan passed")

    if blockers:
        lines.extend(
            ["", "Public release tree audit failed:", *[f"- {blocker}" for blocker in blockers]]
        )
        return 1, lines

    lines.extend(["", "Public release tree audit passed."])
    return 0, lines


def week_audit_files(week_root: Path) -> list[Path]:
    """Return the public-text files below a week root."""

    return sorted(
        path
        for path in week_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.name != ".gitkeep"
        and path.suffix.lower() in {".md", ".py"}
    )


def audit_tabular_frame(week_root: Path, check: dict[str, object]):
    """Load a tabular file described by a maintainer week spec."""

    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional in narrow environments
        raise WorkflowError("week audit requires pandas") from exc

    rel_path = str(check["path"])
    data_path = week_root / rel_path
    if not data_path.exists():
        raise WorkflowError(f"week audit data file is missing: {rel_path}")

    format_name = str(check.get("format") or data_path.suffix.lstrip(".")).lower()
    parse_dates = list(check.get("parse_dates", []))
    dayfirst = bool(check.get("dayfirst", False))

    if format_name == "csv":
        frame = pd.read_csv(data_path, parse_dates=parse_dates or None, dayfirst=dayfirst)
    elif format_name == "tsv":
        frame = pd.read_csv(
            data_path,
            sep="\t",
            parse_dates=parse_dates or None,
            dayfirst=dayfirst,
        )
    elif format_name == "parquet":
        frame = pd.read_parquet(data_path)
    else:  # pragma: no cover - guarded by committed specs
        raise WorkflowError(f"unsupported audit-week tabular format: {format_name}")

    raw_shape = frame.shape
    date_from_column = check.get("date_from_column")
    if date_from_column:
        date_new_column = str(check.get("date_new_column") or "Date")
        date_from_format = str(check.get("date_from_format") or "")
        frame[date_new_column] = pd.to_datetime(
            frame[str(date_from_column)],
            format=date_from_format,
        )

    frame.attrs["audit_raw_shape"] = raw_shape

    return frame


def audit_required_paths(
    week_root: Path,
    *,
    required_files: list[str],
    results_dirs: list[str],
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check required week files and result directories."""

    missing_files = [path for path in required_files if not (week_root / path).exists()]
    missing_dirs = [path for path in results_dirs if not (week_root / path).exists()]

    if missing_files:
        blockers.extend(f"missing required file: {path}" for path in missing_files)
    else:
        lines.append(f"[OK] Required files present: {len(required_files)}")

    if missing_dirs:
        blockers.extend(f"missing required results dir: {path}" for path in missing_dirs)
    else:
        lines.append(f"[OK] Results directories present: {len(results_dirs)}")


def audit_required_substrings(
    week_root: Path,
    substring_checks: dict[str, object],
    *,
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check that required substrings appear in key week files."""

    checked_files = 0
    failures = 0
    for rel_path, expected in substring_checks.items():
        target = week_root / rel_path
        if not target.exists():
            blockers.append(f"substring check target is missing: {rel_path}")
            failures += 1
            continue
        expected_bits = (
            [str(expected)] if isinstance(expected, str) else [str(item) for item in list(expected)]
        )
        text = read_text(target)
        missing = [bit for bit in expected_bits if bit not in text]
        if missing:
            blockers.append(
                f"missing required text in {rel_path}: " + ", ".join(f"`{bit}`" for bit in missing)
            )
            failures += 1
            continue
        checked_files += 1
    if substring_checks and failures == 0:
        lines.append(f"[OK] Required text checks passed: {checked_files}")


def audit_public_text(
    week_root: Path,
    *,
    banned_markers: list[str],
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check public week text for banned internal markers."""

    files = week_audit_files(week_root)
    banned = [marker.lower() for marker in banned_markers]
    violations = 0
    for path in files:
        lowered = read_text(path).lower()
        rel_path = path.relative_to(week_root).as_posix()
        for marker in banned:
            if marker in lowered:
                blockers.append(f"banned marker `{marker}` found in {rel_path}")
                violations += 1
    if not violations:
        lines.append(f"[OK] Public text scan passed: {len(files)} files")


def audit_script_portability(
    week_root: Path,
    *,
    script_files: list[str],
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check canonical week scripts for obvious platform-specific patterns."""

    portability_markers = [
        "powershell",
        "cmd /c",
        "cmd.exe",
        "os.startfile",
        ".venv\\",
        "c:\\users\\",
        "/users/",
    ]
    issues = 0
    for rel_path in script_files:
        script_path = week_root / rel_path
        if not script_path.exists():
            continue
        text = read_text(script_path)
        lowered = text.lower()
        for marker in portability_markers:
            if marker in lowered:
                blockers.append(f"platform-specific marker `{marker}` found in {rel_path}")
                issues += 1
        uses_agg = 'matplotlib.use("Agg")' in text or "matplotlib.use('Agg')" in text
        if "savefig(" in text and not uses_agg:
            blockers.append(f"plot-writing script missing headless matplotlib backend: {rel_path}")
            issues += 1
    if not issues:
        lines.append(f"[OK] Script portability scan passed: {len(script_files)} files")


def audit_tabular_checks(
    week_root: Path,
    checks: list[dict[str, object]],
    *,
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check week tabular invariants from a maintainer spec."""

    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional in narrow environments
        raise WorkflowError("week audit requires pandas") from exc

    completed = 0
    for check in checks:
        frame = audit_tabular_frame(week_root, check)
        label = str(check.get("label") or check["path"])

        expected_shape = tuple(int(part) for part in list(check.get("shape", [])))
        actual_shape = tuple(frame.attrs.get("audit_raw_shape", frame.shape))
        if expected_shape and actual_shape != expected_shape:
            blockers.append(f"{label}: expected shape {expected_shape}, got {actual_shape}")
            continue

        duplicate_keys = [str(item) for item in list(check.get("duplicate_keys", []))]
        if duplicate_keys and "duplicate_count" in check:
            actual_duplicates = int(frame.duplicated(duplicate_keys).sum())
            if actual_duplicates != int(check["duplicate_count"]):
                blockers.append(
                    f"{label}: expected {int(check['duplicate_count'])} duplicate rows on "
                    f"{duplicate_keys}, got {actual_duplicates}"
                )
                continue

        if "null_cells" in check:
            actual_nulls = int(frame.isna().sum().sum())
            if actual_nulls != int(check["null_cells"]):
                blockers.append(
                    f"{label}: expected {int(check['null_cells'])} null cells, got {actual_nulls}"
                )
                continue

        date_column = check.get("date_column")
        if date_column:
            actual_min = str(pd.Timestamp(frame[str(date_column)].min()).date())
            actual_max = str(pd.Timestamp(frame[str(date_column)].max()).date())
            if "date_min" in check and actual_min != str(check["date_min"]):
                blockers.append(f"{label}: expected min date {check['date_min']}, got {actual_min}")
                continue
            if "date_max" in check and actual_max != str(check["date_max"]):
                blockers.append(f"{label}: expected max date {check['date_max']}, got {actual_max}")
                continue

        group_count_column = check.get("group_count_column")
        group_counts = check.get("group_counts")
        if group_count_column and isinstance(group_counts, dict):
            actual_counts = {
                str(key): int(value)
                for key, value in frame.groupby(str(group_count_column)).size().to_dict().items()
            }
            expected_counts = {str(key): int(value) for key, value in group_counts.items()}
            if actual_counts != expected_counts:
                blockers.append(
                    f"{label}: expected group counts {expected_counts}, got {actual_counts}"
                )
                continue

        completed += 1
    if checks and completed == len(checks):
        lines.append(f"[OK] Tabular checks passed: {completed}")


def audit_cross_section_checks(
    week_root: Path,
    checks: list[dict[str, object]],
    *,
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check week cross-section invariants from a maintainer spec."""

    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional in narrow environments
        raise WorkflowError("week audit requires pandas") from exc

    completed = 0
    for check in checks:
        frame = audit_tabular_frame(week_root, check)
        label = str(check.get("label") or check["path"])
        date_column = str(check.get("date_column") or "Date")
        filter_date = pd.Timestamp(str(check["filter_date"]))
        cross_section = frame.loc[frame[date_column] == filter_date]

        if "row_count" in check and len(cross_section) != int(check["row_count"]):
            blockers.append(
                f"{label}: expected {int(check['row_count'])} rows on {filter_date.date()}, "
                f"got {len(cross_section)}"
            )
            continue

        key_column = check.get("key_column")
        value_column = check.get("value_column")
        expected_values = check.get("expected_values")
        if key_column and value_column and isinstance(expected_values, dict):
            actual_values = {
                str(key): float(value)
                for key, value in (
                    cross_section.set_index(str(key_column))[str(value_column)].to_dict().items()
                )
            }
            tolerance = float(check.get("abs_tolerance") or 1e-9)
            mismatches = [
                key
                for key, expected in expected_values.items()
                if key not in actual_values
                or abs(actual_values[key] - float(expected)) > tolerance
            ]
            if mismatches:
                blockers.append(
                    f"{label}: value check failed for {', '.join(str(key) for key in mismatches)}"
                )
                continue

        completed += 1
    if checks and completed == len(checks):
        lines.append(f"[OK] Cross-section checks passed: {completed}")


def audit_growth_checks(
    week_root: Path,
    checks: list[dict[str, object]],
    *,
    lines: list[str],
    blockers: list[str],
) -> None:
    """Check growth-of-one-dollar invariants from a maintainer spec."""

    completed = 0
    for check in checks:
        frame = audit_tabular_frame(week_root, check)
        label = str(check.get("label") or check["path"])
        wide = frame.pivot(
            index=str(check.get("index_column") or "Date"),
            columns=str(check.get("columns_column") or "Ticker"),
            values=str(check.get("values_column") or "Return"),
        ).dropna()
        ending_values = (1 + wide).cumprod().iloc[-1]

        expected_values = check.get("expected_final_values")
        if isinstance(expected_values, dict):
            tolerance = float(check.get("abs_tolerance") or 1e-9)
            mismatches = [
                key
                for key, expected in expected_values.items()
                if key not in ending_values
                or abs(float(ending_values[key]) - float(expected)) > tolerance
            ]
            if mismatches:
                blockers.append(
                    f"{label}: final growth values failed for "
                    f"{', '.join(str(key) for key in mismatches)}"
                )
                continue

        numerator = check.get("ratio_numerator")
        denominator = check.get("ratio_denominator")
        expected_ratio = check.get("expected_ratio")
        if numerator and denominator and expected_ratio is not None:
            actual_ratio = float(ending_values[str(numerator)] / ending_values[str(denominator)])
            tolerance = float(check.get("ratio_abs_tolerance") or 1e-9)
            if abs(actual_ratio - float(expected_ratio)) > tolerance:
                blockers.append(
                    f"{label}: expected ratio {expected_ratio}, got {actual_ratio:.4f}"
                )
                continue

        completed += 1
    if checks and completed == len(checks):
        lines.append(f"[OK] Growth checks passed: {completed}")


def audit_week(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    spec: str | None,
) -> tuple[int, list[str]]:
    """Audit a weekly folder against the week contract and data invariants."""

    week_root = resolve_week_target(root, cwd, target=target)
    spec_label, spec_data = load_week_audit_spec(root, cwd, week_root, spec=spec)

    blockers: list[str] = []
    lines = [
        f"Week audit for: {week_root.relative_to(root).as_posix()}",
        f"Spec: {spec_label}",
        "",
    ]

    expected_week_id = str(spec_data.get("week_id") or "")
    if expected_week_id and expected_week_id != week_root.name:
        blockers.append(f"spec week_id is `{expected_week_id}`, expected `{week_root.name}`")

    audit_required_paths(
        week_root,
        required_files=[str(item) for item in list(spec_data.get("required_files", []))],
        results_dirs=[str(item) for item in list(spec_data.get("results_dirs", []))],
        lines=lines,
        blockers=blockers,
    )

    expected_title = str(spec_data.get("title") or "")
    if expected_title and (week_root / "README.md").exists():
        readme_title, _ = summarize_markdown_file(week_root / "README.md")
        if readme_title != expected_title:
            blockers.append(
                f"README title mismatch: expected `{expected_title}`, got `{readme_title}`"
            )
        else:
            lines.append("[OK] Week identity matches spec")
    audit_required_substrings(
        week_root,
        spec_data.get("required_substrings", {}),
        lines=lines,
        blockers=blockers,
    )
    audit_public_text(
        week_root,
        banned_markers=[str(item) for item in list(spec_data.get("banned_markers", []))],
        lines=lines,
        blockers=blockers,
    )
    audit_script_portability(
        week_root,
        script_files=[str(item) for item in list(spec_data.get("script_files", []))],
        lines=lines,
        blockers=blockers,
    )
    audit_tabular_checks(
        week_root,
        list(spec_data.get("tabular_checks", [])),
        lines=lines,
        blockers=blockers,
    )
    audit_cross_section_checks(
        week_root,
        list(spec_data.get("cross_section_checks", [])),
        lines=lines,
        blockers=blockers,
    )
    audit_growth_checks(
        week_root,
        list(spec_data.get("growth_checks", [])),
        lines=lines,
        blockers=blockers,
    )

    if blockers:
        lines.extend(["", "Week audit failed:", *[f"- {blocker}" for blocker in blockers]])
        return 1, lines

    lines.extend(["", "Week audit passed."])
    return 0, lines


def extract_week_timing_notes(paths: list[Path]) -> list[str]:
    """Return documented endpoint, cadence, and observability notes from week docs."""

    keywords = (
        "reference endpoint",
        "information set",
        "observable",
        "release lag",
        "reference date",
        "month-end",
        "quarter-end",
        "mixed-frequency",
        "point-in-time",
    )
    notes: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        raw_lines = read_text(path).splitlines()
        index = 0
        while index < len(raw_lines):
            raw_line = raw_lines[index]
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                index += 1
                continue
            if not stripped.startswith("- "):
                index += 1
                continue
            parts = [stripped[2:].strip()]
            index += 1
            while index < len(raw_lines):
                continuation = raw_lines[index].strip()
                if (
                    not continuation
                    or continuation.startswith("#")
                    or continuation.startswith("- ")
                ):
                    break
                parts.append(continuation)
                index += 1
            cleaned = " ".join(parts).strip()
            lowered = cleaned.lower()
            if not any(keyword in lowered for keyword in keywords):
                continue
            if "results/" in lowered or "guidance/" in lowered or ".csv" in lowered:
                continue
            if not cleaned:
                continue
            cleaned = cleaned.rstrip(".") + "."
            if cleaned not in seen:
                notes.append(cleaned)
                seen.add(cleaned)
            continue
    return notes[:8]


def build_week_context(
    root: Path,
    cwd: Path,
    *,
    target: str | None = None,
) -> tuple[list[Path], list[str]]:
    """Generate guidance files for a weekly scaffold."""

    week_root = resolve_week_target(root, cwd, target=target)
    guidance_dir = week_root / "guidance"
    guidance_dir.mkdir(parents=True, exist_ok=True)
    tracked_relpaths = tracked_file_set(root)

    week_rel = week_root.relative_to(root).as_posix()
    readme_path = week_root / "README.md"
    readme_title, readme_summary = summarize_markdown_file(readme_path)
    workshop_path = week_root / "WORKSHOP.md"
    data_guide_path = week_root / "DATA_GUIDE.md"
    submission_path = week_root / "SUBMISSION_CHECKLIST.md"
    prompts_dir = week_root / "prompts"
    scripts_dir = week_root / "scripts"
    data_dir = week_root / "data"
    results_dir = week_root / "results"
    extra_docs = sorted(
        path
        for path in week_root.glob("*.md")
        if path.name
        not in {
            "AGENTS.md",
            "CLAUDE.md",
            "DATA_GUIDE.md",
            "GEMINI.md",
            "QWEN.md",
            "README.md",
            "SUBMISSION_CHECKLIST.md",
            "WORKSHOP.md",
        }
    )
    prompt_files = sorted(path for path in prompts_dir.glob("*.md") if path.is_file())
    script_files = sorted(path for path in scripts_dir.glob("*.py") if path.is_file())
    timing_notes = extract_week_timing_notes(
        [readme_path, data_guide_path, week_root / "AGENTS.md"]
    )

    week_lines = ["# Week Context", ""]
    week_lines.extend(
        [
            "## Week Identity",
            f"- Week folder: `{week_rel}`",
            f"- Title: {readme_title}",
            f"- README summary: {readme_summary}",
            "",
            "## Core Guides",
            "",
        ]
    )
    for guide_path in [readme_path, workshop_path, data_guide_path, submission_path]:
        title_text, summary_text = summarize_markdown_file(guide_path)
        week_lines.append(
            f"- `{guide_path.relative_to(root).as_posix()}`: {title_text}. {summary_text}"
        )
    if extra_docs:
        week_lines.extend(["", "## Additional Week Docs", ""])
        for path in extra_docs:
            title_text, summary_text = summarize_markdown_file(path)
            week_lines.append(
                f"- `{path.relative_to(root).as_posix()}`: {title_text}. {summary_text}"
            )
    if prompt_files:
        week_lines.extend(["", "## Prompt Files", ""])
        for path in prompt_files:
            title_text, summary_text = summarize_markdown_file(path)
            week_lines.append(
                f"- `{path.relative_to(root).as_posix()}`: {title_text}. {summary_text}"
            )
    week_lines.extend(["", "## Current Scripts", ""])
    if script_files:
        for path in script_files:
            week_lines.append(
                f"- `{path.relative_to(root).as_posix()}`: {summarize_python_file(path)}"
            )
    else:
        week_lines.append("- No canonical scripts are present yet.")
    week_lines.extend(
        [
            "",
            "## Standard Working Rules",
            "",
            "- `data/` is for committed source inputs.",
            "- `results/data/` is for generated, downloaded, cleaned, or merged datasets.",
            "- `scratch/` is for disposable experiments, not the final path.",
            "- Promote reused week-local logic into `code/` and cross-week logic into `fintools/`.",
        ]
    )
    if timing_notes:
        week_lines.extend(["", "## Timing And Alignment Notes", ""])
        week_lines.extend(f"- {note}" for note in timing_notes)
    week_lines.extend(
        [
            "",
            "## Current Paths",
            "",
            f"- Source data: `{data_dir.relative_to(root).as_posix()}`",
            f"- Generated outputs: `{results_dir.relative_to(root).as_posix()}`",
            f"- Current context files: `{guidance_dir.relative_to(root).as_posix()}`",
            "",
        ]
    )

    data_lines = ["# Data Context", ""]
    data_lines.extend(
        data_context_section_lines(
            root,
            week_root / "data",
            label="Committed Inputs",
            tracked_relpaths=tracked_relpaths,
        )
    )
    data_lines.extend(
        data_context_section_lines(
            root,
            week_root / "results" / "data",
            label="Generated Data",
            tracked_relpaths=tracked_relpaths,
        )
    )
    if timing_notes:
        data_lines.extend(["", "## Timing And Alignment Notes", ""])
        data_lines.extend(f"- {note}" for note in timing_notes)

    output_lines = ["# Output Context", ""]
    output_lines.extend(
        output_context_section_lines(
            root,
            week_root / "results" / "data",
            label="Data Outputs",
            tracked_relpaths=tracked_relpaths,
        )
    )
    output_lines.extend(
        output_context_section_lines(
            root,
            week_root / "results" / "figures",
            label="Figure Outputs",
            tracked_relpaths=tracked_relpaths,
        )
    )
    output_lines.extend(
        output_context_section_lines(
            root,
            week_root / "results" / "tables",
            label="Table Outputs",
            tracked_relpaths=tracked_relpaths,
        )
    )
    output_lines.extend(
        output_context_section_lines(
            root,
            week_root / "results" / "forecasts",
            label="Forecast Outputs",
            tracked_relpaths=tracked_relpaths,
        )
    )
    output_lines.extend(
        output_context_section_lines(
            root,
            week_root / "results" / "app",
            label="App Outputs",
            tracked_relpaths=tracked_relpaths,
        )
    )

    outputs = {
        guidance_dir / "week-context.md": "\n".join(week_lines).rstrip() + "\n",
        guidance_dir / "data-context.md": "\n".join(data_lines).rstrip() + "\n",
        guidance_dir / "output-context.md": "\n".join(output_lines).rstrip() + "\n",
    }
    for path, text in outputs.items():
        write_text(path, text)
    report_lines = [
        f"Generated week context for: {week_rel}",
        "Wrote files:",
    ]
    report_lines.extend(f"- {path.relative_to(root)}" for path in outputs)
    return list(outputs), report_lines


def scaffold_week(
    root: Path,
    cwd: Path,
    *,
    target: str,
    title: str = "",
) -> tuple[Path, list[str]]:
    """Create or backfill the standard weekly scaffold."""

    week_root = resolve_week_target(root, cwd, target=target)
    if week_root.exists() and week_root.is_file():
        raise WorkflowError(f"week target is a file, not a folder: {week_root}")

    directories = [
        week_root,
        week_root / "app",
        week_root / "app" / "tests",
        week_root / "code",
        week_root / "data",
        week_root / "guidance",
        week_root / "prompts",
        week_root / "results" / "app",
        week_root / "results" / "data",
        week_root / "results" / "figures",
        week_root / "results" / "tables",
        week_root / "scratch",
        week_root / "scripts",
        week_root / "tests",
    ]
    created_directories: list[Path] = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created_directories.append(directory)

    created_files: list[Path] = []
    for relative, text in week_file_texts(root, week_root, title=title).items():
        target_path = week_root / relative
        if target_path.exists():
            continue
        write_text(target_path, text)
        created_files.append(target_path)

    _, context_lines = build_week_context(
        root,
        week_root,
        target=week_root.relative_to(root).as_posix(),
    )
    report_lines = [f"Scaffolded week folder: {week_root.relative_to(root)}"]
    report_lines.append("Created directories:")
    if created_directories:
        report_lines.extend(f"- {path.relative_to(root)}" for path in created_directories)
    else:
        report_lines.append("- none")
    report_lines.append("Created starter files:")
    if created_files:
        report_lines.extend(f"- {path.relative_to(root)}" for path in created_files)
    else:
        report_lines.append("- none")
    report_lines.extend(context_lines)
    return week_root, report_lines


def build_app_scaffold(
    root: Path,
    cwd: Path,
    *,
    target: str = ".",
    title: str = "Insight App",
    description: str = "Turn data analysis into an interactive Streamlit app.",
) -> tuple[Path, list[str]]:
    """Create a Streamlit app scaffold in an existing project or week folder."""

    target_root = ensure_within_repo(resolve_path(cwd, Path(target)), root)
    app_root = target_root / "app"
    entrypoint = app_root / "streamlit_app.py"
    if entrypoint.exists():
        raise WorkflowError(f"refusing to overwrite existing app scaffold: {entrypoint}")
    for directory in [
        app_root,
        app_root / "tests",
        target_root / "results" / "app",
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    folder_name = target_root.name if target_root != root else "course_app"
    entrypoint_label = entrypoint.relative_to(root).as_posix()
    for relative, text in app_file_texts(
        name=folder_name,
        title=title,
        description=description,
        entrypoint_path=entrypoint_label,
    ).items():
        write_text(target_root / relative, text)

    return app_root, [
        f"Created Streamlit app scaffold in: {app_root.relative_to(root)}",
        f"Local run command: streamlit run {entrypoint_label}",
        "Submit the public Streamlit URL plus an accessible GitHub repo URL.",
    ]


def repo_relative(path: Path, root: Path) -> str:
    """Return a repo-relative POSIX path for user-facing output."""

    return path.resolve().relative_to(root).as_posix()


def workflow_python_version(root: Path) -> str:
    """Return the Python version students should select for deployment."""

    version_file = root / ".python-version"
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8").strip()
        if version:
            return version
    return f"{SUPPORTED_PYTHON[0]}.{SUPPORTED_PYTHON[1]}"


def git_report(root: Path, command: list[str]) -> CommandReport:
    """Run a git command in the repo root."""

    return run_command(["git", *command], cwd=root, timeout=30)


def git_output(root: Path, command: list[str]) -> str:
    """Return stripped git stdout or an empty string on failure."""

    report = git_report(root, command)
    if report.returncode != 0:
        return ""
    return report.stdout.strip()


def tracked_files(root: Path) -> list[str]:
    """Return files tracked by git, or an empty list if git is unavailable."""

    output = git_output(root, ["ls-files"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def is_dangerous_tracked_path(path: str) -> bool:
    """Return whether a tracked path should never appear in a submission repo."""

    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    parts = normalized.split("/")
    return (
        name == ".env"
        or name.startswith(".env.")
        or normalized.endswith(".streamlit/secrets.toml")
        or ".venv" in parts
        or "venv" in parts
    )


def is_submission_placeholder(value: str) -> bool:
    """Return whether a submission metadata field is still a template value."""

    return not value.strip() or bool(SUBMISSION_PLACEHOLDER_RE.search(value.strip()))


def normalize_github_repo_url(url: str) -> str:
    """Normalize common GitHub remote URL variants for comparisons."""

    normalized = url.strip()
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.split(":", 1)[1]
    elif normalized.startswith("ssh://git@github.com/"):
        normalized = "https://github.com/" + normalized.removeprefix("ssh://git@github.com/")
    return normalized.removesuffix(".git").rstrip("/")


def resolve_submission_metadata_path(root: Path, target_root: Path) -> Path | None:
    """Return the preferred submission metadata path for an app target."""

    candidates = [target_root / "submission.json"]
    root_candidate = root / "submission.json"
    if root_candidate not in candidates:
        candidates.append(root_candidate)
    for path in candidates:
        if path.exists():
            return path
    return None


def validate_submission_metadata(
    *,
    root: Path,
    target_root: Path,
    target_label: str,
    entrypoint_label: str,
    branch: str,
    remote_url: str,
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    """Validate optional deployment metadata and summarize the declared contract."""

    blockers: list[str] = []
    warnings: list[str] = []
    pending: list[str] = []
    summary: list[str] = []
    public_app_value = "https://<your-app-name>.streamlit.app"
    submission_path = resolve_submission_metadata_path(root, target_root)
    if submission_path is None:
        summary.extend(
            [
                "Deployment metadata:",
                "- File: not present",
                "- Mode: inferred from the target, entrypoint, and Git state",
            ]
        )
        return public_app_value, blockers, warnings, pending, summary

    try:
        raw = json.loads(submission_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        blockers.append(
            f"Invalid submission.json ({repo_relative(submission_path, root)}): {exc.msg}"
        )
        return public_app_value, blockers, warnings, pending, summary

    if not isinstance(raw, dict):
        blockers.append(
            f"submission.json must contain a JSON object: {repo_relative(submission_path, root)}"
        )
        return public_app_value, blockers, warnings, pending, summary

    def require_string(key: str) -> str:
        value = raw.get(key, "")
        if not isinstance(value, str):
            blockers.append(f"submission.json field `{key}` must be a string.")
            return ""
        stripped = value.strip()
        if not stripped:
            blockers.append(f"submission.json field `{key}` is required.")
        return stripped

    repo_url_value = require_string("repo_url")
    branch_value = require_string("branch")
    target_value = require_string("target")
    entrypoint_value = require_string("entrypoint")
    public_app_value = require_string("public_app_url") or public_app_value
    repo_visibility_value = require_string("repo_visibility")
    teaching_team_access = raw.get("teaching_team_access")

    if target_value and target_value != target_label:
        blockers.append(
            f"submission.json target does not match the checked app target: {target_value}"
        )
    if entrypoint_value and entrypoint_value != entrypoint_label:
        blockers.append(
            "submission.json entrypoint does not match the checked app entrypoint: "
            f"{entrypoint_value}"
        )
    if (
        branch
        and branch_value
        and not is_submission_placeholder(branch_value)
        and branch_value != branch
    ):
        blockers.append(
            f"submission.json branch does not match the current Git branch: {branch_value}"
        )

    if repo_url_value and not is_submission_placeholder(repo_url_value):
        if "github.com/" not in repo_url_value:
            blockers.append("submission.json repo_url must point to GitHub.")
        elif remote_url and normalize_github_repo_url(repo_url_value) != normalize_github_repo_url(
            remote_url
        ):
            blockers.append("submission.json repo_url does not match Git remote 'origin'.")
    else:
        pending.append(
            "Replace the placeholder repo_url in submission.json once the deploy repo exists."
        )

    if is_submission_placeholder(public_app_value):
        pending.append(
            "Deploy the app and replace the placeholder public_app_url in submission.json."
        )
    else:
        if "localhost" in public_app_value:
            blockers.append("submission.json public_app_url cannot use localhost.")
        if not public_app_value.startswith("https://") or "streamlit.app" not in public_app_value:
            blockers.append(
                "submission.json public_app_url must be the public https://...streamlit.app URL."
            )

    if repo_visibility_value and repo_visibility_value not in {"private", "public"}:
        blockers.append("submission.json repo_visibility must be `private` or `public`.")

    collaborator_names: list[str] = []
    collaborator_mode = ""
    if not isinstance(teaching_team_access, dict):
        blockers.append("submission.json teaching_team_access must be an object.")
    else:
        mode_value = teaching_team_access.get("mode", "")
        if not isinstance(mode_value, str) or not mode_value.strip():
            blockers.append("submission.json teaching_team_access.mode is required.")
        else:
            collaborator_mode = mode_value.strip()
            if collaborator_mode not in SUBMISSION_ACCESS_MODES:
                blockers.append(
                    "submission.json teaching_team_access.mode must be one of: "
                    + ", ".join(sorted(SUBMISSION_ACCESS_MODES))
                )

        raw_usernames = teaching_team_access.get("github_usernames", [])
        if raw_usernames is None:
            raw_usernames = []
        if not isinstance(raw_usernames, list) or any(
            not isinstance(item, str) for item in raw_usernames
        ):
            blockers.append(
                "submission.json teaching_team_access.github_usernames must be a list of strings."
            )
        else:
            collaborator_names = [item.strip() for item in raw_usernames if item.strip()]
            if collaborator_mode == "private_collaborators":
                if not collaborator_names:
                    pending.append(
                        "List the instructor and marker GitHub usernames in submission.json."
                    )
                elif any(is_submission_placeholder(item) for item in collaborator_names):
                    pending.append(
                        "Replace the placeholder teaching-team GitHub usernames in submission.json."
                    )

    summary.extend(
        [
            "Deployment metadata:",
            f"- File: {repo_relative(submission_path, root)}",
            f"- Repo visibility: {repo_visibility_value or 'TODO'}",
            f"- Teaching-team access: {collaborator_mode or 'TODO'}",
        ]
    )
    if collaborator_names:
        summary.append("- Teaching-team GitHub usernames: " + ", ".join(collaborator_names))
    return public_app_value, blockers, warnings, pending, summary


def should_scan_submission_file(path: Path) -> bool:
    """Return whether a file should be scanned for machine-local paths."""

    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    ignored_parts = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "results",
        ".venv",
        "venv",
    }
    return not any(part in ignored_parts for part in path.parts)


def local_absolute_path_hits(target_root: Path) -> list[str]:
    """Find obvious local absolute paths inside text files under target_root."""

    hits: list[str] = []
    patterns = [
        re.compile(r"[A-Za-z]:[\\/](Users|Documents and Settings)[\\/]"),
        re.compile(r"/Users/[^/\s]+/"),
    ]
    for path in sorted(target_root.rglob("*")):
        if not path.is_file() or not should_scan_submission_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                hits.append(f"{path.relative_to(target_root).as_posix()}:{line_no}")
                break
    return hits


def resolve_app_entrypoint(
    root: Path,
    cwd: Path,
    *,
    target: str,
    entrypoint: str | None,
) -> tuple[Path, Path]:
    """Resolve the target folder and app entrypoint for submission checks."""

    target_root = ensure_within_repo(resolve_path(cwd, Path(target)), root)
    if entrypoint:
        app_entrypoint = ensure_within_repo(resolve_path(cwd, Path(entrypoint)), root)
    elif (target_root / "app" / "streamlit_app.py").exists():
        app_entrypoint = target_root / "app" / "streamlit_app.py"
    elif target_root.name == "app" and (target_root / "streamlit_app.py").exists():
        app_entrypoint = target_root / "streamlit_app.py"
        target_root = target_root.parent
    else:
        app_entrypoint = target_root / "app" / "streamlit_app.py"
    return target_root, app_entrypoint


def check_app_submission(
    root: Path,
    cwd: Path,
    *,
    target: str = ".",
    entrypoint: str | None = None,
    run_tests: bool = False,
    require_remote: bool = True,
) -> tuple[int, list[str]]:
    """Check whether a Streamlit app is ready for deployment."""

    target_root, app_entrypoint = resolve_app_entrypoint(
        root,
        cwd,
        target=target,
        entrypoint=entrypoint,
    )
    target_label = repo_relative(target_root, root)
    entrypoint_label = repo_relative(app_entrypoint, root)
    python_version = workflow_python_version(root)
    blockers: list[str] = []
    warnings: list[str] = []
    pending_fields: list[str] = []

    if not target_root.exists():
        blockers.append(f"Target folder does not exist: {target_label}")
    if not app_entrypoint.exists():
        blockers.append(f"Streamlit entrypoint does not exist: {entrypoint_label}")

    if not (root / "requirements.txt").exists():
        blockers.append("Missing root requirements.txt for Streamlit deployment.")
    if not (root / ".streamlit" / "config.toml").exists():
        blockers.append("Missing root .streamlit/config.toml.")

    inside_git = git_output(root, ["rev-parse", "--is-inside-work-tree"]) == "true"
    branch = git_output(root, ["branch", "--show-current"]) if inside_git else ""
    remote_url = git_output(root, ["remote", "get-url", "origin"]) if inside_git else ""
    commit_hash = git_output(root, ["rev-parse", "--short", "HEAD"]) if inside_git else ""
    dirty_status = git_output(root, ["status", "--short"]) if inside_git else ""

    if not inside_git:
        blockers.append("This folder is not inside a Git repository.")
    if inside_git and not branch:
        blockers.append("Git branch could not be determined.")
    if inside_git and not remote_url and require_remote:
        blockers.append("Git remote 'origin' is not configured.")
    elif inside_git and not remote_url:
        warnings.append("Git remote 'origin' is not configured yet; push before deployment.")
    if inside_git and not commit_hash:
        blockers.append("Git commit hash could not be determined.")
    if inside_git and dirty_status:
        blockers.append("Working tree is not clean; commit and push the final app first.")

    public_app_value, metadata_blockers, metadata_warnings, metadata_pending, metadata_summary = (
        validate_submission_metadata(
            root=root,
            target_root=target_root,
            target_label=target_label,
            entrypoint_label=entrypoint_label,
            branch=branch,
            remote_url=remote_url,
        )
    )
    blockers.extend(metadata_blockers)
    warnings.extend(metadata_warnings)
    pending_fields.extend(metadata_pending)

    dangerous = [path for path in tracked_files(root) if is_dangerous_tracked_path(path)]
    if dangerous:
        blockers.append("Tracked secret/environment files found: " + ", ".join(dangerous[:8]))

    if target_root.exists():
        local_hits = local_absolute_path_hits(target_root)
        if local_hits:
            blockers.append(
                "Local absolute paths found under app target: " + ", ".join(local_hits[:8])
            )

    secrets_hint = "none detected"
    if target_root.exists():
        secret_refs: list[str] = []
        for path in sorted(target_root.rglob("*.py")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "st.secrets" in text or "streamlit.secrets" in text:
                secret_refs.append(path.relative_to(target_root).as_posix())
        if secret_refs:
            secrets_hint = "app references Streamlit secrets; configure them in Cloud settings"
            warnings.append(
                "App references Streamlit secrets; configure them in Cloud and do not commit "
                "local secrets."
            )

    if run_tests:
        test_dir = target_root / "app" / "tests"
        if test_dir.exists():
            python_path = venv_python_path(root)
            python_command = str(python_path) if python_path.exists() else sys.executable
            test_report = run_command(
                [python_command, "-m", "pytest", "-q", repo_relative(test_dir, root)],
                cwd=root,
                timeout=120,
            )
            if test_report.returncode != 0:
                blockers.append("App tests failed; run pytest for details.")
        else:
            warnings.append("No app/tests folder found for optional smoke tests.")

    status_label = "BLOCKED" if blockers else "WARNINGS" if warnings else "READY"
    repo_value = remote_url or "TODO: configure GitHub remote"
    branch_value = branch or "TODO"
    commit_value = commit_hash or "TODO"

    lines = [
        "Streamlit app deployment readiness",
        f"Status: {status_label}",
        "",
        "App:",
        f"- Target: {target_label}",
        f"- Entrypoint: {entrypoint_label}",
        f"- Python version for Streamlit Cloud: {python_version}",
        f"- Secrets: {secrets_hint}",
        "",
    ]
    if metadata_summary:
        lines.extend(metadata_summary)
        lines.append("")
    lines.extend(
        [
            "Deploy on Streamlit Community Cloud:",
            f"- Repository: {repo_value}",
            f"- Branch: {branch_value}",
            f"- Main file path: {entrypoint_label}",
            f"- Python version: {python_version}",
            "- Sharing: make the Streamlit app public for grading",
            "",
            "Deployment package:",
            f"- Public Streamlit app URL: {public_app_value}",
            f"- GitHub repository URL accessible to teaching team: {repo_value}",
            f"- Branch: {branch_value}",
            f"- Entrypoint: {entrypoint_label}",
            f"- Final commit hash: {commit_value}",
            "",
            "Manual final validation:",
            "- Open the public Streamlit URL in an incognito browser.",
            "- Confirm the app loads without login and does not use localhost.",
            "- Confirm the teaching team can access the GitHub repo if it remains private.",
        ]
    )
    if blockers:
        lines.extend(["", "Blocking issues:"])
        lines.extend(f"- {issue}" for issue in blockers)
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {issue}" for issue in warnings)
    if pending_fields:
        lines.extend(["", "Pending deployment updates:"])
        lines.extend(f"- {issue}" for issue in pending_fields)
    return (1 if blockers else 0), lines


def bundle_readme_text(*, source: str, entrypoint: str, python_version: str) -> str:
    """Return the README text for a prepared app repository."""

    readiness_command = (
        "python tools/workflow.py check-app-submission"
        f" --target {source} --entrypoint {entrypoint}"
    )
    return "\n".join(
        [
            "# Streamlit App Deploy Bundle",
            "",
            "This repository is a minimal deployable app bundle prepared from the course repo.",
            "",
            "## Local Check",
            "",
            "Run from the repository root:",
            "",
            "```bash",
            readiness_command,
            "```",
            "",
            "## Local Run",
            "",
            "```bash",
            f"streamlit run {entrypoint}",
            "```",
            "",
            "Keep the terminal open while using `localhost`.",
            "",
            "## GitHub Actions",
            "",
            "This bundle includes `.github/workflows/submission-check.yml`. Every push runs",
            "the same deployment readiness gate used locally by `check-app-submission`.",
            "",
            "## Streamlit Community Cloud",
            "",
            "- Branch: `main`",
            f"- Main file path: `{entrypoint}`",
            f"- Python version: `{python_version}`",
            "- Secrets: none unless the app explicitly uses `st.secrets`",
            "",
            "Make the deployed Streamlit app public for grading. The GitHub repo may remain",
            "private if the teaching team has access.",
            "",
        ]
    )


def bundle_submission_checklist_text(*, source: str, entrypoint: str) -> str:
    """Return the root deployment checklist for a prepared app repository."""

    readiness_command = (
        "python tools/workflow.py check-app-submission"
        f" --target {source} --entrypoint {entrypoint}"
    )
    return "\n".join(
        [
            "# Streamlit Deployment Checklist",
            "",
            "## Required Deployment Fields",
            "",
            "- Public Streamlit app URL: TODO",
            "- GitHub repository URL accessible to the teaching team: TODO",
            "- Branch: `main`",
            f"- App entrypoint: `{entrypoint}`",
            "- Final commit hash: TODO",
            "",
            "## Before Hand-In",
            "",
            "- [ ] Run",
            f"  `{readiness_command}`.",
            "- [ ] Resolve every blocking issue.",
            "- [ ] Commit and push the latest code to the private GitHub repo.",
            "- [ ] Deploy on Streamlit Community Cloud.",
            "- [ ] Make the Streamlit app public for grading.",
            "- [ ] Open the public app URL in an incognito browser.",
            "- [ ] Confirm the teaching team can access the GitHub repo.",
            "",
            "A `localhost` URL is not a valid submission.",
            "",
        ]
    )


def bundle_gitignore_text() -> str:
    """Return a conservative gitignore for prepared app repositories."""

    return "\n".join(
        [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".venv/",
            "venv/",
            ".env",
            ".env.*",
            ".streamlit/secrets.toml",
            "**/.streamlit/secrets.toml",
            ".pytest_cache/",
            ".ruff_cache/",
            ".mypy_cache/",
            ".DS_Store",
            "Thumbs.db",
            "results/",
            "",
        ]
    )


def should_exclude_bundle_path(relative: Path) -> bool:
    """Return whether a relative path should be excluded from an app bundle."""

    parts = set(relative.parts)
    if parts & BUNDLE_EXCLUDED_DIRS:
        return True
    name = relative.name
    if name == ".env" or name.startswith(".env."):
        return True
    normalized = relative.as_posix()
    if normalized.endswith(".streamlit/secrets.toml"):
        return True
    return any(normalized.endswith(suffix) for suffix in BUNDLE_EXCLUDED_SUFFIXES)


def copy_filtered_tree(source: Path, destination: Path) -> None:
    """Copy a file or directory tree while omitting local/generated artifacts."""

    if source.is_file():
        if should_exclude_bundle_path(Path(source.name)):
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return

    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if should_exclude_bundle_path(relative):
            if path.is_dir():
                continue
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def should_exclude_public_release_path(relative: Path) -> bool:
    """Return whether a tracked path should stay out of the public mirror."""

    if not relative.parts:
        return True
    if relative.parts[0] not in PUBLIC_RELEASE_ALLOWED_TOP_LEVELS:
        return True
    if "_solutions" in relative.parts:
        return True
    for blocked in PUBLIC_RELEASE_BLOCKED_PATHS:
        if relative == blocked or blocked in relative.parents:
            return True
    name = relative.name
    normalized = relative.as_posix()
    return (
        name == ".env"
        or name.startswith(".env.")
        or normalized.endswith(".streamlit/secrets.toml")
    )


def copy_public_release_tree(root: Path, destination: Path) -> tuple[int, int]:
    """Copy the tracked public-release tree into destination."""

    tracked = tracked_file_set(root)
    if tracked is None:
        raise WorkflowError("public release prep requires a clean Git-tracked source repo")

    copied = 0
    skipped = 0
    for rel_path in sorted(tracked):
        relative = Path(rel_path)
        if should_exclude_public_release_path(relative):
            skipped += 1
            continue
        source = root / relative
        if not source.exists():
            skipped += 1
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
    return copied, skipped


def safe_prepare_destination(dest: Path, *, source_root: Path, force: bool) -> None:
    """Create or clear a destination directory for a prepared app repository."""

    resolved = dest.resolve()
    if resolved == source_root.resolve() or path_is_within(source_root, resolved):
        raise WorkflowError("destination cannot be the source repo or a parent of it")
    if resolved.exists() and any(resolved.iterdir()):
        if not force:
            raise WorkflowError(f"destination is not empty; use --force to replace it: {resolved}")
        for child in resolved.iterdir():
            if child.is_dir():
                shutil.rmtree(child, onexc=clear_readonly_and_retry)
            else:
                clear_readonly(child)
                child.unlink()
    resolved.mkdir(parents=True, exist_ok=True)


def clear_readonly(path: Path) -> None:
    """Make a path writable before deleting it on Windows/OneDrive."""

    with suppress(OSError):
        path.chmod(0o700 if path.is_dir() else 0o600)


def clear_readonly_and_retry(function, path: str, excinfo) -> None:
    """Retry shutil.rmtree after clearing read-only attributes."""

    del excinfo
    target = Path(path)
    clear_readonly(target)
    function(path)


def copy_app_bundle(
    root: Path,
    *,
    source_root: Path,
    destination: Path,
    source_label: str,
    entrypoint_label: str,
    repo_name: str = "",
) -> None:
    """Copy the minimal deployable app bundle into destination."""

    required_files = [
        Path("requirements.txt"),
        Path("requirements-dev.txt"),
        Path(".python-version"),
        Path(".streamlit/config.toml"),
        Path("tools/__init__.py"),
        Path("tools/workflow.py"),
        Path("tools/workflow_lib.py"),
        Path(".github/workflows/submission-check.yml"),
    ]
    for relative in required_files:
        source = root / relative
        if not source.exists():
            raise WorkflowError(f"required bundle file is missing: {relative.as_posix()}")
        copy_filtered_tree(source, destination / relative)

    requirements_dev_path = destination / "requirements-dev.txt"
    if requirements_dev_path.exists():
        write_text(
            requirements_dev_path,
            sanitize_bundle_requirements_dev(read_text(requirements_dev_path)),
        )

    for relative in [Path("fintools"), Path("docs/apps/streamlit")]:
        source = root / relative
        if source.exists():
            copy_filtered_tree(source, destination / relative)

    copy_filtered_tree(source_root, destination / source_label)

    python_version = workflow_python_version(root)
    write_text(
        destination / "README.md",
        bundle_readme_text(
            source=source_label,
            entrypoint=entrypoint_label,
            python_version=python_version,
        ),
    )
    write_text(
        destination / "SUBMISSION_CHECKLIST.md",
        bundle_submission_checklist_text(source=source_label, entrypoint=entrypoint_label),
    )
    write_text(
        destination / ".github" / "workflows" / "submission-check.yml",
        submission_check_workflow_text(target=source_label, entrypoint=entrypoint_label),
    )
    write_text(destination / ".gitignore", bundle_gitignore_text())


def require_success(report: CommandReport, *, action: str) -> None:
    """Raise a workflow error if a subprocess report failed."""

    if report.returncode == 0:
        return
    detail = report.stderr.strip() or report.stdout.strip()
    if detail:
        raise WorkflowError(f"{action} failed: {detail}")
    raise WorkflowError(f"{action} failed")


def initialize_prepared_git_repo(
    destination: Path,
    *,
    commit_message: str = "Prepare Streamlit app deploy bundle",
) -> str:
    """Initialize and commit a prepared app repository."""

    require_success(git_report(destination, ["init"]), action="git init")
    require_success(git_report(destination, ["branch", "-M", "main"]), action="git branch")
    if not git_output(destination, ["config", "user.email"]):
        require_success(
            git_report(destination, ["config", "user.email", "fins-agent@example.invalid"]),
            action="git config user.email",
        )
    if not git_output(destination, ["config", "user.name"]):
        require_success(
            git_report(destination, ["config", "user.name", "fins-agent"]),
            action="git config user.name",
        )
    require_success(git_report(destination, ["add", "-A", "--force"]), action="git add")
    require_success(
        git_report(destination, ["commit", "-m", commit_message]),
        action="git commit",
    )
    return git_output(destination, ["rev-parse", "--short", "HEAD"])


def prepare_public_repo(
    root: Path,
    cwd: Path,
    *,
    dest: str,
    force: bool = False,
    init_git: bool = False,
) -> tuple[int, list[str]]:
    """Prepare a fresh-history student-facing public mirror from the private repo."""

    destination = resolve_path(cwd, Path(dest))
    safe_prepare_destination(destination, source_root=root, force=force)
    copied, skipped = copy_public_release_tree(root, destination)

    audit_status, audit_lines = audit_public_release_tree(destination)
    if audit_status != 0:
        return audit_status, audit_lines

    commit_hash = ""
    if init_git:
        commit_hash = initialize_prepared_git_repo(
            destination,
            commit_message="Prepare public student release",
        )

    lines = [
        "Prepared public student release",
        f"- Source: {root}",
        f"- Destination: {destination}",
        f"- Copied tracked files: {copied}",
        f"- Skipped tracked files: {skipped}",
        f"- Published weeks: {PUBLISHED_WEEK_NAMES[0]} through {PUBLISHED_WEEK_NAMES[-1]}",
    ]
    if init_git:
        lines.append("- Git history: fresh local repository initialized")
        lines.append(f"- Local commit: {commit_hash}")
    lines.extend(["", *audit_lines])
    return 0, lines


def push_prepared_app_repo(destination: Path, *, repo: str) -> tuple[int, list[str]]:
    """Create a private GitHub repo and push a prepared bundle when gh is ready."""

    if not shutil.which("gh"):
        return 1, [
            "GitHub push skipped: GitHub CLI is not installed.",
            "Install GitHub CLI or create a private repo manually, then push this folder.",
        ]
    auth = run_command(["gh", "auth", "status", "-h", "github.com"], cwd=destination, timeout=30)
    if auth.returncode != 0:
        return 1, [
            "GitHub push skipped: GitHub CLI is not authenticated.",
            "Run `gh auth login -h github.com`, then rerun with `--push`.",
        ]
    existing = run_command(
        ["gh", "repo", "view", repo, "--json", "sshUrl", "--jq", ".sshUrl"],
        cwd=destination,
        timeout=30,
    )
    if existing.returncode == 0 and existing.stdout.strip():
        remote_url = existing.stdout.strip()
        run_command(["git", "remote", "remove", "origin"], cwd=destination, timeout=30)
        require_success(
            git_report(destination, ["remote", "add", "origin", remote_url]),
            action="git remote add origin",
        )
        require_success(
            git_report(destination, ["push", "-u", "--force", "origin", "main"]),
            action="git push",
        )
        return 0, ["Pushed `main` to existing private GitHub repo with GitHub CLI."]
    create = run_command(
        [
            "gh",
            "repo",
            "create",
            repo,
            "--private",
            "--source",
            str(destination),
            "--remote",
            "origin",
            "--push",
        ],
        cwd=destination,
        timeout=180,
    )
    if create.returncode != 0:
        detail = create.stderr.strip() or create.stdout.strip()
        return 1, [f"GitHub private repo creation/push failed: {detail}"]
    return 0, ["Created private GitHub repo and pushed `main` with GitHub CLI."]


def prepare_app_repo(
    root: Path,
    cwd: Path,
    *,
    source: str,
    dest: str,
    repo: str = "",
    entrypoint: str | None = None,
    push: bool = False,
    force: bool = False,
) -> tuple[int, list[str]]:
    """Prepare a minimal private-repo bundle for Streamlit app deployment."""

    source_root, app_entrypoint = resolve_app_entrypoint(
        root,
        cwd,
        target=source,
        entrypoint=entrypoint,
    )
    if not source_root.exists():
        raise WorkflowError(f"source folder does not exist: {source_root}")
    if not app_entrypoint.exists():
        raise WorkflowError(f"entrypoint does not exist: {app_entrypoint}")

    destination = resolve_path(cwd, Path(dest))
    safe_prepare_destination(destination, source_root=root, force=force)

    source_label = repo_relative(source_root, root)
    entrypoint_label = repo_relative(app_entrypoint, root)
    repo_name = repo or destination.name
    copy_app_bundle(
        root,
        source_root=source_root,
        destination=destination,
        source_label=source_label,
        entrypoint_label=entrypoint_label,
        repo_name=repo_name,
    )
    commit_hash = initialize_prepared_git_repo(destination)

    readiness_status, readiness_lines = check_app_submission(
        destination,
        destination,
        target=source_label,
        entrypoint=entrypoint_label,
        require_remote=push,
    )
    push_status = 0
    push_lines: list[str] = []
    if push:
        push_status, push_lines = push_prepared_app_repo(destination, repo=repo_name)
        if push_status == 0:
            readiness_status, readiness_lines = check_app_submission(
                destination,
                destination,
                target=source_label,
                entrypoint=entrypoint_label,
                require_remote=True,
            )

    lines = [
        "Prepared Streamlit app deploy repository",
        f"- Destination: {destination}",
        f"- Source: {source_label}",
        f"- Entrypoint: {entrypoint_label}",
        "- Branch: main",
        f"- Local commit: {commit_hash}",
        f"- GitHub repo name: {repo_name}",
        "",
    ]
    if push_lines:
        lines.extend(["GitHub push:", *[f"- {line}" for line in push_lines], ""])
    lines.extend(readiness_lines)
    if push and push_status != 0:
        return 1, lines
    return readiness_status, lines


def dataset_sample_label(data_index: object) -> str:
    """Return a compact sample-period label for a datetime-like index."""

    try:
        start = data_index.min()
        end = data_index.max()
    except AttributeError:
        return ""
    if hasattr(start, "strftime") and hasattr(end, "strftime"):
        return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
    return ""


def build_figure_examples(
    root: Path,
    cwd: Path,
    *,
    output: str | None = None,
    docx: bool = False,
    style: str = "fins",
    ft_background: bool = False,
    plotly_demo: bool = False,
) -> tuple[int, list[str]]:
    """Generate a small set of validation figures with the public toolkit."""

    if style not in {"fins", "ft"}:
        raise WorkflowError("figure style must be one of: fins, ft")

    output_path = resolve_path(cwd, Path(output or "results/figures"))
    output_path = ensure_within_repo(output_path, root)

    try:
        import matplotlib

        matplotlib.use("Agg", force=False)
        import matplotlib.pyplot as plt
        import pandas as pd

        from fintools.datasets import load_validation_dataset
        from fintools.figures import (
            FigureContext,
            WordFigureEntry,
            area_balance_plot,
            bubble_scatter_plot,
            calendar_heatmap,
            correlation_heatmap,
            cumulative_returns_plot,
            distribution_comparison_plot,
            distribution_plot,
            diverging_bar_plot,
            dumbbell_plot,
            ecdf_plot,
            export_figure_bundle,
            export_word_figure,
            indexed_time_series_plot,
            insert_figures_docx,
            lollipop_plot,
            mean_return_bar_plot,
            proportional_stacked_bar_plot,
            rolling_stat_plot,
            scatter_plot,
            slope_chart,
            small_multiples,
            stacked_bar_plot,
            time_series_plot,
            uncertainty_band_plot,
            validate_category_label_count,
            validate_display_labels,
            validate_docx_images_fit_page,
            validate_image_not_blank,
            validate_markers_within_axes,
            validate_no_text_overlap,
            validate_no_tick_label_overlap,
            validate_series_identification,
            validate_unique_series_colors,
            value_heatmap,
        )
    except ImportError as exc:
        raise WorkflowError(
            "figure dependencies are missing; reinstall with the repo interpreter and "
            "-m pip install -r requirements.txt -r requirements-dev.txt"
        ) from exc

    stem_prefix = "validation" if style == "fins" else "ft_validation"
    docx_name = "validation_figures.docx" if style == "fins" else "validation_figures_ft.docx"
    docx_title = (
        "Validation Figure Examples"
        if style == "fins"
        else "FT-Style Validation Figure Examples"
    )

    base_gallery_stems = {
        "factor_stacked_returns",
        "ff25_distribution_by_value",
        "ff25_mean_heatmap",
        "ff3_full_cumulative",
        "ff3_full_returns",
        "industry_correlations",
        "industry_ecdf",
        "industry_excess_diverging",
        "industry_mean_returns",
        "industry_small_multiples",
        "macro_indexed",
        "macro_scatter_fit",
        "market_cumulative",
        "market_return_distribution",
        "shiller_cape",
        "shiller_real_market",
        "stress_calendar_heatmap",
        "stress_rolling",
        "stress_uncertainty_band",
        "treasury_rates",
        "world_bank_bubble",
        "world_bank_gdp_per_capita_dumbbell",
        "world_bank_gdp_share_stacked",
        "yield_spreads",
    }
    if style == "ft":
        base_gallery_stems.update(
            {
                "macro_policy_episode",
                "world_bank_gdp_lollipop",
                "world_bank_gdp_slope",
                "yield_spread_deviation",
            }
        )
    if plotly_demo and style == "ft":
        base_gallery_stems.add("plotly_gdp_bar")

    gallery_stems = {f"{stem_prefix}_{name}" for name in base_gallery_stems}

    def output_stem(name: str) -> str:
        return f"{stem_prefix}_{name}"

    def gallery_stem(path: Path) -> str:
        if path.name.endswith(".caption.md"):
            return path.name.removesuffix(".caption.md")
        return path.stem

    output_path.mkdir(parents=True, exist_ok=True)
    stale_pattern = "validation_*" if style == "fins" else "ft_validation_*"
    for stale_path in output_path.glob(stale_pattern):
        if stale_path.name == docx_name:
            continue
        if stale_path.suffix == ".docx" or gallery_stem(stale_path) not in gallery_stems:
            stale_path.unlink(missing_ok=True)

    generated: list[Path] = []
    docx_entries: list[WordFigureEntry] = []
    notes: list[str] = []

    def emit(
        fig: object,
        stem: str,
        context: FigureContext,
        *,
        spec: str = "full_width",
        pdf: bool = True,
        unique_series_colors: int | None = None,
    ) -> None:
        bundle = export_word_figure(fig, output_path, stem, context=context, spec=spec)
        if pdf:
            bundle.update(export_figure_bundle(fig, output_path, stem, formats=("pdf",)))
        issues = validate_image_not_blank(bundle["png"])
        if issues:
            details = "; ".join(issue.message for issue in issues)
            raise WorkflowError(f"generated figure failed image validation: {stem}: {details}")
        rendered_issues = []
        for axis in getattr(fig, "axes", []):
            rendered_issues.extend(validate_display_labels(axis))
            rendered_issues.extend(validate_markers_within_axes(axis))
            rendered_issues.extend(validate_no_text_overlap(axis))
            rendered_issues.extend(validate_no_tick_label_overlap(axis))
            rendered_issues.extend(validate_no_tick_label_overlap(axis, axis="y"))
            rendered_issues.extend(validate_category_label_count(axis))
            rendered_issues.extend(validate_category_label_count(axis, axis="y"))
            rendered_issues.extend(validate_series_identification(axis))
            if unique_series_colors is not None:
                rendered_issues.extend(
                    validate_unique_series_colors(axis, minimum=unique_series_colors)
                )
        if rendered_issues:
            details = "; ".join(issue.message for issue in rendered_issues)
            raise WorkflowError(f"generated figure failed rendered validation: {stem}: {details}")
        generated.extend(bundle.values())
        if docx:
            docx_entries.append(WordFigureEntry(bundle["png"], context=context, spec=spec))

    ff3 = load_validation_dataset("ff3_monthly")
    ff25 = load_validation_dataset("ff25_size_value_monthly")
    industries = load_validation_dataset("ff_industry_10_monthly")
    macro = load_validation_dataset("fred_macro_monthly")
    rates = load_validation_dataset("fred_rates_daily")
    stress = load_validation_dataset("fred_financial_stress_daily")
    shiller = load_validation_dataset("shiller_market_monthly")
    gdp_panel = load_validation_dataset("world_bank_country_panel_annual")
    gdp = load_validation_dataset("world_bank_gdp_annual") if style == "ft" else None
    plot_kwargs = {"profile": "word_a4", "style": style, "ft_background": ft_background}

    context = FigureContext(
        title="Full-Sample Fama/French Factor Returns",
        note=(
            "Monthly market, size, and value factor returns over the full available"
            " sample. Gray bands denote NBER recessions."
        ),
        source=ff3.source,
        sample=dataset_sample_label(ff3.data.index),
        units="Monthly return (%)",
    )
    fig, _ = time_series_plot(
        ff3.data,
        ["Mkt-RF", "SMB", "HML"],
        title=context.title,
        ylabel="Monthly return (%)",
        **plot_kwargs,
    )
    emit(fig, output_stem("ff3_full_returns"), context)
    plt.close(fig)

    context = FigureContext(
        title="Full-Sample Fama/French Growth Of One Dollar",
        note=(
            "Growth of one dollar from monthly market, size, and value factor"
            " returns, shown on a log scale so all factors remain inspectable."
        ),
        source=ff3.source,
        sample=dataset_sample_label(ff3.data.index),
        units="Growth of one dollar, log scale",
    )
    fig, _ = cumulative_returns_plot(
        ff3.data,
        ["Mkt-RF", "SMB", "HML"],
        returns_are_percent=True,
        wealth_index=True,
        log_scale=True,
        title=context.title,
        **plot_kwargs,
    )
    emit(fig, output_stem("ff3_full_cumulative"), context)
    plt.close(fig)

    context = FigureContext(
        title="Cumulative Market Excess Return",
        note=(
            "Growth of one dollar from monthly Fama/French market excess returns,"
            " shown on a log scale with dollar values on the y-axis."
        ),
        source=ff3.source,
        sample=dataset_sample_label(ff3.data.index),
        units="Growth of one dollar, log scale",
    )
    fig, _ = cumulative_returns_plot(
        ff3.data,
        "Mkt-RF",
        returns_are_percent=True,
        wealth_index=True,
        log_scale=True,
        title=context.title,
        **plot_kwargs,
    )
    emit(fig, output_stem("market_cumulative"), context)
    plt.close(fig)

    context = FigureContext(
        title="Indexed Macro Activity Series",
        note=(
            "Industrial production, payroll employment, and CPI are indexed to each"
            " series' first non-missing observation so different units can be compared."
        ),
        source=macro.source,
        sample=dataset_sample_label(macro.data.index),
        units="Index, first observation = 100",
    )
    fig, _ = indexed_time_series_plot(
        macro.data,
        ["INDPRO", "PAYEMS", "CPIAUCSL"],
        title=context.title,
        ylabel="Index",
        **plot_kwargs,
    )
    emit(fig, output_stem("macro_indexed"), context)
    plt.close(fig)

    context = FigureContext(
        title="Treasury Rates Across Maturities",
        note=(
            "Daily 10-year, 2-year, and 3-month Treasury rates. Missing early"
            " observations are trimmed only when all requested series are missing."
        ),
        source=rates.source,
        sample=dataset_sample_label(rates.data.index),
        units="Percent",
    )
    fig, _ = time_series_plot(
        rates.data,
        ["DGS10", "DGS2", "DTB3"],
        title=context.title,
        ylabel="Percent",
        **plot_kwargs,
    )
    emit(fig, output_stem("treasury_rates"), context)
    plt.close(fig)

    context = FigureContext(
        title="Yield-Curve Spread Validation Series",
        note=(
            "Daily 10-year minus 2-year and 10-year minus 3-month Treasury spreads."
            " The zero line helps identify inversions."
        ),
        source=rates.source,
        sample=dataset_sample_label(rates.data.index),
        units="Percentage points",
    )
    fig, ax = time_series_plot(
        rates.data,
        ["T10Y2Y", "T10Y3M"],
        title=context.title,
        ylabel="Percentage points",
        **plot_kwargs,
    )
    ax.axhline(0, color="#111827", linewidth=0.8)
    emit(fig, output_stem("yield_spreads"), context)
    plt.close(fig)

    context = FigureContext(
        title="Shiller Real Market Fundamentals",
        note=(
            "Inflation-adjusted price, dividend, and earnings series indexed to the"
            " first non-missing observation in Robert Shiller's long market dataset."
        ),
        source=shiller.source,
        sample=dataset_sample_label(shiller.data.index),
        units="Index, first observation = 100",
    )
    fig, _ = indexed_time_series_plot(
        shiller.data,
        ["real_price", "real_dividend", "real_earnings"],
        title=context.title,
        ylabel="Index",
        **plot_kwargs,
    )
    emit(fig, output_stem("shiller_real_market"), context)
    plt.close(fig)

    context = FigureContext(
        title="Shiller CAPE Ratio",
        note="Cyclically adjusted price-earnings ratio from the long Shiller workbook.",
        source=shiller.source,
        sample=dataset_sample_label(shiller.data["cape"].dropna().index),
        units="Price divided by 10-year average real earnings",
    )
    fig, _ = time_series_plot(
        shiller.data,
        "cape",
        title=context.title,
        ylabel="CAPE",
        **plot_kwargs,
    )
    emit(fig, output_stem("shiller_cape"), context)
    plt.close(fig)

    context = FigureContext(
        title="Mean Industry Returns With Standard Errors",
        note=(
            "Mean monthly returns across 10 industry portfolios. Error bars are"
            " standard errors of the monthly mean."
        ),
        source=industries.source,
        sample=dataset_sample_label(industries.data.index),
        units="Mean monthly return (%)",
    )
    fig, _, _ = mean_return_bar_plot(
        industries.data,
        industries.data.columns,
        title=context.title,
        ylabel="Mean monthly return (%)",
        error="se",
        **plot_kwargs,
    )
    emit(fig, output_stem("industry_mean_returns"), context)
    plt.close(fig)

    context = FigureContext(
        title="Fama/French Factor Return Composition",
        note=(
            "Stacked monthly returns for the market, size, and value factors over"
            " the latest 24 months. Positive and negative values are stacked separately."
        ),
        source=ff3.source,
        sample=dataset_sample_label(ff3.data.tail(24).index),
        units="Monthly return (%)",
    )
    fig, _ = stacked_bar_plot(
        ff3.data,
        ["Mkt-RF", "SMB", "HML"],
        title=context.title,
        ylabel="Monthly return (%)",
        max_bars=24,
        **plot_kwargs,
    )
    emit(fig, output_stem("factor_stacked_returns"), context)
    plt.close(fig)

    scatter_frame = macro.data[["FEDFUNDS", "UNRATE"]].dropna()
    context = FigureContext(
        title="Federal Funds Rate And Unemployment",
        note=(
            "Scatter plot with fitted line, slope, R-squared, sample size, and"
            " labels for the most unusual months."
        ),
        source=macro.source,
        sample=dataset_sample_label(scatter_frame.index),
        units="Percent",
    )
    fig, _ = scatter_plot(
        scatter_frame,
        "FEDFUNDS",
        "UNRATE",
        fit=True,
        label_outliers=4,
        stats_location="lower right",
        title=context.title,
        xlabel="Federal funds rate (%)",
        ylabel="Unemployment rate (%)",
        **plot_kwargs,
    )
    emit(fig, output_stem("macro_scatter_fit"), context)
    plt.close(fig)

    context = FigureContext(
        title="Distribution Of Market Excess Returns",
        note="Histogram and kernel density estimate for monthly market excess returns.",
        source=ff3.source,
        sample=dataset_sample_label(ff3.data.index),
        units="Monthly return (%)",
    )
    fig, _ = distribution_plot(
        ff3.data.reset_index(),
        "Mkt-RF",
        title=context.title,
        **plot_kwargs,
    )
    emit(fig, output_stem("market_return_distribution"), context)
    plt.close(fig)

    context = FigureContext(
        title="Industry Return Correlations",
        note="Pairwise correlations across monthly 10-industry portfolio returns.",
        source=industries.source,
        sample=dataset_sample_label(industries.data.index),
        units="Correlation",
    )
    fig, _ = correlation_heatmap(industries.data, title=context.title, **plot_kwargs)
    emit(fig, output_stem("industry_correlations"), context, spec="two_panel")
    plt.close(fig)

    context = FigureContext(
        title="Selected Industry Return Small Multiples",
        note=(
            "Small-multiple time-series view for four industry portfolios. Each"
            " panel uses the same reusable time-series styling rules."
        ),
        source=industries.source,
        sample=dataset_sample_label(industries.data.index),
        units="Monthly return (%)",
    )
    fig, _ = small_multiples(
        industries.data,
        ["NoDur", "Durbl", "HiTec", "Utils"],
        title=context.title,
        ylabel="Return (%)",
        **plot_kwargs,
    )
    emit(fig, output_stem("industry_small_multiples"), context, spec="two_panel")
    plt.close(fig)

    ff25_size_labels = ["Small", "2", "3", "4", "Big"]
    ff25_value_labels = ["Low BM", "2", "3", "4", "High BM"]
    ff25_records = []
    ff25_long_parts = []
    for position, column in enumerate(ff25.data.columns):
        size_label = ff25_size_labels[position // 5]
        value_label = ff25_value_labels[position % 5]
        ff25_records.append(
            {
                "size": size_label,
                "value": value_label,
                "mean_return": float(ff25.data[column].mean()),
            }
        )
        long_part = ff25.data[column].rename("return").reset_index()
        long_part["size"] = size_label
        long_part["value"] = value_label
        long_part["portfolio"] = str(column)
        ff25_long_parts.append(long_part)
    ff25_mean_frame = pd.DataFrame.from_records(ff25_records)
    ff25_long_frame = pd.concat(ff25_long_parts, ignore_index=True)

    context = FigureContext(
        title="Average Returns Across Size-Value Portfolios",
        note=(
            "Heatmap of average monthly returns for the 25 Fama/French portfolios"
            " formed on size and book-to-market."
        ),
        source=ff25.source,
        sample=dataset_sample_label(ff25.data.index),
        units="Mean monthly return (%)",
    )
    fig, _ = value_heatmap(
        ff25_mean_frame,
        "size",
        "value",
        "mean_return",
        title=context.title,
        cbar_label="Mean monthly return (%)",
        fmt=".2f",
        **plot_kwargs,
    )
    emit(fig, output_stem("ff25_mean_heatmap"), context, spec="two_panel")
    plt.close(fig)

    context = FigureContext(
        title="Return Distributions By Value Quintile",
        note=(
            "Distribution comparison for Fama/French 25 portfolios grouped by"
            " book-to-market quintile."
        ),
        source=ff25.source,
        sample=dataset_sample_label(ff25.data.index),
        units="Monthly return (%)",
    )
    fig, _ = distribution_comparison_plot(
        ff25_long_frame,
        "return",
        "value",
        title=context.title,
        ylabel="Monthly return (%)",
        kind="box",
        order=ff25_value_labels,
        **plot_kwargs,
    )
    emit(fig, output_stem("ff25_distribution_by_value"), context)
    plt.close(fig)

    industry_excess = (
        industries.data.mean()
        .sub(float(ff3.data["Mkt-RF"].mean()))
        .rename("excess_mean")
        .reset_index()
        .rename(columns={"index": "industry"})
    )
    context = FigureContext(
        title="Industry Mean Returns Relative To The Market",
        note=(
            "Diverging bar chart of average industry returns relative to the"
            " average Fama/French market excess return."
        ),
        source=f"{industries.source}; {ff3.source}",
        sample=dataset_sample_label(industries.data.index),
        units="Monthly return spread (%)",
    )
    fig, _ = diverging_bar_plot(
        industry_excess,
        "industry",
        "excess_mean",
        title=context.title,
        xlabel="Mean return spread versus market (%)",
        **plot_kwargs,
    )
    emit(fig, output_stem("industry_excess_diverging"), context)
    plt.close(fig)

    context = FigureContext(
        title="Cumulative Distribution Of Selected Industry Returns",
        note=(
            "Empirical cumulative distribution curves for selected monthly"
            " industry portfolio returns."
        ),
        source=industries.source,
        sample=dataset_sample_label(industries.data.index),
        units="Monthly return (%)",
    )
    fig, _ = ecdf_plot(
        industries.data,
        ["NoDur", "HiTec", "Enrgy"],
        title=context.title,
        xlabel="Monthly return (%)",
        **plot_kwargs,
    )
    emit(fig, output_stem("industry_ecdf"), context)
    plt.close(fig)

    gdp_panel_frame = gdp_panel.data.reset_index()
    gdp_panel_frame["year"] = gdp_panel_frame["date"].dt.year
    latest_panel = gdp_panel_frame[gdp_panel_frame["year"] == 2024].copy()

    gdp_per_capita = (
        gdp_panel_frame[gdp_panel_frame["year"].isin([2010, 2024])]
        .pivot(index="country", columns="year", values="gdp_per_capita_usd")
        .reset_index()
        .rename(columns={2010: "gdp_pc_2010", 2024: "gdp_pc_2024"})
    )
    context = FigureContext(
        title="GDP Per Capita Change Across Major Economies",
        note="Dumbbell chart comparing GDP per capita in 2010 and 2024.",
        source=gdp_panel.source,
        sample="2010 to 2024",
        units="Current U.S. dollars per person",
    )
    fig, _ = dumbbell_plot(
        gdp_per_capita,
        "country",
        "gdp_pc_2010",
        "gdp_pc_2024",
        title=context.title,
        xlabel="GDP per capita (current U.S. dollars)",
        start_label="2010",
        end_label="2024",
        limit=8,
        **plot_kwargs,
    )
    emit(fig, output_stem("world_bank_gdp_per_capita_dumbbell"), context)
    plt.close(fig)

    top_share_countries = (
        latest_panel.sort_values("gdp_current_usd", ascending=False)
        .head(6)["country"]
        .tolist()
    )
    share_frame = gdp_panel_frame[
        gdp_panel_frame["year"].isin([2010, 2024])
        & gdp_panel_frame["country"].isin(top_share_countries)
    ].copy()
    context = FigureContext(
        title="GDP Share Among Major Economies",
        note=(
            "Proportional stacked bars compare country shares among the six largest"
            " economies in the validation panel."
        ),
        source=gdp_panel.source,
        sample="2010 and 2024",
        units="Share of GDP among selected economies",
    )
    fig, _ = proportional_stacked_bar_plot(
        share_frame,
        "year",
        "country",
        "gdp_current_usd",
        title=context.title,
        ylabel="Share of selected-economy GDP",
        **plot_kwargs,
    )
    emit(fig, output_stem("world_bank_gdp_share_stacked"), context)
    plt.close(fig)

    context = FigureContext(
        title="Population, Income, And GDP Scale",
        note=(
            "Bubble scatterplot using population on the x-axis, GDP per capita on"
            " the y-axis, and total GDP as bubble size. Labels identify the largest"
            " economies by total GDP in the plotted year."
        ),
        source=gdp_panel.source,
        sample="2024",
        units="Population, GDP per capita, and GDP",
    )
    fig, _ = bubble_scatter_plot(
        latest_panel,
        "population_millions",
        "gdp_per_capita_usd",
        "gdp_trillions_usd",
        label="country",
        label_top=4,
        title=context.title,
        xlabel="Population (millions)",
        ylabel="GDP per capita (current U.S. dollars)",
        size_label="GDP (trillions of current U.S. dollars)",
        **plot_kwargs,
    )
    emit(fig, output_stem("world_bank_bubble"), context)
    plt.close(fig)

    stress_frame = stress.data.dropna(how="all")
    context = FigureContext(
        title="Daily VIX Calendar Heatmap During 2020",
        note="Calendar heatmap showing daily VIX levels during the 2020 stress episode.",
        source=stress.source,
        sample="2020",
        units="VIX index",
    )
    fig, _ = calendar_heatmap(
        stress_frame,
        "VIXCLS",
        year=2020,
        title=context.title,
        cbar_label="VIX index",
        **plot_kwargs,
    )
    emit(fig, output_stem("stress_calendar_heatmap"), context, spec="two_panel")
    plt.close(fig)

    context = FigureContext(
        title="Rolling Financial Stress Volatility",
        note="Rolling 21-trading-day volatility of daily VIX levels.",
        source=stress.source,
        sample=dataset_sample_label(stress_frame["VIXCLS"].dropna().index),
        units="VIX index points",
    )
    fig, _ = rolling_stat_plot(
        stress_frame,
        "VIXCLS",
        window=21,
        statistic="volatility",
        title=context.title,
        ylabel="21-day rolling standard deviation",
        **plot_kwargs,
    )
    emit(fig, output_stem("stress_rolling"), context)
    plt.close(fig)

    vix = stress_frame["VIXCLS"].dropna()
    rolling_mean = vix.rolling(window=63, min_periods=21).mean()
    rolling_std = vix.rolling(window=63, min_periods=21).std()
    band_frame = pd.DataFrame(
        {
            "rolling_mean": rolling_mean,
            "lower": (rolling_mean - rolling_std).clip(lower=0),
            "upper": rolling_mean + rolling_std,
        }
    ).dropna()
    context = FigureContext(
        title="VIX Rolling Mean With Uncertainty Band",
        note=(
            "Rolling 63-trading-day mean with a one-standard-deviation band,"
            " using daily VIX observations."
        ),
        source=stress.source,
        sample=dataset_sample_label(band_frame.index),
        units="VIX index",
    )
    fig, _ = uncertainty_band_plot(
        band_frame,
        "rolling_mean",
        "lower",
        "upper",
        title=context.title,
        ylabel="VIX index",
        **plot_kwargs,
    )
    emit(fig, output_stem("stress_uncertainty_band"), context)
    plt.close(fig)

    if style == "ft" and gdp is not None:
        gdp_frame = gdp.data.reset_index()
        gdp_frame["year"] = gdp_frame["date"].dt.year
        latest_gdp = gdp_frame[gdp_frame["year"] == 2024].copy()

        context = FigureContext(
            title="Largest Economies In Current U.S. Dollars",
            note=(
                "Ranked lollipop chart using World Bank annual GDP data. The United"
                " States, China, and India are highlighted; other economies are muted"
                " comparison points."
            ),
            source=gdp.source,
            sample="2024",
            units="Trillions of current U.S. dollars",
        )
        fig, _ = lollipop_plot(
            latest_gdp,
            "country",
            "gdp_trillions_usd",
            title=context.title,
            xlabel="GDP (trillions of current U.S. dollars)",
            ylabel="Country",
            limit=10,
            highlight=["United States", "China", "India"],
            **plot_kwargs,
        )
        emit(fig, output_stem("world_bank_gdp_lollipop"), context)
        plt.close(fig)

        slope_frame = (
            gdp_frame.pivot(index="country", columns="year", values="gdp_trillions_usd")
            .reset_index()
            .rename(columns={2010: "gdp_2010", 2024: "gdp_2024"})
        )
        context = FigureContext(
            title="GDP Rankings Shifted Over The 2010s And 2020s",
            note=(
                "Slope chart comparing 2010 and 2024 GDP for the eight largest"
                " economies in the validation fixture by 2024 GDP."
            ),
            source=gdp.source,
            sample="2010 to 2024",
            units="Trillions of current U.S. dollars",
        )
        fig, _ = slope_chart(
            slope_frame,
            "country",
            "gdp_2010",
            "gdp_2024",
            title=context.title,
            ylabel="GDP (trillions of current U.S. dollars)",
            start_label="2010",
            end_label="2024",
            limit=8,
            **plot_kwargs,
        )
        emit(
            fig,
            output_stem("world_bank_gdp_slope"),
            context,
            spec="portrait_tall",
            unique_series_colors=8,
        )
        plt.close(fig)

        policy_frame = macro.data[["FEDFUNDS", "UNRATE"]].dropna().loc["2007":"2012"]
        context = FigureContext(
            title="Policy Rates And Unemployment During The Financial Crisis",
            note=(
                "Monthly time-series view of the federal funds rate and unemployment"
                " during and after the 2007-2009 financial crisis. Gray bands denote"
                " NBER recessions."
            ),
            source=macro.source,
            sample=dataset_sample_label(policy_frame.index),
            units="Percent",
        )
        fig, _ = time_series_plot(
            policy_frame,
            ["FEDFUNDS", "UNRATE"],
            title=context.title,
            ylabel="Percent",
            **plot_kwargs,
        )
        emit(fig, output_stem("macro_policy_episode"), context)
        plt.close(fig)

        spread_frame = rates.data[["T10Y2Y"]].dropna()
        context = FigureContext(
            title="Yield-Curve Inversions Against Zero",
            note=(
                "Deviation-style area chart for the 10-year minus 2-year Treasury"
                " spread. Values below zero indicate inversions."
            ),
            source=rates.source,
            sample=dataset_sample_label(spread_frame.index),
            units="Percentage points",
        )
        fig, _ = area_balance_plot(
            spread_frame,
            "T10Y2Y",
            title=context.title,
            ylabel="Percentage points",
            **plot_kwargs,
        )
        emit(fig, output_stem("yield_spread_deviation"), context)
        plt.close(fig)

        if plotly_demo:
            context = FigureContext(
                title="Plotly FT-Style GDP Bar Demo",
                note=(
                    "Optional Plotly export example using the same World Bank GDP"
                    " fixture. This is skipped when Plotly, Kaleido, or Chrome is"
                    " unavailable."
                ),
                source=gdp.source,
                sample="2024",
                units="Trillions of current U.S. dollars",
            )
            try:
                import plotly.express as px

                from fintools.figures import apply_ft_plotly_layout, export_plotly_image

                plotly_frame = latest_gdp.sort_values(
                    "gdp_trillions_usd",
                    ascending=False,
                ).head(8)
                plotly_fig = px.bar(
                    plotly_frame,
                    x="country",
                    y="gdp_trillions_usd",
                    color="country",
                    labels={"gdp_trillions_usd": "GDP, current US$ trillions"},
                )
                apply_ft_plotly_layout(
                    plotly_fig,
                    title=context.title,
                    ft_background=ft_background,
                    showlegend=False,
                )
                plotly_path = export_plotly_image(
                    plotly_fig,
                    output_path / f"{output_stem('plotly_gdp_bar')}.png",
                )
                issues = validate_image_not_blank(plotly_path)
                if issues:
                    details = "; ".join(issue.message for issue in issues)
                    raise WorkflowError(
                        f"generated Plotly figure failed image validation: {details}"
                    )
                generated.append(plotly_path)
                if docx:
                    docx_entries.append(WordFigureEntry(plotly_path, context=context))
            except Exception as exc:
                notes.append(f"Skipped optional Plotly demo: {exc}")

    if docx:
        docx_path = insert_figures_docx(
            docx_entries,
            output_path / docx_name,
            title=docx_title,
        )
        issues = validate_docx_images_fit_page(docx_path)
        if issues:
            details = "; ".join(issue.message for issue in issues)
            raise WorkflowError(f"generated Word proof pack failed validation: {details}")
        generated.append(docx_path)

    lines = [f"Generated {style} validation figures in: {output_path.relative_to(root)}"]
    lines.extend(notes)
    lines.append("Files:")
    lines.extend(f"- {path.relative_to(root)}" for path in generated)
    return 0, lines


def build_figure_suite(
    root: Path,
    cwd: Path,
    *,
    input_path: str,
    output: str | None = None,
    docx: bool = True,
    style: str = "ft",
    ft_background: bool = False,
    date: str | None = None,
    source: str = "",
    title_prefix: str = "",
    max_figures: int = 8,
    narrative: bool = False,
) -> tuple[int, list[str]]:
    """Generate a dataframe-driven figure suite from a CSV file."""

    if style not in {"fins", "ft"}:
        raise WorkflowError("figure style must be one of: fins, ft")

    csv_path = resolve_path(cwd, Path(input_path))
    if not csv_path.exists():
        raise WorkflowError(f"input CSV does not exist: {csv_path}")
    output_path = resolve_path(cwd, Path(output or "results/figures"))
    output_path = ensure_within_repo(output_path, root)

    try:
        import matplotlib

        matplotlib.use("Agg", force=False)
        import pandas as pd

        from fintools.figures import create_figure_suite
    except ImportError as exc:
        raise WorkflowError(
            "figure dependencies are missing; reinstall with the repo interpreter and "
            "-m pip install -r requirements.txt -r requirements-dev.txt"
        ) from exc

    data = pd.read_csv(csv_path)
    result = create_figure_suite(
        data,
        output_path,
        date=date,
        style=style,
        ft_background=ft_background,
        docx=docx,
        source=source,
        title_prefix=title_prefix,
        max_figures=max_figures,
        narrative=narrative,
    )

    try:
        relative_output = output_path.relative_to(root)
    except ValueError:
        relative_output = output_path

    lines = [
        f"Generated {style} dataframe figure suite in: {relative_output}",
        (
            "Profile: "
            f"{result.profile.row_count:,} rows, {result.profile.column_count:,} columns, "
            f"{len(result.profile.numeric_columns)} numeric, "
            f"{len(result.profile.categorical_columns)} categorical."
        ),
    ]
    if narrative:
        lines.append("Narrative mode: enabled.")
    if result.profile.date_column or result.profile.date_kind == "index":
        date_label = result.profile.date_column or "index"
        lines.append(f"Detected date field: {date_label}; sample: {result.profile.sample}.")
    else:
        lines.append("Detected no date field; generated cross-sectional figures only.")
    lines.append("Planned figures:")
    lines.extend(f"- {item.kind}: {item.title}" for item in result.plan)
    if result.skipped:
        lines.append("Skipped figures:")
        lines.extend(f"- {message}" for message in result.skipped)
    if result.issues:
        lines.append("Validation notes:")
        lines.extend(f"- {issue.code}: {issue.message}" for issue in result.issues)
    lines.append("Files:")
    lines.extend(f"- {path.relative_to(root)}" for path in result.generated_paths)
    return (0 if result.generated_figures else 1), lines


def render_authors(authors: str) -> str:
    """Convert a simple author string to LaTeX line breaks."""

    parts = [part.strip() for part in re.split(r"[;|]", authors) if part.strip()]
    if not parts:
        return authors.strip()
    return " \\\\ ".join(parts)


def topic_rewrite(text: str, topic: str) -> str:
    """Apply a light topic-aware rewrite while preserving [REMOVE] markers."""

    abstract_placeholder = (
        "[REMOVE] Write a concise summary of your report here. State the research\n"
        "question, the data or methodology used, and the main findings. Aim for\n"
        "100--200 words."
    )
    intro_placeholder = (
        "[REMOVE] Open with the broad topic and why it matters. What is the\n"
        "research question or practical problem you are addressing?"
    )
    literature_placeholder = (
        "[REMOVE] Briefly summarise how prior work has approached this topic.\n"
        "Cite key references, for example \\citet{FamaFrench_1993}."
    )
    replacements = {
        abstract_placeholder: (
            f"[REMOVE] Summarise the report on {topic}. State the research question,"
            " the data or methodology used, and the main findings. Aim for 100--200 words."
        ),
        intro_placeholder: (
            f"[REMOVE] Open with {topic} and explain why it matters. State the research"
            " question or practical problem you are addressing."
        ),
        literature_placeholder: (
            f"[REMOVE] Briefly summarise how prior work has approached {topic}."
            " Cite key references, for example \\citet{FamaFrench_1993}."
        ),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def discover_project_root(start: Path, root: Path) -> Path | None:
    """Return the containing project root if inside projects/<name>/."""

    for candidate in [start, *start.parents]:
        if candidate == root:
            break
        if candidate.parent == root / "projects":
            return candidate
    return None


def resolve_paper_target(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
) -> Path:
    """Resolve the directory that should receive a paper scaffold."""

    if target:
        target_path = Path(target)
        resolved = resolve_path(cwd, target_path)
        if resolved.suffix == ".tex":
            resolved = resolved.parent
        project_root = discover_project_root(resolved, root)
        if resolved.name == "latex":
            final_dir = resolved
        elif project_root == resolved:
            final_dir = resolved / "latex"
        else:
            final_dir = resolved
        ensure_within_repo(final_dir, root)
        final_dir.mkdir(parents=True, exist_ok=True)
        return final_dir

    project_root = discover_project_root(cwd, root)
    if project_root:
        target_dir = project_root / "latex"
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    if cwd.name == "latex":
        ensure_within_repo(cwd, root)
        return cwd
    raise WorkflowError("could not infer the paper directory; use --target")


def resolve_word_report_path(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
) -> Path:
    """Resolve the Word report path that should be created."""

    if target:
        target_path = Path(target)
        resolved = resolve_path(cwd, target_path)
        if resolved.suffix.lower() == ".docx":
            output_path = resolved
        else:
            project_root = discover_project_root(resolved, root)
            if project_root == resolved:
                output_path = resolved / "report" / "report.docx"
            elif resolved.name == "report":
                output_path = resolved / "report.docx"
            else:
                output_path = resolved / "report" / "report.docx"
        ensure_within_repo(output_path, root)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    project_root = discover_project_root(cwd, root)
    if project_root:
        output_path = project_root / "report" / "report.docx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path
    if cwd.name == "report":
        output_path = cwd / "report.docx"
        ensure_within_repo(output_path, root)
        return output_path
    raise WorkflowError("could not infer the Word report path; use --target")


def setup_latex_paper(
    root: Path,
    cwd: Path,
    *,
    title: str,
    authors: str = "",
    topic: str = "",
    target: str | None = None,
) -> tuple[Path, list[str]]:
    """Copy the legacy LaTeX boilerplate into a target directory."""

    target_dir = resolve_paper_target(root, cwd, target=target)
    main_tex = target_dir / "main.tex"
    references_bib = target_dir / "references.bib"
    if main_tex.exists() or references_bib.exists():
        raise WorkflowError(f"refusing to overwrite existing paper scaffold in {target_dir}")

    tex_text = read_text(root / "boilerplate" / "template_main.tex")
    bib_text = read_text(root / "boilerplate" / "template_references.bib")
    tex_text = tex_text.replace(
        r"\title{[REMOVE] Your Report Title Here}",
        rf"\title{{{title}}}",
    )
    if authors:
        tex_text = tex_text.replace(
            r"\author{[REMOVE] Student Name \\ [REMOVE] Student ID \\ FINS2026 --- Fintech}",
            rf"\author{{{render_authors(authors)}}}",
        )
    if topic:
        tex_text = topic_rewrite(tex_text, topic)

    write_text(main_tex, tex_text)
    write_text(references_bib, bib_text)

    lines = [
        f"Created paper scaffold in: {target_dir.relative_to(root)}",
        f"- {main_tex.relative_to(root)}",
        f"- {references_bib.relative_to(root)}",
    ]
    return target_dir, lines


def setup_word_report(
    root: Path,
    cwd: Path,
    *,
    title: str,
    authors: str = "",
    topic: str = "",
    target: str | None = None,
) -> tuple[Path, list[str]]:
    """Create a Word report scaffold in a target project."""

    from fintools.documents import create_word_report

    report_path = resolve_word_report_path(root, cwd, target=target)
    if report_path.exists():
        raise WorkflowError(f"refusing to overwrite existing Word report scaffold: {report_path}")
    create_word_report(report_path, title=title, authors=authors, topic=topic)
    return report_path.parent, [
        f"Created Word report scaffold in: {report_path.parent.relative_to(root)}",
        f"- {report_path.relative_to(root)}",
        "Open the document in Word and update fields after editing.",
    ]


def setup_paper(
    root: Path,
    cwd: Path,
    *,
    title: str,
    authors: str = "",
    topic: str = "",
    target: str | None = None,
    format: str = "word",
) -> tuple[Path, list[str]]:
    """Create a report scaffold, Word-first with legacy LaTeX opt-in."""

    if format == "word":
        return setup_word_report(
            root,
            cwd,
            title=title,
            authors=authors,
            topic=topic,
            target=target,
        )
    if format == "latex":
        return setup_latex_paper(
            root,
            cwd,
            title=title,
            authors=authors,
            topic=topic,
            target=target,
        )
    raise WorkflowError("format must be word or latex")


def discover_tex_candidates(start: Path, *, include_decks: bool = True) -> list[Path]:
    """Discover likely TeX targets beneath a directory."""

    candidates: list[Path] = []
    preferred_names = {"main.tex"}
    if include_decks:
        preferred_names.update({"slides.tex", "deck.tex"})
    for path in start.rglob("*.tex"):
        if ".venv" in path.parts:
            continue
        if path.name in {"template_main.tex", "template_slides.tex"}:
            continue
        candidates.append(path)
    candidates.sort(key=lambda path: (path.name not in preferred_names, str(path)))
    return candidates


def resolve_tex_target(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    include_decks: bool = True,
) -> Path:
    """Resolve a target TeX file."""

    if target:
        target_path = Path(target)
        resolved = resolve_path(cwd, target_path)
        ensure_within_repo(resolved, root)
        if resolved.is_dir():
            candidates = discover_tex_candidates(resolved, include_decks=include_decks)
            if not candidates:
                raise WorkflowError(f"no .tex files found in {resolved}")
            return candidates[0]
        if resolved.suffix != ".tex":
            raise WorkflowError("target must be a .tex file or directory")
        return resolved

    candidates = discover_tex_candidates(cwd, include_decks=include_decks)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise WorkflowError("no .tex files found; pass an explicit target")
    if (cwd / "main.tex").exists():
        return cwd / "main.tex"
    raise WorkflowError(
        "multiple .tex files found; pass an explicit target: "
        + ", ".join(str(path.relative_to(cwd)) for path in candidates[:5])
    )


def discover_report_candidates(start: Path) -> list[Path]:
    """Discover likely Word or legacy TeX report sources beneath a directory."""

    preferred = [
        start / "report" / "report.docx",
        start / "report.docx",
        start / "main.tex",
    ]
    for path in preferred:
        if path.exists():
            return [path]
    candidates = [
        path
        for path in start.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".docx", ".tex"}
        and ".venv" not in path.parts
        and "__pycache__" not in path.parts
    ]
    candidates.sort(key=lambda path: (path.suffix.lower() != ".docx", str(path)))
    return candidates


def resolve_report_source(root: Path, cwd: Path, *, target: str | None) -> Path:
    """Resolve a Word-first report source for outline and proofread workflows."""

    if target:
        resolved = resolve_path(cwd, Path(target))
        ensure_within_repo(resolved, root)
        if resolved.is_dir():
            candidates = discover_report_candidates(resolved)
            if not candidates:
                raise WorkflowError(f"no .docx or .tex report files found in {resolved}")
            return candidates[0]
        if resolved.suffix.lower() not in {".docx", ".tex"}:
            raise WorkflowError("target must be a .docx file, .tex file, or directory")
        return resolved

    candidates = discover_report_candidates(cwd)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise WorkflowError("no .docx or .tex report files found; pass an explicit target")
    raise WorkflowError(
        "multiple report files found; pass an explicit target: "
        + ", ".join(str(path.relative_to(cwd)) for path in candidates[:5])
    )


def count_warnings(text: str) -> int:
    """Count warning-like messages."""

    return len(re.findall(r"\bwarning\b", text, flags=re.IGNORECASE))


def count_errors(text: str) -> int:
    """Count error-like messages."""

    return text.count("\n!") + len(re.findall(r"\berror\b", text, flags=re.IGNORECASE))


def aux_uses_bibtex(aux_path: Path) -> bool:
    """Return whether an aux file indicates BibTeX usage."""

    if not aux_path.exists():
        return False
    aux_text = read_text(aux_path)
    return "\\bibdata" in aux_text or "\\citation" in aux_text


def compile_tex(
    target: Path,
    *,
    quick: bool = False,
    use_bibtex: bool = True,
) -> tuple[int, list[str]]:
    """Compile a TeX file and return a report."""

    if not shutil.which("pdflatex"):
        raise WorkflowError("pdflatex is not installed; see docs/setup/latex.md")

    cwd = target.parent
    basename = target.stem
    passes: list[list[str]] = [
        ["pdflatex", "-interaction=nonstopmode", target.name],
    ]
    if not quick and use_bibtex:
        passes.append(["bibtex", basename])
        passes.append(["pdflatex", "-interaction=nonstopmode", target.name])
        passes.append(["pdflatex", "-interaction=nonstopmode", target.name])

    lines = [f"Compiling {target.name} in {cwd}"]
    total_warnings = 0
    total_errors = 0
    for index, command in enumerate(passes, start=1):
        if command[0] == "bibtex" and not aux_uses_bibtex(cwd / f"{basename}.aux"):
            lines.append("Skipped bibtex because the aux file has no bibliography entries.")
            continue
        report = run_command(command, cwd=cwd, timeout=180)
        output = "\n".join(part for part in [report.stdout, report.stderr] if part)
        total_warnings += count_warnings(output)
        total_errors += count_errors(output)
        lines.append(f"Pass {index}: {format_command(command)}")
        if report.returncode != 0:
            lines.append("Compilation failed.")
            if output.strip():
                tail = output.strip().splitlines()[-10:]
                lines.extend(tail)
            lines.extend(
                [
                    f"Warnings: {total_warnings}",
                    f"Errors: {total_errors}",
                ]
            )
            return report.returncode, lines

    pdf_path = cwd / f"{basename}.pdf"
    lines.append(f"Warnings: {total_warnings}")
    lines.append(f"Errors: {total_errors}")
    lines.append(f"PDF: {pdf_path}")
    return 0, lines


def extract_section_body(text: str, section_name: str) -> str:
    """Extract a named section body from LaTeX text."""

    section_pattern = re.compile(
        rf"\\section\{{{re.escape(section_name)}\}}.*?(?=\\section\{{|\Z)",
        re.DOTALL,
    )
    match = section_pattern.search(text)
    return match.group(0).strip() if match else ""


def clean_inline(text: str) -> str:
    """Normalize extracted text for summaries."""

    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_sections(text: str) -> list[SectionEntry]:
    """Parse LaTeX section headings."""

    sections: list[SectionEntry] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in SECTION_RE.finditer(line):
            sections.append(
                SectionEntry(level=match.group(1), title=match.group(2).strip(), line_no=line_no)
            )
    return sections


def extract_tex_context(path: Path) -> dict[str, object]:
    """Extract structured context from a TeX file."""

    text = read_text(path)
    title_match = re.search(r"\\title\{([^}]*)\}", text)
    abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.DOTALL)
    sections = parse_sections(text)
    labels = LABEL_RE.findall(text)
    citations = sorted(set(re.findall(r"\\cite\w*\{([^}]*)\}", text)))
    citation_keys: list[str] = []
    for raw in citations:
        citation_keys.extend(key.strip() for key in raw.split(",") if key.strip())
    data_body = clean_inline(extract_section_body(text, "Data"))
    results_body = clean_inline(extract_section_body(text, "Results"))
    abstract = clean_inline(abstract_match.group(1)) if abstract_match else ""
    return {
        "source": path,
        "title": title_match.group(1).strip() if title_match else path.stem,
        "abstract": abstract,
        "sections": sections,
        "labels": labels,
        "citations": sorted(set(citation_keys)),
        "data_summary": data_body[:400],
        "results_summary": results_body[:400],
    }


def extract_md_context(path: Path) -> dict[str, object]:
    """Extract structured context from a Markdown file."""

    text = read_text(path)
    title = path.stem
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]

    def normalize_block(block: str) -> str:
        lines: list[str] = []
        for raw_line in block.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith(">"):
                stripped = stripped.lstrip(">").strip()
            lines.append(stripped)
        return clean_inline(" ".join(lines))

    def bullet_items(blocks: list[str]) -> list[str]:
        items: list[str] = []
        for block in blocks:
            current_parts: list[str] = []
            for raw_line in block.splitlines():
                stripped = raw_line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith("|"):
                    continue
                if stripped.startswith(">"):
                    stripped = stripped.lstrip(">").strip()
                match = re.match(r"^(?:[-*+]|\d+\.)\s+(.*)$", stripped)
                if match:
                    if current_parts:
                        item = clean_inline(" ".join(current_parts)).rstrip(" .")
                        if item:
                            items.append(item)
                    current_parts = [match.group(1)]
                    continue
                if not current_parts:
                    continue
                current_parts.append(stripped)
            if current_parts:
                item = clean_inline(" ".join(current_parts)).rstrip(" .")
                if item:
                    items.append(item)
        return items

    def trim_summary(text: str, *, max_length: int = 320) -> str:
        cleaned = clean_inline(text)
        if len(cleaned) <= max_length:
            return cleaned
        truncated = cleaned[: max_length + 1]
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        return truncated.rstrip(" ,;:.")

    def fit_bullet_summary(items: list[str], *, max_length: int = 320) -> str:
        fitted: list[str] = []
        for item in items:
            candidate = "; ".join([*fitted, item])
            if len(clean_inline(candidate)) > max_length:
                break
            fitted.append(item)
        if fitted:
            return "; ".join(fitted)
        return trim_summary(items[0], max_length=max_length) if items else ""

    candidate_blocks = (
        paragraphs[1:]
        if paragraphs and paragraphs[0].startswith("#") and len(paragraphs) > 1
        else paragraphs
    )
    abstract = ""
    for block in candidate_blocks:
        block_start = block.lstrip()
        if re.match(r"^(?:[-*+]|\d+\.)\s+", block_start) or block_start.startswith("|"):
            continue
        normalized = normalize_block(block)
        if normalized:
            abstract = normalized
            break
    if not abstract:
        items = bullet_items(candidate_blocks)
        if items:
            abstract = fit_bullet_summary(items, max_length=240)
        elif candidate_blocks:
            abstract = normalize_block(candidate_blocks[0])
    return {
        "source": path,
        "title": title,
        "abstract": trim_summary(abstract),
        "sections": [],
        "labels": [],
        "citations": [],
        "data_summary": "",
        "results_summary": "",
    }


def extract_pdf_context(path: Path) -> dict[str, object]:
    """Extract context from a PDF when pypdf is available."""

    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise WorkflowError(
            "PDF support requires pypdf; use a .docx, .tex, or .md source instead"
        ) from exc

    reader = PdfReader(str(path))
    text = " ".join(page.extract_text() or "" for page in reader.pages[:3])
    cleaned = clean_inline(text)
    first_sentence = cleaned.split(". ")[0].strip()
    return {
        "source": path,
        "title": path.stem,
        "abstract": first_sentence,
        "sections": [],
        "labels": [],
        "citations": [],
        "data_summary": "",
        "results_summary": cleaned[:400],
    }


def extract_docx_context(path: Path) -> dict[str, object]:
    """Extract structured context from a Word document."""

    from fintools.documents import read_word_paragraphs, word_heading_level

    paragraphs = read_word_paragraphs(path)
    headings = [
        SectionEntry(
            level=f"heading-{level}",
            title=paragraph.text,
            line_no=paragraph.index,
        )
        for paragraph in paragraphs
        if (level := word_heading_level(paragraph.style)) is not None
    ]
    title = next(
        (paragraph.text for paragraph in paragraphs if paragraph.style.lower() == "title"),
        path.stem,
    )

    def section_body(section_title: str) -> str:
        start: int | None = None
        for index, paragraph in enumerate(paragraphs):
            level = word_heading_level(paragraph.style)
            if level == 1 and paragraph.text.lower() == section_title.lower():
                start = index + 1
                continue
            if start is not None and level == 1:
                break
            if start is not None:
                continue
        if start is None:
            return ""
        body_parts: list[str] = []
        for paragraph in paragraphs[start:]:
            if word_heading_level(paragraph.style) == 1:
                break
            body_parts.append(paragraph.text)
        return clean_inline(" ".join(body_parts))

    abstract = section_body("Abstract")
    data_body = section_body("Data")
    results_body = section_body("Results")
    return {
        "source": path,
        "title": title,
        "abstract": abstract[:400],
        "sections": headings,
        "labels": [],
        "citations": [],
        "data_summary": data_body[:400],
        "results_summary": results_body[:400],
    }


def extract_context(path: Path) -> dict[str, object]:
    """Dispatch to the right extractor by file suffix."""

    suffix = path.suffix.lower()
    if suffix == ".docx":
        return extract_docx_context(path)
    if suffix == ".tex":
        return extract_tex_context(path)
    if suffix == ".md":
        return extract_md_context(path)
    if suffix == ".pdf":
        return extract_pdf_context(path)
    raise WorkflowError(f"unsupported context source: {path}")


def find_context_output_dir(root: Path, cwd: Path, sources: list[Path]) -> Path:
    """Choose where guidance/paper-context.md should live."""

    source = sources[0]
    project_root = discover_project_root(source.parent if source.is_file() else source, root)
    if project_root:
        return project_root / "guidance"
    project_root = discover_project_root(cwd, root)
    if project_root:
        return project_root / "guidance"
    return cwd / "guidance"


def discover_context_sources(cwd: Path) -> list[Path]:
    """Discover likely source files for build-context."""

    for preferred in ["report/report.docx", "report.docx", "main.tex", "README.md"]:
        preferred_path = cwd / preferred
        if preferred_path.exists():
            return [preferred_path]
    candidates = [
        path
        for path in cwd.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".docx", ".tex", ".md", ".pdf"}
        and ".venv" not in path.parts
    ]
    candidates.sort(key=lambda path: (path.suffix.lower() != ".docx", str(path)))
    return candidates


def build_context(
    root: Path,
    cwd: Path,
    *,
    sources: list[str],
) -> tuple[Path, list[str]]:
    """Build guidance/paper-context.md from report sources."""

    resolved_sources: list[Path] = []
    if sources:
        for source in sources:
            source_path = Path(source)
            resolved = resolve_path(cwd, source_path)
            ensure_within_repo(resolved, root)
            if not resolved.exists():
                raise WorkflowError(f"source does not exist: {resolved}")
            resolved_sources.append(resolved)
    else:
        resolved_sources = discover_context_sources(cwd)
        if not resolved_sources:
            raise WorkflowError("no .docx, .tex, .md, or .pdf sources found; pass explicit paths")
        if len(resolved_sources) > 1:
            raise WorkflowError(
                "multiple candidate sources found; pass explicit paths: "
                + ", ".join(str(path.relative_to(cwd)) for path in resolved_sources[:5])
            )

    contexts = [extract_context(path) for path in resolved_sources]
    output_dir = find_context_output_dir(root, cwd, resolved_sources)
    output_path = output_dir / "paper-context.md"

    lines = ["# Paper Context", ""]
    lines.append("## Sources")
    for context in contexts:
        source = Path(context["source"])
        lines.append(f"- `{source}`")
    lines.append("")
    primary = contexts[0]
    lines.append("## Paper Identity")
    lines.append(f"- Title: {primary['title']}")
    lines.append("")
    if primary["abstract"]:
        lines.append("## Abstract")
        lines.append(str(primary["abstract"]))
        lines.append("")
    if primary["data_summary"]:
        lines.append("## Sample And Data")
        lines.append(str(primary["data_summary"]))
        lines.append("")
    if primary["results_summary"]:
        lines.append("## Key Results")
        lines.append(str(primary["results_summary"]))
        lines.append("")
    lines.append("## Terminology And Structure")
    section_titles: list[str] = []
    label_values: list[str] = []
    citation_values: list[str] = []
    for context in contexts:
        section_titles.extend(entry.title for entry in context["sections"])
        label_values.extend(str(label) for label in context["labels"])
        citation_values.extend(str(citation) for citation in context["citations"])
    if section_titles:
        lines.append("- Sections: " + ", ".join(section_titles))
    if label_values:
        lines.append("- Labels: " + ", ".join(sorted(set(label_values))))
    if citation_values:
        lines.append("- Citations: " + ", ".join(sorted(set(citation_values))))
    if not section_titles and not label_values and not citation_values:
        lines.append("- No structured report sections were found in the supplied sources.")
    lines.append("")

    write_text(output_path, "\n".join(lines).rstrip() + "\n")
    report = [
        f"Wrote context file: {output_path.relative_to(root)}",
        "Sources:",
    ]
    report.extend(f"- {path.relative_to(root)}" for path in resolved_sources)
    return output_path, report


def parse_markers(text: str) -> list[MarkerEntry]:
    """Parse BEGIN/END markers from a TeX file."""

    markers: list[MarkerEntry] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = MARKER_RE.match(line)
        if match:
            markers.append(MarkerEntry(kind=match.group(1), key=match.group(2), line_no=line_no))
    return markers


def marker_report(text: str) -> tuple[list[MarkerSpan], list[str]]:
    """Match BEGIN/END markers and return any integrity issues."""

    stack: list[MarkerEntry] = []
    spans: list[MarkerSpan] = []
    issues: list[str] = []
    lines = text.splitlines()
    for marker in parse_markers(text):
        if marker.kind == "BEGIN":
            stack.append(marker)
            continue
        if not stack:
            issues.append(f"line {marker.line_no}: END {marker.key} without a matching BEGIN")
            continue
        start = stack.pop()
        if start.key != marker.key:
            issues.append(
                f"line {marker.line_no}: END {marker.key} closes BEGIN {start.key}"
                f" from line {start.line_no}"
            )
            continue
        body_lines = sum(1 for line in lines[start.line_no : marker.line_no - 1] if line.strip())
        spans.append(
            MarkerSpan(
                key=marker.key,
                start_line=start.line_no,
                end_line=marker.line_no,
                body_lines=body_lines,
            )
        )
    for start in stack:
        issues.append(f"line {start.line_no}: BEGIN {start.key} has no matching END")
    return spans, issues


def outline_docx_report(path: Path) -> tuple[int, list[str]]:
    """Produce a structured outline report for a Word document."""

    from fintools.documents import read_word_paragraphs, word_heading_level

    paragraphs = read_word_paragraphs(path)
    headings = [
        (paragraph.index, word_heading_level(paragraph.style), paragraph.text)
        for paragraph in paragraphs
        if word_heading_level(paragraph.style) is not None
    ]
    lines = [f"Outline report for {path}"]
    if headings:
        lines.append("Headings:")
        for paragraph_index, level, title in headings:
            lines.append(f"- paragraph {paragraph_index}: heading {level} {title}")
    else:
        lines.append("No Word heading styles found.")
    expected = ["Introduction", "Data", "Methodology", "Results", "Conclusion"]
    present_titles = {title.lower() for _, _, title in headings}
    missing = [title for title in expected if title.lower() not in present_titles]
    if missing:
        lines.append("Missing standard sections: " + ", ".join(missing))
    lines.append("Marker spans: not used for Word reports.")
    return 0, lines


def outline_tex_report(path: Path) -> tuple[int, list[str]]:
    """Produce a structured outline report for a TeX document."""

    text = read_text(path)
    sections = parse_sections(text)
    spans, marker_issues = marker_report(text)
    lines = [f"Outline report for {path}"]
    if sections:
        lines.append("Sections:")
        for section in sections:
            lines.append(f"- line {section.line_no}: {section.level} {section.title}")
    else:
        lines.append("No sections found.")

    expected = ["Introduction", "Data", "Methodology", "Results", "Conclusion"]
    present_titles = {section.title.lower() for section in sections}
    missing = [title for title in expected if title.lower() not in present_titles]
    if missing:
        lines.append("Missing standard sections: " + ", ".join(missing))

    if spans:
        lines.append("Marker spans:")
        for span in spans:
            lines.append(
                f"- {span.key}: lines {span.start_line}-{span.end_line},"
                f" nonblank body lines {span.body_lines}"
            )
        body_sizes = [span.body_lines for span in spans if not span.key.startswith("appendix")]
        if len(body_sizes) >= 2:
            smallest = min(body_sizes)
            largest = max(body_sizes)
            if smallest > 0 and largest / smallest >= 3:
                lines.append(
                    "Section balance warning: the largest body section is at least"
                    " 3x the smallest."
                )
    else:
        lines.append("No BEGIN/END markers found.")

    if marker_issues:
        lines.append("Marker issues:")
        lines.extend(f"- {issue}" for issue in marker_issues)
        return 1, lines
    return 0, lines


def outline_report(root: Path, cwd: Path, *, target: str | None) -> tuple[int, list[str]]:
    """Produce a structured outline report."""

    report_path = resolve_report_source(root, cwd, target=target)
    if report_path.suffix.lower() == ".docx":
        return outline_docx_report(report_path)
    return outline_tex_report(report_path)


def slice_lines_by_range(lines: list[str], line_range: str | None) -> tuple[int, list[str]]:
    """Slice lines by a 1-based inclusive range."""

    if not line_range:
        return 1, lines
    match = re.fullmatch(r"(\d+)-(\d+)", line_range)
    if not match:
        raise WorkflowError("line range must be START-END")
    start = int(match.group(1))
    end = int(match.group(2))
    if start > end:
        raise WorkflowError("line range start cannot be greater than end")
    return start, lines[start - 1 : end]


def slice_lines_by_marker(text: str, section_key: str) -> tuple[int, list[str]]:
    """Slice lines by a BEGIN/END marker block."""

    lines = text.splitlines()
    begin_line = None
    end_line = None
    for index, line in enumerate(lines, start=1):
        if re.fullmatch(rf"\s*%%\s*BEGIN\s+{re.escape(section_key)}\s*", line):
            begin_line = index
        if re.fullmatch(rf"\s*%%\s*END\s+{re.escape(section_key)}\s*", line):
            end_line = index
            break
    if begin_line is None or end_line is None:
        raise WorkflowError(f"section key not found: {section_key}")
    return begin_line, lines[begin_line - 1 : end_line]


def collect_proofread_findings(
    lines: list[str],
    *,
    start_line: int,
    unit_label: str = "line",
    source_format: str = "tex",
) -> dict[str, list[str]]:
    """Collect simple mechanical findings from a report excerpt."""

    findings: dict[str, list[str]] = {
        "doubled words": [],
        "spacing": [],
        "references": [],
        "placeholders": [],
    }
    for offset, line in enumerate(lines, start=start_line):
        if re.search(r"\b(\w+)\s+\1\b", line, flags=re.IGNORECASE):
            findings["doubled words"].append(f"{unit_label} {offset}: doubled word")
        if "  " in line.rstrip():
            findings["spacing"].append(f"{unit_label} {offset}: multiple consecutive spaces")
        if source_format == "tex" and re.search(r"\b(Figure|Table|Section|Equation) \\ref\{", line):
            findings["references"].append(
                f"{unit_label} {offset}: use nonbreaking space before \\ref"
            )
        if "[REMOVE]" in line:
            findings["placeholders"].append(
                f"{unit_label} {offset}: unresolved [REMOVE] placeholder"
            )
    return findings


def slugify_section_title(text: str) -> str:
    """Return the section-key form used for matching Word headings."""

    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def slice_docx_by_heading(
    paragraphs: list[object],
    section_key: str,
) -> tuple[int, list[str]]:
    """Slice Word paragraphs by a Heading 1 title or slug."""

    from fintools.documents import word_heading_level

    wanted = slugify_section_title(section_key)
    start: int | None = None
    start_index = 1
    for index, paragraph in enumerate(paragraphs):
        level = word_heading_level(paragraph.style)
        if level == 1 and slugify_section_title(paragraph.text) == wanted:
            start = index + 1
            start_index = paragraph.index + 1
            break
    if start is None:
        raise WorkflowError(f"section key not found: {section_key}")
    body: list[str] = []
    for paragraph in paragraphs[start:]:
        if word_heading_level(paragraph.style) == 1:
            break
        body.append(paragraph.text)
    return start_index, body


def proofread_docx_report(
    path: Path,
    *,
    section_key: str | None,
    line_range: str | None,
) -> tuple[int, list[str]]:
    """Produce a paragraph-numbered proofread report for a Word document."""

    from fintools.documents import read_word_paragraphs

    paragraphs = read_word_paragraphs(path)
    start_index = 1
    excerpt = [paragraph.text for paragraph in paragraphs]
    if section_key:
        start_index, excerpt = slice_docx_by_heading(paragraphs, section_key)
    elif line_range:
        start_index, excerpt = slice_lines_by_range(excerpt, line_range)
    findings = collect_proofread_findings(
        excerpt,
        start_line=start_index,
        unit_label="paragraph",
        source_format="docx",
    )
    report = [f"Proofread report for {path}"]
    total = 0
    for category, entries in findings.items():
        report.append(f"{category.title()}: {len(entries)}")
        total += len(entries)
        for entry in entries:
            report.append(f"- {entry}")
    report.append(f"Total findings: {total}")
    return (1 if total else 0), report


def proofread_report(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    section_key: str | None,
    line_range: str | None,
) -> tuple[int, list[str]]:
    """Produce a line-numbered proofread report."""

    report_path = resolve_report_source(root, cwd, target=target)
    if report_path.suffix.lower() == ".docx":
        return proofread_docx_report(
            report_path,
            section_key=section_key,
            line_range=line_range,
        )

    tex_path = report_path
    text = read_text(tex_path)
    lines = text.splitlines()
    start_line = 1
    excerpt = lines
    if section_key:
        start_line, excerpt = slice_lines_by_marker(text, section_key)
    elif line_range:
        start_line, excerpt = slice_lines_by_range(lines, line_range)
    findings = collect_proofread_findings(excerpt, start_line=start_line)
    report = [f"Proofread report for {tex_path}"]
    total = 0
    for category, entries in findings.items():
        report.append(f"{category.title()}: {len(entries)}")
        total += len(entries)
        for entry in entries:
            report.append(f"- {entry}")
    report.append(f"Total findings: {total}")
    return (1 if total else 0), report


def find_marker_span(text: str, section_key: str) -> MarkerSpan:
    """Return the matched span for a section key."""

    spans, issues = marker_report(text)
    if issues:
        raise WorkflowError("cannot inspect section until marker issues are fixed")
    for span in spans:
        if span.key == section_key:
            return span
    raise WorkflowError(f"section key not found: {section_key}")


def extract_section_details(
    text: str,
    *,
    section_key: str,
) -> dict[str, object]:
    """Extract section-specific structure and references."""

    span = find_marker_span(text, section_key)
    lines = text.splitlines()
    excerpt = lines[span.start_line - 1 : span.end_line]
    excerpt_text = "\n".join(excerpt)
    headings = parse_sections(excerpt_text)
    labels = LABEL_RE.findall(excerpt_text)
    cites = re.findall(r"\\cite\w*\{([^}]*)\}", excerpt_text)
    cite_keys: list[str] = []
    for raw in cites:
        cite_keys.extend(key.strip() for key in raw.split(",") if key.strip())
    return {
        "span": span,
        "headings": headings,
        "labels": labels,
        "cite_keys": sorted(set(cite_keys)),
        "has_placeholders": "[REMOVE]" in excerpt_text,
    }


def section_context_report(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    section_key: str,
) -> tuple[int, list[str]]:
    """Report structural context for one marked section."""

    tex_path = resolve_tex_target(root, cwd, target=target, include_decks=False)
    text = read_text(tex_path)
    details = extract_section_details(text, section_key=section_key)
    span = details["span"]
    lines = [
        f"Section context for {tex_path}",
        f"- key: {section_key}",
        f"- lines: {span.start_line}-{span.end_line}",
        f"- nonblank body lines: {span.body_lines}",
    ]
    headings = details["headings"]
    if headings:
        lines.append("- headings:")
        for heading in headings:
            lines.append(f"  - {heading.level} {heading.title}")
    labels = details["labels"]
    lines.append(
        "- labels: " + (", ".join(str(label) for label in labels) if labels else "none")
    )
    cite_keys = details["cite_keys"]
    lines.append(
        "- citation keys: "
        + (", ".join(str(key) for key in cite_keys) if cite_keys else "none")
    )
    lines.append(
        "- unresolved placeholders: "
        + ("yes" if bool(details["has_placeholders"]) else "no")
    )
    return 0, lines


def parse_bib_entries(path: Path) -> list[BibEntry]:
    """Parse BibTeX entry keys with line numbers."""

    entries: list[BibEntry] = []
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        match = BIB_ENTRY_RE.search(line)
        if match:
            entries.append(BibEntry(key=match.group(1).strip(), line_no=line_no))
    return entries


def resolve_bib_file(root: Path, tex_path: Path) -> Path:
    """Resolve the bibliography file associated with a TeX file."""

    tex_text = read_text(tex_path)
    bib_match = re.search(r"\\bibliography\{([^}]*)\}", tex_text)
    if bib_match:
        name = bib_match.group(1).split(",")[0].strip()
        candidate = tex_path.parent / f"{name}.bib"
        if candidate.exists():
            return candidate
    bib_files = sorted(tex_path.parent.glob("*.bib"))
    if len(bib_files) == 1:
        return bib_files[0]
    for candidate in bib_files:
        if candidate.name == "references.bib":
            return candidate
    raise WorkflowError(
        f"could not resolve a .bib file for {tex_path.relative_to(root)}"
    )


def citation_keys_from_text(text: str) -> list[str]:
    """Extract cite keys from LaTeX text."""

    cite_keys: list[str] = []
    for raw in re.findall(r"\\cite\w*\{([^}]*)\}", text):
        cite_keys.extend(key.strip() for key in raw.split(",") if key.strip())
    return sorted(set(cite_keys))


def check_citations_report(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    section_key: str | None,
    line_range: str | None,
) -> tuple[int, list[str]]:
    """Verify that cite keys in a TeX file or section exist in the .bib file."""

    tex_path = resolve_tex_target(root, cwd, target=target, include_decks=False)
    text = read_text(tex_path)
    excerpt_text = text
    if section_key:
        _, excerpt = slice_lines_by_marker(text, section_key)
        excerpt_text = "\n".join(excerpt)
    elif line_range:
        _, excerpt = slice_lines_by_range(text.splitlines(), line_range)
        excerpt_text = "\n".join(excerpt)

    cite_keys = citation_keys_from_text(excerpt_text)
    bib_path = resolve_bib_file(root, tex_path)
    bib_entries = parse_bib_entries(bib_path)
    available = {entry.key for entry in bib_entries}
    missing = [key for key in cite_keys if key not in available]
    report = [
        f"Citation check for {tex_path}",
        f"- bibliography: {bib_path.relative_to(root)}",
        "- citation keys used: " + (", ".join(cite_keys) if cite_keys else "none"),
    ]
    if missing:
        report.append("- missing keys: " + ", ".join(missing))
        return 1, report
    report.append("- all citation keys resolve in the bibliography")
    return 0, report


def removable_comment_lines(text: str) -> list[int]:
    """Return comment lines that look safe to remove manually."""

    removable: list[int] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("%"):
            continue
        if stripped.startswith("%% BEGIN") or stripped.startswith("%% END"):
            continue
        if stripped.startswith("% !TeX"):
            continue
        if (
            stripped.startswith("%%%")
            or stripped.startswith("% ---")
            or stripped.startswith("% ===")
        ):
            continue
        removable.append(line_no)
    return removable


def latex_doctor(
    root: Path,
    cwd: Path,
    *,
    target: str | None,
    mode: str,
) -> tuple[int, list[str]]:
    """Run deterministic latex doctor checks."""

    tex_path = resolve_tex_target(root, cwd, target=target, include_decks=False)
    text = read_text(tex_path)
    lines = [f"LaTeX doctor report for {tex_path}"]
    status = 0

    if mode in {"all", "comments"}:
        comment_lines = removable_comment_lines(text)
        lines.append(f"Comment cleanup candidates: {len(comment_lines)}")
        if comment_lines:
            lines.append("- lines: " + ", ".join(str(line_no) for line_no in comment_lines[:15]))

    if mode in {"all", "markers"}:
        _, marker_lines = outline_report(root, cwd, target=str(tex_path))
        lines.append("Marker check:")
        lines.extend(marker_lines[1:])
        if any("Marker issues:" in line for line in marker_lines):
            status = 1

    if mode in {"all", "compile"}:
        try:
            compile_status, compile_lines = compile_tex(tex_path)
        except WorkflowError as exc:
            compile_status = 1
            compile_lines = [str(exc)]
        lines.append("Compile check:")
        lines.extend(compile_lines)
        status = max(status, 1 if compile_status else 0)

    return status, lines


WORKFLOW_DESCRIPTIONS = {
    "list": "List the shared deterministic workflow commands.",
    "onboard": "Run the repo onboarding helper and verification script.",
    "audit-week": "Audit a weekly folder against the week contract and data invariants.",
    "prepare-public-repo": "Prepare a fresh-history public student release mirror.",
    "new-project": "Create a project scaffold under projects/<name>/.",
    "scaffold-week": "Create or backfill the standard weekly scaffold under fins2026/weekN/.",
    "setup-paper": "Create a Word report scaffold, or legacy LaTeX with --format latex.",
    "word-report": "Create or inspect a Word report scaffold.",
    "build-paper": "Compile a legacy report .tex file with pdflatex and bibtex.",
    "build-deck": "Compile an explicit legacy Beamer deck .tex file with pdflatex.",
    "build-figure": "Generate validation figures using the public figure toolkit.",
    "build-figure-suite": "Generate a dataframe-driven FT/FINS figure suite from a CSV.",
    "build-app": "Create a Streamlit app scaffold for a project or weekly lab.",
    "check-app-submission": "Check Streamlit app deployment readiness.",
    "prepare-app-repo": "Prepare a minimal private GitHub repo bundle for deployment.",
    "build-context": "Generate guidance/paper-context.md from source files.",
    "build-week-context": (
        "Generate guidance/week-context.md, data-context.md, and output-context.md."
    ),
    "outline": "Report section structure, balance, and marker integrity.",
    "proofread": "Run a mechanical proofread scan on a Word or legacy LaTeX report.",
    "latex-doctor": "Run deterministic legacy LaTeX comment, marker, and compile checks.",
    "section-context": "Inspect one marked section for headings, labels, and cite keys.",
    "check-citations": "Verify that cite keys in a TeX file or section exist in the .bib file.",
}


def create_parser() -> argparse.ArgumentParser:
    """Create the workflow CLI parser."""

    parser = argparse.ArgumentParser(
        description="Shared deterministic workflow helpers for fins-agent."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help=WORKFLOW_DESCRIPTIONS["list"])
    onboard_parser = subparsers.add_parser("onboard", help=WORKFLOW_DESCRIPTIONS["onboard"])
    onboard_mode = onboard_parser.add_mutually_exclusive_group()
    onboard_mode.add_argument("--check", action="store_true", help="verify setup without changes")
    onboard_mode.add_argument(
        "--rebuild",
        action="store_true",
        help="recreate .venv after preflight",
    )
    audit_week_parser = subparsers.add_parser(
        "audit-week",
        help=WORKFLOW_DESCRIPTIONS["audit-week"],
    )
    audit_week_parser.add_argument("--target", default=".")
    audit_week_parser.add_argument("--spec", default=None)
    prepare_public_repo_parser = subparsers.add_parser(
        "prepare-public-repo",
        help=WORKFLOW_DESCRIPTIONS["prepare-public-repo"],
    )
    prepare_public_repo_parser.add_argument("--dest", required=True)
    prepare_public_repo_parser.add_argument("--force", action="store_true")
    prepare_public_repo_parser.add_argument("--init-git", action="store_true")

    new_project_parser = subparsers.add_parser(
        "new-project",
        help=WORKFLOW_DESCRIPTIONS["new-project"],
    )
    new_project_parser.add_argument("name")
    new_project_parser.add_argument("--description", default="")
    new_project_parser.add_argument("--datasets", default="")
    new_project_parser.add_argument("--notes", default="")
    new_project_parser.add_argument("--setup-paper", action="store_true")
    new_project_parser.add_argument("--paper-format", choices=["word", "latex"], default="word")
    new_project_parser.add_argument("--with-app", action="store_true")
    new_project_parser.add_argument("--title", default="")

    scaffold_week_parser = subparsers.add_parser(
        "scaffold-week",
        help=WORKFLOW_DESCRIPTIONS["scaffold-week"],
    )
    scaffold_week_parser.add_argument("--target", required=True)
    scaffold_week_parser.add_argument("--title", default="")

    setup_paper_parser = subparsers.add_parser(
        "setup-paper",
        help=WORKFLOW_DESCRIPTIONS["setup-paper"],
    )
    setup_paper_parser.add_argument("--title", required=True)
    setup_paper_parser.add_argument("--authors", default="")
    setup_paper_parser.add_argument("--topic", default="")
    setup_paper_parser.add_argument("--target", default=None)
    setup_paper_parser.add_argument("--format", choices=["word", "latex"], default="word")
    setup_paper_parser.add_argument("--no-compile", action="store_true")

    word_report_parser = subparsers.add_parser(
        "word-report",
        help=WORKFLOW_DESCRIPTIONS["word-report"],
    )
    word_report_parser.add_argument("target", nargs="?")
    word_report_parser.add_argument("--title", default="")
    word_report_parser.add_argument("--authors", default="")
    word_report_parser.add_argument("--topic", default="")

    build_paper_parser = subparsers.add_parser(
        "build-paper",
        help=WORKFLOW_DESCRIPTIONS["build-paper"],
    )
    build_paper_parser.add_argument("target", nargs="?")
    build_paper_parser.add_argument("--quick", action="store_true")

    build_deck_parser = subparsers.add_parser(
        "build-deck",
        help=WORKFLOW_DESCRIPTIONS["build-deck"],
    )
    build_deck_parser.add_argument("target", nargs="?")

    build_figure_parser = subparsers.add_parser(
        "build-figure",
        help=WORKFLOW_DESCRIPTIONS["build-figure"],
    )
    build_figure_parser.add_argument("--output", default="results/figures")
    build_figure_parser.add_argument("--docx", action="store_true")
    build_figure_parser.add_argument("--style", choices=["fins", "ft"], default="fins")
    build_figure_parser.add_argument("--ft-background", action="store_true")
    build_figure_parser.add_argument("--plotly-demo", action="store_true")

    build_figure_suite_parser = subparsers.add_parser(
        "build-figure-suite",
        help=WORKFLOW_DESCRIPTIONS["build-figure-suite"],
    )
    build_figure_suite_parser.add_argument("input")
    build_figure_suite_parser.add_argument("--output", default="results/figures")
    build_figure_suite_parser.add_argument("--style", choices=["fins", "ft"], default="ft")
    build_figure_suite_parser.add_argument("--ft-background", action="store_true")
    build_figure_suite_parser.add_argument("--no-docx", action="store_true")
    build_figure_suite_parser.add_argument("--date")
    build_figure_suite_parser.add_argument("--source", default="")
    build_figure_suite_parser.add_argument("--title-prefix", default="")
    build_figure_suite_parser.add_argument("--max-figures", type=int, default=8)
    build_figure_suite_parser.add_argument("--narrative", action="store_true")

    build_app_parser = subparsers.add_parser(
        "build-app",
        help=WORKFLOW_DESCRIPTIONS["build-app"],
    )
    build_app_parser.add_argument("--target", default=".")
    build_app_parser.add_argument("--title", default="Insight App")
    build_app_parser.add_argument(
        "--description",
        default="Turn data analysis into an interactive Streamlit app.",
    )

    check_app_parser = subparsers.add_parser(
        "check-app-submission",
        help=WORKFLOW_DESCRIPTIONS["check-app-submission"],
    )
    check_app_parser.add_argument("--target", default=".")
    check_app_parser.add_argument("--entrypoint")
    check_app_parser.add_argument("--run-tests", action="store_true")

    prepare_app_parser = subparsers.add_parser(
        "prepare-app-repo",
        help=WORKFLOW_DESCRIPTIONS["prepare-app-repo"],
    )
    prepare_app_parser.add_argument("--source", required=True)
    prepare_app_parser.add_argument("--dest", required=True)
    prepare_app_parser.add_argument("--repo", default="")
    prepare_app_parser.add_argument("--entrypoint")
    prepare_app_parser.add_argument("--push", action="store_true")
    prepare_app_parser.add_argument("--force", action="store_true")

    build_context_parser = subparsers.add_parser(
        "build-context",
        help=WORKFLOW_DESCRIPTIONS["build-context"],
    )
    build_context_parser.add_argument("sources", nargs="*")

    build_week_context_parser = subparsers.add_parser(
        "build-week-context",
        help=WORKFLOW_DESCRIPTIONS["build-week-context"],
    )
    build_week_context_parser.add_argument("--target", default=".")

    outline_parser = subparsers.add_parser("outline", help=WORKFLOW_DESCRIPTIONS["outline"])
    outline_parser.add_argument("target", nargs="?")

    proofread_parser = subparsers.add_parser("proofread", help=WORKFLOW_DESCRIPTIONS["proofread"])
    proofread_parser.add_argument("target", nargs="?")
    proofread_parser.add_argument("--section")
    proofread_parser.add_argument("--lines")

    section_context_parser = subparsers.add_parser(
        "section-context",
        help=WORKFLOW_DESCRIPTIONS["section-context"],
    )
    section_context_parser.add_argument("section")
    section_context_parser.add_argument("target", nargs="?")

    check_citations_parser = subparsers.add_parser(
        "check-citations",
        help=WORKFLOW_DESCRIPTIONS["check-citations"],
    )
    check_citations_parser.add_argument("target", nargs="?")
    check_citations_parser.add_argument("--section")
    check_citations_parser.add_argument("--lines")

    latex_doctor_parser = subparsers.add_parser(
        "latex-doctor",
        help=WORKFLOW_DESCRIPTIONS["latex-doctor"],
    )
    latex_doctor_parser.add_argument("target", nargs="?")
    latex_doctor_parser.add_argument(
        "--mode",
        choices=["all", "comments", "markers", "compile"],
        default="all",
    )

    return parser


def handle_command(args: argparse.Namespace, *, root: Path, cwd: Path) -> tuple[int, list[str]]:
    """Dispatch a parsed workflow command."""

    if args.command == "list":
        lines = ["Available workflow helpers:"]
        for name, description in WORKFLOW_DESCRIPTIONS.items():
            if name == "list" or name in INTERNAL_WORKFLOWS:
                continue
            lines.append(f"- {name}: {description}")
        return 0, lines

    if args.command == "onboard":
        return onboard(root, cwd, check_only=args.check, rebuild=args.rebuild)

    if args.command == "audit-week":
        return audit_week(root, cwd, target=args.target, spec=args.spec)

    if args.command == "prepare-public-repo":
        return prepare_public_repo(
            root,
            cwd,
            dest=args.dest,
            force=args.force,
            init_git=args.init_git,
        )

    if args.command == "new-project":
        project_root, lines = create_project(
            root,
            name=args.name,
            description=args.description,
            datasets=args.datasets,
            notes=args.notes,
            with_app=args.with_app,
        )
        if args.setup_paper:
            title = args.title or args.name.replace("_", " ").title()
            _, paper_lines = setup_paper(
                root,
                project_root,
                title=title,
                authors="",
                topic=args.description,
                target=".",
                format=args.paper_format,
            )
            lines.extend(paper_lines)
        return 0, lines

    if args.command == "scaffold-week":
        _, lines = scaffold_week(root, cwd, target=args.target, title=args.title)
        return 0, lines

    if args.command == "setup-paper":
        target_dir, lines = setup_paper(
            root,
            cwd,
            title=args.title,
            authors=args.authors,
            topic=args.topic,
            target=args.target,
            format=args.format,
        )
        if args.format == "word":
            if args.no_compile:
                lines.append("Skipped compilation because Word reports do not compile here.")
            return 0, lines
        if args.no_compile:
            lines.append("Skipped compilation because --no-compile was requested.")
            return 0, lines
        main_tex = target_dir / "main.tex"
        try:
            compile_status, compile_lines = compile_tex(main_tex)
        except WorkflowError as exc:
            lines.append(str(exc))
            return 1, lines
        lines.extend(compile_lines)
        return compile_status, lines

    if args.command == "word-report":
        if args.title:
            _, lines = setup_word_report(
                root,
                cwd,
                title=args.title,
                authors=args.authors,
                topic=args.topic,
                target=args.target,
            )
            return 0, lines
        status, outline_lines = outline_report(root, cwd, target=args.target)
        proofread_status, proofread_lines = proofread_report(
            root,
            cwd,
            target=args.target,
            section_key=None,
            line_range=None,
        )
        return max(status, proofread_status), [*outline_lines, "", *proofread_lines]

    if args.command == "build-paper":
        tex_path = resolve_tex_target(root, cwd, target=args.target, include_decks=False)
        return compile_tex(tex_path, quick=args.quick)

    if args.command == "build-deck":
        tex_path = resolve_tex_target(root, cwd, target=args.target, include_decks=True)
        return compile_tex(tex_path, quick=False, use_bibtex=False)

    if args.command == "build-figure":
        return build_figure_examples(
            root,
            cwd,
            output=args.output,
            docx=args.docx,
            style=args.style,
            ft_background=args.ft_background,
            plotly_demo=args.plotly_demo,
        )

    if args.command == "build-figure-suite":
        return build_figure_suite(
            root,
            cwd,
            input_path=args.input,
            output=args.output,
            docx=not args.no_docx,
            style=args.style,
            ft_background=args.ft_background,
            date=args.date,
            source=args.source,
            title_prefix=args.title_prefix,
            max_figures=args.max_figures,
            narrative=args.narrative,
        )

    if args.command == "build-app":
        _, lines = build_app_scaffold(
            root,
            cwd,
            target=args.target,
            title=args.title,
            description=args.description,
        )
        return 0, lines

    if args.command == "check-app-submission":
        return check_app_submission(
            root,
            cwd,
            target=args.target,
            entrypoint=args.entrypoint,
            run_tests=args.run_tests,
        )

    if args.command == "prepare-app-repo":
        return prepare_app_repo(
            root,
            cwd,
            source=args.source,
            dest=args.dest,
            repo=args.repo,
            entrypoint=args.entrypoint,
            push=args.push,
            force=args.force,
        )

    if args.command == "build-context":
        _, lines = build_context(root, cwd, sources=args.sources)
        return 0, lines

    if args.command == "build-week-context":
        _, lines = build_week_context(root, cwd, target=args.target)
        return 0, lines

    if args.command == "outline":
        return outline_report(root, cwd, target=args.target)

    if args.command == "proofread":
        return proofread_report(
            root,
            cwd,
            target=args.target,
            section_key=args.section,
            line_range=args.lines,
        )

    if args.command == "section-context":
        return section_context_report(
            root,
            cwd,
            target=args.target,
            section_key=args.section,
        )

    if args.command == "check-citations":
        return check_citations_report(
            root,
            cwd,
            target=args.target,
            section_key=args.section,
            line_range=args.lines,
        )

    if args.command == "latex-doctor":
        return latex_doctor(root, cwd, target=args.target, mode=args.mode)

    raise WorkflowError(f"unknown command: {args.command}")  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    """Run the workflow CLI."""

    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        status, lines = handle_command(args, root=repo_root(), cwd=current_workdir())
    except WorkflowError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print_lines(lines)
    return status


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
