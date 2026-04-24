from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from .abc_converter import melody_spec_to_events
from .domain import MelodySpec
from .schema import METER_TO_BEATS, load_melody_spec, validate_melody_spec


@dataclass
class ValidationReport:
    spec_id: str
    spec_title: str
    valid: bool
    severity: str
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, object]
    suggestions: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def validate_spec_with_report(spec: MelodySpec) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        validate_melody_spec(spec)
    except ValueError as exc:
        errors.append(str(exc))

    events = melody_spec_to_events(spec)
    note_events = [event for event in events if event.midi is not None]
    if len(spec.bars) > 4:
        errors.append("当前阶段只建议 4 小节以内 hook")
    lyric_tokens = []
    note_count_per_lyric = 0
    for bar in spec.bars:
        lyric_tokens.extend(bar.lyrics.split())
        note_count_per_lyric += len([token for token in bar.degrees.split() if token not in {"|", "0", "-"}])
    if lyric_tokens and abs(len(lyric_tokens) - note_count_per_lyric) > 2:
        warnings.append("歌词字数与有效音符数偏差较大，建议人工复核")

    if note_events:
        pitches = [event.midi for event in note_events if event.midi is not None]
        pitch_min = min(pitches)
        pitch_max = max(pitches)
        if pitch_max - pitch_min > 12:
            warnings.append("音域超过八度，可能不利于当前 hook 阶段的快速筛选")
        if pitch_max - pitch_min > 14:
            errors.append("音域超过建议限制")
        jumps = [abs(note_events[i + 1].midi - note_events[i].midi) for i in range(len(note_events) - 1)]
        large_jumps = [jump for jump in jumps if jump >= 7]
        if len(large_jumps) > 2:
            warnings.append("大跳较多，可能影响顺口度")
        if spec.highest_word:
            highest_events = [event for event in events if event.midi == pitch_max]
            highest_lyrics = {event.lyric for event in highest_events if event.lyric}
            if highest_lyrics and spec.highest_word not in highest_lyrics:
                errors.append("highest_word 没有真正落在旋律最高点")

    if spec.cadence == "stable" and note_events:
        last_note = note_events[-1].midi
        tonic_pc = note_events[0].midi % 12
        if last_note % 12 != tonic_pc:
            warnings.append("cadence 声明为 stable，但句尾未明显落稳到主音")

    suggestions: list[str] = []
    if errors:
        if any("highest_word" in error for error in errors):
            suggestions.append("调整最高音位置，使 highest_word 真正落在峰值")
        if any("小节" in error or "meter" in error for error in errors):
            suggestions.append("重写 rhythm，使每小节总拍数与拍号一致")
    if warnings:
        if any("歌词字数" in warning for warning in warnings):
            suggestions.append("检查 lyrics 与音符数的对齐关系")
        if any("大跳" in warning for warning in warnings):
            suggestions.append("适当减少大跳，提升顺口度")
        if any("cadence" in warning for warning in warnings):
            suggestions.append("若想落稳，可把句尾改到主音或稳定级")

    metrics = {
        "bar_count": len(spec.bars),
        "meter": spec.meter,
        "beats_per_bar": METER_TO_BEATS[spec.meter],
        "lyric_token_count": len(lyric_tokens),
        "effective_note_count": note_count_per_lyric,
        "midi_note_count": len(note_events),
    }
    severity = "error" if errors else ("warning" if warnings else "ok")
    return ValidationReport(
        spec_id=spec.id,
        spec_title=spec.title,
        valid=not errors,
        severity=severity,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
        suggestions=suggestions,
    )


def validate_spec_file(input_path: Path, output_path: Path | None = None) -> ValidationReport:
    spec = load_melody_spec(input_path)
    report = validate_spec_with_report(spec)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return report
