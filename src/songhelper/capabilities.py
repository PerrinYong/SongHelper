from __future__ import annotations

CAPABILITY_GROUPS = {
    "创作与策划": [
        "主题/情绪/风格拆解",
        "歌曲结构设计",
        "歌词与 hook 优化",
        "参考曲拆解与方向建议",
    ],
    "乐理与音频分析": [
        "BPM/节拍估计",
        "调性、和弦、段落分析",
        "旋律动机与能量曲线分析",
        "参考曲对比报告",
    ],
    "音频处理": [
        "vocal/instrument 分离",
        "裁剪、拼接、归一化",
        "基础效果链建议",
        "版本导出与整理",
    ],
    "旋律与乐谱": [
        "人声音高提取",
        "MIDI 生成",
        "简谱/音名/lead sheet 草稿",
        "旋律版本对比",
    ],
    "工程化支持": [
        "工作目录初始化",
        "分析报告沉淀",
        "批处理脚本编写",
        "可扩展 CLI 工作台",
    ],
}


def render_capabilities() -> str:
    lines: list[str] = ["SongHelper 当前可支持能力："]
    for group, items in CAPABILITY_GROUPS.items():
        lines.append(f"\n[{group}]")
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)
