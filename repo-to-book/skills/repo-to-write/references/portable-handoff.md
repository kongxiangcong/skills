# 不依赖 Codex 的写作交接

## 必需输入

一个普通研究目录/ZIP，包括 research.json、START_HERE.md、plan.md、sources.md、review.md、
逐章 materials.md、实际图片，以及必要证据文件。输入不需要原仓库完整 checkout，
更不需要 Codex 登录、原聊天、子代理 thread id 或生成图片的临时目录。

research.json 的 schema_version 为 1；status 和全部章节、图片应 ready。
文件检查不代表事实正确，先读 review.md 了解实际核验与限制。
拒绝把只有提纲/链接/图片提示词的目录认作“材料全部准备好了”。

## 有文件与终端的任意 agent

将独立写作技能放到任意路径，按 SKILL.md 执行；用自带 Python 出版脚本。
`prepare` 不读取另一技能目录，不联网、不请求模型 API，不安装或调用 Codex。
只复制 research.json 登记的素材，新建 manuscript/ 与 book.json，研究原目录不变。

```text
publication/
├── research.json, plan.md, sources.md, review.md
├── chapters/*/materials.md       # 输入材料原样保留
├── chapters/*/assets/*           # 实际图片及编辑源原样保留
├── evidence/*                   # 输入证据原样保留
├── book.json                    # 出版标题、章节顺序、来源附录
├── manuscript/*.md              # 第二阶段的正式书稿
├── writing-review.md             # 写作与实际渲染检查
└── dist/book.html               # 默认产物；book.pdf 仅按需
```

这就是完整原始目录，不能只交付不可编辑的 HTML/PDF。
`book.json` 可调章节叙事顺序，但不要改写 research.json 来隐藏输入证据或改变研究范围。

## 仅聊天平台

不要求对方支持 `$skill` 语法。用户可以把 SKILL.md 当作工作说明，并上传材料包；
每章按需提供材料、引用来源及图片附件。模型输出可保存的完整章节 Markdown、图片插入位置与题注，
由用户在任意本地 Python 环境运行出版脚本。没有执行能力与图像读取能力时要分别说明。

单次上下文装不下整本书时，先读计划，逐章输入；用 manuscript/ 和 writing-review.md 接续。
不要把材料重新总结成更短摘要再反复转述，容易丢失限定条件和证据。
允许任何模型写作，并不意味着任何纯聊天界面都能执行文件生成或排版。

## 缺口与返修恢复

1. 在 `writing-review.md` 定位缺口、受影响的正文/题注/跨章结论；在 `book.json`
   的 `core_gaps` 登记核心缺口，例如
   `{"id":"G1","chapters":["manuscript/02-trace.md"],"status":"open","resolution":""}`。
   非核心未知可明示；核心缺证章保持待复核，其他无依赖章节继续。
2. 用户另行委派研究，交回**完整的新研究包**，不是覆盖原稿的散文件。
   新包保留稳定章节/来源 id，记录修订原因及核验依据；不要自动启动研究。
3. 先比较，再应用：

   ```bash
   python <skill-dir>/scripts/book.py refresh <补齐后的完整研究包> <已有写作目录>
   python <skill-dir>/scripts/book.py refresh <补齐后的完整研究包> <已有写作目录> --apply
   ```

   第一条只列出变更文件和需重审的成书章节。第二条保留 `manuscript/` 与用户文件，
   在临时副本完成素材替换后切换目录；复制失败保留原目录。
   若目录切换及回滚同时失败，错误会给出保留完整原稿的 `previous` 绝对路径；
   不删除该备份，解决占用/权限问题后将它恢复为原写作目录，再继续。
   只替换登记素材，删除不再登记的旧素材，拒绝与未登记文件冲突或原材料被私自修改。
   不手工修改 `research_files` 哈希来通过检查。
4. 章节局部材料变化使对应成书章节的 `chapter_reviews` 变为 `pending`；公共来源、
   证据、目录或图片元数据变化保守地使全部成书章节重审。
   检查图义、题注、正文主张及引用该结论的其他章节；程序无法判断语义依赖，
   主编应将额外受影响章节设为 pending。所有返修都要求重新统稿和视觉验收。
5. 阅读新旧差异后修订已有正文，而不是重新 `prepare` 或丢弃书稿。
   按需调整 `coverage`：每个研究章节映射到一个或多个成书章节，合并、拆分、
   删除都写 `reason`；`research_scope` 保留初始及历次新增章节 id，不能随着返修缩减。
   研究包移除的章节仍保留 coverage 项并说明理由，即使正文仍有对应章节也须交代
   证据移除后的处理方式；不能删除旧 coverage 项来隐藏范围减少。
   核心缺口只有在补充证据已核验且正文已修正后才能标 `resolved`，填写 `resolution`。
6. 受影响章节复核后将相应 `chapter_reviews` 标 `approved`，在 writing-review.md
   写实际审查结果，移除 pending 标记并保留 `<!-- r2b:reviewed -->`。
   重建后实际查看 HTML；通过才设置 `visual_review: "passed"`，最后执行
   `check <已有写作目录> --delivery`。返修应用会移除旧 `dist/`，避免旧成品冒充新证据版本。

`prepare` 始终只接受新目录。`refresh` 不调用模型、不联网、不改动输入研究包，
也不会自动宣布缺口解决或替你批准写作复核。两条命令都不能证明材料本身准确。
对于旧版本准备、尚无 `research_files` 的目录，先保留完整备份；用 `prepare` 在新目录
接收当时的原始研究包，再复制旧 `manuscript/` 和编排配置，保留新生成的快照字段。
核对覆盖关系、重审后再使用 refresh；不要用未经确认的新材料给旧书稿补做“已验证”快照。
