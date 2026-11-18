#!/usr/bin/env python3
"""Initialize, check, and export a portable research topic directory. Never writes a book."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional
from zipfile import ZipFile, ZIP_DEFLATED
from handoff import HandoffError, bundle_files, read_bundle, start_here

ROOT = Path(__file__).resolve().parents[1]


def init_research(root: Path, title: str, repository: str = "") -> None:
    if root.exists():
        if not root.is_dir():
            raise HandoffError(f"目标不是目录：{root}")
        existing = {p.name for p in root.iterdir()}
        if existing - {"outline.md"}:
            raise HandoffError(f"目标非空，未覆盖：{root}")
    (root / "chapters/01-overview/assets").mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    obj = {
        "schema_version": 1, "title": title,
        "language": "zh-CN", "status": "draft", "outline": "outline.md",
        "sources": "sources.md", "review": "review.md", "evidence_files": [],
        "chapters": [{"id": "01-overview", "title": "第 1 章 · 系统边界与执行主线",
                      "materials": "chapters/01-overview/materials.md", "status": "draft", "assets": []}],
    }
    (root / "research.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outline_path = root / "outline.md"
    if not outline_path.exists():
        outline_text = (
            f"# {title}：全书大纲\n\n<!-- r2b:pending -->\n\n仓库：{repository or '待确认'}\n\n"
            "## 全书约定\n\n"
            "- **目标读者与预期收获**：面向软件与架构工程师，读完掌握核心数据流、关键结构定义与设计边界。\n"
            "- **叙述与例子规则**：先给出格式、结构或机制定义，再给具体输入走读例子；不脱离源码铺陈背景。\n"
            "- **术语与标题要求**：章名与小节名直接陈述技术对象，不用引导式问题标题；保留必要英文术语，不机械翻译。\n"
            "- **图表与文风要求**：并列字段与状态转换优先进表或配图；开门见山写因果，不写公关式套话与总结升华。\n\n"
            "## 逐章大纲\n\n"
            "### 第 1 章 · 系统边界与执行主线（`01-overview`）\n\n"
            "- **本章作用**：界定模块边界、核心数据结构与一次完整执行的入口路径。\n"
            "- **小节顺序与必讲内容**：\n"
            "  1. `1.1 输入输出与核心对象`：说明主要对象定义与职责分工。\n"
            "  2. `1.2 端到端执行路径`：沿一条真实输入跟踪控制流与状态变化。\n"
            "- **配图与表格**：需配系统边界与数据流向图（`fig-01-01`）。\n"
            "- **留给后续章节的细节**：底层算子内部实现与异常边界留给后续章节展开。\n"
        )
        outline_path.write_text(outline_text, encoding="utf-8")
    templates = {
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
    with ZipFile(output, "x", ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, "research/" + p.relative_to(root).as_posix())
        z.writestr("research/START_HERE.md", start_here(obj))
    return len(paths) + 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("directory", type=Path)
    init.add_argument("--title", default="开源项目技术解析"); init.add_argument("--repo", default="")
    check = sub.add_parser("check"); check.add_argument("directory", type=Path)
    check.add_argument("--draft", action="store_true", help="检查未完成目录结构，不表示可交接")
    export = sub.add_parser("export"); export.add_argument("directory", type=Path)
    export.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            init_research(args.directory, args.title, args.repo)
            print(f"已初始化专题目录：{args.directory}。先确认 outline.md，再按章收集 materials.md 与配图。")
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
