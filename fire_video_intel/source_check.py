from dataclasses import dataclass
from typing import Callable
from urllib.request import Request, urlopen

from fire_video_intel.collectors.youtube_rss import resolve_channel_id
from fire_video_intel.config import Source


@dataclass(frozen=True)
class SourceCheck:
    name: str
    source_type: str
    url: str
    ok: bool
    detail: str


def default_web_probe(url: str, timeout: int) -> int:
    request = Request(url, headers={"User-Agent": "fire-video-intel/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.status


def check_source(
    source: Source,
    timeout: int = 15,
    web_probe: Callable[[str, int], int] = default_web_probe,
    channel_resolver: Callable[[str, int], str] = resolve_channel_id,
) -> SourceCheck:
    try:
        if source.type == "youtube_channel":
            channel_id = source.channel_id or channel_resolver(source.url, timeout)
            if not channel_id:
                return SourceCheck(source.name, source.type, source.url, False, "channel_id_not_found")
            return SourceCheck(source.name, source.type, source.url, True, f"channel_id={channel_id}")

        status = web_probe(source.url, timeout)
        ok = 200 <= status < 400
        return SourceCheck(source.name, source.type, source.url, ok, f"HTTP {status}")
    except Exception as exc:
        return SourceCheck(source.name, source.type, source.url, False, f"{exc.__class__.__name__}: {exc}")


def render_source_checks(checks: list[SourceCheck]) -> str:
    lines = [
        "# 信息源体检报告",
        "",
        "| 信息源 | 类型 | 状态 | 详情 | URL |",
        "|---|---|---|---|---|",
    ]
    for check in checks:
        state = "OK" if check.ok else "FAIL"
        lines.append(f"| {check.name} | {check.source_type} | {state} | {check.detail} | {check.url} |")
    return "\n".join(lines) + "\n"
