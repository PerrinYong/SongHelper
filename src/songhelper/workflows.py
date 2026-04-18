from __future__ import annotations

WORKFLOW_STEPS = [
    (
        "1. 灵感与方向定义",
        ["主题/情绪澄清", "参考曲拆解", "结构草图", "BPM/调性候选"],
    ),
    (
        "2. Demo 与素材分析",
        ["文件探测", "节拍识别", "调性估计", "段落切分", "旋律/和弦候选"],
    ),
    (
        "3. 声部拆分与清理",
        ["vocal/instrument 分离", "HPSS/中置粗分离", "片段裁剪", "噪声与静音处理"],
    ),
    (
        "4. 旋律转写与乐谱化",
        ["音高轨迹", "MIDI", "简谱/lead sheet 草稿"],
    ),
    (
        "5. 编曲与制作辅助",
        ["配器层次建议", "和声建议", "节奏型建议"],
    ),
    (
        "6. 混音审听与导出",
        ["问题清单", "混响/响度处理", "效果链建议", "版本归档与导出"],
    ),
]


def render_workflow() -> str:
    lines: list[str] = ["歌曲创作辅助建议流程："]
    for title, items in WORKFLOW_STEPS:
        lines.append(f"\n{title}")
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)
