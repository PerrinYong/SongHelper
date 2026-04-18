from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

REVERB_PRESETS = {
    "small_room": "aecho=0.8:0.7:40|80:0.25|0.15",
    "hall": "aecho=0.8:0.8:60|120|180:0.30|0.22|0.12",
    "plate": "aecho=0.8:0.75:20|40|70:0.30|0.22|0.12",
}


def run_command(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Command failed")


def build_concat_command(list_path: str, output_path: str) -> list[str]:
    return [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_path,
        "-c",
        "copy",
        output_path,
    ]


def concat_audio(inputs: list[Path], output_path: Path) -> None:
    for input_path in inputs:
        if not input_path.exists():
            raise FileNotFoundError(f"Missing input: {input_path}")
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    ) as handle:
        for input_path in inputs:
            handle.write(f"file '{input_path.resolve()}'\n")
        list_path = handle.name
    run_command(build_concat_command(list_path, str(output_path)))


def build_reverb_command(input_path: str, output_path: str, preset: str) -> list[str]:
    return ["ffmpeg", "-y", "-i", input_path, "-af", REVERB_PRESETS[preset], output_path]


def apply_reverb(input_path: Path, output_path: Path, preset: str) -> None:
    if preset not in REVERB_PRESETS:
        raise ValueError(f"Unknown preset: {preset}")
    run_command(build_reverb_command(str(input_path), str(output_path), preset))


def build_normalize_command(
    input_path: str,
    output_path: str,
    integrated_lufs: float,
    true_peak: float,
    loudness_range: float,
) -> list[str]:
    filt = f"loudnorm=I={integrated_lufs}:TP={true_peak}:LRA={loudness_range}"
    return ["ffmpeg", "-y", "-i", input_path, "-af", filt, output_path]


def normalize_audio(
    input_path: Path,
    output_path: Path,
    integrated_lufs: float = -16.0,
    true_peak: float = -1.5,
    loudness_range: float = 11.0,
) -> None:
    run_command(
        build_normalize_command(
            str(input_path),
            str(output_path),
            integrated_lufs,
            true_peak,
            loudness_range,
        )
    )
