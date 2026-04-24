from __future__ import annotations

import json
from pathlib import Path


def build_preview_manifest(song_root: Path) -> dict[str, object]:
    factory_root = song_root / "melody_factory"
    specs_dir = factory_root / "specs"
    abc_dir = factory_root / "abc"
    midi_dir = factory_root / "midi"
    audio_dir = factory_root / "audio"
    xml_dir = factory_root / "exports"

    candidates: list[dict[str, object]] = []
    for spec_path in sorted(specs_dir.glob("*.json")):
        stem = spec_path.stem
        candidates.append(
            {
                "id": stem,
                "spec": str(spec_path),
                "abc": str(abc_dir / f"{stem}.abc"),
                "midi": str(midi_dir / f"{stem}.mid"),
                "audio": str(audio_dir / f"{stem}.wav"),
                "musicxml": str(xml_dir / f"{stem}.musicxml"),
            }
        )

    return {
        "song": song_root.name,
        "factory_root": str(factory_root),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def save_preview_manifest(song_root: Path, output_path: Path | None = None) -> dict[str, object]:
    manifest = build_preview_manifest(song_root)
    target = output_path or (song_root / "melody_factory" / "preview_manifest.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
