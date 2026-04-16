from __future__ import annotations

import argparse
from pathlib import Path

from .audio_analysis import save_analysis
from .capabilities import render_capabilities
from .melody_cleanup import save_cleaned_melody
from .midi_tools import export_midi_to_jianpu
from .project import ensure_song_workspace, ensure_workspace
from .transcription import save_transcription
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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
