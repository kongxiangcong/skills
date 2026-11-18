"""The portable topic-directory contract. Standard library only.

This file is shipped identically in both skills so either can be installed alone.
Checks establish completeness of files/references, never factual correctness.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Set


class HandoffError(ValueError):
    """Invalid or unfinished portable topic package."""


def outline_field(obj: Dict[str, Any]) -> str:
    """Return the outline filename ('outline' preferred, 'plan' accepted for compatibility)."""
    value = obj.get("outline") or obj.get("plan")
    if not isinstance(value, str) or not value.strip():
        raise HandoffError("research.json 缺少 outline（应指向 outline.md）")
    return value


def local_file(root: Path, value: str) -> Path:
    if (not isinstance(value, str) or not value.strip() or "\\" in value
            or re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/|~)", value)):
        raise HandoffError(f"交接路径必须是包内 POSIX 相对路径：{value!r}")
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        raise HandoffError(f"交接路径越出素材目录：{value}")
    if not path.is_file():
        raise HandoffError(f"缺少交接文件：{value}")
    return path


def read_text(root: Path, value: str, ready: bool) -> str:
    path = local_file(root, value)
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError) as exc:
        raise HandoffError(f"无法读取 UTF-8 文本 {value}：{exc}") from exc
    if not text.strip():
        raise HandoffError(f"交接文本为空：{value}")
    if ready and "<!-- r2b:pending -->" in text:
        raise HandoffError(f"交接文本仍有未完成标记：{value}")
    return text


def read_bundle(root: Path, require_ready: bool = True) -> Dict[str, Any]:
    """Load a topic research package; reject missing real assets and unresolved source IDs."""
    root = root.resolve()
    try:
        obj = json.loads((root / "research.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HandoffError(f"无法读取 research.json：{exc}") from exc
    if not isinstance(obj, dict) or obj.get("schema_version") != 1:
        raise HandoffError("仅支持 research.json 的 schema_version: 1")
    if not isinstance(obj.get("title"), str) or not obj["title"].strip():
        raise HandoffError("research.json 缺少非空 title")
    if obj.get("status") not in {"draft", "ready"}:
        raise HandoffError("research.json 的 status 必须是 draft 或 ready")
    if require_ready and obj["status"] != "ready":
        raise HandoffError("素材仍是 draft；先完成研究、实际出图与核验，再由用户启动写作")
    outline_rel = outline_field(obj)
    read_text(root, outline_rel, require_ready)
    for key in ("sources", "review"):
        if key not in obj:
            raise HandoffError(f"research.json 缺少 {key}")
        read_text(root, obj[key], require_ready)
    source_text = read_text(root, obj["sources"], require_ready)
    anchors = re.findall(r"\{#([\w-]+)\}", source_text)
    if len(set(anchors)) != len(anchors):
        raise HandoffError("sources.md 中有重复来源锚点")
    if require_ready and not anchors:
        raise HandoffError("sources.md 需要可引用的来源锚点，例如 {#s01}")
    available = set(anchors)
    chapters = obj.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise HandoffError("research.json 需要非空 chapters 列表")
    chapter_ids: Set[str] = set()
    asset_ids: Set[str] = set()
    materials_paths: Set[Path] = set()
    asset_paths: Set[Path] = set()
    for ch in chapters:
        if not isinstance(ch, dict):
            raise HandoffError("chapters 元素应为对象")
        cid = ch.get("id", "")
        if not isinstance(cid, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", cid):
            raise HandoffError(f"章节 id 无效：{cid!r}")
        if cid in chapter_ids:
            raise HandoffError(f"重复章节 id：{cid}")
        chapter_ids.add(cid)
        if not isinstance(ch.get("title"), str) or not ch["title"].strip():
            raise HandoffError(f"章节 {cid} 缺少 title")
        if ch.get("status") not in {"draft", "ready"}:
            raise HandoffError(f"章节 {cid} 的 status 必须是 draft 或 ready")
        if require_ready and ch["status"] != "ready":
            raise HandoffError(f"章节尚未就绪：{cid}")
        path = local_file(root, ch.get("materials", ""))
        if path in materials_paths:
            raise HandoffError(f"章节重复引用同一材料文件：{cid}")
        materials_paths.add(path)
        read_text(root, ch["materials"], require_ready)
        assets = ch.get("assets", [])
        if not isinstance(assets, list):
            raise HandoffError(f"章节 {cid} 的 assets 应为列表")
        for asset in assets:
            if not isinstance(asset, dict):
                raise HandoffError(f"章节 {cid} 的 assets 元素应为对象")
            aid = asset.get("id", "")
            if not isinstance(aid, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", aid) or aid in asset_ids:
                raise HandoffError(f"图片 id 无效或重复：{aid!r}")
            asset_ids.add(aid)
            if asset.get("method") not in {"diagram-design", "imagegen", "provided", "static-svg"}:
                raise HandoffError(f"图片 {aid} 的 method 无效；必须记录真实制作方式")
            if asset.get("status") not in {"pending", "ready"}:
                raise HandoffError(f"图片 {aid} 的 status 必须是 pending 或 ready")
            if require_ready and asset["status"] != "ready":
                raise HandoffError(f"图片尚未实际生成并核验：{aid}")
            if not isinstance(asset.get("caption"), str) or not asset["caption"].strip():
                raise HandoffError(f"图片缺少题注：{aid}")
            refs = asset.get("evidence", [])
            if not isinstance(refs, list) or not all(isinstance(s, str) for s in refs):
                raise HandoffError(f"图片 {aid} 的 evidence 应是来源 id 列表")
            if require_ready and not refs:
                raise HandoffError(f"图片 {aid} 缺少依据（概念插画也要说明所解释的概念出处）")
            if set(refs) - available:
                raise HandoffError(f"图片 {aid} 引用了不存在的来源：{sorted(set(refs)-available)}")
            if require_ready or asset["status"] == "ready":
                p = local_file(root, asset.get("file", ""))
                if p.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
                    raise HandoffError(f"图片不是静态交付格式：{p.name}")
                if p.stat().st_size == 0:
                    raise HandoffError(f"图片是空文件：{p.name}")
                with p.open("rb") as image_file:
                    header = image_file.read(12)
                suffix = p.suffix.lower()
                valid_bitmap = (suffix == ".svg"
                    or suffix == ".png" and header.startswith(b"\x89PNG\r\n\x1a\n")
                    or suffix in {".jpg", ".jpeg"} and header.startswith(b"\xff\xd8\xff")
                    or suffix == ".webp" and header[:4] == b"RIFF" and header[8:12] == b"WEBP")
                if not valid_bitmap:
                    raise HandoffError(f"图片内容与扩展名不符：{p.name}")
                if p in asset_paths:
                    raise HandoffError(f"同一图片被重复登记，请复用同一 id：{aid}")
                asset_paths.add(p)
                if asset["method"] == "imagegen":
                    if p.suffix.lower() == ".svg":
                        raise HandoffError(f"imagegen 应记录实际位图，不可把 SVG 冒充生成图：{aid}")
                    read_text(root, asset.get("prompt", ""), require_ready)
                if asset["method"] == "diagram-design":
                    local_file(root, asset.get("editable", ""))
                for optional in ("editable", "prompt"):
                    if asset.get(optional):
                        local_file(root, asset[optional])
    evidence = obj.get("evidence_files", [])
    if not isinstance(evidence, list):
        raise HandoffError("evidence_files 应为包内相对路径列表")
    for value in evidence:
        local_file(root, value)
    return obj


def bundle_files(root: Path, obj: Dict[str, Any]) -> List[Path]:
    """Only explicitly registered research files travel; never zip an entire code checkout."""
    outline_rel = outline_field(obj)
    values = {"research.json", outline_rel, obj["sources"], obj["review"]}
    values.update(obj.get("evidence_files", []))
    for ch in obj["chapters"]:
        values.add(ch["materials"])
        for asset in ch.get("assets", []):
            for key in ("file", "editable", "prompt"):
                if asset.get(key):
                    values.add(asset[key])
    return sorted({local_file(root, v) for v in values}, key=lambda p: p.relative_to(root.resolve()).as_posix())


def start_here(obj: Dict[str, Any]) -> str:
    """Platform-neutral entry telling the next writer the 4 essential handoff facts."""
    outline_rel = outline_field(obj)
    rows = "\n".join(
        f'- **{c["id"]} · {c["title"]}**：材料 `{c["materials"]}` → 正文 `chapters/{c["id"]}/manuscript.md`'
        for c in obj["chapters"]
    )
    return f'''# 从这里开始：{obj["title"]}

本专题目录由研究与写作共用。研究阶段已完成备料并停止；**只有用户另行调用 `repo-to-write` 或明确委托写作时，才开始写作阶段。**

## 1. 读哪份大纲

先读 `{outline_rel}`（包含全书约定与逐章大纲，是唯一结构版本）以及 `research.json`（章节顺序与配图索引）。
章数、章序、各章小节分工和例子放置约定均以 `{outline_rel}` 为准，写作阶段不拆章、不合章、不重排。

## 2. 各章材料在哪

写每章时按需读取该章的 `materials.md`、所引来源与本章 `assets/` 配图，不要一次塞入全书材料：

{rows}

共同来源见 `{obj["sources"]}`，多章共用证据见 `evidence/`。`materials.md` 中标为“仅供作者核对”的源码路径、行号与具体 case 地址只供核对事实，不直接抄入读者正文或字段表。

## 3. 正文写到哪

直接在当前专题目录内逐章写入 `chapters/<id>/manuscript.md`，不另建 `-publication` 兄弟目录：

```bash
python <repo-to-write>/scripts/book.py prepare <本专题目录>
# 按 outline.md 和各章 materials.md 写完 chapters/*/manuscript.md，并更新 writing-review.md
python <repo-to-write>/scripts/book.py check <本专题目录>
python <repo-to-write>/scripts/book.py build <本专题目录>
# 只有明确需要 PDF 时：安装 requirements-pdf.txt 和 Chromium，再加 --format pdf
```

## 4. 研究核验与已知缺口

研究阶段的实际核验范围与已知缺口见 `{obj["review"]}`。写作中若发现影响核心结论的新缺口，记入 `writing-review.md` 与 `book.json` 的 `core_gaps`，不要用常识补造项目事实。
'''
