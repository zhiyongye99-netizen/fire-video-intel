import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Source:
    name: str
    type: str
    url: str
    channel_id: str = ""
    priority: str = "medium"
    language: str = "unknown"
    tags: List[str] = None
    link_keywords: List[str] = None
    exclude_keywords: List[str] = None
    max_items: str = "5"
    crawl_depth: str = "1"

    def __post_init__(self):
        if self.tags is None:
            object.__setattr__(self, "tags", [])
        if self.link_keywords is None:
            object.__setattr__(self, "link_keywords", [])
        if self.exclude_keywords is None:
            object.__setattr__(self, "exclude_keywords", [])


def _clean(value: str):
    value = value.strip().strip('"').strip("'")
    if value.startswith("[") and value.endswith("]"):
        parsed = ast.literal_eval(value)
        return list(parsed)
    return value


def load_sources(path: Path) -> List[Source]:
    sources = []
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line == "sources:":
            continue
        if line.startswith("- "):
            if current:
                sources.append(Source(**current))
            current = {}
            key, value = line[2:].split(":", 1)
            current[key.strip()] = _clean(value)
            continue
        if ":" in line and current is not None:
            key, value = line.split(":", 1)
            current[key.strip()] = _clean(value)
    if current:
        sources.append(Source(**current))
    return sources
