from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import librosa
import mido
import numpy as np

from .music_theory import detect_key_from_chroma, midi_to_jianpu


@dataclass
class NoteEvent:
    start_sec: float
    end_sec: float
    duration_sec: float
    midi: int
    note_name: str
    jianpu: str
    beats: float


def _note_name(midi_note: int) -> str:
    return librosa.midi_to_note(int(midi_note))


def extract_note_events(
    audio_path: Path,
    tempo: float | None = None,
    tonic_hint: str | None = None,
    mode_hint: str | None = None,
) -> tuple[list[NoteEvent], dict[str, str | int | float]]:
    y, sr = librosa.load(audio_path, sr=22050, mono=True)
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        frame_length=2048,
        hop_length=256,
    )
    times = librosa.times_like(f0, sr=sr, hop_length=256)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_info = detect_key_from_chroma(chroma.mean(axis=1).tolist())
    tonic_pc = int(key_info["tonic_pc"])
    mode = str(key_info["mode"])
    if tonic_hint:
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        tonic_pc = note_names.index(tonic_hint)
    if mode_hint:
        mode = mode_hint

    if tempo is None or tempo <= 0:
        tempo_detected, _ = librosa.beat.beat_track(y=y, sr=sr, trim=False)
        tempo = float(np.atleast_1d(tempo_detected)[0])

    notes: list[NoteEvent] = []
    start_idx: int | None = None
    midi_values = librosa.hz_to_midi(f0)
    for i, voiced in enumerate(voiced_flag):
        if bool(voiced) and start_idx is None:
            start_idx = i
        if start_idx is not None and (i == len(voiced_flag) - 1 or not bool(voiced)):
            end_idx = i if not bool(voiced) else i + 1
            segment = midi_values[start_idx:end_idx]
            segment = segment[~np.isnan(segment)]
            if len(segment) == 0:
                start_idx = None
                continue
            midi_note = int(round(float(np.median(segment))))
            start_sec = float(times[start_idx])
            end_sec = float(times[end_idx - 1] + 256 / sr)
            duration = max(0.0, end_sec - start_sec)
            if duration < 0.08:
                start_idx = None
                continue
            beats = duration / (60.0 / tempo)
            notes.append(
                NoteEvent(
                    start_sec=round(start_sec, 3),
                    end_sec=round(end_sec, 3),
                    duration_sec=round(duration, 3),
                    midi=midi_note,
                    note_name=_note_name(midi_note),
                    jianpu=midi_to_jianpu(midi_note, tonic_pc, mode),
                    beats=round(beats, 3),
                )
            )
            start_idx = None

    return notes, {"tempo": round(float(tempo), 2), "tonic_pc": tonic_pc, "mode": mode}


def write_midi(note_events: list[NoteEvent], midi_path: Path, tempo_bpm: float) -> None:
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    tempo_meta = mido.bpm2tempo(tempo_bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo_meta, time=0))

    current_tick = 0
    for event in note_events:
        start_tick = int(round(event.start_sec / (60.0 / tempo_bpm) * 480))
        duration_tick = max(60, int(round(event.beats * 480)))
        delta = max(0, start_tick - current_tick)
        track.append(mido.Message("note_on", note=event.midi, velocity=72, time=delta))
        track.append(
            mido.Message("note_off", note=event.midi, velocity=0, time=duration_tick)
        )
        current_tick = start_tick + duration_tick
    midi_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(midi_path)


def write_jianpu(note_events: list[NoteEvent], jianpu_path: Path) -> None:
    lines = ["# 简谱草稿", "# 格式: 序号\t开始(s)\t时长(s)\t时值(拍)\t音名\t简谱"]
    for idx, event in enumerate(note_events, start=1):
        lines.append(
            f"{idx}\t{event.start_sec:.3f}\t{event.duration_sec:.3f}\t{event.beats:.3f}\t{event.note_name}\t{event.jianpu}"
        )
    jianpu_path.parent.mkdir(parents=True, exist_ok=True)
    jianpu_path.write_text("\n".join(lines), encoding="utf-8")


def save_transcription(
    audio_path: Path,
    midi_path: Path,
    jianpu_path: Path,
    json_path: Path,
    tempo: float | None = None,
    tonic_hint: str | None = None,
    mode_hint: str | None = None,
) -> dict[str, str | int | float]:
    notes, meta = extract_note_events(
        audio_path, tempo=tempo, tonic_hint=tonic_hint, mode_hint=mode_hint
    )
    write_midi(notes, midi_path, float(meta["tempo"]))
    write_jianpu(notes, jianpu_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "file": str(audio_path),
        "tempo": meta["tempo"],
        "mode": meta["mode"],
        "tonic_pc": meta["tonic_pc"],
        "note_count": len(notes),
        "notes": [asdict(note) for note in notes],
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload
