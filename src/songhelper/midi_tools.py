from __future__ import annotations

from pathlib import Path

import mido

from .music_theory import midi_to_jianpu

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def export_midi_to_jianpu(
    midi_path: Path, output_path: Path, tonic: str, mode: str
) -> None:
    tonic_pc = NOTE_NAMES.index(tonic)
    mid = mido.MidiFile(midi_path)
    absolute_ticks = 0
    active_notes: dict[int, int] = {}
    rows: list[str] = ["# MIDI 转简谱", "# 格式: 序号\t开始(拍)\t时值(拍)\tMIDI\t简谱"]
    index = 1

    for msg in mid.tracks[0]:
        absolute_ticks += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            active_notes[msg.note] = absolute_ticks
        elif msg.type in {"note_off", "note_on"} and msg.note in active_notes:
            start_tick = active_notes.pop(msg.note)
            duration_tick = max(1, absolute_ticks - start_tick)
            start_beats = start_tick / mid.ticks_per_beat
            duration_beats = duration_tick / mid.ticks_per_beat
            rows.append(
                f"{index}\t{start_beats:.3f}\t{duration_beats:.3f}\t{msg.note}\t{midi_to_jianpu(msg.note, tonic_pc, mode)}"
            )
            index += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(rows), encoding="utf-8")
