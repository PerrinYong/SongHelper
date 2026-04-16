from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import librosa.segment
import numpy as np

from .music_theory import detect_key_from_chroma


@dataclass
class Section:
    index: int
    label: str
    start_sec: float
    end_sec: float
    duration_sec: float


@dataclass
class AudioAnalysisResult:
    file: str
    duration_sec: float
    sample_rate: int
    bpm: float
    beat_count: int
    key: str
    key_confidence: float
    sections: list[Section]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["sections"] = [asdict(section) for section in self.sections]
        return data


def _assign_section_labels(segment_chroma: list[np.ndarray]) -> list[str]:
    labels: list[str] = []
    prototypes: list[np.ndarray] = []
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for chroma in segment_chroma:
        if not prototypes:
            prototypes.append(chroma)
            labels.append(alphabet[0])
            continue
        sims = []
        for proto in prototypes:
            denom = float(np.linalg.norm(proto) * np.linalg.norm(chroma))
            sims.append(float(np.dot(proto, chroma) / denom) if denom else 0.0)
        best_idx = int(np.argmax(sims))
        if sims[best_idx] >= 0.96:
            labels.append(alphabet[best_idx])
            prototypes[best_idx] = (prototypes[best_idx] + chroma) / 2
        else:
            prototypes.append(chroma)
            labels.append(alphabet[len(prototypes) - 1])
    return labels


def analyze_audio(audio_path: Path) -> AudioAnalysisResult:
    y, sr = librosa.load(audio_path, sr=22050, mono=True)
    duration = librosa.get_duration(y=y, sr=sr)

    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, trim=False)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    rms = librosa.feature.rms(y=y)[0][None, :]

    if len(beat_frames) >= 8:
        chroma_sync = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
        mfcc_sync = librosa.util.sync(mfcc, beat_frames, aggregate=np.mean)
        rms_sync = librosa.util.sync(rms, beat_frames, aggregate=np.mean)
        features = np.vstack(
            [
                librosa.util.normalize(chroma_sync),
                librosa.util.normalize(mfcc_sync),
                librosa.util.normalize(rms_sync),
            ]
        )
        target_segments = max(6, min(12, int(round(duration / 24))))
        boundaries = [
            int(x)
            for x in np.atleast_1d(
                librosa.segment.agglomerative(features, k=target_segments)
            ).tolist()
        ]
        boundaries.append(len(beat_times) - 1)
        boundaries = sorted({idx for idx in boundaries if 0 <= idx < len(beat_times)})
    else:
        boundaries = [0, len(beat_times) - 1] if len(beat_times) else [0]

    if len(boundaries) < 2:
        boundaries = [0, len(beat_times) - 1] if len(beat_times) > 1 else [0, 0]

    global_chroma = chroma.mean(axis=1).tolist()
    key_info = detect_key_from_chroma(global_chroma)

    sections: list[Section] = []
    segment_chroma: list[np.ndarray] = []
    section_bounds: list[tuple[float, float]] = []
    for start_idx, end_idx in zip(boundaries[:-1], boundaries[1:]):
        start_sec = float(beat_times[start_idx]) if len(beat_times) else 0.0
        end_sec = float(beat_times[end_idx]) if len(beat_times) else duration
        if end_sec <= start_sec:
            continue
        start_frame = librosa.time_to_frames(start_sec, sr=sr)
        end_frame = max(start_frame + 1, librosa.time_to_frames(end_sec, sr=sr))
        mean_chroma = chroma[:, start_frame:end_frame].mean(axis=1)
        segment_chroma.append(mean_chroma)
        section_bounds.append((start_sec, end_sec))

    labels = _assign_section_labels(segment_chroma) if segment_chroma else ["A"]

    for idx, ((start_sec, end_sec), label) in enumerate(
        zip(section_bounds, labels), start=1
    ):
        sections.append(
            Section(
                index=idx,
                label=label,
                start_sec=round(start_sec, 2),
                end_sec=round(end_sec, 2),
                duration_sec=round(end_sec - start_sec, 2),
            )
        )

    if not sections:
        sections = [
            Section(
                index=1,
                label="A",
                start_sec=0.0,
                end_sec=round(duration, 2),
                duration_sec=round(duration, 2),
            )
        ]
    return AudioAnalysisResult(
        file=str(audio_path),
        duration_sec=round(float(duration), 2),
        sample_rate=sr,
        bpm=round(float(np.atleast_1d(tempo)[0]), 2),
        beat_count=int(len(beat_times)),
        key=f"{key_info['tonic']} {key_info['mode']}",
        key_confidence=round(float(key_info["score"]), 3),
        sections=sections,
    )


def save_analysis(audio_path: Path, output_path: Path) -> AudioAnalysisResult:
    result = analyze_audio(audio_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result
