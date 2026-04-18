# 从 music_agent_workspace 合并进 SongHelper 的内容

本次已将 `E:\1-Art\music_agent_workspace` 中的代码工具、技能说明、文档知识与任务方法整合进当前工程。

## 已合并的代码能力

来源脚本：

- `audio_probe.py`
- `source_separation.py`
- `concat_audio.py`
- `apply_reverb.py`
- `normalize_audio.py`

在 SongHelper 中的落点：

- `src/songhelper/audio_probe.py`
- `src/songhelper/rough_separation.py`
- `src/songhelper/ffmpeg_tools.py`
- CLI 子命令：
  - `probe-audio`
  - `rough-separate`
  - `concat-audio`
  - `apply-reverb`
  - `normalize-audio`

## 已合并的知识与方法

来源文档：

- `README.md`
- `PROJECT_FRAMEWORK.md`
- `docs/capability_map.md`
- `docs/workflow_blueprint.md`
- `examples/tasks.md`
- `AGENT_SKILL_MUSIC_CREATION.md`

在 SongHelper 中的落点：

- `docs/MUSIC_CREATION_SKILL.md`
- `docs/MERGED_MUSIC_AGENT_WORKSPACE.md`
- `docs/TASK_EXAMPLES.md`
- `README.md` 与现有能力说明文档的增强

## 合并策略说明

- 没有把来源工程原样复制成平行目录
- 优先保留 SongHelper 现有更强实现
- 对来源工程中仍有价值的内容，改造成当前包结构、CLI 和文档体系中的一等能力

## 当前工程因此新增的能力

- 音频基础探测（更偏元数据 / 频谱统计）
- HPSS 粗分离
- 中置声像粗分离
- ffmpeg 音频拼接
- ffmpeg 简单混响预设
- ffmpeg 响度标准化
- 更明确的音乐创作 Agent 技能与任务模板文档
