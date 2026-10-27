#!/usr/bin/env python3
"""Install either or both independent skills. Existing installations are not overwritten."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("repo-to-research", "repo-to-book")


def install(destination: Path, names=NAMES) -> None:
    destination = destination.expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("安装位置不能在项目源码内部")
    for name in names:
        if name not in NAMES:
            raise ValueError(f"未知技能：{name}")
        if (destination / name).exists():
            raise ValueError(f"目标已存在，未覆盖：{destination / name}。请先备份/移走旧技能，或改 --dest。")
    installed = []
    try:
        for name in names:
            target = destination / name
            shutil.copytree(ROOT / "skills" / name, target,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            installed.append(target)
    except Exception:
        for target in installed:
            shutil.rmtree(target)
        raise


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dest", type=Path, default=Path.home() / ".agents/skills",
                   help="技能父目录，默认 ~/.agents/skills；也可以是其他平台的技能目录")
    p.add_argument("--skill", choices=["all"] + list(NAMES), default="all")
    args = p.parse_args(argv)
    names = NAMES if args.skill == "all" else (args.skill,)
    try:
        install(args.dest, names)
        print("已安装：" + ", ".join(names) + " → " + str(args.dest.expanduser()))
        print("未安装任何模型、浏览器、diagram-design 或 imagegen；写作技能也可直接作为普通文件使用。")
        return 0
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
