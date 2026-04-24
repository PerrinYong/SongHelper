from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audio_analysis import save_analysis
from .audio_probe import save_audio_probe
from .capabilities import render_capabilities
from .ffmpeg_tools import REVERB_PRESETS, apply_reverb, concat_audio, normalize_audio
from .lrc_tools import generate_lrc_from_files, transcribe_audio_to_segments
from .melody_factory.workflow import (
    build_preview_manifest,
    export_abc_to_audio,
    export_abc_to_midi,
    export_abc_to_musicxml,
    export_spec_to_abc,
    export_spec_to_audio,
    export_spec_to_midi,
    export_spec_to_musicxml,
    init_melody_factory,
    render_notation_to_audio,
    validate_spec,
)
from .melody_cleanup import save_cleaned_melody
from .midi_tools import export_midi_to_jianpu
from .project import ensure_song_workspace, ensure_workspace
from .rough_separation import rough_separate
from .score_render import save_human_jianpu
from .transcription import NoteEvent, save_transcription
from .workflows import render_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="songhelper", description="Song creation helper workspace"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("capabilities", help="Show supported capabilities")
    subparsers.add_parser("workflow", help="Show recommended songwriting workflow")

    init_parser = subparsers.add_parser(
        "init-workspace", help="Create standard workspace folders"
    )
    init_parser.add_argument("--root", default=".", help="Project root")

    init_song_parser = subparsers.add_parser(
        "init-song", help="Create standard folders for one song under workspace"
    )
    init_song_parser.add_argument("song_name", help="Song directory name")
    init_song_parser.add_argument("--root", default=".", help="Project root")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze BPM, key, and structure"
    )
    analyze_parser.add_argument("input", help="Input audio path")
    analyze_parser.add_argument("output", help="Output JSON path")

    probe_parser = subparsers.add_parser(
        "probe-audio", help="Probe metadata and rough musical statistics"
    )
    probe_parser.add_argument("input", help="Input audio path")
    probe_parser.add_argument("output", help="Output JSON path")

    rough_sep_parser = subparsers.add_parser(
        "rough-separate", help="Run HPSS or center-extraction rough separation"
    )
    rough_sep_parser.add_argument("input", help="Input audio path")
    rough_sep_parser.add_argument("output_dir", help="Output directory")
    rough_sep_parser.add_argument(
        "--mode", required=True, choices=["hpss", "center"], help="Rough separation mode"
    )

    transcribe_parser = subparsers.add_parser(
        "transcribe", help="Extract melody and export MIDI/Jianpu"
    )
    transcribe_parser.add_argument("input", help="Input vocal audio path")
    transcribe_parser.add_argument("midi_output", help="Output MIDI path")
    transcribe_parser.add_argument("jianpu_output", help="Output Jianpu text path")
    transcribe_parser.add_argument("json_output", help="Output note JSON path")
    transcribe_parser.add_argument(
        "--tempo", type=float, default=None, help="Tempo in BPM"
    )
    transcribe_parser.add_argument(
        "--tonic", default=None, help="Tonic note name like C or F#"
    )
    transcribe_parser.add_argument(
        "--mode", default=None, choices=["major", "minor"], help="Key mode hint"
    )

    midi_to_jianpu_parser = subparsers.add_parser(
        "midi-to-jianpu", help="Convert MIDI to Jianpu text"
    )
    midi_to_jianpu_parser.add_argument("input", help="Input MIDI path")
    midi_to_jianpu_parser.add_argument("output", help="Output Jianpu text path")
    midi_to_jianpu_parser.add_argument(
        "--tonic", required=True, help="Tonic note name like C or F#"
    )
    midi_to_jianpu_parser.add_argument(
        "--mode", required=True, choices=["major", "minor"], help="Key mode"
    )

    clean_melody_parser = subparsers.add_parser(
        "clean-melody", help="Clean extracted melody notes and export a cleaner MIDI"
    )
    clean_melody_parser.add_argument("input", help="Input note JSON path")
    clean_melody_parser.add_argument("midi_output", help="Output cleaned MIDI path")
    clean_melody_parser.add_argument("jianpu_output", help="Output cleaned Jianpu path")
    clean_melody_parser.add_argument(
        "json_output", help="Output cleaned note JSON path"
    )
    clean_melody_parser.add_argument(
        "--min-duration",
        type=float,
        default=0.12,
        help="Remove notes shorter than this",
    )
    clean_melody_parser.add_argument(
        "--max-midi", type=int, default=None, help="Optional hard upper MIDI limit"
    )

    human_jianpu_parser = subparsers.add_parser(
        "human-jianpu", help="Render cleaned melody as a more readable Jianpu text"
    )
    human_jianpu_parser.add_argument("input", help="Input cleaned note JSON path")
    human_jianpu_parser.add_argument("output", help="Output human-readable Jianpu path")
    human_jianpu_parser.add_argument("--title", required=True, help="Score title")
    human_jianpu_parser.add_argument("--meter", default="4/4", help="Meter label")
    human_jianpu_parser.add_argument("--key", default=None, help="Key label")

    concat_parser = subparsers.add_parser(
        "concat-audio", help="Concatenate audio clips via ffmpeg"
    )
    concat_parser.add_argument("inputs", nargs="+", help="Input audio files in order")
    concat_parser.add_argument("--output", required=True, help="Output audio path")

    reverb_parser = subparsers.add_parser(
        "apply-reverb", help="Apply simple ffmpeg reverb preset"
    )
    reverb_parser.add_argument("input", help="Input audio path")
    reverb_parser.add_argument("output", help="Output audio path")
    reverb_parser.add_argument(
        "--preset", required=True, choices=sorted(REVERB_PRESETS.keys()), help="Reverb preset"
    )

    normalize_parser = subparsers.add_parser(
        "normalize-audio", help="Normalize loudness via ffmpeg loudnorm"
    )
    normalize_parser.add_argument("input", help="Input audio path")
    normalize_parser.add_argument("output", help="Output audio path")
    normalize_parser.add_argument("--i", type=float, default=-16.0, help="Integrated loudness target")
    normalize_parser.add_argument("--tp", type=float, default=-1.5, help="True peak target")
    normalize_parser.add_argument("--lra", type=float, default=11.0, help="Loudness range target")

    transcribe_segments_parser = subparsers.add_parser(
        "transcribe-segments", help="Transcribe audio into Whisper segment JSON"
    )
    transcribe_segments_parser.add_argument("input", help="Input audio path")
    transcribe_segments_parser.add_argument("output", help="Output segments JSON path")
    transcribe_segments_parser.add_argument("--model", default="base", help="Whisper model name")
    transcribe_segments_parser.add_argument("--language", default="zh", help="Language hint")

    generate_lrc_parser = subparsers.add_parser(
        "generate-lrc", help="Generate line-level LRC from lyrics text and segment JSON"
    )
    generate_lrc_parser.add_argument("lyrics", help="Lyrics text file path")
    generate_lrc_parser.add_argument("segments", help="Whisper segments JSON path")
    generate_lrc_parser.add_argument("output", help="Output LRC path")
    generate_lrc_parser.add_argument("--title", default=None, help="Song title")
    generate_lrc_parser.add_argument("--artist", default=None, help="Artist")
    generate_lrc_parser.add_argument("--album", default=None, help="Album")

    melody_factory_parser = subparsers.add_parser(
        "melody-factory", help="Technical workflow for melody spec, ABC, MIDI, and audio"
    )
    melody_factory_subparsers = melody_factory_parser.add_subparsers(dest="melody_factory_command")

    mf_init = melody_factory_subparsers.add_parser("init", help="Initialize melody_factory workspace for one song")
    mf_init.add_argument("song_name", help="Song directory name")
    mf_init.add_argument("--root", default=".", help="Project root")

    mf_spec_to_abc = melody_factory_subparsers.add_parser("spec-to-abc", help="Convert MelodySpec JSON to ABC")
    mf_spec_to_abc.add_argument("input", help="Input MelodySpec JSON path")
    mf_spec_to_abc.add_argument("output", help="Output ABC path")

    mf_spec_to_midi = melody_factory_subparsers.add_parser("spec-to-midi", help="Convert MelodySpec JSON to MIDI")
    mf_spec_to_midi.add_argument("input", help="Input MelodySpec JSON path")
    mf_spec_to_midi.add_argument("output", help="Output MIDI path")

    mf_validate = melody_factory_subparsers.add_parser("validate", help="Validate MelodySpec JSON and output report")
    mf_validate.add_argument("input", help="Input MelodySpec JSON path")
    mf_validate.add_argument("output", nargs="?", default=None, help="Optional output validation report JSON path")

    mf_spec_to_musicxml = melody_factory_subparsers.add_parser("spec-to-musicxml", help="Convert MelodySpec JSON to MusicXML")
    mf_spec_to_musicxml.add_argument("input", help="Input MelodySpec JSON path")
    mf_spec_to_musicxml.add_argument("output", help="Output MusicXML path")

    mf_spec_to_audio = melody_factory_subparsers.add_parser("spec-to-audio", help="Convert MelodySpec JSON to WAV preview")
    mf_spec_to_audio.add_argument("input", help="Input MelodySpec JSON path")
    mf_spec_to_audio.add_argument("output", help="Output WAV path")

    mf_abc_to_midi = melody_factory_subparsers.add_parser("abc-to-midi", help="Convert ABC to MIDI")
    mf_abc_to_midi.add_argument("input", help="Input ABC path")
    mf_abc_to_midi.add_argument("output", help="Output MIDI path")

    mf_abc_to_audio = melody_factory_subparsers.add_parser("abc-to-audio", help="Convert ABC to WAV preview")
    mf_abc_to_audio.add_argument("input", help="Input ABC path")
    mf_abc_to_audio.add_argument("output", help="Output WAV path")

    mf_abc_to_musicxml = melody_factory_subparsers.add_parser("abc-to-musicxml", help="Convert ABC to MusicXML")
    mf_abc_to_musicxml.add_argument("input", help="Input ABC path")
    mf_abc_to_musicxml.add_argument("output", help="Output MusicXML path")

    mf_render_audio = melody_factory_subparsers.add_parser("render-audio", help="Render MIDI or MusicXML to audio via MuseScore CLI")
    mf_render_audio.add_argument("input", help="Input MIDI or MusicXML path")
    mf_render_audio.add_argument("output", help="Output audio path")
    mf_render_audio.add_argument("--musescore", default=None, help="Optional MuseScore executable path")

    mf_preview_manifest = melody_factory_subparsers.add_parser("preview-manifest", help="Build preview manifest for one song")
    mf_preview_manifest.add_argument("song_name", help="Song directory name")
    mf_preview_manifest.add_argument("--root", default=".", help="Project root")
    mf_preview_manifest.add_argument("--output", default=None, help="Optional output manifest path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "capabilities":
        print(render_capabilities())
        return 0

    if args.command == "workflow":
        print(render_workflow())
        return 0

    if args.command == "init-workspace":
        root = Path(args.root).resolve()
        created = ensure_workspace(root)
        print("Workspace folders ensured:")
        for item in created:
            print(f"- {item}")
        return 0

    if args.command == "init-song":
        root = Path(args.root).resolve()
        created = ensure_song_workspace(root, args.song_name)
        print("Song workspace folders ensured:")
        for item in created:
            print(f"- {item}")
        return 0

    if args.command == "analyze":
        result = save_analysis(Path(args.input), Path(args.output))
        print(f"BPM: {result.bpm}")
        print(f"Key: {result.key}")
        print("Sections:")
        for section in result.sections:
            print(
                f"- {section.label}{section.index}: {section.start_sec:.2f}s -> {section.end_sec:.2f}s"
            )
        return 0

    if args.command == "probe-audio":
        result = save_audio_probe(Path(args.input), Path(args.output))
        print(f"Tempo estimate: {result['tempo_bpm_estimate']}")
        print(f"Key estimate: {result['key_estimate']}")
        print(f"Duration: {result['duration_sec']}")
        return 0

    if args.command == "rough-separate":
        written = rough_separate(Path(args.input), Path(args.output_dir), args.mode)
        for item in written:
            print(f"Wrote: {item}")
        if args.mode == "hpss":
            print("Note: HPSS separates harmonic vs percussive content, not true vocal vs accompaniment.")
        else:
            print("Note: Center extraction is a rough stereo trick and may only partially isolate centered vocal.")
        return 0

    if args.command == "transcribe":
        payload = save_transcription(
            Path(args.input),
            Path(args.midi_output),
            Path(args.jianpu_output),
            Path(args.json_output),
            tempo=args.tempo,
            tonic_hint=args.tonic,
            mode_hint=args.mode,
        )
        print(f"Notes: {payload['note_count']}")
        print(f"Tempo: {payload['tempo']}")
        print(f"Mode: {payload['mode']}")
        return 0

    if args.command == "midi-to-jianpu":
        export_midi_to_jianpu(
            Path(args.input), Path(args.output), tonic=args.tonic, mode=args.mode
        )
        print(f"Jianpu written to: {args.output}")
        return 0

    if args.command == "clean-melody":
        payload = save_cleaned_melody(
            Path(args.input),
            Path(args.midi_output),
            Path(args.jianpu_output),
            Path(args.json_output),
            min_duration_sec=args.min_duration,
            max_midi=args.max_midi,
        )
        print(f"Cleaned notes: {payload['note_count']}")
        print(f"Cleanup stats: {payload['cleanup']}")
        return 0

    if args.command == "human-jianpu":
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        notes = [NoteEvent(**row) for row in payload["notes"]]
        text = save_human_jianpu(
            notes,
            Path(args.output),
            tempo=float(payload["tempo"]),
            title=args.title,
            meter=args.meter,
            key=args.key,
        )
        print(f"Human-readable Jianpu written to: {args.output}")
        print(f"Lines: {len(text.splitlines())}")
        return 0

    if args.command == "concat-audio":
        concat_audio([Path(item) for item in args.inputs], Path(args.output))
        print(f"Wrote: {args.output}")
        return 0

    if args.command == "apply-reverb":
        apply_reverb(Path(args.input), Path(args.output), args.preset)
        print(f"Wrote: {args.output}")
        return 0

    if args.command == "normalize-audio":
        normalize_audio(Path(args.input), Path(args.output), args.i, args.tp, args.lra)
        print(f"Wrote: {args.output}")
        return 0

    if args.command == "transcribe-segments":
        payload = transcribe_audio_to_segments(
            Path(args.input), Path(args.output), model_name=args.model, language=args.language
        )
        print(f"Segments: {len(payload['segments'])}")
        print(f"Wrote: {args.output}")
        return 0

    if args.command == "generate-lrc":
        generate_lrc_from_files(
            Path(args.lyrics),
            Path(args.segments),
            Path(args.output),
            title=args.title,
            artist=args.artist,
            album=args.album,
        )
        print(f"Wrote: {args.output}")
        return 0

    if args.command == "melody-factory":
        if args.melody_factory_command == "init":
            created = init_melody_factory(Path(args.root).resolve(), args.song_name)
            for item in created:
                print(f"- {item}")
            return 0
        if args.melody_factory_command == "spec-to-abc":
            export_spec_to_abc(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "spec-to-midi":
            export_spec_to_midi(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "validate":
            report = validate_spec(Path(args.input), Path(args.output) if args.output else None)
            print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            return 0
        if args.melody_factory_command == "spec-to-musicxml":
            export_spec_to_musicxml(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "spec-to-audio":
            export_spec_to_audio(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "abc-to-midi":
            export_abc_to_midi(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "abc-to-audio":
            export_abc_to_audio(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "abc-to-musicxml":
            export_abc_to_musicxml(Path(args.input), Path(args.output))
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "render-audio":
            render_notation_to_audio(Path(args.input), Path(args.output), args.musescore)
            print(f"Wrote: {args.output}")
            return 0
        if args.melody_factory_command == "preview-manifest":
            song_root = Path(args.root).resolve() / "workspace" / args.song_name
            manifest = build_preview_manifest(song_root, Path(args.output) if args.output else None)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            return 0
        parser.print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
