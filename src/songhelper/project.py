from __future__ import annotations

from pathlib import Path


DEFAULT_WORKSPACE_DIRS = [
    "workspace/analysis",
    "workspace/notes",
    "workspace/stems",
    "workspace/scores",
    "workspace/mixes",
    "workspace/exports",
    "workspace/temp",
]


def ensure_workspace(root: Path) -> list[Path]:
    created: list[Path] = []
    for relative in DEFAULT_WORKSPACE_DIRS:
        target = root / relative
        target.mkdir(parents=True, exist_ok=True)
        created.append(target)
    return created
