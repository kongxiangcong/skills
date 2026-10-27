# boltons 优先队列：真实两阶段小型验收

范围仅为两个章节：一次任务从加入到弹出，以及删除/更新/边界。不是整个 boltons 教材。

- `research/`：固定源码、两章研究材料、两张 diagram-design SVG/HTML、一张 imagegen 概念图、来源、原始运行输出与独立核验记录。
- `publication/`：独立写作者的正式正文、现成图片、编排与复核记录，`dist/book.html` 可离线阅读。
- `validation/`：故意缺证时的原稿、核心缺口记录、补包前后哈希，以及错误主张独立核验结果。

```bash
python skills/repo-to-research/scripts/research.py check examples/priority-queue/research
python skills/repo-to-write/scripts/book.py check examples/priority-queue/publication --delivery
python skills/repo-to-write/scripts/book.py build examples/priority-queue/publication
```

以上在项目根目录执行。没有 PDF 默认依赖；图片与必要源码按许可随包。

实际经历：独立研究 → 上游图解导出与内置 imagegen → 独立核验 → 注入核心证据缺口 → 独立写作者登记缺口且继续 → 完整补包 refresh 保留原稿 → 重审与出版。
实际命令、失败及局限见 [验证记录](../../docs/VALIDATION.md)。两个阶段使用分离上下文，不代表不同厂商模型已实测；范围小，不代表长篇稳定性。
