#!/usr/bin/env python3
"""Platform-neutral in-place writing and offline publisher. No research or model calls."""
from __future__ import annotations

import argparse
import base64
import html
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from handoff import HandoffError, outline_field, read_bundle, start_here

SKILL_ROOT = Path(__file__).resolve().parent.parent


class BookError(ValueError):
    """An actionable content or environment error."""


def slug(text: str) -> str:
    value = re.sub(r"[^\w-]+", "-", text.lower(), flags=re.UNICODE).strip("-")
    return value or "section"


def chapter_anchor_id(root: Path, path: Path) -> str:
    """Derive a stable chapter anchor from chapters/<id>/manuscript.md or legacy manuscript/<id>.md."""
    if path.stem == "manuscript" and path.parent != root:
        return "ch-" + slug(path.parent.name)
    return "ch-" + slug(path.stem)


def local_path(root: Path, base: Path, value: str) -> Path:
    path = (base / unquote(value)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        raise BookError("本书引用必须在专题目录内：" + value)
    return path


def validate_svg(path: Path) -> Tuple[float, float]:
    """Validate the supported static/offline SVG subset, not visual correctness."""
    try:
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
    except (OSError, UnicodeError, ET.ParseError) as exc:
        raise BookError(f"SVG 无法读取或解析：{path.name}: {exc}")
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise BookError(f"SVG 根元素需要正确的 xmlns：{path.name}")
    try:
        box = [float(v) for v in re.split(r"[\s,]+", root.attrib["viewBox"].strip())]
        if len(box) != 4 or not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
            raise ValueError()
    except (KeyError, ValueError):
        raise BookError(f"SVG 缺少有效 viewBox：{path.name}")
    children = list(root)
    title = root.find("{http://www.w3.org/2000/svg}title")
    desc = root.find("{http://www.w3.org/2000/svg}desc")
    if (not children or children[0] is not title or title is None or desc is None
            or not "".join(title.itertext()).strip() or not "".join(desc.itertext()).strip()):
        raise BookError(f"SVG 需要首元素 title 和非空 desc：{path.name}")
    labels = set(root.get("aria-labelledby", "").split())
    if root.get("role") != "img" or not title.get("id") or not desc.get("id") or not {title.get("id"), desc.get("id")} <= labels:
        raise BookError(f"SVG 的 role / aria-labelledby 不完整：{path.name}")
    ids: set = set()
    for node in root.iter():
        name = node.tag.rsplit("}", 1)[-1].lower()
        if name in {"script", "foreignobject", "animate", "animatetransform", "set"}:
            raise BookError(f"成书使用静态 SVG，不支持 {name}：{path.name}")
        identifier = node.get("id")
        if identifier:
            if identifier in ids:
                raise BookError(f"SVG 存在重复 id {identifier}：{path.name}")
            ids.add(identifier)
        for key, value in node.attrib.items():
            attr = key.rsplit("}", 1)[-1].lower()
            if attr.startswith("on"):
                raise BookError(f"SVG 不应含事件脚本：{path.name}")
            if attr == "href" and value and not value.startswith(("#", "data:")):
                raise BookError(f"SVG 不应依赖外部文件或 URL：{path.name}")
    if re.search(r"@import\b", text, re.I):
        raise BookError(f"SVG 不应导入远程样式或字体：{path.name}")
    for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", text, re.I):
        if not match.group(1).strip().startswith(("#", "data:")):
            raise BookError(f"SVG 含外部 CSS 资源：{path.name}")
    return box[2], box[3]


def read_config(root: Path) -> Dict:
    try:
        config = json.loads((root / "book.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BookError(f"无法读取 book.json：{exc}")
    if not isinstance(config, dict):
        raise BookError("book.json 应是 JSON 对象")
    for key in ("title", "sources"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise BookError(f"book.json 缺少 {key}")
    chapters = config.get("chapters")
    if not isinstance(chapters, list) or not chapters or not all(isinstance(p, str) and p for p in chapters):
        raise BookError("book.json 的 chapters 需要非空路径列表")
    paths = [local_path(root, root, p) for p in chapters + [config["sources"]]]
    if len(set(paths)) != len(paths):
        raise BookError("章节或 sources 重复")
    for path in paths:
        if not path.is_file() or path.suffix.lower() != ".md":
            raise BookError(f"缺少 Markdown 文件：{path}")
    return config


def browser_options(executable: Optional[str], no_sandbox: bool) -> Dict:
    chosen = executable or os.environ.get("CHROME_BIN")
    if not chosen:
        for command in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
            chosen = shutil.which(command)
            if chosen:
                break
    options = {"headless": True, "chromium_sandbox": not no_sandbox}
    if chosen:
        if not Path(chosen).is_file():
            raise BookError("浏览器路径不存在：" + chosen)
        options["executable_path"] = chosen
    return options


class Book:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.config = read_config(self.root)
        self.paths = [local_path(self.root, self.root, p) for p in self.config["chapters"] + [self.config["sources"]]]
        self.names = {p: chapter_anchor_id(self.root, p) for p in self.paths}
        self.names[self.paths[-1]] = "sources"
        if len(set(self.names.values())) != len(self.names):
            raise BookError("不同章节生成了重复锚点，请检查章节目录或文件名")
        self.ids: set = set()
        self.links: List[str] = []
        self.toc: List[Tuple[int, str, str]] = []
        self.figures: set = set()
        self.warnings: List[str] = []

    def _image(self, current: Path, token) -> None:
        src = token.attrGet("src") or ""
        parsed = urlsplit(src)
        if parsed.scheme or parsed.netloc:
            raise BookError(f"图片必须下载到本地，不能引用远程 URL：{src}")
        path = local_path(self.root, current.parent, parsed.path)
        if not path.is_file():
            raise BookError(f"图片缺失：{src}（{current.relative_to(self.root).as_posix()}）")
        suffix = path.suffix.lower()
        if suffix not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
            raise BookError("不支持的静态图片格式：" + src)
        if suffix == ".svg":
            validate_svg(path)
        if not token.content.strip():
            raise BookError("图片需要描述性题注（alt）：" + src)
        mime = "image/svg+xml" if suffix == ".svg" else mimetypes.guess_type(path.name)[0]
        token.attrSet("src", "data:" + str(mime) + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii"))
        self.figures.add(path)

    def _link(self, current: Path, token) -> None:
        href = token.attrGet("href") or ""
        parsed = urlsplit(href)
        if parsed.scheme in {"http", "https", "mailto"}:
            return
        if parsed.scheme or parsed.netloc:
            raise BookError("不支持的链接协议：" + href)
        if parsed.query:
            raise BookError("书内文件链接不使用 query 参数：" + href)
        target = local_path(self.root, current.parent, parsed.path) if parsed.path else current
        if target not in self.names:
            raise BookError(f"本地链接不在 chapters/sources 中：{href}（{current.relative_to(self.root).as_posix()}）")
        anchor = self.names[target]
        if parsed.fragment:
            anchor += "--" + unquote(parsed.fragment)
        token.attrSet("href", "#" + anchor)
        self.links.append(anchor)

    def render_body(self) -> str:
        try:
            from markdown_it import MarkdownIt
        except ImportError:
            raise BookError("缺少 markdown-it-py；请安装 requirements.txt")
        md = MarkdownIt("commonmark", {"html": False}).enable("table")

        def render_image(tokens, idx, options, env):
            token = tokens[idx]
            return '<span class="figure-content"><img src="' + html.escape(token.attrGet("src") or "", quote=True) + '" alt="' + html.escape(token.content, quote=True) + '"/><span class="figcaption">' + html.escape(token.content) + '</span></span>'

        md.renderer.rules["image"] = render_image
        sections: List[str] = []
        self.ids.clear(); self.links.clear(); self.toc.clear(); self.figures.clear(); self.warnings.clear()
        for path in self.paths:
            label = path.relative_to(self.root).as_posix()
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise BookError("空稿：" + label)
            if re.search(r"\{\{[^}\n]+\}\}", text):
                raise BookError("尚有未替换模板变量：" + label)
            tokens = md.parse(text)
            docid = self.names[path]
            self.ids.add(docid)
            used: set = set()
            h1_count = 0
            for i, token in enumerate(tokens):
                if token.type == "fence" and token.info.strip() in {"mermaid", "math", "latex"}:
                    raise BookError(f"{label} 中的 {token.info} 代码块不会渲染成图，请先导出静态 SVG")
                if token.type == "heading_open":
                    inline = tokens[i + 1]
                    match = re.search(r"\s*\{#([\w-]+)\}\s*$", inline.content)
                    title = inline.content[:match.start()].rstrip() if match else inline.content
                    anchor = match.group(1) if match else slug(title)
                    if anchor in used and match:
                        raise BookError(f"{label} 中的显式锚点重复：{anchor}")
                    original = anchor
                    counter = 2
                    while anchor in used:
                        anchor = original + "-" + str(counter); counter += 1
                    used.add(anchor)
                    target = docid + "--" + anchor
                    token.attrSet("id", target)
                    self.ids.add(target)
                    inline.content = title
                    inline.children = md.parseInline(title)[0].children
                    level = int(token.tag[1])
                    h1_count += level == 1
                    if level <= 3:
                        visible = "".join(t.content for t in inline.children or [] if t.type in {"text", "code_inline"})
                        self.toc.append((level, target, visible))
                if token.type == "inline":
                    for child in token.children or []:
                        if child.type == "image":
                            self._image(path, child)
                        elif child.type == "link_open":
                            self._link(path, child)
            if h1_count != 1:
                raise BookError(f"{label} 应有且只有一个一级标题，实际 {h1_count}")
            body = md.renderer.render(tokens, md.options, {})
            body = re.sub(r'<p>(<span class="figure-content">.*?</span></span>)</p>', r'<figure>\1</figure>', body, flags=re.S)
            sections.append('<section class="chapter" id="' + docid + '">' + body + '</section>')
        missing = sorted(set(self.links) - self.ids)
        if missing:
            raise BookError("链接锚点不存在：" + ", ".join(missing))
        if not self.figures:
            self.warnings.append("当前没有图片：请按内容确认是否缺少关键机制图；不以图数强制判失败。")
        return "\n".join(sections)

    def render_overview(self) -> str:
        """Embed an authored Mermaid export; do not execute source or infer dependencies."""
        overview = self.config.get("overview")
        if overview is None:
            return ""
        if not isinstance(overview, dict):
            raise BookError("overview 应包含 source、image、alt 和 chapters")
        for key in ("source", "image", "alt"):
            if not isinstance(overview.get(key), str) or not overview[key].strip():
                raise BookError("overview 缺少 " + key)
        if overview.get("chapters") != self.config["chapters"]:
            raise BookError("overview.chapters 必须与当前章节列表一致；章节变更后请重审结构图")
        source = local_path(self.root, self.root, overview["source"])
        picture = local_path(self.root, self.root, overview["image"])
        if source.suffix.lower() != ".mmd" or not source.is_file():
            raise BookError("overview.source 需要本地 Mermaid .mmd 文件")
        if not source.read_text(encoding="utf-8").strip():
            raise BookError("Mermaid 全书结构图源文件为空")
        if picture.suffix.lower() != ".svg" or not picture.is_file():
            raise BookError("overview.image 需要实际渲染的本地 SVG")
        validate_svg(picture)
        data = base64.b64encode(picture.read_bytes()).decode("ascii")
        return '<figure class="book-overview" aria-label="全书结构"><div class="figure-content"><img src="data:image/svg+xml;base64,' + data + '" alt="' + html.escape(overview["alt"], quote=True) + '"></div></figure>'

    def html(self) -> str:
        body = self.render_body()
        cfg = self.config
        overview = self.render_overview()
        title = html.escape(cfg["title"])
        css = (SKILL_ROOT / "assets" / "book.css").read_text(encoding="utf-8")
        toc = "\n".join('<li class="level-' + str(level) + '"><a href="#' + ident + '"><span class="toc-text">' + html.escape(name) + '</span><span class="toc-leader" aria-hidden="true"></span><span class="toc-page" data-target="' + ident + '"></span></a></li>' for level, ident, name in self.toc)
        return f'''<!doctype html>
<html lang="{html.escape(str(cfg.get('language', 'zh-CN')), quote=True)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>{title}</title><style>{css}</style></head>
<body><main>
<header class="book-header"><div class="book-title">{title}</div></header>
{overview}
<nav class="toc" aria-label="目录"><div class="toc-title">目录</div><ol>{toc}</ol></nav>
{body}
</main></body></html>'''


def write_pdf(html_path: Path, pdf_path: Path, title: str, executable: Optional[str], no_sandbox: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright
        import pymupdf
    except ImportError:
        raise BookError("PDF 需要 playwright 和 pymupdf；请安装 requirements-pdf.txt，并运行 python -m playwright install chromium")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**browser_options(executable, no_sandbox))
            context = browser.new_context(java_script_enabled=False)
            context.route(re.compile(r"^https?://"), lambda route: route.abort())
            page = context.new_page()
            page.set_content(html_path.read_text(encoding="utf-8"), wait_until="load")
            page.evaluate("document.fonts.ready")
            source = html_path.read_text(encoding="utf-8")
            targets = re.findall(r'data-target="([^"]+)"', source)
            previous = None
            with tempfile.TemporaryDirectory() as temp:
                candidate = Path(temp) / "book.pdf"
                for attempt in range(5):
                    page.pdf(path=str(candidate), format="A4", prefer_css_page_size=True,
                             print_background=True, outline=True, tagged=True,
                             display_header_footer=True, header_template="<div></div>",
                             footer_template='<div style="font-family:sans-serif;font-size:8px;color:#6f6a63;width:100%;text-align:right;padding-right:19mm"><span class="pageNumber"></span></div>')
                    with pymupdf.open(candidate) as document:
                        entries = [entry for entry in document.get_toc() if entry[0] <= 3]
                        numbers = [entry[2] for entry in entries]
                    if len(numbers) != len(targets) or any(n < 1 for n in numbers):
                        raise BookError("PDF 目录书签与标题不匹配，不能可靠生成页码。")
                    if numbers == previous:
                        shutil.copyfile(candidate, pdf_path)
                        html_path.write_text(source, encoding="utf-8")
                        break
                    previous = numbers
                    mapping = dict(zip(targets, numbers))
                    source = re.sub(r'(<span class="toc-page" data-target="([^"]+)">).*?(</span>)',
                                    lambda m: m[1] + str(mapping[m[2]]) + m[3], source)
                    page.set_content(source, wait_until="load")
                    page.evaluate("document.fonts.ready")
                else:
                    raise BookError("PDF 页码在多次排版后仍未稳定，未交付不可靠页码。")
            browser.close()
    except BookError:
        raise
    except Exception as exc:
        raise BookError("PDF 构建失败。确认 Chromium 可用或指定 --browser / CHROME_BIN。HTML 已保留。\n" + str(exc))


def init_book(root: Path, title: str) -> None:
    if root.exists() and any(root.iterdir()):
        raise BookError("目标目录非空，拒绝覆盖：" + str(root))
    shutil.copytree(SKILL_ROOT / "assets" / "book-template", root, dirs_exist_ok=True)
    config_path = root / "book.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["title"] = title
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_book(root: Path) -> None:
    """Initialize writing files in-place inside a completed research topic directory.

    Research owns outline.md, chapters/<id>/materials.md, and chapters/<id>/assets/.
    Writing owns chapters/<id>/manuscript.md, book.json, writing-review.md, and dist/.
    Existing manuscript.md files are preserved untouched.
    """
    root = root.resolve()
    try:
        research = read_bundle(root)
        outline_rel = outline_field(research)
    except HandoffError as exc:
        raise BookError(str(exc)) from exc
    reserved = {"book.json", "writing-review.md"}
    for ev in research.get("evidence_files", []):
        rel = Path(ev).as_posix()
        if rel in reserved or rel.endswith("/manuscript.md") or rel.startswith("dist/"):
            raise BookError("研究素材占用写作阶段路径：" + rel)
    expected_chapters: List[str] = []
    for ch in research["chapters"]:
        cid = ch["id"]
        chapter_dir = root / "chapters" / cid
        chapter_dir.mkdir(parents=True, exist_ok=True)
        rel = f"chapters/{cid}/manuscript.md"
        expected_chapters.append(rel)
        manuscript_path = root / rel
        if not manuscript_path.exists():
            prose = f"# {ch['title']}\n\n{{{{请依据 ../../{outline_rel} 与同目录 materials.md 撰写本章正文，不得发布占位模板。}}}}\n"
            for asset in ch.get("assets", []):
                caption = asset["caption"].replace("[", "\\[").replace("]", "\\]")
                asset_path = Path(asset["file"])
                try:
                    rel_asset = asset_path.relative_to(Path("chapters") / cid).as_posix()
                except ValueError:
                    rel_asset = "../../" + asset_path.as_posix()
                prose += f"\n![{caption}](<{rel_asset}>)\n\n{{{{围绕这张图解释核心机制、状态变化和设计边界。}}}}\n"
            manuscript_path.write_text(prose, encoding="utf-8")
    config_path = root / "book.json"
    existing_cfg = {}
    if config_path.is_file():
        try:
            existing_cfg = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            existing_cfg = {}
    old_reviews = existing_cfg.get("chapter_reviews", {}) if isinstance(existing_cfg, dict) else {}
    config = {
        "title": research["title"],
        "language": research.get("language", "zh-CN"),
        "author": existing_cfg.get("author", ""),
        "edition": existing_cfg.get("edition", ""),
        "outline": outline_rel,
        "chapters": expected_chapters,
        "sources": research["sources"],
        "chapter_reviews": {p: old_reviews.get(p, "pending") for p in expected_chapters},
        "core_gaps": existing_cfg.get("core_gaps", []),
        "visual_review": existing_cfg.get("visual_review", "pending"),
    }
    if "overview" in existing_cfg:
        config["overview"] = existing_cfg["overview"]
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    review_path = root / "writing-review.md"
    if not review_path.exists():
        review_path.write_text(
            "# 写作与出版复核\n\n<!-- r2b:pending -->\n\n"
            "## 大纲约定兑现与术语检查\n\n## 图文及来源一致性\n\n"
            "## 影响写作的已知缺口\n\n"
            "## 实际渲染检查与未执行项\n\n尚未完成统稿或出版。HTML 默认，PDF 仅用户要求时生成。\n",
            encoding="utf-8",
        )
    (root / "START_HERE.md").write_text(start_here(research), encoding="utf-8")


def check_delivery(root: Path, config: Dict) -> None:
    """Check outline chapter alignment and review completion records."""
    if (root / "research.json").is_file():
        try:
            research = read_bundle(root)
        except HandoffError as exc:
            raise BookError(str(exc)) from exc
        expected = [f"chapters/{ch['id']}/manuscript.md" for ch in research["chapters"]]
        legacy_expected = [f"manuscript/{ch['id']}.md" for ch in research["chapters"]]
        if config.get("chapters") not in (expected, legacy_expected):
            raise BookError(
                "book.json 的章节列表必须与已确认大纲（research.json）严格一致，不允许私自拆章、合章、删章或重排"
            )
    published = config["chapters"]
    reviews = config.get("chapter_reviews", {})
    if not isinstance(reviews, dict) or any(reviews.get(p) != "approved" for p in published):
        raise BookError("出版章节仍需写作复核（chapter_reviews）")
    gaps = config.get("core_gaps", [])
    if not isinstance(gaps, list) or any(not isinstance(g, dict) or g.get("status") != "resolved"
                                         or not str(g.get("resolution", "")).strip() for g in gaps):
        raise BookError("仍有未解决核心缺口；core_gaps 需逐项记录 resolution 和 resolved")
    review = root / "writing-review.md"
    text = review.read_text(encoding="utf-8") if review.is_file() else ""
    if "<!-- r2b:pending -->" in text or "<!-- r2b:reviewed -->" not in text:
        raise BookError("writing-review.md 尚未完成统稿（需 reviewed 标记和实际记录）")
    if config.get("visual_review") != "passed":
        raise BookError("HTML 可构建，但视觉验收尚未完成（visual_review）")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="在已就绪专题目录内生成 book.json 与各章 manuscript.md 初始骨架")
    prepare.add_argument("directory", type=Path)
    init = sub.add_parser("init", help="手工初始化空专题目录；不用于绕过研究交接")
    init.add_argument("directory", type=Path)
    init.add_argument("--title", default="开源项目技术解析")
    check = sub.add_parser("check", help="检查结构、引用和静态图片；不判断技术事实")
    check.add_argument("directory", type=Path)
    check.add_argument("--delivery", action="store_true", help="核对大纲章节对齐、复核记录与核心缺口")
    build = sub.add_parser("build", help="生成离线 HTML 和／或 PDF")
    build.add_argument("directory", type=Path)
    build.add_argument("--format", choices=["html", "pdf", "all"], default="html")
    build.add_argument("--out", type=Path)
    build.add_argument("--browser", help="Chrome / Chromium 可执行文件")
    build.add_argument("--no-sandbox", action="store_true", help="仅用于受控容器，不推荐日常使用")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            prepare_book(args.directory)
            print("已在专题目录内就绪写作配置：" + str(args.directory) + "；请逐章完成 chapters/*/manuscript.md 后再 build。")
            return 0
        if args.command == "init":
            init_book(args.directory, args.title)
            print("已创建：" + str(args.directory) + "；请填写 outline.md、sources.md 和章节正文。")
            return 0
        book = Book(args.directory)
        rendered = book.html()
        for warning in book.warnings:
            print("提示：" + warning, file=sys.stderr)
        print(f"结构检查通过：{len(book.config['chapters'])} 章，{len(book.figures)} 张插图，{len(book.links)} 个书内链接。不是事实审校结论。")
        if args.command == "check":
            if args.delivery:
                check_delivery(book.root, book.config)
                print("交付记录检查通过；仅确认大纲章节一致及复核记录齐备，不证明模型判断正确。")
            return 0
        output = args.out.resolve() if args.out else book.root / "dist"
        output.mkdir(parents=True, exist_ok=True)
        html_path = output / "book.html"
        html_path.write_text(rendered, encoding="utf-8")
        print("HTML：" + str(html_path))
        if args.format in {"all", "pdf"}:
            write_pdf(html_path, output / "book.pdf", book.config["title"], args.browser, args.no_sandbox)
            print("PDF：" + str(output / "book.pdf"))
        return 0
    except (BookError, OSError, UnicodeError) as exc:
        print("错误：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
