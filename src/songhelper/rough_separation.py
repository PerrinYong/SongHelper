from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


def center_extract(y_stereo: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    left = y_stereo[0]
    right = y_stereo[1]
    center = (left + right) / 2.0
    side = (left - right) / 2.0
    return center, side


def rough_separate(input_path: Path, output_dir: Path, mode: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if mode == "hpss":
        y, sr = librosa.load(str(input_path), sr=None, mono=True)
        harmonic, percussive = librosa.effects.hpss(y)
        harmonic_path = output_dir / "harmonic.wav"
        percussive_path = output_dir / "percussive.wav"
        sf.write(harmonic_path, harmonic, sr)
        sf.write(percussive_path, percussive, sr)
        written.extend([harmonic_path, percussive_path])
        return written
    if mode == "center":
        y, sr = librosa.load(str(input_path), sr=None, mono=False)
        if y.ndim == 1:
            raise ValueError("Center extraction expects stereo audio; input appears mono.")
        center, side = center_extract(y)
        center_path = output_dir / "center_mono.wav"
        side_path = output_dir / "side_mono.wav"
        minus_center_path = output_dir / "minus_center_stereo.wav"
        sf.write(center_path, center, sr)
        sf.write(side_path, side, sr)
        sf.write(minus_center_path, np.vstack([side, -side]).T, sr)
        written.extend([center_path, side_path, minus_center_path])
        return written
    raise ValueError(f"Unsupported separation mode: {mode}")
