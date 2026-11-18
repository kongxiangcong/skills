# repo-to-write

独立的阶段二写作与出版技能，不需要 Codex、研究技能或出图工具。
直接在研究阶段产出的同一个 `<专题目录>` 内工作，**不另建 `-publication` 兄弟目录，也不拆章、合章或重排**。

读取专题目录下的 `START_HERE.md`、`outline.md` 与各章 `chapters/<id>/materials.md`，按 [references/writing-style.md](references/writing-style.md) 的文风约定（不用引导式问题标题、保留必要英文术语、去 AI 腔写因果），逐章写入 `chapters/<id>/manuscript.md`。

```bash
python -m pip install -r requirements.txt
python scripts/book.py prepare <专题目录>
# 逐章完成 chapters/<id>/manuscript.md 并更新 writing-review.md
python scripts/book.py check <专题目录>
python scripts/book.py check <专题目录> --delivery
python scripts/book.py build <专题目录>
```

默认生成离线 `dist/book.html`。仅当用户明确要求 PDF 时：

```bash
python -m pip install -r requirements-pdf.txt
python -m playwright install chromium
python scripts/book.py build <专题目录> --format pdf
```
