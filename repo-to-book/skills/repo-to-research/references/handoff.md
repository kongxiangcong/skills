# 专题目录结构与跨模型交接

研究与写作共用同一个专题目录，按文件划分职责，不交换聊天状态，也不另建 `-publication` 兄弟目录。

```text
专题目录/
├── outline.md                    # 全书约定和逐章大纲，唯一版本
├── START_HERE.md                 # 另一模型接手时的简短说明
├── research.json                 # 章节顺序、材料和配图路径、就绪状态
├── sources.md                    # 研究来源索引，供核对
├── review.md                     # 研究核验结果与已知缺口
├── evidence/                     # 多章共用的证据切片或资料摘要
├── chapters/
│   ├── 01-toolchain/
│   │   ├── materials.md          # 研究阶段写，按 outline.md 小节组织
│   │   ├── assets/               # 本章实际使用的图片及可编辑源
│   │   │   ├── fig-01-01.html
│   │   │   ├── fig-01-01.svg
│   │   │   ├── fig-01-02.png
│   │   │   └── fig-01-02.prompt.md
│   │   └── manuscript.md         # 写作阶段写，本章正式正文
│   └── 02-architecture/
│       └── …
├── book.json                     # 写作阶段登记正文、编排和构建配置
├── writing-review.md             # 写作阶段复核记录
└── dist/                         # 离线 HTML，按需生成 PDF
```

所有索引路径相对专题目录根，统一使用 `/`。图片必须在各章 `assets/` 中，不能只给本机绝对路径、临时 URL 或会话 id。需要离线解释的证据内容写进 `materials.md` 或 `evidence/`。

## `research.json` 示例

```json
{
  "schema_version": 1,
  "title": "TARS 架构与工具链",
  "language": "zh-CN",
  "status": "ready",
  "outline": "outline.md",
  "sources": "sources.md",
  "review": "review.md",
  "evidence_files": ["evidence/entrypoint.py", "evidence/spec-notes.md"],
  "chapters": [{
    "id": "01-toolchain",
    "title": "第 1 章 · 工具链总体流程",
    "materials": "chapters/01-toolchain/materials.md",
    "status": "ready",
    "assets": [{
      "id": "fig-01-01",
      "file": "chapters/01-toolchain/assets/fig-01-01.svg",
      "editable": "chapters/01-toolchain/assets/fig-01-01.html",
      "method": "diagram-design",
      "status": "ready",
      "caption": "图 1-1 · 编译与运行期数据流边界",
      "evidence": ["s01", "s02"]
    }]
  }]
}
```

来源编号在 `sources.md` 用 `## S01 · 标题 {#s01}` 登记。`method` 记录真实制作方式：`diagram-design`、`imagegen`、`provided`、`static-svg`。尚未生成的图片用 `pending`，未完成的章和总包用 `draft`。

## `START_HERE.md` 的四项交接信息

`START_HERE.md` 向接手的写作模型直接交代四件事：

1. **读哪份大纲**：`outline.md`（全书约定与逐章大纲，唯一结构依据）。
2. **各章材料在哪**：`chapters/<id>/materials.md` 与 `chapters/<id>/assets/`，公共来源见 `sources.md`。
3. **正文写到哪**：直接在本目录各章写入 `chapters/<id>/manuscript.md`，通过 `book.json` 登记并构建到 `dist/`。
4. **已知缺口与边界**：见 `review.md` 与各章材料末尾的限制说明。

## 检查与导出命令

```bash
python <skill-dir>/scripts/research.py init <专题目录> --title "专题名称" --repo "<仓库路径或URL>"
python <skill-dir>/scripts/research.py check <专题目录> --draft
python <skill-dir>/scripts/research.py check <专题目录>
# 默认直接在同一专题目录交接，不压缩；仅在需要跨机传输时运行 export：
python <skill-dir>/scripts/research.py export <专题目录> --out <输出路径.zip>
```
