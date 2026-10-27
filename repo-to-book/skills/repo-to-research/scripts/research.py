#!/usr/bin/env python3
"""Initialize, check, and export a portable research package. Never writes a book."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
from typing import List, Optional
from zipfile import ZipFile, ZIP_DEFLATED
from handoff import HandoffError, bundle_files, read_bundle, start_here

ROOT = Path(__file__).resolve().parents[1]


def init_research(root: Path, title: str, repository: str = "") -> None:
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise HandoffError(f"目标非空，未覆盖：{root}")
    (root / "chapters/01-overview/assets").mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    obj = {
        "schema_version": 1, "title": title, "subtitle": "从真实执行路径理解系统",
        "language": "zh-CN", "status": "draft", "plan": "plan.md",
        "sources": "sources.md", "review": "review.md", "evidence_files": [],
        "chapters": [{"id": "01-overview", "title": "项目的边界与执行主线",
                      "materials": "chapters/01-overview/materials.md", "status": "draft", "assets": []}],
    }
    (root / "research.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    templates = {
        "plan.md": f"# {title}：研究与规划\n\n<!-- r2b:pending -->\n\n仓库：{repository or '待确认'}\n\n" +
                   "## 读者、目标与不研究的范围\n\n## 固定源码版本和本地改动\n\n## 全书主题与学习主线\n\n" +
                   "## 章节顺序、问题与前置知识\n\n## 配图计划与共同视觉风格\n\n" +
                   "## 调研分工与下一步\n\n主 agent 规划与综合；源码子 agent、外部调研子 agent、独立核验子 agent 分工执行。\n",
        "sources.md": "# 共同来源与版本\n\n<!-- r2b:pending -->\n\n" +
                      "## S01 · 项目源码 {#s01}\n\n填写仓库 URL、完整 commit 或文件哈希、符号与行号、随包证据路径、许可和获取日期。\n",
        "review.md": "# 研究与素材核验\n\n<!-- r2b:pending -->\n\n" +
                     "## 实际执行与角色\n\n记录实际子代理分工；未执行不得写已完成。\n\n" +
                     "## 实际出图工具与结果\n\ndiagram-design：未执行。imagegen：未执行。\n\n" +
                     "## 具体核验发现及处理\n\n## 仍未知的边界与缺口\n\n## 交接结论\n\n尚不可开始正式写作。\n",
    }
    for filename, text in templates.items():
        (root / filename).write_text(text, encoding="utf-8")
    template = (ROOT / "assets/materials-template.md").read_text(encoding="utf-8")
    (root / "chapters/01-overview/materials.md").write_text(template, encoding="utf-8")
    (root / "START_HERE.md").write_text(start_here(obj), encoding="utf-8")


def check_figures(root: Path, obj: dict) -> None:
    from figure_support import validate_svg
    for ch in obj["chapters"]:
        for a in ch.get("assets", []):
            if a.get("status") == "ready" and a["file"].lower().endswith(".svg"):
                validate_svg(root / a["file"])


def export_bundle(root: Path, output: Path) -> int:
    root = root.resolve()
    obj = read_bundle(root)
    check_figures(root, obj)
    paths = bundle_files(root, obj)
    output = output.resolve()
    if output.suffix.lower() != ".zip":
        raise HandoffError("交接包输出文件应为 .zip")
    if output.exists():
        raise HandoffError(f"交接包已存在，未覆盖：{output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    # A fixed top-level name makes the zip portable even if the source folder uses local-specific names.
    with ZipFile(output, "x", ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, "research/" + p.relative_to(root).as_posix())
        z.writestr("research/START_HERE.md", start_here(obj))
    return len(paths) + 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("directory", type=Path)
    init.add_argument("--title", default="读懂一个开源项目"); init.add_argument("--repo", default="")
    check = sub.add_parser("check"); check.add_argument("directory", type=Path)
    check.add_argument("--draft", action="store_true", help="检查未完成目录结构，不表示可交接")
    export = sub.add_parser("export"); export.add_argument("directory", type=Path)
    export.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_research(args.directory, args.title, args.repo)
            print(f"已创建研究目录：{args.directory}。只做研究与出图，不写最终章节。")
        elif args.command == "check":
            obj = read_bundle(args.directory, require_ready=not args.draft)
            check_figures(args.directory, obj)
            print(f"{'草稿结构' if args.draft else '交接文件'}检查通过：{len(obj['chapters'])} 章。不是事实正确性或独立审校证明。")
        else:
            count = export_bundle(args.directory, args.out)
            print(f"已导出 {count} 个交接文件：{args.out}。到此停止；由用户另行启动 repo-to-write。")
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
