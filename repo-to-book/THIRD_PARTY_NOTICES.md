# 来源与第三方许可

核查日期：2026-10-27。此项目独立实现出版与安装脚本，不是以下项目的官方分支。

## diagram-design

来源：https://github.com/cathrynlavery/diagram-design

图解指导结合该项目的编辑式 HTML/SVG 方法、图型选择、连接线、复杂度与可访问性规范。研究技能中的 `references/visual-production.md` 是面向中文技术书的精简适配，不是完整技能镜像。本项目提供对上游 `self_check.py` 与 `export_svg.py --system-fonts` 的薄调用器；未包含上游实现或字体。安装上游后，以实际安装版本为准。

实际参考：
- `skills/diagram-design/SKILL.md`（frontmatter 版本 2.6）
- `skills/diagram-design/references/type-architecture.md`，blob `139082e743dfa692f064897d2a109c35b94e9a56`
- `skills/diagram-design/references/export.md`
- 根目录 `LICENSE`，blob `5270ecfc40942fc2da652a7a2f3e687fc6851ba3`

为适配的指导保留上游 MIT 通知：

```text
MIT License

Copyright (c) 2025 Cathryn Lavery

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## deepinfer-book

来源：https://github.com/JerryLiu369/deepinfer-book

借鉴源码侦察、知识主线、研究与写作分离、版本固定和章节审查的组织方法。未复制其书稿、研究笔记、图稿或构建代码。它是一部具体项目专著，不是本项目的运行依赖。

## deep-dive-research

来源：https://github.com/da-damu/deep-dive-research

借鉴问题驱动研究、成稿自足、证据核对和 Markdown 到 PDF 的交付方式。未复制金融规则、配套读物、图稿或脚本。该项目代码与配套读物使用不同许可，本项目不分发其配套读物。

## Codex 技能格式

https://developers.openai.com/codex/build-skills

采用 SKILL.md、按需 references、agents/openai.yaml，以及当前官方 `.agents/skills` 本地发现路径。不固定模型名称；阶段一默认使用 Codex 的子代理能力，阶段二无此依赖。

## 输出中的源码与字体

生成书籍不改变被研究项目的许可。少量必要代码摘录注明来源与原许可，不复制完整受限资料。模板使用系统字体名称；本仓库和压缩包不分发字体文件。示例源码、图稿与示例书为本项目原创，按根目录 MIT 许可发布。

## Codex 内置 imagegen（阶段一）

2026-10-27 核对官方技能：
https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md

读取的文件 blob：c39b1f921ce679f08416ab16ceb01945835bb950。
本项目只指导调用已安装技能，不分发上游技能实现或创建 API runner。
默认使用内置 image_gen；CLI/API 回退必须用户明确选择。
运行时以实际安装的技能与可用工具为准。

## v2 的独立包装

研究和写作各携带同一份轻量 handoff.py 文件契约，测试保证两份一致，
是为了使两个技能均可单独安装，不是两个相互依赖的运行服务。

## boltons 行为验收样例

`examples/priority-queue/research/evidence/upstream/` 保存了 mahmoud/boltons
commit `d31d821d56c8f7756af9c30a864077f2e5855321` 的必要源码、构建说明与测试，
遵循随附 `LICENSE`（BSD）及文件头许可。详见 evidence/upstream-provenance.json。
研究/写作材料由本次任务生成；概念插画由内置 imagegen 实际生成，提示词随图保存。
diagram-design 仅作为外部制作工具调用；本项目不把上游工具及字体打包。

## Diátaxis 与 Humanizer：写作规范来源（2026-10-27）

Diátaxis，Daniele Procida，源码固定 commit `957c09ca40b4a1edc23874f713e01937d50d54d5`：
- https://diataxis.fr/
- https://diataxis.fr/explanation/
- https://diataxis.fr/reference-explanation/
- https://github.com/evildmp/diataxis-documentation-framework/tree/957c09ca40b4a1edc23874f713e01937d50d54d5

实际阅读三页及源码 `source/index.rst`、`source/explanation.rst`、`source/reference-explanation.rst` 和 `LICENSE.rst`。上游为 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，提供内容不作保证。本项目借鉴读者需求与四类内容的思想，自写中文技术书规则和教学假设；未复制/翻译上游段落、图、比喻或示例，不将上游全文纳入 MIT。写作规范没有要求写作者联网获取上游。若后续复制或改编其受保护表达，须为该部分保留归属、改动和相同许可，不能沿用根 MIT 代替。

Humanizer，Siqi Chen，`SKILL.md` version 3.1.0，固定 commit `8c307f367c91bd974002f10f2be2965d642c13df`：
https://github.com/blader/humanizer/blob/8c307f367c91bd974002f10f2be2965d642c13df/SKILL.md

实际阅读完整技能与 LICENSE。`references/writing.md` 将保留信息、整段编辑和用户风格优先等方法适配为中文技术写作规则，未镜像完整规则表；英语标点硬规则不移植，也不分发其链接的 Wikipedia 文本。为这部分方法适配保留 MIT 通知；项目其他部分许可不变：

```text
MIT License

Copyright (c) 2025 Siqi Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
