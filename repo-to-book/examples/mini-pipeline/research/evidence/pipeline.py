"""A teaching-only compiler/executor; not an inference engine or simulator."""
from dataclasses import dataclass
import sys


@dataclass(frozen=True)
class Plan:
    op: str
    lhs: int
    rhs: int


def compile_expression(text: str) -> Plan:
    parts = text.split()
    if len(parts) != 3:
        raise ValueError("expected: OP INTEGER INTEGER")
    op = parts[0].upper()
    if op not in {"ADD", "MUL"}:
        raise ValueError("unsupported operation: " + op)
    lhs, rhs = int(parts[1]), int(parts[2])
    return Plan(op, lhs, rhs)


def execute(plan: Plan) -> int:
    if plan.op == "ADD":
        return plan.lhs + plan.rhs
    if plan.op == "MUL":
        return plan.lhs * plan.rhs
    raise ValueError("unsupported plan: " + plan.op)


def run(text: str) -> int:
    return execute(compile_expression(text))


if __name__ == "__main__":
    expression = " ".join(sys.argv[1:]) or "ADD 2 3"
    print(run(expression))
