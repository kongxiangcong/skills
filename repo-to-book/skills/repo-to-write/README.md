# repo-to-write

这是独立的阶段二写作与出版技能，不需要 Codex、研究技能或出图工具。
在任何能读文件的模型环境中读取 SKILL.md，再读研究包的 START_HERE.md 即可。
Codex 安装时可放进 `~/.agents/skills/repo-to-write`，但不是使用前提。

```bash
python -m pip install -r requirements.txt
python scripts/book.py prepare <research-dir> <新的book-dir>
# 根据材料完成 manuscript/ 内正式书稿
python scripts/book.py build <book-dir>
```

默认只生成离线 HTML，保留完整图文原始目录。PDF 仅用户要求时：

```bash
python -m pip install -r requirements-pdf.txt
python -m playwright install chromium
python scripts/book.py build <book-dir> --format pdf
```

仅聊天的模型可交付逐章 Markdown 与插图位置，再由用户运行上述命令。
不得自动返回研究阶段，不能把材料缺口补成未经证实的项目事实。

返修保留原稿：`python scripts/book.py refresh <完整补包> <book-dir>` 先比较，再加 `--apply` 接收并失效相关复核。完成统稿与实际视觉检查后执行 `python scripts/book.py check <book-dir> --delivery`；普通 check/build 允许部分稿预览。详见 references/portable-handoff.md 与 references/publishing.md。
