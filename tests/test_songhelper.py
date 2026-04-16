from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.capabilities import render_capabilities
from songhelper.project import ensure_workspace
from songhelper.workflows import render_workflow


def test_render_capabilities_contains_core_sections() -> None:
    output = render_capabilities()
    assert "创作与策划" in output
    assert "vocal/instrument 分离" in output


def test_render_workflow_contains_expected_step() -> None:
    output = render_workflow()
    assert "灵感与方向定义" in output
    assert "混音审听与导出" in output


def test_ensure_workspace_creates_expected_directories(tmp_path: Path) -> None:
    created = ensure_workspace(tmp_path)
    assert created
    assert (tmp_path / "workspace" / "analysis").exists()
    assert (tmp_path / "workspace" / "exports").exists()
