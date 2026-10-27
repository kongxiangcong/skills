# 可移植研究目录 v1

这是两个技能之间唯一的数据交接，不交换聊天状态，不调用对方的 agent。

```text
research/
├── START_HERE.md                 # 给任意写作者的入口；export 会重建
├── research.json                 # 章节顺序、文件索引和实际完成状态
├── plan.md                       # 读者、主题、主线、范围、章节问题
├── sources.md                    # 公共来源与固定版本，稳定来源编号
├── review.md                     # 实际分工、检查发现、工具与未知
├── evidence/                     # 允许携带的必要源码切片/资料/摘要
└── chapters/
    └── 01-overview/
        ├── materials.md          # 本章素材，非书稿
        └── assets/
            ├── fig-01-01.html    # diagram-design 可编辑图稿
            ├── fig-01-01.svg     # 实际出版用的静态图
            ├── fig-01-02.png     # imagegen 的实际位图
            └── fig-01-02.prompt.md
```

所有索引路径相对目录根，统一 `/`。图片要在包里，不能只给本机绝对路径、临时 URL 或会话 id。
需要离线解释的证据内容写进材料或 evidence/，不是“请作者再打开这些网站读”。
原始书籍/论文能否携带取决于许可，不默认复制全文；有依据的自写摘要与定位通常已经足够。

## 索引示例

```json
{
  "schema_version": 1,
  "title": "读懂项目 X",
  "subtitle": "从一条执行路径理解系统",
  "language": "zh-CN",
  "status": "ready",
  "plan": "plan.md",
  "sources": "sources.md",
  "review": "review.md",
  "evidence_files": ["evidence/entrypoint.py", "evidence/paper-notes.md"],
  "chapters": [{
    "id": "01-overview",
    "title": "系统为什么分成这几层",
    "materials": "chapters/01-overview/materials.md",
    "status": "ready",
    "assets": [{
      "id": "fig-01-01",
      "file": "chapters/01-overview/assets/fig-01-01.svg",
      "editable": "chapters/01-overview/assets/fig-01-01.html",
      "method": "diagram-design",
      "status": "ready",
      "caption": "图 1-1 · 开源组件与系统边界",
      "evidence": ["s01", "s02"]
    }, {
      "id": "fig-01-02",
      "file": "chapters/01-overview/assets/fig-01-02.png",
      "prompt": "chapters/01-overview/assets/fig-01-02.prompt.md",
      "method": "imagegen",
      "status": "ready",
      "caption": "图 1-2 · 请求与资源关系的概念示意，不代表实际硬件布局",
      "evidence": ["s02"]
    }]
  }]
}
```

来源编号在 sources.md 用 `## S01 · 标题 {#s01}` 登记。
图片详细目的、读法、简化、局限写在 materials.md，避免在 JSON 再存一份长解释。
无图章节可以 assets=[]，但必须确认不是漏掉该画的核心机制。不按图数、字数验收。

`method` 只能记录真实来源：diagram-design、imagegen、provided、static-svg。
imagegen 需要真实位图和提示词；diagram-design 需要实际静态图和可编辑源。
尚未生成的图片用 pending、章和总包用 draft。未经语义/视觉核验不能只改状态交差。
明确的非核心未知可以写清后 ready；关键事实没有依据时不能。

## 工具

```bash
python <skill-dir>/scripts/research.py check <research-dir> --draft
python <skill-dir>/scripts/research.py check <research-dir>
python <skill-dir>/scripts/research.py export <research-dir> --out research-handoff.zip
```

检查器只验证结构、占位标记、文件、来源锚点和静态 SVG 基本约定。
不证明事实真伪、子 agent 是否确实调用、imagegen 是否确实执行，也不证明图片视觉正确。
这些必须由实际执行记录和审阅承担，不增加假的自动证书。

导出只包含 research.json 明确登记的文件及自动生成的 START_HERE.md。
不扫描打包整个工作区，因此 `.git`、其他项目、预览和未登记文件不会被默认带走。
所有必要证据必须加入 evidence_files；记录的图片、提示词与编辑源会自动跟随。

导出后停止，由用户把素材包与 repo-to-book 技能交给所选写作模型。
不得因该模型不同而要求重做研究；不得自行发送给第三方。
