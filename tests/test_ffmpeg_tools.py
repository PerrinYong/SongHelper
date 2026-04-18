from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.ffmpeg_tools import (
    REVERB_PRESETS,
    build_concat_command,
    build_normalize_command,
    build_reverb_command,
)


def test_reverb_presets_include_expected_values() -> None:
    assert "hall" in REVERB_PRESETS
    assert "aecho" in REVERB_PRESETS["hall"]


def test_build_concat_command_contains_concat_flags() -> None:
    cmd = build_concat_command("list.txt", "out.wav")
    assert cmd[:6] == ["ffmpeg", "-y", "-f", "concat", "-safe", "0"]
    assert cmd[-1] == "out.wav"


def test_build_normalize_command_contains_loudnorm() -> None:
    cmd = build_normalize_command("in.wav", "out.wav", -16.0, -1.5, 11.0)
    assert "loudnorm=I=-16.0:TP=-1.5:LRA=11.0" in cmd


def test_build_reverb_command_uses_selected_preset() -> None:
    cmd = build_reverb_command("in.wav", "out.wav", "plate")
    assert REVERB_PRESETS["plate"] in cmd
