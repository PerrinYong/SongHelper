from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class MelodySeedCard:
    id: str
    title: str
    source: list[str]
    core_sentence: str
    emotion_pair: str
    contour: str
    rhythm_face: str
    highest_word: str
    cadence: str
    range_hint: str
    motion_hint: str
    avoid: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class MelodyBar:
    degrees: str
    rhythm: str
    lyrics: str = ""
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass
class MelodySpec:
    id: str
    title: str
    key: str
    meter: str
    tempo: float
    bars: list[MelodyBar]
    highest_word: str | None = None
    cadence: str | None = None
    contour: str | None = None
    range_limit: str | None = None
    constraints: list[str] = field(default_factory=list)
    confidence_note: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
