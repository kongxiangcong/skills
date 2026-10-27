#!/usr/bin/env python3
"""Platform-neutral writing workspace and offline publisher. No research or model calls."""
from __future__ import annotations

import argparse
import base64
import html
import hashlib
import tempfile
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import sys
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote, urlsplit
from handoff import HandoffError, bundle_files, read_bundle, start_here
import xml.etree.ElementTree as ET

SKILL_ROOT = Path(__file__).resolve().parent.parent


class BookError(ValueError):
    """An actionable content or environment error."""


def slug(text: str) -> str:
    value = re.sub(r"[^\w-]+", "-", text.lower(), flags=re.UNICODE).strip("-")
    return value or "section"


def local_path(root: Path, base: Path, value: str) -> Path:
    path = (base / unquote(value)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        raise BookError("本书引用必须在图书目录内：" + value)
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
        self.names = {p: "ch-" + slug(p.stem) for p in self.paths}
        self.names[self.paths[-1]] = "sources"
        if len(set(self.names.values())) != len(self.names):
            raise BookError("不同章节文件名生成了重复锚点，请使用不同文件名")
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
            raise BookError(f"图片缺失：{src}（{current.name}）")
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
            raise BookError(f"本地链接不在 chapters/sources 中：{href}（{current.name}）")
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
        # Raw HTML is deliberately treated as text. SVG figures are separate assets.
        md = MarkdownIt("commonmark", {"html": False}).enable("table")

        def render_image(tokens, idx, options, env):
            token = tokens[idx]
            return '<span class="figure-content"><img src="' + html.escape(token.attrGet("src") or "", quote=True) + '" alt="' + html.escape(token.content, quote=True) + '"/><span class="figcaption">' + html.escape(token.content) + '</span></span>'

        md.renderer.rules["image"] = render_image
        sections: List[str] = []
        self.ids.clear(); self.links.clear(); self.toc.clear(); self.figures.clear(); self.warnings.clear()
        for path in self.paths:
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise BookError("空稿：" + path.name)
            if re.search(r"\{\{[^}\n]+\}\}", text):
                raise BookError("尚有未替换模板变量：" + path.name)
            tokens = md.parse(text)
            docid = self.names[path]
            self.ids.add(docid)
            used: set = set()
            h1_count = 0
            for i, token in enumerate(tokens):
                if token.type == "fence" and token.info.strip() in {"mermaid", "math", "latex"}:
                    raise BookError(f"{path.name} 中的 {token.info} 代码块不会渲染成图，请先导出静态 SVG")
                if token.type == "heading_open":
                    inline = tokens[i + 1]
                    match = re.search(r"\s*\{#([\w-]+)\}\s*$", inline.content)
                    title = inline.content[:match.start()].rstrip() if match else inline.content
                    anchor = match.group(1) if match else slug(title)
                    if anchor in used and match:
                        raise BookError(f"{path.name} 中的显式锚点重复：{anchor}")
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
                    if level <= 2:
                        visible = "".join(t.content for t in inline.children or [] if t.type in {"text", "code_inline"})
                        self.toc.append((level, target, visible))
                if token.type == "inline":
                    for child in token.children or []:
                        if child.type == "image":
                            self._image(path, child)
                        elif child.type == "link_open":
                            self._link(path, child)
            if h1_count != 1:
                raise BookError(f"{path.name} 应有且只有一个一级标题，实际 {h1_count}")
            body = md.renderer.render(tokens, md.options, {})
            # Images should be standalone paragraphs. This makes each figure an unbroken block.
            body = re.sub(r'<p>(<span class="figure-content">.*?</span></span>)</p>', r'<figure>\1</figure>', body, flags=re.S)
            sections.append('<section class="chapter" id="' + docid + '">' + body + '</section>')
        missing = sorted(set(self.links) - self.ids)
        if missing:
            raise BookError("链接锚点不存在：" + ", ".join(missing))
        if not self.figures:
            self.warnings.append("当前没有图片：请按内容确认是否缺少关键机制图；不以图数强制判失败。")
        return "\n".join(sections)

    def html(self) -> str:
        body = self.render_body()
        cfg = self.config
        title = html.escape(cfg["title"])
        css = (SKILL_ROOT / "assets" / "book.css").read_text(encoding="utf-8")
        toc = "\n".join('<li class="level-' + str(level) + '"><a href="#' + ident + '">' + html.escape(name) + '</a></li>' for level, ident, name in self.toc)
        metadata = " · ".join(str(cfg.get(k, "")) for k in ("author", "edition") if cfg.get(k))
        return f'''<!doctype html>
<html lang="{html.escape(str(cfg.get('language', 'zh-CN')), quote=True)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>{title}</title><style>{css}</style></head>
<body><main>
<header class="cover"><p class="eyebrow">REPO TO BOOK / 图解技术书</p><h1>{title}</h1>
<p class="subtitle">{html.escape(str(cfg.get('subtitle', '')))}</p>
<div class="cover-rule"></div><p class="metadata">{html.escape(metadata)}</p>
<p class="cover-note">沿一条真实执行路径，理解系统的结构、机制与取舍。</p></header>
<nav class="toc" aria-label="目录"><p class="eyebrow">CONTENTS</p><h1>阅读路线</h1><ol>{toc}</ol></nav>
{body}
</main></body></html>'''


def write_pdf(html_path: Path, pdf_path: Path, title: str, executable: Optional[str], no_sandbox: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise BookError("PDF 需要 playwright；请安装 requirements-pdf.txt，并运行 python -m playwright install chromium")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**browser_options(executable, no_sandbox))
            context = browser.new_context(java_script_enabled=False)
            context.route(re.compile(r"^https?://"), lambda route: route.abort())
            page = context.new_page()
            page.set_content(html_path.read_text(encoding="utf-8"), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(pdf_path), format="A4", prefer_css_page_size=True,
                     print_background=True, outline=True, tagged=True,
                     display_header_footer=True, header_template="<div></div>",
                     footer_template='<div style="font-family:sans-serif;font-size:8px;color:#526472;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>')
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
    (root / "figures").mkdir(exist_ok=True)


def prepare_book(source: Path, destination: Path) -> None:
    """Create a writing workspace from an explicitly completed research package.

    Copies only registered handoff files; preserves the research package unchanged.
    It creates placeholders, not generated prose. No Codex, network, or image tool.
    """
    source, destination = source.resolve(), destination.resolve()
    if (destination == source or source in destination.parents
            or destination in source.parents):
        raise BookError("研究目录与写作目录不能互相包含；请用两个独立目录")
    if destination.exists():
        raise BookError("写作目录已存在，未覆盖：" + str(destination))
    try:
        research = read_bundle(source)
        paths = bundle_files(source, research)
    except HandoffError as exc:
        raise BookError(str(exc)) from exc
    # These names belong to stage two, not to arbitrary research evidence.
    reserved = {"book.json", "writing-review.md"}
    for path in paths:
        rel = path.relative_to(source)
        if rel.as_posix() in reserved or rel.parts[0] in {"manuscript", "dist"}:
            raise BookError("研究素材占用写作阶段路径：" + rel.as_posix())
    destination.mkdir(parents=True)
    try:
        for path in paths:
            out = destination / path.relative_to(source)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
        (destination / "START_HERE.md").write_text(start_here(research), encoding="utf-8")
        (destination / "manuscript").mkdir()
        config = {key: research[key] for key in ("title", "subtitle", "language") if key in research}
        config.update({"author": "", "edition": "", "chapters": [], "sources": research["sources"]})
        for ch in research["chapters"]:
            rel = "manuscript/" + ch["id"] + ".md"
            config["chapters"].append(rel)
            # Deliberate placeholders prevent accidentally publishing the research dossier as a book.
            prose = "# " + ch["title"] + "\n\n{{请根据 ../" + ch["materials"] + " 组织本章正文，不得发布占位模板。}}\n"
            for asset in ch.get("assets", []):
                caption = asset["caption"].replace("[", "\\[").replace("]", "\\]")
                prose += "\n![" + caption + "](<../" + asset["file"] + ">)\n\n{{围绕这张图解释问题、关键变化和设计边界。}}\n"
            (destination / rel).write_text(prose, encoding="utf-8")
        config["research_files"] = research_hashes(source, research)
        config["research_scope"] = [ch["id"] for ch in research["chapters"]]
        config["coverage"] = {ch["id"]: {"chapters": ["manuscript/" + ch["id"] + ".md"], "reason": ""}
                              for ch in research["chapters"]}
        config["chapter_reviews"] = {p: "pending" for p in config["chapters"]}
        config["core_gaps"] = []
        config["visual_review"] = "pending"
        (destination / "book.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (destination / "writing-review.md").write_text(
            "# 写作与出版复核\n\n<!-- r2b:pending -->\n\n"
            "## 叙事、概念顺序与术语\n\n## 图文及来源一致性\n\n"
            "## 退回研究的缺口（若无，说明实际核验范围）\n\n"
            "## 实际渲染检查与未执行项目\n\n尚未写作或出版。HTML 默认，PDF 仅用户要求时生成。\n", encoding="utf-8")
    except Exception:
        shutil.rmtree(destination)
        raise


def research_hashes(root: Path, research: Dict) -> Dict[str, str]:
    return {p.relative_to(root.resolve()).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in bundle_files(root, research)}


def check_delivery(root: Path, config: Dict) -> None:
    """Check recorded scope/review obligations, not the truth of review assertions."""
    try:
        research = read_bundle(root)
        actual = research_hashes(root, research)
    except HandoffError as exc:
        raise BookError(str(exc)) from exc
    if config.get("research_files") != actual:
        raise BookError("研究素材与接收快照不一致；使用 refresh 接收完整返修包，不能手工混用证据")
    coverage = config.get("coverage")
    ids = {ch["id"] for ch in research["chapters"]}
    retained = config.get("research_scope")
    if (not isinstance(retained, list) or not all(isinstance(cid, str) for cid in retained)
            or len(set(retained)) != len(retained) or not ids <= set(retained)):
        raise BookError("research_scope 必须保留初始及历次新增研究章节 id，不能随返修缩减")
    if not isinstance(coverage, dict) or set(coverage) != set(retained):
        raise BookError("交付 coverage 必须覆盖研究范围全部章节 id（可有理由地合并、拆分或删除）")
    published = set(config["chapters"])
    mapped = set()
    counts = {}
    for cid, row in coverage.items():
        if not isinstance(row, dict):
            raise BookError("coverage 项应包含 chapters 与 reason：" + cid)
        targets = row.get("chapters")
        if (not isinstance(targets, list) or not all(isinstance(p, str) for p in targets)
                or len(set(targets)) != len(targets) or set(targets) - published):
            raise BookError("coverage 指向未出版章节或无效路径：" + cid)
        mapped.update(targets)
        for target in targets:
            counts[target] = counts.get(target, 0) + 1
    if mapped != published:
        raise BookError("成书章节未说明对应研究范围：" + str(sorted(published - mapped)))
    for cid, row in coverage.items():
        targets = row["chapters"]
        if (cid not in ids or len(targets) != 1 or any(counts[t] > 1 for t in targets)) and not str(row.get("reason", "")).strip():
            raise BookError("删除、合并或拆分研究章节需要说明理由：" + cid)
    reviews = config.get("chapter_reviews", {})
    if not isinstance(reviews, dict) or any(reviews.get(p) != "approved" for p in published):
        raise BookError("出版章节仍需写作复核（chapter_reviews）")
    gaps = config.get("core_gaps")
    if not isinstance(gaps, list) or any(not isinstance(g, dict) or g.get("status") != "resolved"
                                         or not str(g.get("resolution", "")).strip() for g in gaps):
        raise BookError("仍有未解决核心缺口；core_gaps 需逐项记录 resolution 和 resolved")
    review = root / "writing-review.md"
    text = review.read_text(encoding="utf-8") if review.is_file() else ""
    if "<!-- r2b:pending -->" in text or "<!-- r2b:reviewed -->" not in text:
        raise BookError("writing-review.md 尚未完成统稿（需 reviewed 标记和实际记录）")
    if config.get("visual_review") != "passed":
        raise BookError("HTML 可构建，但视觉验收尚未完成（visual_review）")


def refresh_book(source: Path, destination: Path, apply: bool = False) -> Dict:
    """Compare or apply a complete repaired bundle, retaining all manuscript files.

    Work in a sibling staging directory. Swap only after every copy succeeds;
    rollback the original directory if the second rename fails.
    """
    source, destination = source.resolve(), destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise BookError("返修研究包与写作目录不能互相包含")
    config = read_config(destination)
    try:
        old = read_bundle(destination)
        new = read_bundle(source)
        previous = research_hashes(destination, old)
        incoming = research_hashes(source, new)
    except HandoffError as exc:
        raise BookError(str(exc)) from exc
    if config.get("research_files") != previous:
        raise BookError("现有素材已偏离接收快照；请先恢复原材料，不能覆盖未登记修改")
    for rel in incoming:
        if rel in {"book.json", "writing-review.md"} or Path(rel).parts[0] in {"manuscript", "dist"}:
            raise BookError("返修素材占用写作路径：" + rel)
        target = destination / rel
        if target.exists() and rel not in previous:
            raise BookError("新素材与未登记的本地文件冲突：" + rel)
    changed = sorted(p for p in set(previous) | set(incoming) if previous.get(p) != incoming.get(p))
    # Chapter-local material/figure changes only invalidate their mapped chapters.
    # Shared evidence, source metadata, scope, or unknown dependencies invalidate all.
    ownership = {}
    for ch in old["chapters"]:
        for rel in [ch["materials"]] + [a[k] for a in ch.get("assets", [])
                                               for k in ("file", "editable", "prompt") if a.get(k)]:
            ownership.setdefault(rel, set()).add(ch["id"])
    local_changed = set(changed) - {"research.json"}
    old_meta = dict(old); new_meta = dict(new)
    for obj in (old_meta, new_meta):
        obj.pop("chapters", None)
    global_change = old_meta != new_meta or old["chapters"] != new["chapters"] or any(p not in ownership for p in local_changed)
    affected = set(config["chapters"]) if global_change else set()
    for rel in local_changed:
        for cid in ownership.get(rel, []):
            row = config.get("coverage", {}).get(cid, {})
            affected.update(row.get("chapters", config["chapters"]))
    result = {"changed_files": changed, "review_chapters": sorted(affected), "applied": False}
    if not apply or not changed:
        return result
    staging = Path(tempfile.mkdtemp(prefix=".r2b-refresh-", dir=destination.parent))
    staged = staging / "book"
    backup = staging / "previous"
    try:
        shutil.copytree(destination, staged)
        for rel in set(previous) - set(incoming):
            (staged / rel).unlink()
        for rel in changed:
            if rel in incoming:
                target = staged / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / rel, target)
        config["research_files"] = incoming
        config["research_scope"] = list(dict.fromkeys(config.get("research_scope", []) +
            [ch["id"] for ch in old["chapters"]] + [ch["id"] for ch in new["chapters"]]))
        config["sources"] = new["sources"]
        reviews = config.setdefault("chapter_reviews", {})
        for chapter in affected:
            reviews[chapter] = "pending"
        for ch in new["chapters"]:
            config.setdefault("coverage", {}).setdefault(ch["id"], {"chapters": [], "reason": ""})
        config["visual_review"] = "pending"
        (staged / "book.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (staged / "START_HERE.md").write_text(start_here(new), encoding="utf-8")
        with (staged / "writing-review.md").open("a", encoding="utf-8") as stream:
            stream.write("\n\n## 研究返修接收\n\n<!-- r2b:pending -->\n\n变更文件：\n" +
                         "\n".join("- `" + p + "`" for p in changed) +
                         "\n\n需复核正文、题注与跨章引用：" + ", ".join(sorted(affected)) +
                         "\n原稿保留；缺口仅在核验证据后手工关闭。旧 dist 已移除，请重建。\n")
        if (staged / "dist").exists():
            shutil.rmtree(staged / "dist")
        destination.rename(backup)
        try:
            staged.rename(destination)
        except Exception as swap_error:
            try:
                backup.rename(destination)
            except Exception as restore_error:
                raise BookError(
                    "返修切换和回滚均失败；原稿完整保留在：" + str(backup) +
                    "。请勿删除该目录；解决文件占用/权限问题后，将 previous 目录恢复为：" +
                    str(destination) + "; 切换错误：" + str(swap_error) +
                    "; 回滚错误：" + str(restore_error)) from restore_error
            raise
        result["applied"] = True
    finally:
        # A failed rollback (or interruption after moving the original) must
        # never delete the only remaining copy of the user's manuscript.
        if not backup.exists() or result["applied"]:
            shutil.rmtree(staging)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="从已就绪研究包创建独立写作目录；不执行研究或生成正文")
    prepare.add_argument("research", type=Path)
    prepare.add_argument("directory", type=Path)
    refresh = sub.add_parser("refresh", help="比较完整返修包；--apply 更新素材并保留正文、失效相关复核")
    refresh.add_argument("research", type=Path)
    refresh.add_argument("directory", type=Path)
    refresh.add_argument("--apply", action="store_true")
    init = sub.add_parser("init", help="手工初始化空书目录；不用于绕过研究交接")
    init.add_argument("directory", type=Path)
    init.add_argument("--title", default="读懂一个开源项目")
    check = sub.add_parser("check", help="检查结构、引用和静态图片；不判断技术事实")
    check.add_argument("directory", type=Path)
    check.add_argument("--delivery", action="store_true", help="核对范围覆盖、复核、核心缺口和素材快照")
    build = sub.add_parser("build", help="生成离线 HTML 和／或 PDF")
    build.add_argument("directory", type=Path)
    build.add_argument("--format", choices=["html", "pdf", "all"], default="html")
    build.add_argument("--out", type=Path)
    build.add_argument("--browser", help="Chrome / Chromium 可执行文件")
    build.add_argument("--no-sandbox", action="store_true", help="仅用于受控容器，不推荐日常使用")
    args = parser.parse_args(argv)
    try:
        if args.command == "refresh":
            print(json.dumps(refresh_book(args.research, args.directory, args.apply), ensure_ascii=False, indent=2))
            return 0
        if args.command == "prepare":
            prepare_book(args.research, args.directory)
            print("已创建独立写作目录：" + str(args.directory) + "；请写作 manuscript/ 各章后再 build。没有调用模型或研究工具。")
            return 0
        if args.command == "init":
            init_book(args.directory, args.title)
            print("已创建：" + str(args.directory) + "；请填写 sources.md 和章节模板；研究应由 repo-to-research 另行完成。")
            return 0
        book = Book(args.directory)
        rendered = book.html()
        for warning in book.warnings:
            print("提示：" + warning, file=sys.stderr)
        print(f"结构检查通过：{len(book.config['chapters'])} 章，{len(book.figures)} 张插图，{len(book.links)} 个书内链接。不是事实审校结论。")
        if args.command == "check":
            if args.delivery:
                check_delivery(book.root, book.config)
                print("交付记录检查通过；仅确认范围及复核记录齐备，不证明模型判断正确。")
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
