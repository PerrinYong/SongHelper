from __future__ import annotations

import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from .music_theory import detect_key_from_chroma


def probe_audio_file(input_path: Path) -> dict[str, object]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    info = sf.info(str(input_path))
    y, sr = librosa.load(str(input_path), sr=None, mono=True)
    duration = float(len(y) / sr)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    zero_cross = librosa.feature.zero_crossing_rate(y)[0]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key = detect_key_from_chroma(chroma.mean(axis=1).tolist())

    return {
        "file": str(input_path),
        "format": info.format,
        "samplerate": info.samplerate,
        "channels": info.channels,
        "frames": info.frames,
        "duration_sec": round(duration, 3),
        "tempo_bpm_estimate": round(float(np.atleast_1d(tempo)[0]), 3),
        "beat_count_estimate": int(len(beat_frames)),
        "key_estimate": f"{key['tonic']} {key['mode']}",
        "key_confidence": round(float(key["score"]), 4),
        "rms_mean": round(float(rms.mean()), 6),
        "rms_std": round(float(rms.std()), 6),
        "spectral_centroid_mean": round(float(spectral_centroid.mean()), 3),
        "zero_crossing_rate_mean": round(float(zero_cross.mean()), 6),
        "note": "BPM and key are rough estimates and should be verified by ear.",
    }


def save_audio_probe(input_path: Path, output_path: Path | None = None) -> dict[str, object]:
    result = probe_audio_file(input_path)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return result
