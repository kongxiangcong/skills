# 第三章素材：失败路径与公开接口

## 核心问题

正常路径的校验能否让执行器的拒绝分支变成多余？要区分 run 与直接 execute 两条入口。

## 证据

S03：数量不是三个字段先拒绝；DIV 在整数转换之前被拒绝；ADD two 3 在 int 转换时拒绝。
S01：compile_expression 抛异常则 execute 未被调用，源码没有 catch/retry/rollback。
S02：数据类没有 __post_init__ 或操作枚举校验；直接构造 Plan('DIV',2,3) 能完成。
execute 第 24–29 行分别处理 ADD/MUL，最后抛 ValueError。

```python
def execute(plan: Plan) -> int:
    if plan.op == "ADD":
        return plan.lhs + plan.rhs
    if plan.op == "MUL":
        return plan.lhs * plan.rhs
    raise ValueError("unsupported plan: " + plan.op)
```

命令行 DIV 2 3 的实际异常在 S04 的随包记录；直接 Plan 路径由代码和工程单元测试核对。
不能将 frozen 理解为构造时的字段值检查。

## 两张图

fig-03-01 对照成功与在 compile 阶段失败的两行，未到达的格子画虚线。
虚线表示本次未执行，不表示异步、延迟或未来执行。
fig-03-02 表示绕过 compile 直接创建 Plan，再由 execute 拒绝；
这不是 run 会生成非法 Plan 的证据。两张图合起来解释两个接口的约束不同。

## 组织、练习与限制

先解释编译中止，再用直接构造的反例讨论最后检查是否可删除。
建议让读者增加 SUB 时同时修改编译接受集合和执行分支，并测直接 Plan 路径。
能否删除检查取决于公开接口契约，不能只说多一次检查更安全。
没有测量性能。资料够解释这份教学代码，不可外推到真实编译器或 NPU。
