from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def resolve_musescore_executable(explicit_path: str | None = None) -> str:
    candidates = [explicit_path] if explicit_path else []
    candidates.extend(["musescore", "MuseScore4.exe", "MuseScore3.exe", "mscore"])
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    raise FileNotFoundError("MuseScore executable not found. Provide --musescore or install MuseScore CLI.")


def build_musescore_render_command(input_path: str, output_path: str, musescore_executable: str) -> list[str]:
    return [musescore_executable, "-o", output_path, input_path]


def render_score_to_audio(input_path: Path, output_path: Path, musescore_executable: str | None = None) -> None:
    exe = resolve_musescore_executable(musescore_executable)
    command = build_musescore_render_command(str(input_path), str(output_path), exe)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "MuseScore render failed")
