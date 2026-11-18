# 跨模型同目录交接与补调研

## 一、输入与同目录结构

输入为一个已完成研究备料的专题目录，包含 `outline.md`、`START_HERE.md`、`research.json`、`sources.md`、`review.md`、各章 `chapters/<id>/materials.md`、`chapters/<id>/assets/*` 以及 `evidence/*`。不需要原仓库完整 checkout，也不依赖 Codex 会话状态。

写作阶段直接在该专题目录内工作，**不复制创建 `-publication` 兄弟目录**：

```text
专题目录/
├── outline.md                    # 全书约定和逐章大纲，唯一版本
├── START_HERE.md                 # 跨模型接手说明
├── research.json                 # 章节顺序、材料和配图路径、就绪状态
├── sources.md                    # 研究来源索引
├── review.md                     # 研究核验结果与已知缺口
├── evidence/                     # 共用证据文件
├── chapters/
│   └── 01-toolchain/
│       ├── materials.md          # 研究阶段产出（只读参考，写作不覆盖）
│       ├── assets/               # 本章图片及可编辑源
│       └── manuscript.md         # 写作阶段产出（本章正式正文）
├── book.json                     # 写作阶段登记正文路径、结构图与构建状态
├── writing-review.md             # 写作统稿与渲染检查记录
└── dist/                         # 构建输出的 book.html（及按需生成的 book.pdf）
```

## 二、有文件与终端的运行环境

```bash
python <skill-dir>/scripts/book.py prepare <专题目录>
# 逐章完成 chapters/<id>/manuscript.md，并填写 writing-review.md
python <skill-dir>/scripts/book.py check <专题目录>
python <skill-dir>/scripts/book.py build <专题目录>
```

`book.py prepare <专题目录>` 只在专题目录内生成 `book.json`、`writing-review.md` 以及尚未存在的 `chapters/<id>/manuscript.md` 初始骨架；若某章 `manuscript.md` 已经存在（例如作者已写好或手改过），`prepare` 会原样保留，绝不覆盖。

## 三、仅聊天环境

在没有文件执行工具的聊天界面中，可按 `START_HERE.md` 顺序提供 `outline.md` 与对应章节的 `materials.md`、图片。模型直接输出该章 `manuscript.md` 的内容，由用户保存至 `chapters/<id>/manuscript.md` 后在本地运行 `book.py build <专题目录>`。

## 四、补调研与增量更新

由于研究材料（`materials.md`、`assets/`）与正式正文（`manuscript.md`）在同一章节目录下分文件存放：

1. 写作中若发现材料缺口，在 `writing-review.md` 和 `book.json` 的 `core_gaps` 中记录具体问题，继续写其他无依赖章节。
2. 回到研究阶段补充查证时，直接更新对应章的 `materials.md`、`assets/` 或 `sources.md`，手改过的 `manuscript.md` 自然保留。
3. 补齐材料后，写作模型只需对照更新后的 `materials.md` 修订对应章节的 `manuscript.md`，再重新运行 `book.py build <专题目录>`。
