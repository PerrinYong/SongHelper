from __future__ import annotations

import sys
from pathlib import Path

import mido


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.midi_tools import export_midi_to_jianpu


def test_export_midi_to_jianpu(tmp_path: Path) -> None:
    midi_path = tmp_path / "test.mid"
    out_path = tmp_path / "test.txt"
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message("note_on", note=60, velocity=64, time=0))
    track.append(mido.Message("note_off", note=60, velocity=0, time=480))
    mid.save(midi_path)

    export_midi_to_jianpu(midi_path, out_path, tonic="C", mode="major")

    content = out_path.read_text(encoding="utf-8")
    assert "简谱" in content
    assert "\t60\t1" in content
