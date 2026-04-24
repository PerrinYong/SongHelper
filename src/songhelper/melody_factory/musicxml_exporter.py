from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement

from .abc_converter import melody_spec_to_events, parse_abc
from .domain import MelodySpec

DIVISIONS = 2  # 1 beat = 2 divisions when L:1/8


def _build_score(headers: dict[str, str], events, output_path: Path) -> None:
    score = Element("score-partwise", version="3.1")
    part_list = SubElement(score, "part-list")
    score_part = SubElement(part_list, "score-part", id="P1")
    SubElement(score_part, "part-name").text = headers.get("title", "Melody")
    part = SubElement(score, "part", id="P1")

    meter = headers.get("meter", "4/4")
    beats_text, beat_type_text = meter.split("/")
    beats_per_bar = float(beats_text) if meter != "6/8" else 3.0
    measure = None
    measure_no = 0
    current_beats = 0.0
    for index, event in enumerate(events):
        if measure is None or current_beats == 0.0:
            measure_no += 1
            measure = SubElement(part, "measure", number=str(measure_no))
            if measure_no == 1:
                attributes = SubElement(measure, "attributes")
                SubElement(attributes, "divisions").text = str(DIVISIONS)
                time = SubElement(attributes, "time")
                SubElement(time, "beats").text = beats_text
                SubElement(time, "beat-type").text = beat_type_text
                clef = SubElement(attributes, "clef")
                SubElement(clef, "sign").text = "G"
                SubElement(clef, "line").text = "2"
        note = SubElement(measure, "note")
        if event.midi is None:
            SubElement(note, "rest")
        else:
            pitch = SubElement(note, "pitch")
            step_map = {0: ("C", None), 1: ("C", 1), 2: ("D", None), 3: ("D", 1), 4: ("E", None), 5: ("F", None), 6: ("F", 1), 7: ("G", None), 8: ("G", 1), 9: ("A", None), 10: ("A", 1), 11: ("B", None)}
            step, alter = step_map[event.midi % 12]
            octave = event.midi // 12 - 1
            SubElement(pitch, "step").text = step
            if alter is not None:
                SubElement(pitch, "alter").text = str(alter)
            SubElement(pitch, "octave").text = str(octave)
        duration = int(round(event.duration_beats * DIVISIONS))
        SubElement(note, "duration").text = str(duration)
        current_beats += event.duration_beats
        if abs(current_beats - beats_per_bar) < 1e-6:
            current_beats = 0.0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ElementTree(score).write(output_path, encoding="utf-8", xml_declaration=True)


def melody_spec_to_musicxml(spec: MelodySpec, output_path: Path) -> None:
    headers = {"title": spec.title, "meter": spec.meter}
    events = melody_spec_to_events(spec)
    _build_score(headers, events, output_path)


def abc_to_musicxml(abc_text: str, output_path: Path) -> None:
    headers_raw, events = parse_abc(abc_text)
    headers = {
        "title": headers_raw.get("T", "Melody"),
        "meter": headers_raw.get("M", "4/4"),
    }
    _build_score(headers, events, output_path)
