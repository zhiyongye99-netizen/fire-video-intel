from dataclasses import dataclass

from fire_video_intel.models import VideoItem


@dataclass(frozen=True)
class SubtitleResult:
    found: bool
    text: str
    source: str


def apply_subtitle_status(item: VideoItem, result: SubtitleResult) -> VideoItem:
    if result.found:
        return item.with_status("subtitle_found", result.source)
    return item.with_status("needs_transcription", "none")


def fetch_youtube_subtitle(video_id: str, languages=None) -> SubtitleResult:
    languages = languages or ["en", "zh-Hans", "zh-CN"]
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return SubtitleResult(found=False, text="", source="dependency_missing")

    try:
        rows = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except Exception:
        return SubtitleResult(found=False, text="", source="none")
    text = "\n".join(row.get("text", "") for row in rows if row.get("text"))
    return SubtitleResult(found=bool(text.strip()), text=text, source="youtube_transcript_api")
