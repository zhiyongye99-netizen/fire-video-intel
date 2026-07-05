import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fire_video_intel.site_builder import build_site


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the static GitHub Pages site.")
    parser.add_argument("--knowledge-base", type=Path, default=Path("knowledge_base"))
    parser.add_argument("--site-dir", type=Path, default=Path("_site"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output = build_site(args.knowledge_base, args.site_dir)
    print(f"Built {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
