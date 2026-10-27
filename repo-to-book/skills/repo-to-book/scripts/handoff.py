"""The v1 portable research-directory contract. Standard library only.

This file is shipped identically in both skills so either can be installed alone.
Checks establish completeness of files/references, never factual correctness.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Set


class HandoffError(ValueError):
    """Invalid or unfinished portable research package."""


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
    """Load a research package; reject missing real assets and unresolved source IDs."""
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
    for key in ("plan", "sources", "review"):
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
            # Drafts may list planned assets; ready assets must already be files.
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
    """Only explicitly registered files travel; never zip an entire code checkout."""
    values = {"research.json", obj["plan"], obj["sources"], obj["review"]}
    values.update(obj.get("evidence_files", []))
    for ch in obj["chapters"]:
        values.add(ch["materials"])
        for asset in ch.get("assets", []):
            for key in ("file", "editable", "prompt"):
                if asset.get(key):
                    values.add(asset[key])
    return sorted({local_file(root, v) for v in values}, key=lambda p: p.relative_to(root.resolve()).as_posix())


def start_here(obj: Dict[str, Any]) -> str:
    """Platform-neutral entry: it is usable even without chat history or a skill loader."""
    rows = "\n".join(f'- **{c["id"]} · {c["title"]}**：`{c["materials"]}`' for c in obj["chapters"])
    return f'''# 从这里开始：{obj["title"]}

这是阶段一交接的研究素材，不是已写好的书。研究与绘图已经停止，
**只有用户另行调用 repo-to-book，或明确委托其他模型写作时，才开始阶段二。**

## 阅读顺序

先读 `research.json`（版本、章节顺序、图片实际路径），再读 `{obj["plan"]}`
（读者、主题主线与范围）、`{obj["review"]}`（实际核验与已知局限）。
写每章时只加载该章材料、所引来源与图片；不要一次塞入全部材料。

{rows}

共同来源见 `{obj["sources"]}`。`evidence_files` 登记的源码切片与资料摘要随包提供。
图片在各章 `assets/` 中；提示词、可编辑图稿和题注用于理解或修订，不能代替实际图片。

## 给任意写作模型的指令

使用 repo-to-book 的写作方法，将这些材料组织成一部有统一主线的图解技术书。
不要重新运行研究、联网查证或调用 Codex；不要依赖原聊天、临时工具 id 或原机器路径。
先设计各章的叙事与衔接，再逐章独立组织语言，不拼贴研究笔记。
图前交代问题，图后带读关键变化与设计取舍；使用包内静态图片和稳定来源编号。
区分源码事实、文档声明、运行观察、推断及未知。发现证据缺口时明确标出，
不能用常识补成项目事实；影响核心结论的缺口退回研究阶段，其余明示限制。

默认交付源稿目录（章节 Markdown + 实际图片 + 来源 + 编排配置）和离线 HTML。
PDF 仅在用户明确要求时另行生成。不要擅自把图片发往外部服务。

## 有终端的运行环境

将独立 `repo-to-book` 技能包放到任意目录（无需 Codex、模型 API 或研究技能）。
安装它的 `requirements.txt`，然后执行：

```bash
python <repo-to-book>/scripts/book.py prepare <本素材目录> <新的图书目录>
# 按材料写完 manuscript/ 下的各章，并填写 writing-review.md
python <repo-to-book>/scripts/book.py build <新的图书目录>
# 只有明确需要 PDF 时：安装 requirements-pdf.txt 和 Chromium，再用 --format pdf
```

## 仅聊天、没有文件执行工具的环境

上传本包与独立写作技能包；模型可以按章节交付 Markdown 与图片插入位置，
用户将文件保存进图书目录后运行同一出版命令。
没有文件读取能力时，按章提供 materials.md、引用的来源条目及图片附件。
没有执行过出版命令，不能声称已生成或验证 HTML/PDF。

本包只有普通 UTF-8 Markdown、JSON 与本地素材文件；不包含模型会话状态或账号凭据。
打包只证明文件齐备，不代表技术事实正确。给第三方模型前，请确认内部材料允许外传。
'''
