import hashlib
import html
import re
from urllib.request import Request, urlopen

from fire_video_intel.config import Source
from fire_video_intel.models import VideoItem
from fire_video_intel.relevance import score_fire_relevance


def fetch_web_page(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "fire-video-intel/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_web_page(html_text: str, source: Source) -> tuple[VideoItem, str]:
    title = _extract_title(html_text) or source.name
    description = _extract_meta_description(html_text)
    excerpt = description or title
    score = score_fire_relevance(title, description, source.tags)
    resource_id = hashlib.sha1(source.url.encode("utf-8")).hexdigest()[:12]
    item = VideoItem(
        video_id=f"web-{resource_id}",
        source=source.name,
        title=title,
        url=source.url,
        published_at="unknown",
        language=source.language,
        status="needs_review",
        relevance_score=score,
        subtitle_source="web_page",
    )
    return item, excerpt


def _extract_title(html_text: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return _clean(match.group(1))


def _extract_meta_description(html_text: str) -> str:
    patterns = [
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_text, re.IGNORECASE | re.DOTALL)
        if match:
            return _clean(match.group(1))
    return ""


def _clean(value: str) -> str:
    value = re.sub(r"\s+", " ", value)
    return html.unescape(value).strip()
