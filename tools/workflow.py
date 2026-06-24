#!/usr/bin/env python3
"""Shared deterministic workflow entrypoint for fins-agent."""

from __future__ import annotations

try:  # pragma: no cover - import path depends on how the script is launched
    from .workflow_lib import main
except ImportError:  # pragma: no cover
    from workflow_lib import main


if __name__ == "__main__":
    raise SystemExit(main())
