"""Smoke test for the dff 50-stock portfolio app."""

from __future__ import annotations

import os
import platform
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
VIEWS = {
    "Overview": "Portfolio comparison",
    "Portfolio Weights": "Portfolio weights",
    "Historical Performance": "Historical in-sample performance",
    "Efficient Frontier": "Efficient frontier",
    "Data": "Data and downloads",
    "Methodology": "Methodology",
}


@pytest.mark.skipif(
    platform.system() == "Windows"
    and not os.environ.get("RUN_STREAMLIT_APPTEST_ON_WINDOWS"),
    reason=(
        "Streamlit AppTest can leave locked temp files on native Windows; "
        "run in Linux CI or set RUN_STREAMLIT_APPTEST_ON_WINDOWS=1."
    ),
)
@pytest.mark.parametrize("view,expected", list(VIEWS.items()))
def test_dff_app_each_tab(view, expected, monkeypatch) -> None:
    temp_root = ROOT / ".tmp-streamlit-app-test"
    temp_root.mkdir(exist_ok=True)
    monkeypatch.setenv("TMP", str(temp_root))
    monkeypatch.setenv("TEMP", str(temp_root))
    tempfile.tempdir = str(temp_root)

    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "streamlit_app.py"
    at = AppTest.from_file(app_path, default_timeout=60)
    at.query_params["view"] = view
    at.query_params["sample"] = "1Y"
    at.run()
    assert not at.exception, f"{view} tab raised: {at.exception}"
    rendered_text = "\n".join(
        str(element.value)
        for collection in [
            at.title,
            at.subheader,
            at.caption,
            at.markdown,
            at.info,
            at.warning,
            at.button,
            getattr(at, "download_button", []),
        ]
        for element in collection
    )
    assert "50-Stock U.S. Equity Portfolio Comparison" in rendered_text
    assert expected in rendered_text
