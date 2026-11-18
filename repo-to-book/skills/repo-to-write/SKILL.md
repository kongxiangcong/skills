---
name: repo-to-write
description: 用户明确要求按已确认大纲和现成研究素材写作技术书时使用；在同一专题目录逐章写入 chapters/<id>/manuscript.md，统稿并构建离线 HTML（PDF 按需）。不开展源码调研，不拆章合章或另建出版目录。
---

# Repo to Write

独立、平台中立的写作与出版技能。只有用户明确发起写作（如「`$repo-to-write <专题目录>`，按已确认大纲写作」）才启动。默认中文、图解优先、直接输出离线 HTML，PDF 按需生成。

## 调用接口与同目录工作方式

```text
repo-to-write <专题目录>
repo-to-write <专题目录> --format html
repo-to-write <专题目录> --format pdf
repo-to-write <专题目录> --format all
```

直接在同一个 `<专题目录>` 内工作，**不另建 `<目录>-publication` 兄弟目录**。研究模型维护 `outline.md`、`chapters/<id>/materials.md` 和 `chapters/<id>/assets/`；写作模型在同一章节目录下写入 `chapters/<id>/manuscript.md`，并在根目录维护 `book.json`、`writing-review.md` 与 `dist/`。

默认采用纯白纸面，唯一书名深杏红、左对齐，下方先放全书结构 Mermaid 流程图，再接无外框目录。不设封面、副标题、导读或阅读提示。一级、二级、三级标题分别为 26、21、17px，全部加粗，以浅杏红框区分层级；标题文字深暖灰，表格和代码使用中性色。

## 职责与结构边界

- **严守 `outline.md` 的编辑决定**：章数、章序、小节顺序、每节承担的内容、例子出现时机与呈现约定，严格以根目录已确认的 `outline.md` 为准；**不允许写作者擅自拆章、合章、重排章节或缩减范围**。
- **节内自主行文与图表编排**：写作者在既定小节内负责组织段落、串联因果推导、调整措辞，并将 `materials.md` 中的字段表与 `assets/` 中的配图自然编排进 `chapters/<id>/manuscript.md`。
- **区分讲解素材与核对底稿**：`materials.md` 中标为“仅供作者核对”的源码路径、行号或具体 case 地址不直接堆进读者看到的字段表；公共来源引用统一指向 `../../sources.md#s01`。
- **不越界调研**：不默认调用研究技能、子代理、出图工具或外网搜索；发现影响核心结论的证据或配图缺口时登记在 `writing-review.md`，继续完成其他章节。

## 执行导航

开工先读 `START_HERE.md`、`outline.md`、`research.json`、`review.md` 和 [writing-style.md](references/writing-style.md)；写每章时按需读取该章的 `materials.md`、所引来源与图片，不一次塞入全书材料。

| 当前任务 | 必读资料 |
|---|---|
| 标题规范、英文术语保留与去 AI 腔文风约束 | [writing-style.md](references/writing-style.md) |
| 依据大纲与每章材料组织正文、编排图文 | [writing.md](references/writing.md) |
| 同目录交接、缺口处理与跨环境运行 | [portable-handoff.md](references/portable-handoff.md) |
| 初始化配置、构建检查、预览和出版 | [publishing.md](references/publishing.md) |

## 完成标准

按 `outline.md` 完成全部章节的 `chapters/<id>/manuscript.md`，完成全书统稿与事实限定核对并记入 `writing-review.md`。执行 `book.py check <专题目录>` 与 `book.py build <专题目录>` 生成 `dist/book.html`（显式请求时生成 `dist/book.pdf`）。
