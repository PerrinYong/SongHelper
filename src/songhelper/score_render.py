from __future__ import annotations

from pathlib import Path

from .transcription import NoteEvent


def render_human_jianpu(
    notes: list[NoteEvent],
    tempo: float,
    title: str,
    meter: str = "4/4",
    key: str | None = None,
    beat_unit: float = 0.5,
    bars_per_line: int = 4,
) -> str:
    units_per_bar = int(round(4 / beat_unit))
    timeline: list[str] = []
    current_units = 0

    def append_units(token: str, units: int) -> None:
        nonlocal current_units
        units = max(1, units)
        timeline.append(token)
        current_units += 1
        for _ in range(units - 1):
            timeline.append("-")
            current_units += 1

    if not notes:
        return f"# {title}\n\n(无可用旋律)"

    current_beat = round(notes[0].start_sec * tempo / 60 / beat_unit) * beat_unit
    for note in notes:
        note_start = round(note.start_sec * tempo / 60 / beat_unit) * beat_unit
        note_beats = max(beat_unit, round(note.beats / beat_unit) * beat_unit)
        gap = max(0.0, note_start - current_beat)
        if gap >= beat_unit:
            append_units("0", int(round(gap / beat_unit)))
            current_beat += gap
        append_units(note.jianpu, int(round(note_beats / beat_unit)))
        current_beat = note_start + note_beats

    bars: list[str] = []
    for idx in range(0, len(timeline), units_per_bar):
        bar_tokens = timeline[idx : idx + units_per_bar]
        if len(bar_tokens) < units_per_bar:
            bar_tokens.extend(["-"] * (units_per_bar - len(bar_tokens)))
        bars.append(" ".join(bar_tokens))

    lines = [f"# {title}", f"- 速度参考: ♩={tempo:.2f}", f"- 拍号估计: {meter}"]
    if key:
        lines.append(f"- 调式估计: {key}")
    lines.append("- 说明: 基于清理后的主旋律自动量化为半拍网格，供人读谱与后续人工整理。")
    lines.append("")

    for line_idx in range(0, len(bars), bars_per_line):
        chunk = bars[line_idx : line_idx + bars_per_line]
        bar_index = line_idx + 1
        lines.append(f"[{bar_index:02d}] | " + " | ".join(chunk) + " |")

    return "\n".join(lines)


def save_human_jianpu(
    notes: list[NoteEvent],
    output_path: Path,
    tempo: float,
    title: str,
    meter: str = "4/4",
    key: str | None = None,
) -> str:
    text = render_human_jianpu(notes, tempo=tempo, title=title, meter=meter, key=key)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text
