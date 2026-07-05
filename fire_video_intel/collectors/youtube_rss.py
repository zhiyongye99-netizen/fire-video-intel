import re
from collections import Counter
from typing import Iterable, List
from urllib.request import urlopen
from xml.etree import ElementTree

from fire_video_intel.models import VideoItem
from fire_video_intel.relevance import score_fire_relevance


ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"
MEDIA = "{http://search.yahoo.com/mrss/}"


def youtube_rss_url(channel_id: str) -> str:
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def fetch_youtube_rss(channel_id: str, timeout: int = 20) -> str:
    with urlopen(youtube_rss_url(channel_id), timeout=timeout) as response:
        return response.read().decode("utf-8")


def resolve_channel_id(channel_url: str, timeout: int = 20) -> str:
    with urlopen(channel_url, timeout=timeout) as response:
        page = response.read().decode("utf-8", errors="ignore")
    match = re.search(r"https://www\.youtube\.com/channel/(UC[0-9A-Za-z_-]{22})", page)
    if match:
        return match.group(1)
    match = re.search(r'"channelId":"(UC[^"]+)"', page)
    if match and len(match.group(1)) == 24:
        return match.group(1)
    match = re.search(r'<meta itemprop="channelId" content="(UC[^"]+)">', page)
    if match and len(match.group(1)) == 24:
        return match.group(1)
    candidates = re.findall(r"UC[0-9A-Za-z_-]{22}", page)
    if candidates:
        return Counter(candidates).most_common(1)[0][0]
    return ""


def parse_youtube_rss(xml_text: str, source_name: str, language: str, tags: Iterable[str]) -> List[VideoItem]:
    root = ElementTree.fromstring(xml_text)
    items = []
    for entry in root.findall(f"{ATOM}entry"):
        video_id = _text(entry, f"{YT}videoId")
        title = _text(entry, f"{ATOM}title")
        published = _text(entry, f"{ATOM}published")
        description = _text(entry, f"{MEDIA}group/{MEDIA}description")
        link = ""
        link_node = entry.find(f"{ATOM}link")
        if link_node is not None:
            link = link_node.attrib.get("href", "")
        if not link and video_id:
            link = f"https://www.youtube.com/watch?v={video_id}"
        score = score_fire_relevance(title, description, tags)
        items.append(
            VideoItem(
                video_id=video_id,
                source=source_name,
                title=title,
                url=link,
                published_at=published,
                language=language,
                status="discovered",
                relevance_score=score,
            )
        )
    return items


def _text(node: ElementTree.Element, path: str) -> str:
    found = node.find(path)
    if found is None or found.text is None:
        return ""
    return found.text.strip()
