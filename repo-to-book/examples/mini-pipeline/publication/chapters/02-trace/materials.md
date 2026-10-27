# 第二章素材：用一个输入走完执行

## 核心问题与前置

跟踪 ADD 2 3；承接第一章的数据路径，下一章解释失败。

## 证据与中间值

S03：compile_expression 第 13–21 行先 text.split()，检查三个字段，
把操作名 upper()，只接受 ADD/MUL，然后 int 转换两个参数，返回 Plan。

```python
parts = text.split()
if len(parts) != 3:
    raise ValueError("expected: OP INTEGER INTEGER")
op = parts[0].upper()
if op not in {"ADD", "MUL"}:
    raise ValueError("unsupported operation: " + op)
lhs, rhs = int(parts[1]), int(parts[2])
return Plan(op, lhs, rhs)
```

具体值：输入字符串 ADD 2 3 → ['ADD','2','3'] → Plan('ADD',2,3) → 整数 5。
S02 的 execute 在 ADD 分支相加；MUL 相乘。上述中间值由代码走读确定，
命令行输出 5 与 6 的实际运行见 S04 和 evidence/run-results.json。
add 02 3 也得到 5；其中 ADD 大写化、02 转整数是规范化行为。

## 图像

fig-02-01 用三个观察点展示字符串、Plan 字段和整数结果。
列宽不表示耗时；不是三个线程；不得据此推断延迟或吞吐。

## 复现方式

在书籍原始目录运行 python evidence/pipeline.py ADD 2 3 与 MUL 2 3。
源文件随包，作者不需重新找原工程。命令行记录不是推理引擎测试。

## 组织与边界

先让读者看图猜中间值，再解释转换，最后用非法整数的问题引向下一章。
没有额外外部事实；不把手工走读中间状态写成已采集的调试 trace。
