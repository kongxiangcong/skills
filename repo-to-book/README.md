# Repo to Book · v2.2

**Codex 做研究，用户选择模型写书。** 项目包含两个可独立安装的技能，不是新建的代理框架。

| 技能 | 负责什么 | 到哪里停止 |
|---|---|---|
| `repo-to-research` | 主 agent 规划，源码/外部调研子 agent 逐章取证，默认用 diagram-design 与内置 imagegen 按用途完成实际配图 | 交付研究材料目录；不写正文、不出版、不自动调用下一技能 |
| `repo-to-write` | 任意模型按现成素材组织语言、串联章节、编排图文 | 源稿目录 + 默认离线 HTML；用户要求时才另出 PDF |

两个阶段通过普通 Markdown、JSON、静态图片和必要证据文件交接，不传会话状态或私有模型接口。

## 安装

Python 3.9+。完整项目在根目录执行：

```bash
python scripts/install.py
```

默认把两个技能分别安装到 `~/.agents/skills/`。也可只装一个：

```bash
python scripts/install.py --skill repo-to-research
python scripts/install.py --skill repo-to-write --dest ./my-agent-skills
```

**旧版本不会被覆盖。** 已安装旧 `repo-to-book` 或已有 `repo-to-write` 时，先备份并移开对应目录，或使用新的 `--dest`。
也可直接将独立技能 ZIP 中的目录放入目标平台支持的技能目录。
不支持技能发现的平台，直接读取 repo-to-write/SKILL.md 作为写作说明即可。

安装器不安装模型、出图工具、Python 依赖或浏览器。
阶段一需要当前 Codex 真正具备源码/网络读取、子代理、diagram-design 与内置 imagegen 能力。
diagram-design 的安装方法按其官方仓库；内置 imagegen 按当前 Codex 提供的版本读取与调用。
缺工具时不会静默改成自画图、付费 API 或单 agent 并假称完成。

## 阶段一：在 Codex 研究与出图

在新会话使用：

```text
使用 $repo-to-research。
目标项目：<GitHub URL 或本地仓库>
输出素材目录：./research

为懂软件工程、但没系统读过此项目的人准备中文图解技术书素材。
先侦察并固定源码版本，规划主题、知识主线、章节与前置知识。
默认由主 agent 规划与综合，源码和外部资料交给子 agent 逐章深入研究。
使用 diagram-design 绘制精确机制图，使用 Codex 内置 imagegen 生成有教学价值的概念插画。
图像保存为实际本地文件，附题注、来源、读图说明、编辑源或提示词。
各章材料要足够让另一模型离线写作，不只交链接。
完成计划中的所有章节素材与核验，交付完整素材目录后停止（默认不生成 ZIP），不写书，不调用 repo-to-write。
```

研究工具仅维护文件，不调用模型或自行启动 agent：

```bash
python skills/repo-to-research/scripts/research.py init ./research --title "读懂某项目" --repo "<URL>"
python skills/repo-to-research/scripts/research.py check ./research
# 检查通过后直接交付 ./research 素材目录；默认无需 ZIP。
```

研究不是收集越多越好：围绕章节问题取证，源码/文档/运行/推断/未知分别记录。
实际多 agent 分工、图的事实核验和视觉核验仍由当前 Codex 执行；程序不伪造这些能力。

## 交接目录

```text
research/
├── START_HERE.md                 # 另一模型先读的说明
├── research.json                 # 章节顺序、实际图片索引、完成状态
├── plan.md                       # 读者、主线、范围、章节问题
├── sources.md                    # 固定版本、公共来源和编号
├── review.md                     # 实际分工、工具、核验与限制
├── evidence/                     # 可随包的必要证据，不默认拷整个仓库
└── chapters/
    └── 01-overview/
        ├── materials.md          # 事实、例子、背景、图义、组织建议
        └── assets/               # 实际 SVG/PNG、HTML 编辑源、生成提示词
```

实际图片必须入包。不存在“在原 Codex 会话里看图”的隐含依赖。
研究/图片未完成时 status=draft，不能导出为完整交接包。
有依据的非核心未知可明确说明后交接，不为了追求所有问题都有答案而编造。
导出只打包登记文件，不带 `.git`、未登记工作文件或本机凭据。私有材料转第三方前仍需用户授权。
完整格式见 [handoff.md](skills/repo-to-research/references/handoff.md)。

## 阶段二：用任意模型写作与出版

调用：`repo-to-write <research-path>`，默认 HTML；`--format pdf` 请求 PDF，`--format all` 同时生成 HTML 和 PDF。输入为素材目录。默认纯白纸面、杏红浅框标题、深杏红左对齐书名；书名后先放整理全书阅读关系的 Mermaid 流程图，再接无框目录，不设封面、副标题或导读。

用户明确另开一次写作任务；研究结束不会自动启动这一步。
向所选模型提供研究包，以及独立的 repo-to-write 技能包：

```text
请按 repo-to-write/SKILL.md，将这份研究素材包写成完整中文图解技术书。
先读 START_HERE.md 和全书计划，再逐章读取素材、来源与实际图片。
你只负责自主组织语言、串联章节、编排现有图片和出版，不重复调研，不依赖 Codex。
图前说明要看什么，图后解释机制、原因与边界，不拼贴研究笔记。
发现核心证据或图片缺口时明确列出，不能自己补成项目事实。
保留正式章节 Markdown、实际图片、来源和编排配置，默认交付离线 HTML；本次不生成 PDF。
```

有文件和终端的执行环境：

```bash
python -m pip install -r skills/repo-to-write/requirements.txt
python skills/repo-to-write/scripts/book.py prepare ./research ./publication
# 模型完成 publication/manuscript/*.md 与 writing-review.md 后：
python skills/repo-to-write/scripts/book.py build ./publication
```

**HTML 不需要 Playwright/Chromium**，运行时不联网、不请求模型服务。
原始 `publication/` 保留全部研究输入、正式正文 `manuscript/`、实际图像、sources.md、book.json 和写作核验记录。
`dist/book.html` 自包含样式和图片；精确 SVG 在窄屏中可局部横向滚动，避免字被无限缩小。

只有用户明确要求 PDF 时：

```bash
python -m pip install -r skills/repo-to-write/requirements-pdf.txt
python -m playwright install chromium
python skills/repo-to-write/scripts/book.py build ./publication --format pdf
```

已有浏览器使用 `--browser` 或 `CHROME_BIN`。PDF 失败时保留 HTML 并返回非零码。

仅聊天、不能执行文件的模型仍可按章交付 Markdown 与插图位置，再由用户运行出版脚本；
它不能声称已经生成或验证 HTML/PDF。详见 [跨平台交接](skills/repo-to-write/references/portable-handoff.md)。

## 实现范围

仅使用宿主 agent 已有的能力。没有 API key 管理、模型路由、向量数据库、后台服务或自动阶段串联。
`research.py` 负责初始化/文件检查/交接导出；`figure.py` 是阶段一的上游导出适配器；
`book.py` 只建立写作目录并出版，默认 `--format html`。
两个独立技能携带一致的 `handoff.py`，无需安装对方；测试保证契约副本一致。

构建检查只检查当前配置中的章节文件、引用、图片与 SVG 约定；完整交付另用 `check --delivery` 检查研究覆盖和复核记录。技术正确性、独立研究、真实工具调用和教学价值不能。
不设页数、字数或图片配额，也不把检查通过说成专家审核。
当前出版器不内置动态交互图、LaTeX/KaTeX 排版或 EPUB；需要精排公式时提供静态图。

## 返修与交付

核心缺口先登记在 `book.json` 的 `core_gaps` 与 `writing-review.md`，继续不受影响章节。用户另行委派研究并提供完整返修包后：

```bash
python skills/repo-to-write/scripts/book.py refresh ./repaired-research ./publication
python skills/repo-to-write/scripts/book.py refresh ./repaired-research ./publication --apply
# 按输出重审受影响正文、题注及来源；关闭已核实的缺口，再重建和查看
python skills/repo-to-write/scripts/book.py build ./publication
python skills/repo-to-write/scripts/book.py check ./publication --delivery
```

refresh 默认只比较；`--apply` 保留 manuscript，替换登记材料、删除被撤回的旧证据，标记受影响章节待复核并移除过期 dist。共享证据变化要求全书重审。不得手工混用新旧素材。交付 coverage 允许拆章、合章和有理由的删章；普通 check/build 仍允许部分稿预览。详情见 [返修流程](skills/repo-to-write/references/portable-handoff.md)。

`HTML 已构建` 与 `视觉验收完成` 分别报告；没有浏览器仍可交付待视觉验收稿，不能标为完整验收。交付检查验证记录齐备，不鉴定记录真实性。

源码分发只读取 `release-files.txt` 中明确列出的文件，拒绝符号链接。新增文件须经审阅后加入清单，不靠递归扫描或敏感名称黑名单。

## 示例和测试

`examples/mini-pipeline/research/` 是三章材料与四张静态 SVG；
`examples/mini-pipeline/publication/` 是据此准备的完整图文源稿和 HTML。
示例是教学测试 fixture，未实际调用 Codex 子代理、diagram-design 或 imagegen，也未委派另一模型写作。

```bash
python -m pip install -r skills/repo-to-write/requirements.txt
python -m unittest discover -s tests -v
python skills/repo-to-write/scripts/book.py build examples/mini-pipeline/publication
```

真实小型案例：`examples/priority-queue/` 固定 boltons 源码，两章调研、真实 diagram-design/imagegen 配图、独立写作与缺口恢复。其验证目录保留注入输入、实际审校发现和恢复哈希记录；不代表不同厂商模型或大型长篇已验证。

验证记录：[docs/VALIDATION.md](docs/VALIDATION.md)。实际 Codex/其他模型验收：[docs/ACCEPTANCE.md](docs/ACCEPTANCE.md)。

## 项目文件

```text
skills/repo-to-research/   # 独立阶段一技能
skills/repo-to-write/       # 独立阶段二技能，任意模型可用
scripts/install.py        # 单个/双技能安装，不覆盖旧安装
scripts/package.py        # 项目与两个独立技能打包
examples/mini-pipeline/   # 素材交接与出版示例
tests/                   # 结构、交接、隔离与出版回归
docs/                    # 设计边界、验收和实际验证
```

项目 MIT；参考来源与上游通知见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。不分发字体文件。

## v2.2 写作方法与迁移

写作技能现名 `repo-to-write`。外层项目目录仍为 `repo-to-book/`，研究技能仍为 `repo-to-research`。先按 Diátaxis 的读者需求决定结构，再用 Humanizer 做保留事实和限定的克制编辑；具体规则与中文教学示例集中在 [writing.md](skills/repo-to-write/references/writing.md)。

旧安装先备份并移出技能发现目录，再安装 `repo-to-write`；不要让旧 `repo-to-book` 与新写作技能并存。安装器检测到旧名或目标已存在时拒绝安装，不静默覆盖，也不自动删除旧版。研究技能单独安装不受旧写作技能影响。旧研究包 schema、book.json 和 manuscript 路径兼容；旧提示中的技能名改用 `$repo-to-write`，路径使用 `skills/repo-to-write/scripts/book.py`，无需重做研究。

`SNAPSHOT.json`、`SHA256SUMS`、`DELIVERY_STATUS.md`、`REPOSITORY_ROOT_README.md` 和既有案例 validation/evidence 是 historical v2.1 导入/验收记录；原始值不改，不作为当前树的校验清单。当前分发文件由 release-files.txt 决定。历史记录中的旧技能名表示当时版本。当前验证与一页编辑试验见 [WRITER_UPDATE.md](docs/WRITER_UPDATE.md)。
