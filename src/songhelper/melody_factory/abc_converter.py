from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .domain import MelodySpec
from .schema import validate_melody_spec

NOTE_TO_PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
PC_TO_ABC_SHARP = {0: "C", 1: "^C", 2: "D", 3: "^D", 4: "E", 5: "F", 6: "^F", 7: "G", 8: "^G", 9: "A", 10: "^A", 11: "B"}
MAJOR_SCALE = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
MINOR_SCALE = {1: 0, 2: 2, 3: 3, 4: 5, 5: 7, 6: 8, 7: 10}
RHYTHM_TO_BEATS = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25, "w.": 6.0, "h.": 3.0, "q.": 1.5, "e.": 0.75}


@dataclass
class ParsedEvent:
    start_beats: float
    duration_beats: float
    midi: int | None
    lyric: str | None = None


def parse_key(key: str) -> tuple[str, str]:
    parts = key.split()
    if len(parts) != 2:
        raise ValueError(f"Unsupported key format: {key}")
    tonic, mode = parts[0], parts[1].lower()
    if tonic not in NOTE_TO_PC:
        raise ValueError(f"Unsupported tonic: {tonic}")
    if mode not in {"major", "minor"}:
        raise ValueError(f"Unsupported mode: {mode}")
    return tonic, mode


def parse_degree_token(token: str, tonic: str, mode: str, tonic_octave: int = 4) -> int | None:
    if token == "0":
        return None
    match = re.fullmatch(r"([b#]*)([0-7])([',]*)", token)
    if not match:
        raise ValueError(f"Unsupported degree token: {token}")
    accidental_marks, degree_raw, octave_marks = match.groups()
    degree = int(degree_raw)
    if degree == 0:
        return None
    scale = MAJOR_SCALE if mode == "major" else MINOR_SCALE
    semitone = scale[degree]
    semitone += accidental_marks.count("#")
    semitone -= accidental_marks.count("b")
    octave_shift = octave_marks.count("'") - octave_marks.count(",")
    tonic_midi = 12 * (tonic_octave + 1) + NOTE_TO_PC[tonic]
    return tonic_midi + semitone + 12 * octave_shift


def midi_to_abc_note(midi: int) -> str:
    pc = midi % 12
    octave = midi // 12 - 1
    note = PC_TO_ABC_SHARP[pc]
    if octave >= 5:
        note = note.lower()
        note += "'" * max(0, octave - 5)
    elif octave == 4:
        pass
    else:
        note += "," * (4 - octave)
    return note


def beats_to_abc_length(duration_beats: float) -> str:
    units = int(round(duration_beats / 0.5))
    if units <= 1:
        return ""
    return str(units)


def melody_spec_to_events(spec: MelodySpec) -> list[ParsedEvent]:
    validate_melody_spec(spec)
    tonic, mode = parse_key(spec.key)
    events: list[ParsedEvent] = []
    beat_cursor = 0.0
    for bar in spec.bars:
        degrees = [token for token in bar.degrees.split() if token != "|"]
        rhythms = [token for token in bar.rhythm.split() if token != "|"]
        lyrics = [token for token in bar.lyrics.split()] if bar.lyrics else []
        lyric_iter = iter(lyrics)
        for degree, rhythm in zip(degrees, rhythms):
            duration = RHYTHM_TO_BEATS[rhythm]
            lyric = next(lyric_iter, None)
            midi = parse_degree_token(degree, tonic=tonic, mode=mode)
            events.append(ParsedEvent(start_beats=beat_cursor, duration_beats=duration, midi=midi, lyric=lyric))
            beat_cursor += duration
    return events


def melody_spec_to_abc(spec: MelodySpec) -> str:
    events = melody_spec_to_events(spec)
    tonic, mode = parse_key(spec.key)
    key_abc = tonic + ("m" if mode == "minor" else "")
    meter = spec.meter
    beats_per_bar = int(meter.split("/")[0])
    current_bar_beats = 0.0
    note_parts: list[str] = []
    lyric_parts: list[str] = []
    for event in events:
        if current_bar_beats == 0:
            note_parts.append("| ")
        if event.midi is None:
            note_parts.append(f"z{beats_to_abc_length(event.duration_beats)} ")
        else:
            note_parts.append(f"{midi_to_abc_note(event.midi)}{beats_to_abc_length(event.duration_beats)} ")
        if event.lyric:
            lyric_parts.append(event.lyric)
        current_bar_beats += event.duration_beats
        if abs(current_bar_beats - beats_per_bar) < 1e-6:
            current_bar_beats = 0.0
    if note_parts and not note_parts[-1].strip().endswith("|"):
        note_parts.append("|")
    lyric_line = " ".join(lyric_parts)
    return "\n".join([
        "X:1",
        f"T:{spec.title}",
        f"M:{spec.meter}",
        "L:1/8",
        f"Q:1/4={int(round(spec.tempo))}",
        f"K:{key_abc}",
        "".join(note_parts).strip(),
        f"w: {lyric_line}" if lyric_line else "",
    ]).strip() + "\n"


def parse_abc(abc_text: str) -> tuple[dict[str, str], list[ParsedEvent]]:
    lines = [line.strip() for line in abc_text.splitlines() if line.strip()]
    headers: dict[str, str] = {}
    body_lines: list[str] = []
    for line in lines:
        if line.startswith("%"):
            continue
        if re.match(r"^[A-Z]:", line):
            headers[line[0]] = line[2:].strip()
        elif not line.startswith("w:"):
            body_lines.append(line)
    body = " ".join(body_lines).replace("|", " | ")
    note_tokens = [token for token in body.split() if token != "|"]
    events: list[ParsedEvent] = []
    beat_cursor = 0.0
    length_unit = 0.5
    for token in note_tokens:
        match = re.fullmatch(r"(z|[\^=_]?[A-Ga-g][,']*)(\d*)", token)
        if not match:
            raise ValueError(f"Unsupported ABC token: {token}")
        note_token, length_token = match.groups()
        duration = (int(length_token) if length_token else 1) * length_unit
        midi = None if note_token == "z" else abc_note_to_midi(note_token)
        events.append(ParsedEvent(start_beats=beat_cursor, duration_beats=duration, midi=midi))
        beat_cursor += duration
    return headers, events


def abc_note_to_midi(token: str) -> int:
    accidental = 0
    token_body = token
    if token.startswith("^"):
        accidental = 1
        token_body = token[1:]
    elif token.startswith("_"):
        accidental = -1
        token_body = token[1:]
    elif token.startswith("="):
        accidental = 0
        token_body = token[1:]
    note_char = token_body[0]
    octave_marks = token_body[1:]
    base_octave = 5 if note_char.islower() else 4
    pc_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    pc = pc_map[note_char.upper()] + accidental
    octave = base_octave + octave_marks.count("'") - octave_marks.count(",")
    return 12 * (octave + 1) + pc


def save_abc(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
