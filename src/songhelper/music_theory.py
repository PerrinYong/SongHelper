from __future__ import annotations

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]

MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

MAJOR_DEGREE_MAP = {
    0: "1",
    1: "#1",
    2: "2",
    3: "b3",
    4: "3",
    5: "4",
    6: "#4",
    7: "5",
    8: "b6",
    9: "6",
    10: "b7",
    11: "7",
}
MINOR_DEGREE_MAP = {
    0: "1",
    1: "#1",
    2: "2",
    3: "b3",
    4: "3",
    5: "4",
    6: "#4",
    7: "5",
    8: "b6",
    9: "6",
    10: "b7",
    11: "7",
}


def note_name(pc: int) -> str:
    return NOTE_NAMES[pc % 12]


def detect_key_from_chroma(chroma_mean: list[float]) -> dict[str, str | int | float]:
    major_scores: list[float] = []
    minor_scores: list[float] = []
    for shift in range(12):
        rotated = chroma_mean[-shift:] + chroma_mean[:-shift]
        major_scores.append(sum(a * b for a, b in zip(rotated, MAJOR_PROFILE)))
        minor_scores.append(sum(a * b for a, b in zip(rotated, MINOR_PROFILE)))

    major_idx = max(range(12), key=major_scores.__getitem__)
    minor_idx = max(range(12), key=minor_scores.__getitem__)
    major_score = major_scores[major_idx]
    minor_score = minor_scores[minor_idx]

    if major_score >= minor_score:
        return {
            "tonic_pc": major_idx,
            "tonic": note_name(major_idx),
            "mode": "major",
            "score": float(major_score),
        }
    return {
        "tonic_pc": minor_idx,
        "tonic": note_name(minor_idx),
        "mode": "minor",
        "score": float(minor_score),
    }


def midi_to_jianpu(midi_note: int, tonic_pc: int, mode: str) -> str:
    diff = (midi_note - tonic_pc) % 12
    octave_shift = (midi_note - tonic_pc) // 12 - 5
    mapping = MAJOR_DEGREE_MAP if mode == "major" else MINOR_DEGREE_MAP
    degree = mapping[diff]
    if octave_shift > 0:
        degree = degree + ("'" * octave_shift)
    elif octave_shift < 0:
        degree = ("," * abs(octave_shift)) + degree
    return degree
