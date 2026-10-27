# 第一章素材：系统边界与计划对象

## 核心问题与目标

为何不按函数顺序讲，而要跟着一个表达式的形态理解？读者应能解释 Plan 的接口作用。
前置知识仅为函数、参数和数据类。下一章展开具体值，本章不重复逐步算例。

## 源码事实

S01：run(text) 返回 execute(compile_expression(text))；内层成功返回才会调用外层。
证据 pipeline.py:32–33。入口 36–38 行从命令行组装表达式并打印结果。
S02：Plan 是 frozen dataclass，字段为 op:str、lhs:int、rhs:int，见 6–10 行。
字段名与 compile/execute 的接口有关；源码没有线程、队列、设备或异步任务。

## 原始证据摘录

```python
@dataclass(frozen=True)
class Plan:
    op: str
    lhs: int
    rhs: int

def run(text: str) -> int:
    return execute(compile_expression(text))
```

完整快照 evidence/pipeline.py 已随包。不能从类型标注推出运行时自动校验所有字段。

## 图像

fig-01-01 是输入文本→编译→Plan→执行→整数结果的精确值流图。
从左到右读；箭头表示传值，不承诺网络通信、复制次数或吞吐。
图题建议：文本经过计划对象，成为一个整数结果。细节图留到第二章。

## 外部资料与推断

此教学例子不需要外部事实。接口分离有助于分别测试是基于代码结构的解释，不是性能证明。
可指出直接解析并计算也能达到同一功能，不能宣称这份分层设计更快。

## 组织与未知

先给系统边界，解释 Plan 为何值得关注，再引出具体值走读。没有性能测试与硬件结论。
