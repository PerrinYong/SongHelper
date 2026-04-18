# 任务示例（合并自 music_agent_workspace）

## 示例 1：分析一首现有歌曲

```bash
python -m songhelper.cli probe-audio "workspace/某首歌/source/input.wav" "workspace/某首歌/analysis/probe.json"
python -m songhelper.cli analyze "workspace/某首歌/source/input.wav" "workspace/某首歌/analysis/analysis.json"
```

## 示例 2：尝试从录音中粗分离中心声部并提旋律

```bash
python -m songhelper.cli rough-separate "workspace/某首歌/source/input.wav" "workspace/某首歌/stems/rough_center" --mode center
python -m songhelper.cli transcribe "workspace/某首歌/stems/rough_center/center_mono.wav" "workspace/某首歌/scores/melody.mid" "workspace/某首歌/scores/melody_jianpu.txt" "workspace/某首歌/scores/melody_notes.json"
```

## 示例 3：把多个音频片段拼起来并做轻混响、标准化

```bash
python -m songhelper.cli concat-audio clip1.wav clip2.wav clip3.wav --output merged.wav
python -m songhelper.cli apply-reverb merged.wav merged_hall.wav --preset hall
python -m songhelper.cli normalize-audio merged_hall.wav merged_hall_norm.wav
```
