# 外部一手资料摘要（独立外部研究员）

检索日：2026-10-27。目标源码基线：mahmoud/boltons `d31d821d56c8f7756af9c30a864077f2e5855321`。本文件仅提供背景与反证，未读取或执行该版本源码，不能用以下资料证明 boltons 的具体实现。所有中文内容为自写摘要，没有复制原文段落或完整配方。

## E01 · Python heapq 的优先队列配方

- 作者/机构：Python 文档贡献者 / Python Software Foundation。
- URL：https://docs.python.org/3.13/library/heapq.html#priority-queue-implementation-notes
- 读取页面标示 Python 3.13.18；页面更新 2026-10-26。定位：Priority Queue Implementation Notes，网页抽取行 87–135；Theory 行 138–152。
- 许可：PSF License Version 2；文档示例另有 Zero Clause BSD License。本包只保留以下摘要。
- 摘要：小根堆根元素最小，堆数组整体不要求有序。条目采用优先级、唯一递增序号、任务三字段时，序号解决同优先级先入先出，并避免比较任务本身。字典可将任务映射到条目。任意直接删除条目或原地修改优先级可能破坏堆；配方改为标记旧条目已删除，更新时另外插入新条目，出队跳过删除标记。单次底层堆弹出沿树调整，复杂度随堆元素数对数增长。
- 对章节的用途：第 1 章解释为何序号不是装饰；第 2 章解释逻辑成员与物理存储分离。不要把单次 heappop 的复杂度直接等同于可能跳过多个墓碑的公开 pop。
- 适用限制：配方返回最低数值优先级；boltons 是否取负转换、默认值、异常、清理位置，须以锁定源码核对。此资料不能证明历史传承或作者设计动机。

## E02 · float 转换不是有限数验证

- 作者/机构：Python 文档贡献者 / Python Software Foundation。
- URL：https://docs.python.org/3/library/functions.html#float （读取时重定向至 https://docs.python.org/3/builtins/functions.html）
- 读取页面标示 Python 3.15.2；定位 float，网页抽取行 393–435；文档版本为检索返回值，不代表本地运行环境。
- 摘要：float 可由数字或符合语法的字符串构造，接受 NaN 和正负无穷；一般对象可委托 __float__，再退回 __index__。转换受浮点精度及范围限制，超范围数字转换可抛 OverflowError。
- 对章节的用途：如果源码将优先级统一转换成 float，不能据此声称它验证了有限性、保留所有整数差异，或只接受 int/float。
- 限制：没有在本任务中运行数值边界实验；哪些输入经过该函数、失败发生在队列修改前还是之后，必须由源码研究员确认。

## E03 · NaN 与词典序比较的边界

- 作者/机构：Python 文档贡献者 / Python Software Foundation。
- URL：https://docs.python.org/3/reference/expressions.html#value-comparisons
- 读取页面标示 Python 3.15.2；定位 Value comparisons，网页抽取行 967–981。
- 摘要：数值与 NaN 的有序比较为假，NaN 也不等于自身。列表和元组按对应元素词典序比较，首个不等元素决定顺序；容器可对同一对象采用身份相等捷径。因此，“每个条目都有递增计数器”并不足以为任意 NaN 优先级建立正常的数值顺序。
- 对章节的用途：把普通可排序优先级作为稳定顺序说明的前提；不要对 NaN 宣称有意义的最高优先级行为。
- 限制：这是语言语义背景与条件推断，不是 boltons 承诺或已观察到的输出。

## 实际检索与缺口

实际调用 web open 读取上述三份官方资料，并对 heapq 的 Implementation、float 的 NaN、表达式的 NaN 做定位检索；另读取固定 3.13 路径，避免只引用滚动 /3 页面。未进行第三方网页搜索、论文搜索或任何性能实验；该窄主题一手文档已经足够解释背景。

未核实 boltons 的并发承诺、异常原子性、自定义 priority 函数契约；均应回到锁定源码。未发现可据以断言 boltons 来源于 Python 配方的作者声明。当前文档版本与目标仓库提交不是同一个版本轴，交接时应保留此区别。
