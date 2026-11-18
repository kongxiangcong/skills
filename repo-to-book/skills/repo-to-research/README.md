# repo-to-research

独立的阶段一研究技能。围绕同一专题目录与唯一一份 `outline.md` 工作，分为两个明确阶段：

1. **讨论与确认大纲**：新建或更新 `outline.md`（全书约定 + 逐章大纲），更新后停下等待用户确认。
2. **按确认版备料**：用户说「大纲可以了，按这版调研」后，默认委派源码与外部调研子 agent 逐章收集素材写入 `chapters/<id>/materials.md`，调用 `diagram-design` 与内置 `imagegen` 将配图存入 `chapters/<id>/assets/`，独立核验后停止，不写正式正文。

将本目录放入 `~/.agents/skills/repo-to-research`，新会话使用 `$repo-to-research`。

```bash
python scripts/research.py init ./topic-dir --title "项目技术解析" --repo "<仓库路径或URL>"
python scripts/research.py check ./topic-dir --draft
python scripts/research.py check ./topic-dir
```

完整目录契约见 `references/handoff.md`；工作流见 `references/research-workflow.md`；图片生产见 `references/visual-production.md`。之后由用户在所选模型中调用 `repo-to-write` 技能在同一专题目录内写作。
