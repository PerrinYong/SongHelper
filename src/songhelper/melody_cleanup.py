from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .music_theory import midi_to_jianpu, note_name
from .transcription import NoteEvent, write_jianpu, write_midi


def load_note_events(
    json_path: Path,
) -> tuple[list[NoteEvent], dict[str, str | int | float]]:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    notes = [NoteEvent(**item) for item in payload["notes"]]
    meta = {
        "file": payload["file"],
        "tempo": payload["tempo"],
        "mode": payload["mode"],
        "tonic_pc": payload["tonic_pc"],
    }
    return notes, meta


def _rebuild_note(event: NoteEvent, tonic_pc: int, mode: str) -> NoteEvent:
    beats = (
        round(event.duration_sec / (60.0 / 143.55), 3)
        if event.beats <= 0
        else event.beats
    )
    return NoteEvent(
        start_sec=round(event.start_sec, 3),
        end_sec=round(event.end_sec, 3),
        duration_sec=round(event.end_sec - event.start_sec, 3),
        midi=int(event.midi),
        note_name=note_name(int(event.midi) % 12) + str(int(event.midi) // 12 - 1),
        jianpu=midi_to_jianpu(int(event.midi), tonic_pc, mode),
        beats=round(beats, 3),
    )


def _with_tempo(event: NoteEvent, tonic_pc: int, mode: str, tempo: float) -> NoteEvent:
    return NoteEvent(
        start_sec=round(event.start_sec, 3),
        end_sec=round(event.end_sec, 3),
        duration_sec=round(event.end_sec - event.start_sec, 3),
        midi=int(event.midi),
        note_name=note_name(int(event.midi) % 12) + str(int(event.midi) // 12 - 1),
        jianpu=midi_to_jianpu(int(event.midi), tonic_pc, mode),
        beats=round((event.end_sec - event.start_sec) / (60.0 / tempo), 3),
    )


def clean_note_events(
    notes: list[NoteEvent],
    tonic_pc: int,
    mode: str,
    tempo: float,
    min_duration_sec: float = 0.12,
    max_midi: int | None = None,
    spike_interval: int = 9,
    neighbor_tolerance: int = 4,
    merge_gap_sec: float = 0.08,
) -> tuple[list[NoteEvent], dict[str, int | float]]:
    if not notes:
        return [], {"input_count": 0, "output_count": 0}

    durations = np.array([note.duration_sec for note in notes], dtype=float)
    pitches = np.array([note.midi for note in notes], dtype=int)
    inferred_max = (
        int(np.percentile(pitches[durations >= min_duration_sec], 97))
        if np.any(durations >= min_duration_sec)
        else int(np.percentile(pitches, 97))
    )
    effective_max_midi = max_midi if max_midi is not None else max(84, inferred_max)

    filtered: list[NoteEvent] = []
    removed_short = 0
    removed_high = 0
    removed_spike = 0

    for idx, note in enumerate(notes):
        if note.duration_sec < min_duration_sec:
            removed_short += 1
            continue
        if note.midi > effective_max_midi:
            removed_high += 1
            continue
        prev_note = notes[idx - 1] if idx > 0 else None
        next_note = notes[idx + 1] if idx + 1 < len(notes) else None
        if prev_note and next_note:
            prev_diff = abs(note.midi - prev_note.midi)
            next_diff = abs(note.midi - next_note.midi)
            neighbor_diff = abs(prev_note.midi - next_note.midi)
            if (
                prev_diff >= spike_interval
                and next_diff >= spike_interval
                and neighbor_diff <= neighbor_tolerance
                and note.duration_sec <= 0.24
            ):
                removed_spike += 1
                continue
        filtered.append(note)

    merged: list[NoteEvent] = []
    for note in filtered:
        if not merged:
            merged.append(note)
            continue
        last = merged[-1]
        gap = note.start_sec - last.end_sec
        if note.midi == last.midi and gap <= merge_gap_sec:
            merged[-1] = NoteEvent(
                start_sec=last.start_sec,
                end_sec=note.end_sec,
                duration_sec=round(note.end_sec - last.start_sec, 3),
                midi=last.midi,
                note_name=last.note_name,
                jianpu=last.jianpu,
                beats=round((note.end_sec - last.start_sec) / (60.0 / tempo), 3),
            )
            continue
        merged.append(note)

    cleaned = [_with_tempo(note, tonic_pc, mode, tempo) for note in merged]
    stats = {
        "input_count": len(notes),
        "output_count": len(cleaned),
        "removed_short": removed_short,
        "removed_high": removed_high,
        "removed_spike": removed_spike,
        "max_midi": effective_max_midi,
    }
    return cleaned, stats


def save_cleaned_melody(
    input_json_path: Path,
    midi_path: Path,
    jianpu_path: Path,
    json_path: Path,
    min_duration_sec: float = 0.12,
    max_midi: int | None = None,
) -> dict[str, int | float | str]:
    notes, meta = load_note_events(input_json_path)
    tempo = float(meta["tempo"])
    tonic_pc = int(meta["tonic_pc"])
    mode = str(meta["mode"])
    cleaned, stats = clean_note_events(
        notes,
        tonic_pc=tonic_pc,
        mode=mode,
        tempo=tempo,
        min_duration_sec=min_duration_sec,
        max_midi=max_midi,
    )
    write_midi(cleaned, midi_path, tempo)
    write_jianpu(cleaned, jianpu_path)
    payload = {
        "file": str(input_json_path),
        "tempo": tempo,
        "mode": mode,
        "tonic_pc": tonic_pc,
        "note_count": len(cleaned),
        "notes": [asdict(note) for note in cleaned],
        "cleanup": stats,
    }
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return payload
