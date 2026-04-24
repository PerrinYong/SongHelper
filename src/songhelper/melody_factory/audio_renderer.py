from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from .abc_converter import melody_spec_to_events, parse_abc
from .domain import MelodySpec


def midi_to_frequency(midi_note: int) -> float:
    return 440.0 * (2 ** ((midi_note - 69) / 12))


def render_events_to_audio(events, tempo_bpm: float, output_path: Path, sample_rate: int = 22050) -> None:
    seconds_per_beat = 60.0 / tempo_bpm
    total_beats = max((event.start_beats + event.duration_beats) for event in events) if events else 0
    total_samples = int((total_beats * seconds_per_beat + 0.25) * sample_rate)
    waveform = np.zeros(total_samples, dtype=np.float32)
    for event in events:
        start_sample = int(event.start_beats * seconds_per_beat * sample_rate)
        duration_samples = max(1, int(event.duration_beats * seconds_per_beat * sample_rate))
        end_sample = min(total_samples, start_sample + duration_samples)
        if event.midi is None:
            continue
        t = np.arange(end_sample - start_sample) / sample_rate
        freq = midi_to_frequency(event.midi)
        tone = 0.2 * np.sin(2 * np.pi * freq * t)
        fade = min(256, len(tone) // 4)
        if fade > 1:
            tone[:fade] *= np.linspace(0, 1, fade)
            tone[-fade:] *= np.linspace(1, 0, fade)
        waveform[start_sample:end_sample] += tone.astype(np.float32)
    waveform = np.clip(waveform, -0.95, 0.95)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, waveform, sample_rate)


def melody_spec_to_audio(spec: MelodySpec, output_path: Path, sample_rate: int = 22050) -> None:
    render_events_to_audio(melody_spec_to_events(spec), float(spec.tempo), output_path, sample_rate)


def abc_to_audio(abc_text: str, output_path: Path, sample_rate: int = 22050) -> None:
    headers, events = parse_abc(abc_text)
    tempo = float(headers.get("Q", "120").split("=")[-1])
    render_events_to_audio(events, tempo, output_path, sample_rate)
