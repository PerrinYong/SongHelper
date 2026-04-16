from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.melody_cleanup import clean_note_events
from songhelper.transcription import NoteEvent


def test_clean_note_events_removes_short_high_and_spikes() -> None:
    notes = [
        NoteEvent(0.0, 0.3, 0.3, 60, "C4", "1", 0.75),
        NoteEvent(0.3, 0.38, 0.08, 61, "C#4", "#1", 0.2),
        NoteEvent(0.4, 0.58, 0.18, 89, "F6", "4''", 0.45),
        NoteEvent(0.6, 1.0, 0.4, 62, "D4", "2", 1.0),
        NoteEvent(1.05, 1.23, 0.18, 74, "D5", "2'", 0.45),
        NoteEvent(1.25, 1.65, 0.4, 63, "D#4", "b3", 1.0),
    ]
    cleaned, stats = clean_note_events(
        notes, tonic_pc=0, mode="major", tempo=120.0, min_duration_sec=0.12, max_midi=84
    )
    assert [note.midi for note in cleaned] == [60, 62, 63]
    assert stats["removed_short"] == 1
    assert stats["removed_high"] == 1
    assert stats["removed_spike"] == 1
