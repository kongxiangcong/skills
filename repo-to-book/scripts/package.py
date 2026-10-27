#!/usr/bin/env python3
"""Build source archives using the reviewed, exact release-files.txt allowlist.

New source files are not released until explicitly added to that list. No globs,
recursive directory inclusion, or symlinks are accepted. Research handoff exports
use their separate registered-file contract.
"""
from __future__ import annotations
import argparse
from pathlib import Path, PurePosixPath
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).absolute().parents[1]


def release_files(root: Path) -> list[Path]:
    """Validate the complete allowlist before reading any release payload."""
    manifest = root / 'release-files.txt'
    if manifest.is_symlink():
        raise ValueError('发布清单不能是符号链接')
    names = [line.strip() for line in manifest.read_text(encoding='utf-8').splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    seen = set()
    files = []
    for name in names:
        rel = PurePosixPath(name)
        if (rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name
                or rel.as_posix() != name or any(c in name for c in '*?[]')):
            raise ValueError('发布清单必须使用无通配符的相对文件路径：' + name)
        if name in seen:
            raise ValueError('发布清单路径重复：' + name)
        seen.add(name)
        path = root
        for part in rel.parts:
            path = path / part
            if path.is_symlink():
                raise ValueError('发布文件或父目录不能是符号链接：' + name)
        if not path.is_file():
            raise ValueError('发布文件缺失或不是普通文件：' + name)
        files.append(path)
    if not files:
        raise ValueError('发布清单为空')
    return files


def archive(source: Path, out: Path, prefix: str) -> int:
    source = source.absolute()
    source.relative_to(ROOT)  # only project root or its subdirectories
    if not prefix or '/' in prefix or '\\' in prefix or prefix in {'.', '..'}:
        raise ValueError('无效归档前缀')
    # Validate all paths first; only explicitly listed files in this subtree ship.
    files = [p for p in release_files(ROOT) if p.is_relative_to(source)]
    if not files:
        raise ValueError('发布清单没有该目录的文件：' + str(source))
    if out.exists():
        raise ValueError(f'输出已存在，未覆盖：{out}')
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, 'x', ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, prefix + '/' + p.relative_to(source).as_posix())
    return len(files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        print('错误：输出目录应在项目源码之外，避免自包含归档', file=sys.stderr)
        return 2
    try:
        for source, name, prefix in [
            (ROOT, 'repo-to-book-project.zip', 'repo-to-book'),
            (ROOT/'skills/repo-to-research', 'repo-to-research-skill.zip', 'repo-to-research'),
            (ROOT/'skills/repo-to-write', 'repo-to-write-skill.zip', 'repo-to-write')]:
            count = archive(source, out/name, prefix)
            print(f'{name}: {count} files')
        return 0
    except (OSError, ValueError) as exc:
        print(f'错误：{exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
