from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.music_theory import detect_key_from_chroma, midi_to_jianpu


def test_detect_key_from_c_major_profile() -> None:
    chroma = [10.0, 0.1, 4.0, 0.1, 5.0, 6.0, 0.1, 7.0, 0.1, 3.0, 0.1, 2.0]
    result = detect_key_from_chroma(chroma)
    assert result["tonic"] == "C"
    assert result["mode"] == "major"


def test_midi_to_jianpu_major_mapping() -> None:
    assert midi_to_jianpu(60, tonic_pc=0, mode="major") == "1"
    assert midi_to_jianpu(62, tonic_pc=0, mode="major") == "2"
    assert midi_to_jianpu(63, tonic_pc=0, mode="major") == "b3"
