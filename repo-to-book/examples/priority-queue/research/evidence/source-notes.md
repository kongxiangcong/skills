# 源码研究员记录（素材，不是书稿）

执行角色：独立源码调查子 agent `/root/real_research/source`。读取日期 2026-10-27。来源均用 GitHub connector `fetch_file` 读取 `mahmoud/boltons` 固定 commit `d31d821d56c8f7756af9c30a864077f2e5855321`。已保存上游 BSD 源码及 LICENSE；换行统一 LF，末尾空白可能增加一行，无逻辑修改。不是完整 checkout。

## 侦察

- README.md：项目是 pure-Python 工具集；模块允许独立 vendor；无需运行时第三方依赖。这是作者描述，不是性能结论。
- setup.py 返回 GitHub API 404；实际构建入口是 pyproject.toml，flit_core.buildapi，Python >=3.7。未安装项目、未运行全量环境矩阵。
- queueutils.py 31–47：作者定位单线程/协作应用，并提供统一接口的堆与排序两种实现。这不能证明任何具体性能提升。

## 生命周期关键事实（queueutils.py 行号）

| 主张 | 证据 | 支持边界 |
|---|---|---|
| 默认公共别名是排序队列 | L223 `PriorityQueue = SortedPriorityQueue` | 不应把默认队列画成 heap |
| 初始化两个容器及递增计数器 | L108–114 `_pq`, `_entry_map`, `itertools.count()` | `_pq` 包含物理 entry，map 只含有效任务 |
| 默认优先级转换为负浮点 | L104–105 `lambda p: -float(p or 0)` | 大数字先出是默认转换的结果；不是所有自定义 key 的语义 |
| 插入 entry 是可变三元列表 | L132–138 `[priority, count, task]`，先 map 后 backend | map 和 backend 引用同一 entry 对象；并非两份任务记录 |
| 同等有效优先级按本次插入计数稳定排序 | L135–138 与 L199–204/L215–220 | 正常可全序比较的优先级，count 唯一，避免比较 task；更新得到新 count |
| peek 先清理头部墓碑，再读 `_pq[0]` | L147–170 | 不移除有效任务，但可能改变内部物理容器 |
| pop 清理、取 backend 首项，再删 map | L177–185 | 返回 task，不返回 priority/entry |
| len 只计算有效任务 | L187–189 `len(self._entry_map)` | 不代表 `_pq` 的内存或条目数量 |
| heap backend 使用 heappush/heappop | L192–204 | heap 只有根最小，不应画成完全排序数组 |
| sorted backend 使用 BList、insort、pop(0) | L207–220，L76–80 | 成功导入 listutils 时 BList=BarrelList；缺模块退回 list |

## 删除、更新与边界

- 删除（L140–145）先 `entry = self._entry_map.pop(task)`，再 `entry[-1] = _REMOVED`。不会立刻从 backend 搜索或移走；不存在任务自然 KeyError。默认转换值和 count 不变，因此无需恢复排序位置。
- 更新（L132–138）是“转换新 priority → 若已存在则 remove → 新 count → 新 entry → map → backend”。不是原位置改 priority。更新到同优先级也失去旧的同级排队位置。
- `_cull`（L147–156）只反复移走队首 `_REMOVED`，遇到首个有效任务即停止。故 `len(q)==0` 仍可能有未清掉的物理 entry；没有周期性全量 compact。
- `peek()`/`pop()` 无默认值时在空队列抛 IndexError；给出 `None` 等值则返回该值（L158–185）。私有 `_REMOVED` 同时承担内部标记与“没有 default”的标记，不宜作为用户 task/default 使用。
- task 必须可哈希（L127 与 dict 操作），且使用期间应保持稳定的 hash/equality。最后一点是由字典要求推得的使用约束，未测试恶意对象。
- conversion 在 remove 之前（L132），因此转换异常会保留旧 task。实际探针验证 bad 字符串导致 ValueError 后旧 task 仍存在。
- 没有事务回滚：map 在 `_push_entry` 之前改变，用户自定义 priority_key 返回不可比较值等情况下 backend 插入异常可能留下不一致状态。这是源码顺序推断，未注入测试，不建议作为本章核心案例。
- 默认浮点转换会损失某些大整数精度；实际观察 9007199254740993 变成 9007199254740992.0（再取负）。NaN 等非全序值未有输入校验，不承诺稳定语义；本次未测试 NaN。
- `priority_key=lambda p:p` 令较小数先出。已实际验证 low(1) 先于 high(2)，不能写成“key 输出越大越优先”。
- BasePriorityQueue 的抽象方法只是 pass（L116–122），不是 ABC 强制约束；本素材面向两个具体实现。

## 可复核走读（两种 backend 均实际运行）

完整输出见 source-runtime.txt。先 add A(1), B(3), C(3)：有效数/物理数 3/3，peek=B，pop=B 后 2/2。此时更新 A(3)：旧 A entry 被标记，新 A count=3；有效数/物理数 2/3，C 的 count=2 早于新 A。remove C 后 1/3；peek 会清掉 C 墓碑并返回 A，计数 1/2；pop A 后 0/1；pop(None) 清掉最后旧 A 墓碑后返回 None，0/0。

图义建议：一张图分清“有效任务 map”与“物理排序容器”，两处共用 entry；删除箭头是原 entry 的 task 槽被标记，更新另生 entry。若画有序具体列表，用 SortedPriorityQueue 明确标注；不要借排序列表位置解释 heap 的全数组顺序。

## 复杂度与性能的诚实边界

- 用 N 表示物理 entry 数，L 表示有效任务数。remove 是平均 O(1) 字典删除加槽替换（假定常规 hash/equality），不是 O(log L) 后端删除。
- 对 HeapPriorityQueue，正常 add 是 O(log N) 后端操作，加字典操作；pop/peek 可能先清 c 个墓碑，单次不应只标 O(log L)/O(1)。未测耗时，未做吞吐基准。
- SortedPriorityQueue 的 BList 是分桶 BarrelList（listutils.py L60 起），并不是内建 list，也不是外部 blist/B-tree。其 insert、pop、索引转换、len 都有自己的实现；因此不能把内建 list + bisect 的复杂度直接标成这里的严格上界。正文只需说明权衡，精确 BList 渐近分析不在这次范围。
- 持续更新且不 peek/pop 可增加物理墓碑；remove 会替换 task 引用，但仍保留 priority/count 槽和 entry 容器。不是“所有旧 task 引用永久保留”。

## 实际命令及限制

1. GitHub connector fetch_file：queueutils.py、tests/test_queueutils.py、LICENSE、README.md、setup.py（404）、listutils.py、pyproject.toml、typeutils.py，均指定固定 commit。
2. 在 evidence/upstream 执行 `PYTHONPATH=. python -m pytest -q tests/test_queueutils.py`：失败，`No module named pytest`。
3. 在 research 目录执行 `python evidence/source_probe.py > evidence/source-runtime.txt`：退出 0。环境 CPython 3.12.14；脚本先将 evidence/upstream 加入 sys.path，通过 runpy 直接执行上游两个 test 函数，均通过；随后运行上述探针。使用保留的 listutils/typeutils，运行显示默认后端确为 BarrelList。
4. 本次不是 pytest suite、不是 doctest、不是安装验证、不是线程安全测试、不是性能测量。没有改写被研究源码，也未运行网络代码或项目构建钩子。
