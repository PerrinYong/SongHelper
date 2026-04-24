from __future__ import annotations

import json
import re
from pathlib import Path

import torchaudio
import whisper


def format_lrc_timestamp(seconds: float) -> str:
    total_centiseconds = max(0, int(round(seconds * 100)))
    minutes = total_centiseconds // 6000
    remainder = total_centiseconds % 6000
    secs = remainder // 100
    centis = remainder % 100
    return f"{minutes:02d}:{secs:02d}.{centis:02d}"


def normalize_lyrics_text(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\[[^\]]+\]", line):
            continue
        lines.append(line)
    return lines


def transcribe_audio_to_segments(
    audio_path: Path,
    output_path: Path,
    model_name: str = "base",
    language: str = "zh",
) -> dict[str, object]:
    wav, sr = torchaudio.load(str(audio_path))
    wav = wav.mean(dim=0, keepdim=True)
    wav = torchaudio.functional.resample(wav, sr, 16000)
    audio = wav.squeeze(0).numpy()

    model = whisper.load_model(model_name)
    result = model.transcribe(
        audio=audio,
        language=language,
        task="transcribe",
        verbose=False,
        fp16=False,
    )
    payload = {
        "text": result["text"],
        "segments": [
            {
                "id": segment["id"],
                "start": round(segment["start"], 2),
                "end": round(segment["end"], 2),
                "text": segment["text"],
            }
            for segment in result["segments"]
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _resolve_line_times(line_count: int, segment_times: list[float]) -> list[float]:
    if not segment_times:
        return [float(i * 4) for i in range(line_count)]
    if len(segment_times) >= line_count:
        return segment_times[:line_count]

    resolved = list(segment_times)
    last = resolved[-1]
    step = 3.0
    for _ in range(line_count - len(segment_times)):
        last += step
        resolved.append(last)
    return resolved


def build_lrc_text(
    lyrics_lines: list[str],
    segment_starts: list[float],
    *,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    by: str | None = "SongHelper",
    re_tag: str | None = "Whisper line-level alignment",
    version: str | None = "1.0",
) -> str:
    resolved_times = _resolve_line_times(len(lyrics_lines), segment_starts)
    header: list[str] = []
    if title:
        header.append(f"[ti:{title}]")
    if artist:
        header.append(f"[ar:{artist}]")
    if album:
        header.append(f"[al:{album}]")
    if by:
        header.append(f"[by:{by}]")
    if re_tag:
        header.append(f"[re:{re_tag}]")
    if version:
        header.append(f"[ve:{version}]")
    header.append("[offset:0]")

    body = [f"[{format_lrc_timestamp(ts)}]{line}" for ts, line in zip(resolved_times, lyrics_lines)]
    return "\n".join(header + body) + "\n"


def generate_lrc_from_files(
    lyrics_path: Path,
    segments_path: Path,
    output_path: Path,
    *,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    by: str | None = "SongHelper",
    re_tag: str | None = "Whisper line-level alignment",
    version: str | None = "1.0",
) -> str:
    lyrics_lines = normalize_lyrics_text(lyrics_path.read_text(encoding="utf-8"))
    payload = json.loads(segments_path.read_text(encoding="utf-8"))
    segment_starts = [float(segment["start"]) for segment in payload.get("segments", [])]
    text = build_lrc_text(
        lyrics_lines,
        segment_starts,
        title=title,
        artist=artist,
        album=album,
        by=by,
        re_tag=re_tag,
        version=version,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return text
