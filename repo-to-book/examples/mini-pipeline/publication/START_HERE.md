# 从这里开始：读懂 Mini Pipeline

这是阶段一交接的研究素材，不是已写好的书。研究与绘图已经停止，
**只有用户另行调用 repo-to-book，或明确委托其他模型写作时，才开始阶段二。**

## 阅读顺序

先读 `research.json`（版本、章节顺序、图片实际路径），再读 `plan.md`
（读者、主题主线与范围）、`review.md`（实际核验与已知局限）。
写每章时只加载该章材料、所引来源与图片；不要一次塞入全部材料。

- **01-overview · 第 1 章 · 先找到贯穿项目的对象**：`chapters/01-overview/materials.md`
- **02-trace · 第 2 章 · 用具体值走完一次执行**：`chapters/02-trace/materials.md`
- **03-boundaries · 第 3 章 · 正常路径之外，接口还承诺什么**：`chapters/03-boundaries/materials.md`

共同来源见 `sources.md`。`evidence_files` 登记的源码切片与资料摘要随包提供。
图片在各章 `assets/` 中；提示词、可编辑图稿和题注用于理解或修订，不能代替实际图片。

## 给任意写作模型的指令

使用 repo-to-book 的写作方法，将这些材料组织成一部有统一主线的图解技术书。
不要重新运行研究、联网查证或调用 Codex；不要依赖原聊天、临时工具 id 或原机器路径。
先设计各章的叙事与衔接，再逐章独立组织语言，不拼贴研究笔记。
图前交代问题，图后带读关键变化与设计取舍；使用包内静态图片和稳定来源编号。
区分源码事实、文档声明、运行观察、推断及未知。发现证据缺口时明确标出，
不能用常识补成项目事实；影响核心结论的缺口退回研究阶段，其余明示限制。

默认交付源稿目录（章节 Markdown + 实际图片 + 来源 + 编排配置）和离线 HTML。
PDF 仅在用户明确要求时另行生成。不要擅自把图片发往外部服务。

## 有终端的运行环境

将独立 `repo-to-book` 技能包放到任意目录（无需 Codex、模型 API 或研究技能）。
安装它的 `requirements.txt`，然后执行：

```bash
python <repo-to-book>/scripts/book.py prepare <本素材目录> <新的图书目录>
# 按材料写完 manuscript/ 下的各章，并填写 writing-review.md
python <repo-to-book>/scripts/book.py build <新的图书目录>
# 只有明确需要 PDF 时：安装 requirements-pdf.txt 和 Chromium，再用 --format pdf
```

## 仅聊天、没有文件执行工具的环境

上传本包与独立写作技能包；模型可以按章节交付 Markdown 与图片插入位置，
用户将文件保存进图书目录后运行同一出版命令。
没有文件读取能力时，按章提供 materials.md、引用的来源条目及图片附件。
没有执行过出版命令，不能声称已生成或验证 HTML/PDF。

本包只有普通 UTF-8 Markdown、JSON 与本地素材文件；不包含模型会话状态或账号凭据。
打包只证明文件齐备，不代表技术事实正确。给第三方模型前，请确认内部材料允许外传。
