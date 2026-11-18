# Repo to Book

**一个专题一个目录，一份经确认的 `outline.md`；研究按章备料，写作按章成稿。**

项目包含两个可独立安装和跨模型配合使用的技能：

| 技能 | 推荐运行环境 | 职责与停点 |
|---|---|---|
| `repo-to-research` | Codex | 入口一：讨论并更新 `outline.md`（全书约定 + 逐章大纲），停下等确认。<br>入口二：按确认版大纲逐章收集 `chapters/<id>/materials.md` 与 `assets/` 配图，核验后停止。 |
| `repo-to-write` | 任意写作模型 | 在同一专题目录内读取 `outline.md` 与各章 `materials.md`，逐章写入 `chapters/<id>/manuscript.md`，统稿并构建 `dist/book.html`（按需生成 PDF）。不拆章合章，不另建出版目录。 |

## 专题目录结构

```text
专题目录/
├── outline.md                  # 全书约定和逐章大纲，唯一版本
├── START_HERE.md               # 另一模型接手时的四项核心说明
├── research.json               # 章节顺序、材料和配图路径、就绪状态
├── sources.md                  # 研究来源索引，供核对
├── review.md                   # 研究核验结果与已知缺口
├── evidence/                   # 多章共用的证据
├── chapters/
│   ├── 01-toolchain/
│   │   ├── materials.md        # 研究阶段写，按大纲小节组织（区分正文素材与核对底稿）
│   │   ├── assets/             # 本章实际使用的图片及可编辑源
│   │   └── manuscript.md       # 写作阶段写，本章正式正文
│   └── 02-architecture/
│       └── …
├── book.json                   # 写作阶段登记正文、结构图和构建配置
├── writing-review.md           # 写作统稿与渲染检查记录
└── dist/                       # 离线 HTML，按需生成 PDF
```

## 阶段切换指令

| 你的指令 | 技能行为 | 停点 |
|---|---|---|
| 「讨论大纲」「把第二章的几个特点再合并一下」 | 普通对话或 `$repo-to-research` 更新 `outline.md`，按需做少量查证辅助判断章节切分。 | 更新 `outline.md` 后等你继续讨论。 |
| 「大纲可以了，按这版调研」或「`$repo-to-research <专题目录>`，调研各章素材」 | 直接按确认版收集各节素材、制作配图、核验并整理离线目录。 | 所有约定章节完成后交接。 |
| 在当前或另一个模型中说「`$repo-to-write <专题目录>`，按已确认大纲写作」 | 读取 `outline.md` 和各章 `materials.md`，逐章写入 `manuscript.md`，统稿并构建所需格式。 | 交付正文和构建产物。 |

## 写作风格约定

写作风格独立维护在 [skills/repo-to-write/references/writing-style.md](skills/repo-to-write/references/writing-style.md)：

1. **标题直接陈述技术对象，不用引导式问题**（如用“算子融合与输出轴序”，不用“为什么系统要分成这几层？”）。
2. **保留必要英文术语，不要机械翻译**（如 `descriptor`、`tile`、`stride`、`pass`、`pipeline`、`fallback` 直接保留英文）。
3. **开门见山写因果，去 ChatGPT 腔**（删掉公关式开场与总结升华，不造抽象包装词，并列字段直接进表或图）。

## 常用脚本命令

```bash
# 安装技能到 ~/.agents/skills/
python scripts/install.py

# 阶段一：初始化与检查研究素材
python skills/repo-to-research/scripts/research.py init ./topic-dir --title "专题名称" --repo "<URL>"
python skills/repo-to-research/scripts/research.py check ./topic-dir

# 阶段二：同目录准备写作配置、检查与构建
python skills/repo-to-write/scripts/book.py prepare ./topic-dir
python skills/repo-to-write/scripts/book.py check ./topic-dir
python skills/repo-to-write/scripts/book.py check ./topic-dir --delivery
python skills/repo-to-write/scripts/book.py build ./topic-dir

# 运行回归测试与打包
python -m unittest discover -s tests -v
python scripts/package.py --out /tmp/release-out
```
