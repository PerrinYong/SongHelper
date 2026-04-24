from __future__ import annotations

from pathlib import Path

import mido

from .abc_converter import melody_spec_to_events, parse_abc
from .domain import MelodySpec


def _write_midi_from_events(events, output_path: Path, tempo_bpm: float) -> None:
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0))
    current_tick = 0
    for event in events:
        start_tick = int(round(event.start_beats * 480))
        duration_tick = max(1, int(round(event.duration_beats * 480)))
        if event.midi is None:
            current_tick = max(current_tick, start_tick + duration_tick)
            continue
        delta = max(0, start_tick - current_tick)
        track.append(mido.Message("note_on", note=event.midi, velocity=72, time=delta))
        track.append(mido.Message("note_off", note=event.midi, velocity=0, time=duration_tick))
        current_tick = start_tick + duration_tick
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mid.save(output_path)


def melody_spec_to_midi(spec: MelodySpec, output_path: Path) -> None:
    _write_midi_from_events(melody_spec_to_events(spec), output_path, float(spec.tempo))


def abc_to_midi(abc_text: str, output_path: Path) -> None:
    headers, events = parse_abc(abc_text)
    tempo = float(headers.get("Q", "120").split("=")[-1])
    _write_midi_from_events(events, output_path, tempo)
