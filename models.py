from pathlib import Path
from typing import NamedTuple


class Post(NamedTuple):
    year: str
    slug: str
    path: Path
    content: str
