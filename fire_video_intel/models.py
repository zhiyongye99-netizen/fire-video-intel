from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class VideoItem:
    video_id: str
    source: str
    title: str
    url: str
    published_at: str
    language: str = "unknown"
    duration_seconds: Optional[int] = None
    status: str = "discovered"
    relevance_score: int = 0
    subtitle_source: str = "none"
    processed_at: str = ""

    def with_status(self, status: str, subtitle_source: Optional[str] = None) -> "VideoItem":
        return VideoItem(
            video_id=self.video_id,
            source=self.source,
            title=self.title,
            url=self.url,
            published_at=self.published_at,
            language=self.language,
            duration_seconds=self.duration_seconds,
            status=status,
            relevance_score=self.relevance_score,
            subtitle_source=subtitle_source if subtitle_source is not None else self.subtitle_source,
            processed_at=utc_now_iso(),
        )

