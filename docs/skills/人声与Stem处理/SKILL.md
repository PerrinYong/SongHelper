# 技能：人声与 Stem 处理

## 这个技能解决什么问题

当你需要把混合音频拆成更便于处理的部分，比如人声、伴奏、中心声像或谐波/打击内容时，用这个技能。

## 典型需求

- 给一首歌做人声分离
- 提取 center vocal 试着转写
- 先把鼓/打击和谐波拆开做粗分析

## 常用底层工具

- Demucs 分离（外部模型能力）
- `rough-separate --mode center`
- `rough-separate --mode hpss`

## 输入

- 混合音频

## 输出

- vocals / no_vocals（若走 Demucs）
- center / side / minus_center
- harmonic / percussive

## 适用场景

- 为后续旋律提取做准备
- 做 demo 级伴奏 / 练唱版素材
- 粗看一首歌的构成

## 注意事项

- HPSS 和 center 只是粗处理，不等于高质量 stem 分离

> 更完整说明见：`docs/工程能力手册.md`
