from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.score_render import render_human_jianpu
from songhelper.transcription import NoteEvent


def test_render_human_jianpu_outputs_bars() -> None:
    notes = [
        NoteEvent(0.0, 0.5, 0.5, 60, "C4", "1", 1.0),
        NoteEvent(0.5, 1.0, 0.5, 62, "D4", "2", 1.0),
        NoteEvent(1.5, 2.0, 0.5, 64, "E4", "3", 1.0),
    ]
    text = render_human_jianpu(notes, tempo=120.0, title="Test")
    assert "# Test" in text
    assert "|" in text
