# HTML 默认出版

技能入口：`repo-to-write <research-path> [--format html|pdf|all]`，输入为素材目录，不要求 ZIP。默认 HTML；PDF 与双格式都需实际验证 PDF 环境。

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
python <skill-dir>/scripts/book.py build <book-dir> --format all     # 同时交付 HTML 与 PDF
```

## 输入约定

book.json 包含 title、按顺序排列的 chapters 路径、sources 路径；author/language/edition 可选；旧 subtitle 字段兼容读取但不展示。
每个章节一个一级标题，二级、三级标题进入目录；可用 `{#stable-id}` 固定锚点。
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

## 已确认版式

纯白纸面，深杏红书名左对齐，只显示一个书名，下接全书结构流程图，再接无框目录，不设独立封面、目录页、副标题、导读或提示文案。正文宋体回退，标题黑体回退；三级标题 26/21/17px、700 加粗、浅杏红底框；正文与表格用深暖灰，代码与表头用中性浅灰。不要添加大面积红底或红色装饰。

目录覆盖一至三级标题，标题左对齐、页码右对齐，以点线连接。纯 HTML 为连续滚动文档，无固定页码，因此页码栏留空；不估算或填示意页码。PDF 构建通过 Chromium 书签和 PyMuPDF 读取实际页码，回填后重复排版直到页码稳定，输出 PDF 并同步更新 HTML。页码从文档第一页开始，右下角标注，与目录一致。配套 HTML 的页码指向该 PDF，不代表屏幕滚动分页；重建纯 HTML 会清除旧页码。

## 全书结构 Mermaid 流程图

在书名下、目录前嵌入静态 SVG，HTML/PDF 共用；原始 .mmd 随源稿交付。仅制作/更新图时需要 Mermaid CLI 与浏览器；读取已渲染 SVG 的普通 HTML 构建不新增运行依赖。

```json
"overview": {
  "source": "overview.mmd",
  "image": "overview.svg",
  "alt": "全书阅读顺序：先认识对象，再跟踪执行，最后理解边界；箭头表示阅读递进。",
  "chapters": ["manuscript/01-overview.md", "manuscript/02-execution.md", "manuscript/03-boundaries.md"]
}
```

chapters 必须按顺序列出 book.json 当前全部章节；路径需换成本书实际路径。该字段帮助发现过期图，不能替代图义核验。

本轮使用 Mermaid CLI 11.12.0 安装包内的 Mermaid 库完成渲染；CLI 在当前环境被 file:// 策略阻止，因此改用浏览器 set_content + 内联同一库渲染，未关闭访问限制。以下为普通环境的 CLI 用法，按环境安装并使用 `mmdc -i overview.mmd -o overview.svg -b white`（需要时用 `-p <puppeteer配置.json>` 指定现有浏览器）。Mermaid 配置使用 `htmlLabels: false`、系统字体、`theme: base`，白底、浅杏红节点、深暖灰文字和清晰的灰色连线。流程图必须含 `accTitle:` 和 `accDescr:`。CLI 默认导出不一定符合本书静态 SVG 校验：将 title 移至根元素首位，保留 title/desc 的 id，并设置根节点 role="img" 与 aria-labelledby 指向两者；不改变图形布局，不引入 foreignObject、脚本或外部字体。

新写作必须提供此图。旧 book.json 没有 overview 时仍可构建；一旦登记，缺源文件、缺图片、无效 SVG 或章节列表过期都会阻止出版。构建只验证文件契约；实际 Mermaid 渲染、图文对应和视觉检查仍须如实记录。
