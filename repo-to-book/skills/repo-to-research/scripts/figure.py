#!/usr/bin/env python3
"""A thin diagram-design adapter plus a standalone SVG preview wrapper."""
from __future__ import annotations
import argparse
import html
from pathlib import Path
import re
import subprocess
import sys
from typing import List, Optional
from figure_support import BookError, browser_options, validate_svg


def wrap(source: Path, output: Optional[Path] = None) -> Path:
    width, _ = validate_svg(source)
    raw = source.read_text(encoding="utf-8")
    # An inline fragment must not contain XML's document declaration / doctype.
    raw = re.sub(r"<\?xml.*?\?>", "", raw, flags=re.S)
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw, flags=re.I)
    output = output or source.with_suffix(".html")
    if output.resolve() == source.resolve():
        raise BookError("HTML 输出不能覆盖 SVG 原稿")
    title = html.escape(source.stem)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<style>body{{margin:0;padding:24px;background:#f3f6f8;font-family:sans-serif}}main{{max-width:{width:g}px;margin:auto}}.diagram{{overflow-x:auto;background:white}}.diagram svg{{display:block;min-width:{width:g}px;width:{width:g}px;height:auto}}@media print{{body{{padding:0;background:white}}.diagram svg{{min-width:0;width:100%}}}}</style>
</head><body><main><div class="diagram">{raw}</div></main></body></html>''', encoding="utf-8")
    return output


def import_upstream(source: Path, skill: Path) -> Path:
    if source.suffix.lower() != ".html" or not source.is_file():
        raise BookError("import 需要 diagram-design 生成的 HTML 文件")
    for name in ("self_check.py", "export_svg.py"):
        if not (skill / "scripts" / name).is_file():
            raise BookError("上游工具不存在：" + str(skill / "scripts" / name))
    output = source.with_suffix(".svg")
    commands = [
        [sys.executable, str((skill / "scripts/self_check.py").resolve()), str(source.resolve())],
        [sys.executable, str((skill / "scripts/export_svg.py").resolve()), str(source.resolve()), str(output.resolve()), "--system-fonts"],
    ]
    for command in commands:
        try:
            result = subprocess.run(command, check=False)
        except OSError as exc:
            raise BookError("无法运行上游工具：" + str(exc))
        if result.returncode:
            raise BookError("上游检查／导出失败；未绕过失败。命令：" + " ".join(command))
    validate_svg(output)
    return output


def preview(source: Path, output: Path, browser: Optional[str], no_sandbox: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise BookError("预览需要 playwright 和 Chromium；请安装 requirements-preview.txt")
    if not source.is_file() or source.suffix.lower() not in {".svg", ".html"}:
        raise BookError("preview 只接受存在的 SVG / HTML 文件")
    if source.suffix.lower() == ".svg":
        width, height = validate_svg(source)
    else:
        width, height = 1200, 900
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            engine = p.chromium.launch(**browser_options(browser, no_sandbox))
            context = engine.new_context(viewport={"width":min(4000, max(1200, int(width)+64)), "height":min(4000, max(900, int(height)+64))}, device_scale_factor=1.5, java_script_enabled=False, reduced_motion="reduce")
            context.route(re.compile(r"^https?://"), lambda route: route.abort())
            page = context.new_page()
            content = source.read_text(encoding="utf-8")
            if source.suffix.lower() == ".svg":
                content = re.sub(r"<\?xml.*?\?>", "", content, flags=re.S)
                content = "<!doctype html><html><head><meta charset=\"utf-8\"><style>body{margin:0}svg{display:block}</style></head><body>" + content + "</body></html>"
            page.set_content(content, wait_until="load")
            page.evaluate("document.fonts.ready")
            figure = page.locator("svg").first
            if not figure.count():
                raise BookError("页面中没有 SVG")
            figure.screenshot(path=str(output), animations="disabled")
            engine.close()
    except BookError:
        raise
    except Exception as exc:
        raise BookError("图形预览失败：" + str(exc))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    wr = sub.add_parser("wrap", help="给独立 SVG 创建离线 HTML 查看页")
    wr.add_argument("source", type=Path); wr.add_argument("--out", type=Path)
    im = sub.add_parser("import", help="调用已安装的 diagram-design 检查和导出器")
    im.add_argument("source", type=Path); im.add_argument("--diagram-skill", required=True, type=Path)
    pr = sub.add_parser("preview", help="截取实际浏览器中的静态 SVG")
    pr.add_argument("source", type=Path); pr.add_argument("--out", required=True, type=Path)
    pr.add_argument("--browser"); pr.add_argument("--no-sandbox", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "wrap":
            print(wrap(args.source, args.out))
        elif args.command == "import":
            print(import_upstream(args.source, args.diagram_skill))
        else:
            preview(args.source, args.out, args.browser, args.no_sandbox)
            print(args.out)
        return 0
    except (BookError, OSError, UnicodeError) as exc:
        print("错误：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
