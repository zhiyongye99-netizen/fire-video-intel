import re
from pathlib import Path

from fire_video_intel.models import VideoItem, utc_now_iso


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]+", "-", value).strip("-")
    return cleaned[:80] or "video"


def _review_label(status: str) -> str:
    if status in {"needs_review", "subtitle_found", "translated", "summarized"}:
        return "待人工复核"
    if status == "reviewed":
        return "已人工复核"
    if status == "needs_transcription":
        return "无字幕，待本机转写"
    return "自动归档"


def write_video_summary(base_dir: Path, item: VideoItem, transcript: str = "") -> Path:
    video_dir = base_dir / "videos" / _slug(item.video_id)
    video_dir.mkdir(parents=True, exist_ok=True)
    output = video_dir / "summary.zh.md"
    processed_at = item.processed_at or utc_now_iso()
    content = f"""# {item.title}

## 1. 基本信息
- 来源：{item.source}
- 原始链接：{item.url}
- 发布时间：{item.published_at}
- 语言：{item.language}
- 处理状态：{item.status}
- 复核状态：{_review_label(item.status)}
- 相关性评分：{item.relevance_score}/10

## 2. 证据链
- 视频 ID：{item.video_id}
- 字幕来源：{item.subtitle_source}
- 处理时间：{processed_at}

## 3. 原始字幕摘录

```text
{transcript.strip() or "无可用字幕，已进入待处理队列。"}
```

## 4. 消防业务提示
- 本文件为自动生成资料，不得直接作为训练教材或战术结论。
- 伤亡数字、事故原因、战术动作和装备结论必须由人工复核。
- 国外消防制度、编制、战术环境与中国消防救援队伍不同，必须结合本地实际判断。
"""
    output.write_text(content, encoding="utf-8")
    return output
