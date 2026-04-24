from __future__ import annotations

import json
from pathlib import Path

from .domain import MelodyBar, MelodySpec

SUPPORTED_METERS = {"4/4", "3/4", "6/8"}
SUPPORTED_RHYTHMS = {"w", "h", "q", "e", "s", "w.", "h.", "q.", "e."}
RHYTHM_TO_BEATS = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25, "w.": 6.0, "h.": 3.0, "q.": 1.5, "e.": 0.75}
METER_TO_BEATS = {"4/4": 4.0, "3/4": 3.0, "6/8": 3.0}


def validate_melody_spec(spec: MelodySpec) -> None:
    if spec.meter not in SUPPORTED_METERS:
        raise ValueError(f"Unsupported meter: {spec.meter}")
    if spec.tempo <= 0:
        raise ValueError("Tempo must be positive")
    if not spec.bars:
        raise ValueError("MelodySpec must contain at least one bar")
    for index, bar in enumerate(spec.bars, start=1):
        degree_tokens = [token for token in bar.degrees.split() if token != "|"]
        rhythm_tokens = [token for token in bar.rhythm.split() if token != "|"]
        if len(degree_tokens) != len(rhythm_tokens):
            raise ValueError(f"Bar {index} degree/rhythm token count mismatch")
        beat_sum = 0.0
        for rhythm in rhythm_tokens:
            if rhythm not in SUPPORTED_RHYTHMS:
                raise ValueError(f"Unsupported rhythm token '{rhythm}' in bar {index}")
            beat_sum += RHYTHM_TO_BEATS[rhythm]
        if abs(beat_sum - METER_TO_BEATS[spec.meter]) > 1e-6:
            raise ValueError(f"Bar {index} beat sum {beat_sum} does not match meter {spec.meter}")


def load_melody_spec(path: Path) -> MelodySpec:
    payload = json.loads(path.read_text(encoding="utf-8"))
    bars = [MelodyBar(**bar) for bar in payload["bars"]]
    spec = MelodySpec(
        id=payload["id"],
        title=payload["title"],
        key=payload["key"],
        meter=payload["meter"],
        tempo=float(payload["tempo"]),
        bars=bars,
        highest_word=payload.get("highest_word"),
        cadence=payload.get("cadence"),
        contour=payload.get("contour"),
        range_limit=payload.get("range_limit"),
        constraints=payload.get("constraints", []),
        confidence_note=payload.get("confidence_note"),
    )
    validate_melody_spec(spec)
    return spec


def save_melody_spec(spec: MelodySpec, path: Path) -> None:
    validate_melody_spec(spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
