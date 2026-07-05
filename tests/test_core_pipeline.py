import sqlite3
import tempfile
import unittest
from pathlib import Path

from fire_video_intel.models import VideoItem
from fire_video_intel.relevance import is_fire_related, score_fire_relevance
from fire_video_intel.storage.database import IntelDatabase
from fire_video_intel.storage.markdown_writer import write_video_summary


class CorePipelineTest(unittest.TestCase):
    def test_scores_firefighting_content_higher_than_unrelated_content(self):
        fire_score = score_fire_relevance(
            title="UL FSRI ventilation and flashover training for firefighters",
            description="Structure fire, flow path, incident command, SCBA safety.",
            tags=["火灾动力学", "内攻安全"],
        )
        unrelated_score = score_fire_relevance(
            title="Cooking travel vlog",
            description="A weekend city food tour.",
            tags=["旅游"],
        )

        self.assertGreaterEqual(fire_score, 6)
        self.assertEqual(unrelated_score, 0)
        self.assertTrue(is_fire_related("high-rise fire command", "", []))
        self.assertFalse(is_fire_related("music festival highlights", "", []))

    def test_database_deduplicates_by_video_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = IntelDatabase(Path(tmp) / "intel.sqlite")
            item = VideoItem(
                video_id="abc123",
                source="UL FSRI",
                title="Flashover training",
                url="https://www.youtube.com/watch?v=abc123",
                published_at="2026-07-05T00:00:00Z",
                language="en",
                status="discovered",
                relevance_score=8,
            )

            self.assertTrue(db.upsert_video(item))
            self.assertFalse(db.upsert_video(item))

            with sqlite3.connect(Path(tmp) / "intel.sqlite") as conn:
                count = conn.execute("select count(*) from videos").fetchone()[0]
            self.assertEqual(count, 1)

    def test_markdown_summary_preserves_evidence_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = VideoItem(
                video_id="abc123",
                source="UL FSRI",
                title="Flashover training",
                url="https://www.youtube.com/watch?v=abc123",
                published_at="2026-07-05T00:00:00Z",
                language="en",
                status="needs_review",
                relevance_score=9,
                subtitle_source="youtube_auto_caption",
            )

            output = write_video_summary(Path(tmp), item, transcript="Flashover changes fireground risk.")

            text = output.read_text(encoding="utf-8")
            self.assertIn("# Flashover training", text)
            self.assertIn("原始链接", text)
            self.assertIn("https://www.youtube.com/watch?v=abc123", text)
            self.assertIn("字幕来源", text)
            self.assertIn("待人工复核", text)


if __name__ == "__main__":
    unittest.main()
