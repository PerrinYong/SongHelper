from __future__ import annotations

import json
from pathlib import Path

DEFAULT_FACTORY_DIRS = ["inputs", "specs", "abc", "midi", "audio", "exports"]

SAMPLE_SEED_CARD = {
    "id": "seed_01",
    "title": "示例种子卡",
    "source": ["歌词", "动作"],
    "core_sentence": "混天绫在风里燃",
    "emotion_pair": "明亮但危险",
    "contour": "中音起-上推-高点-回落",
    "rhythm_face": "短短长 | 短短长",
    "highest_word": "绫",
    "cadence": "落稳",
    "range_hint": "六度内",
    "motion_hint": "甩开、回卷、立住",
    "avoid": "避免沿用参考曲相同的首句起音与节奏脸"
}

SAMPLE_MELODY_SPEC = {
    "id": "hook_a",
    "title": "Hook A",
    "key": "C minor",
    "meter": "4/4",
    "tempo": 76,
    "bars": [
        {
            "degrees": "5 5 b6 5 3 0 2 1",
            "rhythm": "e e e e e e e e",
            "lyrics": "混 天 绫 在 风 里 燃",
            "annotations": {}
        },
        {
            "degrees": "1 2 3 5 5 0 3 2",
            "rhythm": "e e e e e e e e",
            "lyrics": "少 年 身 上 火 未 熄",
            "annotations": {}
        }
    ],
    "highest_word": "绫",
    "cadence": "stable",
    "contour": "mid-up-peak-fall",
    "range_limit": "octave",
    "constraints": [],
    "confidence_note": "sample template"
}


def _ensure_template_assets(base: Path, song_name: str) -> list[Path]:
    written: list[Path] = []
    sample_seed_path = base / "inputs" / "sample.seed.json"
    if not sample_seed_path.exists():
        sample_seed_path.write_text(json.dumps(SAMPLE_SEED_CARD, ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(sample_seed_path)

    sample_spec_path = base / "specs" / "sample.mspec.json"
    if not sample_spec_path.exists():
        sample_spec_path.write_text(json.dumps(SAMPLE_MELODY_SPEC, ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(sample_spec_path)

    readme_path = base / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            "\n".join(
                [
                    f"# {song_name} / melody_factory 工作目录",
                    "",
                    "当前目录用于承载主旋律发明工作流的技术资产。",
                    "",
                    "- `inputs/sample.seed.json`：示例 Melody Seed Card",
                    "- `specs/sample.mspec.json`：示例 MelodySpec",
                    "- `abc/`：ABC 输出",
                    "- `midi/`：MIDI 输出",
                    "- `audio/`：WAV 预听输出",
                    "- `exports/`：MusicXML 等交换格式",
                    "- `preview_manifest.json`：候选预览清单",
                ]
            ),
            encoding="utf-8",
        )
    written.append(readme_path)
    return written


def ensure_melody_factory_workspace(root: Path, song_name: str) -> list[Path]:
    base = root / "workspace" / song_name / "melody_factory"
    created: list[Path] = []
    for name in DEFAULT_FACTORY_DIRS:
        path = base / name
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)
    session_path = base / "session.json"
    if not session_path.exists():
        session_path.write_text(
            json.dumps(
                {
                    "song": song_name,
                    "status": "initialized",
                    "workflow": "melody_factory",
                    "phases": ["seed", "spec", "validate", "preview", "export"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    created.append(session_path)
    created.extend(_ensure_template_assets(base, song_name))
    return created
