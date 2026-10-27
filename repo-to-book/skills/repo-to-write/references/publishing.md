# HTML 默认出版

## 最小依赖

HTML 只需要 Python 3.9+ 和 requirements.txt 中的 markdown-it-py；没有浏览器也可生成。
运行时不联网、不读密钥、不调用模型。安装依赖本身可能需要网络，亦可由用户离线安装 wheel。
PDF 是可选能力，另安装 requirements-pdf.txt 和 Chromium，或用 --browser / CHROME_BIN 指向已有浏览器。
不为只要 HTML 的用户默认安装 Playwright/下载浏览器。

```bash
python <skill-dir>/scripts/book.py prepare <research-dir> <book-dir>
# 写完 manuscript/*.md
python <skill-dir>/scripts/book.py check <book-dir>               # 构建/预览检查
python <skill-dir>/scripts/book.py check <book-dir> --delivery    # 完整交付记录检查
python <skill-dir>/scripts/book.py build <book-dir>                  # 默认 HTML
python <skill-dir>/scripts/book.py build <book-dir> --format pdf     # 显式 PDF，同时保留 HTML
```

## 输入约定

book.json 包含 title、按顺序排列的 chapters 路径、sources 路径；subtitle/author/language/edition 可选。
每个章节一个一级标题，二级标题进入目录；可用 `{#stable-id}` 固定锚点。
图片独占一段，路径相对章文件，alt 是题注。支持静态 SVG/PNG/JPEG/WebP；
不支持远程图片、未渲染 Mermaid、动态 SVG/foreignObject/脚本或在线字体。

原始 HTML 按文本显示，避免将未知材料脚本执行进书页。
本版本不内置 LaTeX/KaTeX 渲染器；不要把未渲染公式宣称为排好版。
简短公式可用可读 Unicode/代码，必须精排的公式应由研究阶段提供静态图并说明数学含义。

## 构建结果

HTML 内嵌样式与图片，目录和跨章节/来源链接重写为页内锚点。
不依赖外部图片目录即可阅读，但源稿交付仍包含所有原始图文文件，方便重新编排。
PDF 使用相同 HTML 的印刷样式、页码、阅读器大纲；生成失败保留 HTML，返回非零码。

## 实际检查

普通 check/build 只检查 book.json **当前列出的**文件存在、空稿、模板残留、坏锚点、重复章节、缺图、路径越界、SVG 基本约定。
可以生成部分稿预览，不能据此声称“计划全书已经交付”。

最终执行 `check --delivery`，另检查以下记录：

- `research_files`：prepare/refresh 记录的输入文件 SHA-256，防止新旧证据混用。
- `research_scope`：初始及历次新增研究章节 id 的并集，prepare/refresh 维护，返修不可缩减。
- `coverage`：以 research_scope 的全部章节 id 为键，每项包含 `chapters`（成书路径列表）和 `reason`。
  新包已移除的研究章节也保留条目并说明理由，即使仍映射到成书章节。
  删章用空列表并说明理由；拆分/合并也说明理由。每个成书章节必须被覆盖，允许重组叙事。
- `chapter_reviews`：成书路径到 `pending`/`approved` 的映射；全部实际复核后才批准。
- `core_gaps`：没有核心缺口时为空列表；否则每项须 resolved 并有非空 resolution。
- `writing-review.md`：无 pending 标记，包含 reviewed 标记及实际统稿记录。
- `visual_review`：实际浏览器验收后才记 passed；HTML 构建成功并不等于视觉验收通过。

这些字段是可核验的交付声明，仍需要人工/模型审查事实和理由，程序不证明声明真实。
程序不能证明：源码事实正确、文章有教学价值、图义正确、图片确由所声明工具生成。

用实际浏览器打开 HTML，检查桌面和窄屏；确认图文字缩放后能读、表格与代码不裁切、中文显示正常。
用户要求 PDF 时渲染页面检查，不能只看到文件存在。记录实际检查平台，没测 Windows 就不能称跨平台验证。

## 交付与续写

交付完整 book-dir（源稿/素材/来源/配置）及 dist/book.html。
PDF 只有用户要求并实际成功生成时才列为产物。
下一模型读 plan.md、writing-review.md 和当前章材料即可接续，不需要原模型历史。
不要删除研究证据或用户原稿以“清理交付物”；也不把缓存、字体文件和登录信息放进分发包。
