import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fire_video_intel.config import load_sources
from fire_video_intel.source_check import check_source, render_source_checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check configured firefighting intelligence sources.")
    parser.add_argument("--sources", type=Path, default=Path("sources.yaml"))
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("knowledge_base/source-check.md"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    sources = load_sources(args.sources)
    checks = [check_source(source, timeout=args.timeout) for source in sources]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_source_checks(checks), encoding="utf-8")
    failed = [check for check in checks if not check.ok]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
