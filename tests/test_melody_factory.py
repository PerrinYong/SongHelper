from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from songhelper.melody_factory.abc_converter import melody_spec_to_abc, parse_abc
from songhelper.melody_factory.audio_renderer import abc_to_audio
from songhelper.melody_factory.domain import MelodyBar, MelodySpec
from songhelper.melody_factory.midi_exporter import abc_to_midi
from songhelper.melody_factory.musicxml_exporter import abc_to_musicxml
from songhelper.melody_factory.preview_manifest import build_preview_manifest
from songhelper.melody_factory.score_renderer import build_musescore_render_command
from songhelper.melody_factory.schema import save_melody_spec, load_melody_spec
from songhelper.melody_factory.session_store import ensure_melody_factory_workspace
from songhelper.melody_factory.validator import validate_spec_with_report


def build_spec() -> MelodySpec:
    return MelodySpec(
        id="hook_a",
        title="Hook A",
        key="C minor",
        meter="4/4",
        tempo=76,
        bars=[
            MelodyBar(degrees="5 5 b6 5 3 0 2 1", rhythm="e e e e e e e e", lyrics="混 天 绫 在 风 里 燃"),
            MelodyBar(degrees="1 2 3 5 5 0 3 2", rhythm="e e e e e e e e", lyrics="少 年 身 上 火 未 熄"),
        ],
        highest_word="绫",
        cadence="stable",
        contour="mid-up-peak-fall",
    )


def test_melody_spec_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "spec.json"
    spec = build_spec()
    save_melody_spec(spec, path)
    loaded = load_melody_spec(path)
    assert loaded.title == spec.title
    assert len(loaded.bars) == 2


def test_melody_spec_to_abc_contains_headers() -> None:
    abc_text = melody_spec_to_abc(build_spec())
    assert "T:Hook A" in abc_text
    assert "K:Cm" in abc_text
    assert "w:" in abc_text


def test_parse_generated_abc_returns_events() -> None:
    headers, events = parse_abc(melody_spec_to_abc(build_spec()))
    assert headers["K"] == "Cm"
    assert events


def test_abc_to_midi_and_audio_write_files(tmp_path: Path) -> None:
    abc_path = tmp_path / "hook.abc"
    midi_path = tmp_path / "hook.mid"
    audio_path = tmp_path / "hook.wav"
    abc_path.write_text(melody_spec_to_abc(build_spec()), encoding="utf-8")
    abc_to_midi(abc_path.read_text(encoding="utf-8"), midi_path)
    abc_to_audio(abc_path.read_text(encoding="utf-8"), audio_path)
    assert midi_path.exists()
    assert audio_path.exists()
    assert audio_path.stat().st_size > 100


def test_ensure_melody_factory_workspace_creates_expected_dirs(tmp_path: Path) -> None:
    created = ensure_melody_factory_workspace(tmp_path, "混天绫")
    assert created
    assert (tmp_path / "workspace" / "混天绫" / "melody_factory" / "specs").exists()
    assert (tmp_path / "workspace" / "混天绫" / "melody_factory" / "session.json").exists()
    assert (tmp_path / "workspace" / "混天绫" / "melody_factory" / "inputs" / "sample.seed.json").exists()
    assert (tmp_path / "workspace" / "混天绫" / "melody_factory" / "specs" / "sample.mspec.json").exists()


def test_validate_spec_with_report_returns_valid() -> None:
    report = validate_spec_with_report(build_spec())
    assert report.valid is True
    assert not report.errors
    assert report.severity == "warning"
    assert report.spec_id == "hook_a"


def test_abc_to_musicxml_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "hook.musicxml"
    abc_to_musicxml(melody_spec_to_abc(build_spec()), out)
    assert out.exists()
    assert "score-partwise" in out.read_text(encoding="utf-8")


def test_build_musescore_render_command_uses_output_flag() -> None:
    cmd = build_musescore_render_command("in.musicxml", "out.wav", "MuseScore4.exe")
    assert cmd == ["MuseScore4.exe", "-o", "out.wav", "in.musicxml"]


def test_build_preview_manifest_collects_candidate_files(tmp_path: Path) -> None:
    song_root = tmp_path / "workspace" / "混天绫"
    factory_root = song_root / "melody_factory"
    (factory_root / "specs").mkdir(parents=True)
    (factory_root / "abc").mkdir(parents=True)
    (factory_root / "midi").mkdir(parents=True)
    (factory_root / "audio").mkdir(parents=True)
    (factory_root / "exports").mkdir(parents=True)
    (factory_root / "specs" / "hook_a.json").write_text("{}", encoding="utf-8")
    manifest = build_preview_manifest(song_root)
    assert manifest["candidate_count"] == 1
    assert manifest["candidates"][0]["id"] == "hook_a"
