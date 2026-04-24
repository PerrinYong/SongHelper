from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.lrc_tools import (
    build_lrc_text,
    format_lrc_timestamp,
    generate_lrc_from_files,
    normalize_lyrics_text,
)


def test_format_lrc_timestamp_formats_minutes_seconds_centiseconds() -> None:
    assert format_lrc_timestamp(83.24) == "01:23.24"


def test_normalize_lyrics_text_skips_blank_and_section_headers() -> None:
    text = "\n[Verse 1]\n第一行\n\n第二行\n"
    assert normalize_lyrics_text(text) == ["第一行", "第二行"]


def test_build_lrc_text_uses_segment_starts() -> None:
    lines = ["第一行", "第二行"]
    text = build_lrc_text(lines, [1.2, 3.4], title="测试")
    assert "[ti:测试]" in text
    assert "[00:01.20]第一行" in text
    assert "[00:03.40]第二行" in text


def test_generate_lrc_from_files_writes_output(tmp_path: Path) -> None:
    lyrics_path = tmp_path / "lyrics.txt"
    segments_path = tmp_path / "segments.json"
    output_path = tmp_path / "out.lrc"
    lyrics_path.write_text("第一行\n第二行\n", encoding="utf-8")
    segments_path.write_text(
        json.dumps({"segments": [{"start": 0.0}, {"start": 2.5}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    generate_lrc_from_files(lyrics_path, segments_path, output_path, title="测试")
    content = output_path.read_text(encoding="utf-8")
    assert "[00:00.00]第一行" in content
    assert "[00:02.50]第二行" in content
