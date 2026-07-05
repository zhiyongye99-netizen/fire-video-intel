import hashlib
import html
import re
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

from fire_video_intel.config import Source
from fire_video_intel.models import VideoItem
from fire_video_intel.relevance import score_fire_relevance


@dataclass(frozen=True)
class ArticleLink:
    title: str
    url: str


def fetch_web_page(url: str, timeout: int = 20) -> str:
    last_error = None
    for _ in range(2):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 fire-video-intel/0.1"})
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception as exc:
            last_error = exc
    raise last_error


def parse_web_page(html_text: str, source: Source, url: str = "") -> tuple[VideoItem, str]:
    url = url or source.url
    title = _extract_title(html_text) or source.name
    description = _extract_meta_description(html_text)
    excerpt = description or title
    score = score_fire_relevance(title, description, source.tags)
    resource_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    item = VideoItem(
        video_id=f"web-{resource_id}",
        source=source.name,
        title=title,
        url=url,
        published_at="unknown",
        language=source.language,
        status="needs_review",
        relevance_score=score,
        subtitle_source="web_page",
    )
    return item, excerpt


def extract_article_links(html_text: str, source: Source, limit: int = 5) -> list[ArticleLink]:
    keywords = [value.lower() for value in (source.link_keywords or source.tags)]
    excludes = [value.lower() for value in source.exclude_keywords]
    source_host = urlparse(source.url).netloc
    links = []
    seen = set()
    for match in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html_text, re.IGNORECASE | re.DOTALL):
        raw_href = html.unescape(match.group(1)).strip()
        title = _clean(re.sub(r"<[^>]+>", " ", match.group(2)))
        if not raw_href or not title:
            continue
        if raw_href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        url = urldefrag(urljoin(source.url, raw_href))[0]
        parsed = urlparse(url)
        if parsed.netloc and parsed.netloc != source_host:
            continue
        if url == source.url or url in seen:
            continue
        if _is_navigation(title, url):
            continue
        haystack = f"{title} {url}".lower()
        if excludes and any(keyword in haystack for keyword in excludes):
            continue
        if keywords and not any(keyword.lower() in haystack for keyword in keywords):
            continue
        seen.add(url)
        links.append(ArticleLink(title=title, url=url))
        if len(links) >= limit:
            break
    return links


def _is_navigation(title: str, url: str) -> bool:
    title_lower = title.lower()
    if title_lower in {"skip to content", "skip to main content", "search", "view all", "about", "resources", "home"}:
        return True
    if url.endswith(("#", "/")) and len(title) < 12:
        return True
    return False


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
