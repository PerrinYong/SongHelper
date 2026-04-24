# melody_factory 架构说明

## 模块定位

`melody_factory` 是一个独立于音频逆向分析链路之外的“正向主旋律构建模块”。

它的设计原则是：

- 生成与表示分离
- 表示与渲染分离
- 先单旋律、后扩展
- 先技术链路、后灵感链路

## 当前子模块

- `domain.py`：核心数据结构
- `schema.py`：MelodySpec 加载与校验
- `validator.py`：规则校验与 validation report
- `abc_converter.py`：MelodySpec 与 ABC 转换
- `midi_exporter.py`：MIDI 导出
- `musicxml_exporter.py`：MusicXML 导出
- `audio_renderer.py`：可试听音频导出
- `score_renderer.py`：MuseScore CLI 渲染入口
- `session_store.py`：工作目录初始化
- `workflow.py`：面向 CLI 的统一工作流入口
- `prompts/`：阶段一 / 二的 Prompt 资源文件
- `schemas/`：JSON schema 资源

## 当前工作流

1. 准备 MelodySeedCard / MelodySpec 资源
2. 校验 MelodySpec
3. 导出 ABC
4. 导出 MIDI / MusicXML
5. 导出 WAV 预听
6. 可选：通过 MuseScore CLI 渲染正式音频

## 未来可扩展方向

- 引入 LLM idea / melody / refine 阶段
- 增加浏览器试听页面
