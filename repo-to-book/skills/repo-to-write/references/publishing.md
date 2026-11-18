# 出版与构建检查

技能入口：`repo-to-write <专题目录> [--format html|pdf|all]`。默认生成离线 HTML；显式指定 `pdf` 或 `all` 时生成 PDF。

## 最小依赖与命令

HTML 构建仅依赖 Python 3.9+ 和 `requirements.txt` 中的 `markdown-it-py`，运行时不联网、不调用模型。PDF 另需安装 `requirements-pdf.txt` 和 Chromium（或通过 `--browser` / `CHROME_BIN` 指定现有浏览器）。

```bash
python <skill-dir>/scripts/book.py prepare <专题目录>
# 逐章写完 chapters/<id>/manuscript.md
python <skill-dir>/scripts/book.py check <专题目录>               # 结构、引用与图片检查
python <skill-dir>/scripts/book.py check <专题目录> --delivery    # 完整交付记录检查
python <skill-dir>/scripts/book.py build <专题目录>               # 默认输出 dist/book.html
python <skill-dir>/scripts/book.py build <专题目录> --format pdf  # 输出 PDF 并回填 HTML 页码
python <skill-dir>/scripts/book.py build <专题目录> --format all  # 同时交付 HTML 与 PDF
```

## 输入与路径约定

- `book.json` 位于专题目录根，包含 `title`、`outline`（默认 `outline.md`）、按 `research.json` 顺序排列的 `chapters`（`chapters/<id>/manuscript.md`）与 `sources`（`sources.md`）。
- 每个章节的 `manuscript.md` 必须有且只有一个一级标题，二级、三级标题自动进入目录；可用 `{#stable-id}` 固定锚点。
- 图片独占一段，路径相对当前章目录（如 `![图 1-1 · 题注](assets/fig-01-01.svg)`），`alt` 即为图注。公共来源引用相对当前章目录写为 `[S01](../../sources.md#s01)`。

## 全书结构 Mermaid 流程图

在书名下、目录前嵌入静态 SVG（`overview.mmd` + 实际渲染的 `overview.svg`），在 `book.json` 中登记：

```json
"overview": {
  "source": "overview.mmd",
  "image": "overview.svg",
  "alt": "全书阅读顺序：先介绍工具链入口，再展开架构与描述符格式；箭头表示阅读递进。",
  "chapters": [
    "chapters/01-toolchain/manuscript.md",
    "chapters/02-architecture/manuscript.md",
    "chapters/03-descriptor-format/manuscript.md"
  ]
}
```

`overview.chapters` 必须与 `book.json` 的 `chapters` 列表完全一致。静态 SVG 需包含首元素 `<title>`、非空 `<desc>` 以及根节点 `role="img"` 和 `aria-labelledby`。

## 构建检查与交付检查

- `book.py check <专题目录>`：检查 `book.json` 登记的各章 `manuscript.md` 非空、无残留 `{{...}}` 占位符、无断裂内部锚点、图片文件存在且静态 SVG 符合离线规范。
- `book.py check <专题目录> --delivery`：除上述检查外，核对 `book.json` 的章节列表与 `research.json` 确认的章节顺序一致（未私自删章、拆合章或重排），各章 `chapter_reviews` 均为 `approved`，`core_gaps` 无未解决项，`writing-review.md` 标有 `<!-- r2b:reviewed -->`，且 `visual_review` 为 `passed`。
