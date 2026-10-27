# 研究计划：读懂 boltons 优先队列

读者：会 Python 列表、字典与函数的工程师。目标：追踪一个任务从 add 到 pop，解释稳定排序、更新、惰性删除和实际适用边界。语言中文；交付研究材料，不含书稿。

基线：mahmoud/boltons d31d821d56c8f7756af9c30a864077f2e5855321（2026-10-25 提交）；2026-10-27 经 GitHub connector 读取。证据是只读文件快照，不是完整 checkout；未修改源码逻辑。

1. 01-lifecycle：输入如何变成可排序 entry，再由 peek/pop 访问？前置：字典/列表。重点是默认优先级取负浮点、同级计数器、两种后端、默认别名。配图：成功路径流程图与概念性调度插画。
2. 02-removal：删除为什么不等于物理移除，更新怎样改变排队位置？依赖第 1 章 entry 模型。重点是同一 entry 的引用、墓碑、_cull、逻辑数与物理数、异常与数值边界。配图：单个 entry 状态图。

不研究：BarrelList 全实现与严格复杂度证明、并发队列、性能基准、调度公平性、全项目安装矩阵。两章完成后停止，不触发写作。

侦察修正：PriorityQueue 是 SortedPriorityQueue 的别名，不能以常见 heapq 配方推定默认后端；材料明确比较两种实现。

绘图选择：上游 diagram-design；图 1-1 flowchart、图 2-1 ordinary state machine，doc-inline 960×600。该队列没有等待/重试/任务执行状态，故不套用 lifecycle phase map。采用本项目已有中文浅色系统字体皮肤，主要文字 22px、次要 18px（本地书籍皮肤明确覆盖上游小字号）。省略错误分支的部分由表格解释。图 1-2 为父任务实际 imagegen 生成的概念隐喻，不编码源码关系。
