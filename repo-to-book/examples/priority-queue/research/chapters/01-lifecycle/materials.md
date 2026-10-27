# 第一章研究素材：从输入到队首访问

## 学习目标与范围

能解释 `add('B', 3)` 如何变成 `[-3.0, count, 'B']`，为什么 B 能先于低优先级任务返回，以及同级任务如何稳定排序。解释公开 API 和后端实现的差别。本文是素材表与组织纲要，不是书稿。

## 关键事实与离线证据

| 事实 | 必要源码内容 | 证据位置 |
|---|---|---|
| 默认高数值先出 | `_default_priority_key = staticmethod(lambda p: -float(p or 0))` | S01 queueutils.py L104–105 |
| 初始化三部分状态 | `_pq = self._backend_type()`、`_entry_map = {}`、`_counter = itertools.count()` | S01 L108–114 |
| 一条可变 entry 被两处引用 | `entry = [priority, count, task]`; `_entry_map[task] = entry`; `_push_entry(self._pq, entry)` | S01 L135–138 |
| 默认公共类型是排序队列 | `PriorityQueue = SortedPriorityQueue` | S01 L223 |
| 两种后端 | Heap: heappush/heappop；Sorted: BList + insort/pop(0) | S01 L192–220 |
| peek/pop 返回任务 | peek 清理后读 `_pq[0]`；pop 清理后弹出条目、`del _entry_map[task]` | S01 L158–185 |

PriorityQueue 正常安装时的 BList 指 BarrelList（S01 listutils.py），不是内建 list；导入失败才回退 list。heap 数组并不整体有序；本章具体有序列表选用 SortedPriorityQueue。

同等有效优先级先比较唯一递增 count，因此通常不需要比较任务对象。前提是优先级具有正常可排序语义；NaN 边界放第二章。task 要可哈希，成员身份取决于字典的 hash/equality，而非只取对象身份。默认 None/其他假值经 `p or 0` 归零；自定义 `priority_key=lambda p:p` 会让较小输出先出，并非保持“越大越优先”。

## 可复核输入走读

S02 实际两后端都运行成功；以下物理内容只显示 SortedPriorityQueue：

| 调用 | 有效数 / 物理数 | 物理条目（优先级, count, task） | 返回 |
|---|---:|---|---|
| add A(1) | 1 / 1 | [-1,0,A] | None |
| add B(3) | 2 / 2 | [-3,1,B],[-1,0,A] | None |
| add C(3) | 3 / 3 | [-3,1,B],[-3,2,C],[-1,0,A] | None |
| peek() | 3 / 3 | 不变 | B |
| pop() | 2 / 2 | [-3,2,C],[-1,0,A] | B |

表中为可读性省略 `.0`；真实输出在 evidence/source-runtime.txt。peek 的“不变”仅指本例没有队首墓碑；一般情况下它可以清理墓碑。

## 外部背景与取舍

S03 解释用 count 打破平局与避免比较任务的通用配方。boltons 的负号转换和 SortedPriorityQueue 别名只能由 S01 证明。相同 API 便于切换后端；没有基准数据，不能宣布某后端在真实业务更快。

## 配图

- fig-01-01.svg：成功路径流程图，从上向下看 add 的三步，再看后续 peek/pop 两个选择。箭头表示操作流程，不表示 add 会自动调用 peek/pop；标题/图例已明确。删旧任务见第二章。省略异常、内部容器布局和具体 heap 重排，不代表事务保证。依据 S01 L124–185。
- fig-01-02.png：调度员先挑醒目任务卡片的概念隐喻，由父任务实际调用内置 imagegen 生成、复制真实位图，并保留实际提示词。它不编码精确顺序、数据结构、线程、容量或任务数量，不能从图推导任何 API 语义；只用于引入“优先选择”。

## 建议组织与未知

先以 A/B/C 结果引出问题，再讲 entry/count，接着分清 API 与后端，最后引出“删除是否立刻消失”。不讨论 BarrelList 全结构；不声称已验证线程安全、真实吞吐或任意自定义 priority_key。
