from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

from .models import Post


def find_markdown_files(base_dir: Path) -> Iterator[Path]:
    for ext in ("md", "mdx"):
        yield from base_dir.rglob(f"index.{ext}")


def strip_frontmatter(content: str) -> str:
    lines = content.splitlines()
    if not lines or not lines[0].startswith("---"):
        return content
    i = 1
    while i < len(lines) and not lines[i].startswith("---"):
        i += 1
    return "\n".join(lines[i + 1 :])


def read_posts(base_dir: str | Path = "posts") -> Iterator[Post]:
    base = Path(base_dir).resolve()

    for file_path in find_markdown_files(base):
        try:
            parts = file_path.relative_to(base).parts
            year, slug = parts[0], parts[1]
        except (ValueError, IndexError) as _:
            print(f"Skipping unexpected path: {file_path}", file=sys.stderr)
            continue
        try:
            raw = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Cannot read {file_path}: {exc}", file=sys.stderr)
            continue

        raw = strip_frontmatter(raw)
        yield Post(
            year=year,
            slug=slug,
            path=file_path,
            content=raw.strip() if raw else "",
        )
