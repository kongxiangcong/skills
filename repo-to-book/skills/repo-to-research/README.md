# repo-to-research

这是独立的阶段一技能。主 agent 规划，默认用子 agent 做源码/外部研究及关键核验，
按用途调用 diagram-design 与 Codex 内置 imagegen 完成实际图像。交付素材后停止，不写书。

将本目录放入 `~/.agents/skills/repo-to-research`，新会话使用 `$repo-to-research`。
工具与出图能力由当前 Codex 提供，缺失时不能伪装调用；本包不会安装模型或收集 API key。
主指引见 SKILL.md。素材初始化、检查和打包只使用 Python 标准库：

```bash
python scripts/research.py init ./research --title "读懂某项目"
python scripts/research.py check ./research
python scripts/research.py export ./research --out ./research-handoff.zip
```

完整格式见 references/handoff.md；图片生产见 references/visual-production.md。
没有最终正文、HTML 或 PDF 生产命令。之后由用户另行调用独立 repo-to-book 技能。
