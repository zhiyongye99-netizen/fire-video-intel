import argparse
from pathlib import Path

from fire_video_intel.collectors.youtube_rss import fetch_youtube_rss, parse_youtube_rss, resolve_channel_id
from fire_video_intel.config import load_sources
from fire_video_intel.processors.subtitle_fetcher import apply_subtitle_status, fetch_youtube_subtitle
from fire_video_intel.storage.database import IntelDatabase
from fire_video_intel.storage.markdown_writer import write_video_summary


def run_dry_run(sources_path: Path, output_dir: Path) -> int:
    sources = load_sources(sources_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    daily_dir = output_dir / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 免费消防资料自动收集站 - Dry Run",
        "",
        "## 已加载信息源",
    ]
    for source in sources:
        lines.append(f"- {source.name}（{source.type}，优先级：{source.priority}）")
    lines.extend(
        [
            "",
            "## 运行说明",
            "- Dry run 不访问网络，不下载视频，不调用付费 API。",
            "- 正式 daily 模式只抓取公开 RSS 元数据和可用字幕。",
            "- 无字幕视频只进入 needs_transcription 队列，等待本机免费工具处理。",
        ]
    )
    (daily_dir / "dry-run.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def run_daily(sources_path: Path, output_dir: Path, database_path: Path) -> int:
    sources = load_sources(sources_path)
    db = IntelDatabase(database_path)
    processed = 0
    for source in sources:
        if source.type != "youtube_channel":
            continue
        channel_id = source.channel_id or resolve_channel_id(source.url)
        if not channel_id:
            continue
        xml_text = fetch_youtube_rss(channel_id)
        for item in parse_youtube_rss(xml_text, source.name, source.language, source.tags):
            subtitle = fetch_youtube_subtitle(item.video_id, [source.language, "en", "zh-Hans"])
            updated = apply_subtitle_status(item, subtitle)
            is_new = db.upsert_video(updated)
            if is_new:
                write_video_summary(output_dir, updated, subtitle.text)
                processed += 1
    write_daily_queue(output_dir, processed)
    return 0


def write_daily_queue(output_dir: Path, processed: int) -> None:
    daily_dir = output_dir / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    (daily_dir / "latest.md").write_text(
        "\n".join(
            [
                "# 消防专业资料自动收集日报",
                "",
                f"- 本次新增：{processed} 条",
                "- 费用策略：不调用付费 API，不下载完整视频。",
                "- 无字幕资料：进入 needs_transcription 队列，等待本机开源转写。",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Free-first firefighting video intelligence collector.")
    parser.add_argument("--mode", choices=["dry-run", "daily"], default="dry-run")
    parser.add_argument("--sources", type=Path, default=Path("sources.yaml"))
    parser.add_argument("--output", type=Path, default=Path("knowledge_base"))
    parser.add_argument("--database", type=Path, default=Path("data/intel.sqlite"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.mode == "dry-run":
        return run_dry_run(args.sources, args.output)
    return run_daily(args.sources, args.output, args.database)


if __name__ == "__main__":
    raise SystemExit(main())
