from __future__ import annotations

from pathlib import Path


DEFAULT_WORKSPACE_DIRS = ["workspace", "workspace/temp"]

DEFAULT_SONG_SUBDIRS = [
    "source",
    "analysis",
    "stems",
    "scores",
    "mixes",
    "exports",
    "notes",
]


def ensure_workspace(root: Path) -> list[Path]:
    created: list[Path] = []
    for relative in DEFAULT_WORKSPACE_DIRS:
        target = root / relative
        target.mkdir(parents=True, exist_ok=True)
        created.append(target)
    return created


def ensure_song_workspace(root: Path, song_name: str) -> list[Path]:
    song_root = root / "workspace" / song_name
    created: list[Path] = []
    for subdir in DEFAULT_SONG_SUBDIRS:
        target = song_root / subdir
        target.mkdir(parents=True, exist_ok=True)
        created.append(target)
    return created
