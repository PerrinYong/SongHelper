# melody_factory AIAgent 操作手册

本文件面向后续执行任务的 AI Agent。

目标不是解释背景，而是让 Agent 以最短路径掌握：

- 什么时候应该使用 `melody_factory`
- 应该按什么顺序执行
- 每一步读什么、写什么
- 什么时候继续，什么时候停下

---

## 1. 模块定位

`melody_factory` 是 SongHelper 中负责“主旋律创作技术链路”的模块。

当前只负责：

- MelodySpec / ABC / MIDI / MusicXML / WAV 之间的转换
- MelodySpec 规则校验
- melody_factory 工作区初始化
- 预览清单生成
- MuseScore CLI 渲染入口

当前**不负责**：

- 灵感生成
- LLM 自动写种子卡
- LLM 自动写 MelodySpec
- 自动旋律相似度判断

如果任务本质是“帮用户发明旋律”，而不是“处理已有 MelodySpec / ABC”，当前模块只能提供技术支撑，不能独立完成创作阶段。

---

## 2. 什么时候应该调用 melody_factory

当满足以下任一条件时，应优先考虑：

1. 用户已经提供或确认了 MelodySpec JSON
2. 用户已经提供 ABC，需要转成 MIDI / MusicXML / WAV
3. 用户希望把主旋律草稿落成可试听资产
4. 用户需要建立标准化的主旋律工作目录
5. 用户需要对 MelodySpec 做程序规则校验

---

## 3. 工作区约定

目标目录：

`workspace/<作品名>/melody_factory/`

子目录含义：

- `inputs/`：seed 输入
- `specs/`：MelodySpec JSON
- `abc/`：ABC
- `midi/`：MIDI
- `audio/`：WAV 预听
- `exports/`：MusicXML 等交换格式
- `session.json`：当前会话信息
- `preview_manifest.json`：候选清单

初始化后通常会自动包含：

- `inputs/sample.seed.json`
- `specs/sample.mspec.json`
- `README.md`

---

## 4. Agent 推荐执行顺序

### 路径 A：从模板跑通技术链

适用于：

- 模块自检
- 首次初始化某首歌
- 给用户演示当前能力

执行顺序：

1. `melody-factory init <song>`
2. 读取 `workspace/<song>/melody_factory/specs/sample.mspec.json`
3. `melody-factory validate`
4. `melody-factory spec-to-abc`
5. `melody-factory spec-to-midi`
6. `melody-factory spec-to-musicxml`
7. `melody-factory spec-to-audio`
8. `melody-factory preview-manifest`

### 路径 B：处理用户提供的 MelodySpec

适用于：

- 用户已有结构化主旋律
- 用户要导出 ABC / MIDI / MusicXML / WAV

执行顺序：

1. 先 `validate`
2. 如果 `valid=false`，先停下并回报错误
3. 如果只有 warning，可继续，但要向用户说明
4. 再按需要导出：
   - `spec-to-abc`
   - `spec-to-midi`
   - `spec-to-musicxml`
   - `spec-to-audio`
5. 最后生成 `preview-manifest`

### 路径 C：处理用户提供的 ABC

适用于：

- 用户已经有 ABC 文本
- 用户只需要交换格式或试听

执行顺序：

1. `abc-to-midi`
2. `abc-to-musicxml`
3. `abc-to-audio`
4. 如果用户需要正式音源渲染，再 `render-audio`

---

## 5. 命令速查

### 初始化

```bash
python -m songhelper.cli melody-factory init <作品名>
```

### 校验 MelodySpec

```bash
python -m songhelper.cli melody-factory validate <spec.json> [report.json]
```

### MelodySpec 导出

```bash
python -m songhelper.cli melody-factory spec-to-abc <spec.json> <out.abc>
python -m songhelper.cli melody-factory spec-to-midi <spec.json> <out.mid>
python -m songhelper.cli melody-factory spec-to-musicxml <spec.json> <out.musicxml>
python -m songhelper.cli melody-factory spec-to-audio <spec.json> <out.wav>
```

### ABC 导出

```bash
python -m songhelper.cli melody-factory abc-to-midi <in.abc> <out.mid>
python -m songhelper.cli melody-factory abc-to-musicxml <in.abc> <out.musicxml>
python -m songhelper.cli melody-factory abc-to-audio <in.abc> <out.wav>
```

### MuseScore 渲染

```bash
python -m songhelper.cli melody-factory render-audio <in.musicxml|in.mid> <out.wav> --musescore <exe>
```

### 生成预览清单

```bash
python -m songhelper.cli melody-factory preview-manifest <作品名>
```

---

## 6. 关键输入输出约定

### 6.1 `validate`

输入：

- 一个 `.mspec.json`

输出：

- 终端 JSON
- 可选 `validation_report.json`

Agent 必须关注字段：

- `valid`
- `severity`
- `errors`
- `warnings`
- `suggestions`

### 6.2 `spec-to-*`

输入：

- 一个合法或至少可解析的 MelodySpec JSON

输出：

- `.abc`
- `.mid`
- `.musicxml`
- `.wav`

### 6.3 `preview-manifest`

输入：

- 某首歌的 `workspace/<song>/melody_factory/`

输出：

- `preview_manifest.json`

适合后续：

- 前端预览页
- Agent 汇总候选资产
- 批量渲染流程

---

## 7. Agent 的继续 / 停止规则

### 必须停止并回报用户的情况

1. `validate.valid == false`
2. MelodySpec 无法解析
3. ABC 无法解析
4. MuseScore CLI 不存在但用户要求正式音频渲染

### 可以继续但必须说明 warning 的情况

1. `severity == warning`
2. 音域超过八度但仍未到 error
3. cadence 与句尾不完全一致
4. 歌词与音符数量偏差较大

### 默认可继续的情况

1. 仅做技术转换，无结构错误
2. 只需要从 spec / abc 导出中间资产

---

## 8. 常见错误与处理策略

### 错误：`highest_word 没有真正落在旋律最高点`

处理：

- 不要直接假装通过
- 回报用户或调用后续修正步骤
- 可建议调整最高音位置或修改 `highest_word`

### 错误：小节总拍数不匹配

处理：

- 停止导出
- 先修 `rhythm`

### 警告：`cadence 声明为 stable，但句尾未明显落稳到主音`

处理：

- 可以继续导出
- 但必须提示用户：声明与实际结尾不完全一致

### 错误：找不到 MuseScore

处理：

- 不影响 `ABC / MIDI / MusicXML / 简易 WAV` 输出
- 仅停止 `render-audio`
- 建议用户提供 `--musescore`

---

## 9. 推荐给 Agent 的默认策略

### 如果用户没有给任何文件

- 不要硬执行
- 先建议使用 `melody-factory init <song>`

### 如果用户给了 MelodySpec

- 先 `validate`
- 再导出所需格式

### 如果用户只说“帮我做主旋律工作流”

- 当前不要擅自接管灵感生成
- 应说明：模块已具备技术链，可先初始化工作区和模板

---

## 10. Agent 最短可执行闭环

如果 Agent 只想做一条最短的成功路径，直接执行：

1. `melody-factory init <song>`
2. `melody-factory validate workspace/<song>/melody_factory/specs/sample.mspec.json`
3. `melody-factory spec-to-abc ...`
4. `melody-factory spec-to-midi ...`
5. `melody-factory spec-to-musicxml ...`
6. `melody-factory spec-to-audio ...`
7. `melody-factory preview-manifest <song>`

只要这 7 步走通，就说明当前 `melody_factory` 技术链是可工作的。
