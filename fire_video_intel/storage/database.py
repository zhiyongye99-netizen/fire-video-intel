import sqlite3
from pathlib import Path

from fire_video_intel.models import VideoItem, utc_now_iso


class IntelDatabase:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists videos (
                    video_id text primary key,
                    source text not null,
                    title text not null,
                    url text not null,
                    published_at text not null,
                    language text not null,
                    duration_seconds integer,
                    status text not null,
                    relevance_score integer not null,
                    subtitle_source text not null,
                    processed_at text not null,
                    created_at text not null
                )
                """
            )

    def upsert_video(self, item: VideoItem) -> bool:
        now = utc_now_iso()
        processed_at = item.processed_at or now
        with self._connect() as conn:
            existing = conn.execute(
                "select video_id from videos where video_id = ?",
                (item.video_id,),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    update videos
                    set status = ?, relevance_score = ?, subtitle_source = ?, processed_at = ?
                    where video_id = ?
                    """,
                    (item.status, item.relevance_score, item.subtitle_source, processed_at, item.video_id),
                )
                return False
            conn.execute(
                """
                insert into videos (
                    video_id, source, title, url, published_at, language,
                    duration_seconds, status, relevance_score, subtitle_source,
                    processed_at, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.video_id,
                    item.source,
                    item.title,
                    item.url,
                    item.published_at,
                    item.language,
                    item.duration_seconds,
                    item.status,
                    item.relevance_score,
                    item.subtitle_source,
                    processed_at,
                    now,
                ),
            )
            return True

