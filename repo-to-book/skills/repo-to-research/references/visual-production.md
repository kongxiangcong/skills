# 图像生产：diagram-design 与内置 imagegen

默认两者一起进入配图规划，但每张图按用途选择，避免用生成插画代替需要精确核对的拓扑。
绘图在研究阶段完成；写作阶段只需现成图片、题注与图义，不再依赖这些工具。

## 路由

| 要解释的内容 | 默认工具 | 交付 |
|---|---|---|
| 架构边界、模块依赖、调用顺序、状态、内存/张量布局、调度与定量关系 | diagram-design | 可编辑 HTML + 离线静态 SVG |
| 概念或空间直觉、场景化知识、难用简单形状表达的教学插画 | Codex 内置 imagegen | 实际 PNG/JPEG/WebP + 实际提示词 |
| 官方截图、用户提供图 | 原样保留并标来源、许可与图义 | 本地图片；不冒充自己生成 |

重要机制优先多图走读，不把内容压成一张全景海报。若某章没有适合 imagegen 的知识，不硬凑装饰。
全书无合理 imagegen 用途时，在 review.md 说明依据；不以此隐藏工具不可用。

## diagram-design

从当前会话技能列表找到并读取已安装的 SKILL.md，再读本张图的类型/语义规范。
输入为已核实的图义和证据：教学问题、节点、关系方向、准确标签、读图顺序和简化边界；不要求用户预先提供图片素材。已有截图或参考图是可选输入，不能代替事实证据。
本书使用 assets/diagram-style.md 的中文高对比红色离线印刷风格；不修改用户全局默认样式。
优先保留明确的语义层次、少量视觉焦点、直角连线、足够留白；密度高时拆图。
不能为了套样式删除必要节点/边；省略的关系在材料中说明。

生成自包含 HTML；按上游导出约定保存静态 SVG。本流程已经明确要求导出，可执行：

```bash
python <skill-dir>/scripts/figure.py import <figure.html> --diagram-skill <已安装diagram-design目录>
```

适配器调用上游 self_check.py 与 export_svg.py --system-fonts，失败就修图，不能静默绕过。
它不调用模型，也不会凭空创建图。需要视觉检查时：

```bash
python -m pip install -r <skill-dir>/requirements-preview.txt
python <skill-dir>/scripts/figure.py preview <figure.svg> --out <preview.png> --browser <浏览器路径>
```

preview 是校对产物，不必进交接包。静态替代 SVG 仅在用户批准替代或已有素材时使用，
method 必须写 static-svg，不能标 diagram-design。不打包字体文件，使用系统字体与离线回退。

## 内置 imagegen

先读当前 Codex 的 imagegen SKILL.md，按其实际可用能力调用；不臆造参数或命令。
默认内置 image_gen，不需要本技能读取 API key。不擅自用 CLI/API 或替代模型，亦不编写自制 SDK runner。
当前上游规定 CLI 是用户明确选择的回退方式；内置工具不可用时保留 pending 并说明缺口。

提示词描述：教学目的、要显示的概念/过程、信息层级、少量准确标签、不能误画的事实、
读图方向、统一视觉风格、不要出现的装饰或伪数据。生成插画中的箭头、字和数量都要复核。
涉及精确关系可将其画成 SVG 主图，imagegen 提供辅助概念图；不能因图片漂亮就把它作为证据。

工具返回后，使用其实际文件位置，将选中的图复制进本章 assets/。
不假定 image_gen 接受目标输出路径，不把 `$CODEX_HOME/generated_images/...` 留给下一平台。
已有图片编辑前先确保编辑目标在当前模型可见；不凭一个过期 opaque id 编辑。
保存最终提示词与模式，失败变体无需全部归档。

## 每张图的材料

research.json 登记 id/file/method/status/caption/evidence，以及 editable 或 prompt。
materials.md 解释：这张图回答什么、如何阅读、依赖哪个源码事实、有哪些简化、
标签与箭头意味着什么、哪些不能从图中推出。只保留一份事实依据，不另造复杂图数据库。

完成后查看真实渲染，至少检查中文、连线、图例、图义、剪裁、文字大小及缩到正文后的可读性。
源码/证据核对与视觉核对是两项工作；两者完成才标 ready。

## 上游依据（2026-10-27 核对）

- https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/SKILL.md
- https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/export.md
- https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md

路径与工具能力可能随上游变化；运行时以实际安装的技能为准，不固定模型名。
