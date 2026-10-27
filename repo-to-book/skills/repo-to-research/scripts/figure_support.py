"""Static diagram support; no writing or publishing logic."""
from __future__ import annotations
import math, os, re, shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import unquote
import xml.etree.ElementTree as ET

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


