# 公共来源

## S01 · boltons 固定源码与许可证 {#s01}

作者 Mahmoud Hashemi 及贡献者；仓库 https://github.com/mahmoud/boltons ，完整版本 `d31d821d56c8f7756af9c30a864077f2e5855321`，2026-10-27 读取。永久链接：https://github.com/mahmoud/boltons/blob/d31d821d56c8f7756af9c30a864077f2e5855321/boltons/queueutils.py 。位置：L104–189 基类、L192–223 后端/别名。BSD-3-Clause 许可及版权见 evidence/upstream/LICENSE，源码头保留原声明。文件列表、Git blob SHA 和 URL 在 evidence/upstream-provenance.json；离线源码、README、构建入口、两项测试一并提供。研究结论和定位详见 evidence/source-notes.md。

## S02 · 实际运行观察 {#s02}

本任务源码研究员，2026-10-27，CPython 3.12.14。evidence/source_probe.py / source-runtime.txt 保存脚本与输出。直接运行两个上游测试函数、两种后端的成功与边界走读；未运行 pytest（未安装）、完整套件或性能测试。观察只支持列出的输入与环境，不代替所有输入证明。

## S03 · Python heapq 优先队列说明 {#s03}

Python 文档贡献者 / PSF，Python 3.13 文档，2026-10-27 读取。https://docs.python.org/3.13/library/heapq.html#priority-queue-implementation-notes 。定位 Priority Queue Implementation Notes / Theory。自写摘要见 evidence/external-notes.md E01；PSF 文档许可，示例另适用 Zero Clause BSD。说明计数器与惰性删除背景，不证明 boltons 默认后端或历史来源。

## S04 · Python float 与比较语义 {#s04}

Python 文档贡献者 / PSF，2026-10-27 读取滚动 /3 文档。https://docs.python.org/3/library/functions.html#float 与 https://docs.python.org/3/reference/expressions.html#value-comparisons 。定位 float / Value comparisons；自写摘要见 evidence/external-notes.md E02/E03。文档读取版本与运行环境不同，不将滚动文档版本当成运行版本。

## S05 · diagram-design 实际制作工具 {#s05}

cathrynlavery/diagram-design，MIT，固定提交 `97d795138448f6a739a0cebc3d9beb37a42077f1`。https://github.com/cathrynlavery/diagram-design/tree/97d795138448f6a739a0cebc3d9beb37a42077f1/skills/diagram-design 。GitHub connector 实际读取 SKILL.md、相关类型/语义/导出规范、self_check.py 与 export_svg.py；后两者实际经适配器调用。这是制作方式，不是队列事实证据；图的依据为 S01/S02。
