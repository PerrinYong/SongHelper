from __future__ import annotations

from pathlib import Path

from .abc_converter import melody_spec_to_abc, save_abc
from .audio_renderer import abc_to_audio, melody_spec_to_audio
from .midi_exporter import abc_to_midi, melody_spec_to_midi
from .musicxml_exporter import abc_to_musicxml, melody_spec_to_musicxml
from .preview_manifest import save_preview_manifest
from .schema import load_melody_spec
from .score_renderer import render_score_to_audio
from .session_store import ensure_melody_factory_workspace
from .validator import validate_spec_file


def init_melody_factory(root: Path, song_name: str) -> list[Path]:
    return ensure_melody_factory_workspace(root, song_name)


def export_spec_to_abc(spec_path: Path, output_path: Path) -> str:
    spec = load_melody_spec(spec_path)
    abc_text = melody_spec_to_abc(spec)
    save_abc(abc_text, output_path)
    return abc_text


def export_spec_to_midi(spec_path: Path, output_path: Path) -> None:
    spec = load_melody_spec(spec_path)
    melody_spec_to_midi(spec, output_path)


def export_spec_to_audio(spec_path: Path, output_path: Path) -> None:
    spec = load_melody_spec(spec_path)
    melody_spec_to_audio(spec, output_path)


def export_spec_to_musicxml(spec_path: Path, output_path: Path) -> None:
    spec = load_melody_spec(spec_path)
    melody_spec_to_musicxml(spec, output_path)


def export_abc_to_midi(abc_path: Path, output_path: Path) -> None:
    abc_to_midi(abc_path.read_text(encoding="utf-8"), output_path)


def export_abc_to_audio(abc_path: Path, output_path: Path) -> None:
    abc_to_audio(abc_path.read_text(encoding="utf-8"), output_path)


def export_abc_to_musicxml(abc_path: Path, output_path: Path) -> None:
    abc_to_musicxml(abc_path.read_text(encoding="utf-8"), output_path)


def validate_spec(spec_path: Path, output_path: Path | None = None):
    return validate_spec_file(spec_path, output_path)


def render_notation_to_audio(input_path: Path, output_path: Path, musescore_executable: str | None = None) -> None:
    render_score_to_audio(input_path, output_path, musescore_executable)


def build_preview_manifest(song_root: Path, output_path: Path | None = None):
    return save_preview_manifest(song_root, output_path)
