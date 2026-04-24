# melody_factory 模块说明

这是 SongHelper 中专门承载“AI Agent 协助的主旋律创作方法”的技术模块。

## 当前阶段范围

当前只负责**技术流程**，暂不接管灵感生成。

也就是说，它现在关注的是：

- 维护 MelodySeedCard / MelodySpec 资源结构
- 定义 MelodySpec
- 把 MelodySpec 转成 ABC
- 把 MelodySpec / ABC 转成 MIDI
- 把 MelodySpec / ABC 转成 MusicXML
- 把 MelodySpec / ABC 转成可试听音频
- 校验 MelodySpec
- 调用 MuseScore CLI 做正式音频导出
- 为单首歌建立 melody_factory 工作目录

## 当前不负责的部分

- 旋律种子卡自动生成
- LLM 灵感头脑风暴
- 自动旋律相似度 / 版权判断

## 当前核心链路

`MelodySpec JSON -> ABC -> MIDI / WAV`

扩展后可走：

`MelodySpec JSON -> ABC -> MIDI / MusicXML -> MuseScore -> WAV / MP3`

## 当前可直接跑通的技术闭环

1. `init` 初始化工作目录与模板资产
2. 从 `sample.mspec.json` 出发做 `validate`
3. 导出 `ABC / MIDI / MusicXML / WAV`
4. 生成 `preview_manifest.json`

## 当前资源结构

- `prompts/`：阶段一/二使用的 Prompt 资源文件
- `schemas/`：MelodySeedCard / MelodySpec JSON Schema
- `*.py`：技术链路代码实现

## 相关文档

- `src/songhelper/melody_factory/AIAGENT_GUIDE.md`
- `src/songhelper/melody_factory/SKILL.md`
- `src/songhelper/melody_factory/ARCHITECTURE.md`
