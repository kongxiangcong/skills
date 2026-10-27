# 资料与源码依据

本示例的唯一实现来源是随包教学源码 `evidence/pipeline.py`，不是外部开源项目的评测。源码快照 SHA-256：

`a1a2faa8e5371ceeb7c7c6ba080421507a335d54d98a5fb6a5e51c7ec3d2283e`

本书只解释这个文件的行为。没有以外网资料替代源码事实，也没有虚构外部引用。

## S01 · 正常路径与入口 {#s01}

类型：源码事实。定位：`pipeline.py`，`run()`，第 32–33 行；命令行入口，第 36–38 行。

`run(text)` 返回 `execute(compile_expression(text))`。成功时先取得计划再执行；这里没有循环、任务队列或异步启动。

## S02 · 数据结构与执行分支 {#s02}

类型：源码事实。定位：`pipeline.py`，`Plan`，第 6–10 行；`execute()`，第 24–29 行。

Plan 具有 op/lhs/rhs 字段；execute 分别处理 ADD 和 MUL，其他操作抛出 ValueError。数据类没有自行检查操作名的逻辑。

## S03 · 编译与拒绝条件 {#s03}

类型：源码事实。定位：`pipeline.py`，`compile_expression()`，第 13–21 行。

先按空格拆分，检查恰有三个字段；操作名大写化；拒绝 ADD/MUL 之外的操作；把参数转换成整数；返回 Plan。非法整数由 int 转换产生异常。

## S04 · 可复核的运行例子 {#s04}

类型：运行观察。本次环境为 linux、Python 3.13.5。命令行运行记录随包保存于 `evidence/run-results.json`；工程测试另外核对正常与异常路径。

输入 ADD 2 3 对应 5，MUL 2 3 对应 6；DIV 2 3 与非法整数输入应抛出 ValueError。该记录仅限教学代码，不是原始推理引擎执行或性能测试。
