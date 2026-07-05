import tempfile
import unittest
from pathlib import Path

from fire_video_intel.collectors.youtube_rss import parse_youtube_rss
from fire_video_intel.config import load_sources
from fire_video_intel.processors.subtitle_fetcher import SubtitleResult, apply_subtitle_status


class CollectorTest(unittest.TestCase):
    def test_loads_sources_yaml_without_external_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            source_file = Path(tmp) / "sources.yaml"
            source_file.write_text(
                """
sources:
  - name: UL FSRI YouTube
    type: youtube_channel
    url: "https://www.youtube.com/@ULFSRI"
    channel_id: "UC_Test"
    priority: high
    language: en
    tags: ["火灾动力学", "内攻安全"]
""".strip(),
                encoding="utf-8",
            )

            sources = load_sources(source_file)

            self.assertEqual(len(sources), 1)
            self.assertEqual(sources[0].name, "UL FSRI YouTube")
            self.assertEqual(sources[0].channel_id, "UC_Test")
            self.assertEqual(sources[0].tags, ["火灾动力学", "内攻安全"])

    def test_parse_youtube_rss_items(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>abc123</yt:videoId>
    <title>Flashover and flow path training</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=abc123"/>
    <published>2026-07-05T00:00:00+00:00</published>
    <media:group xmlns:media="http://search.yahoo.com/mrss/">
      <media:description>Fireground ventilation training.</media:description>
    </media:group>
  </entry>
</feed>
"""

        items = parse_youtube_rss(xml, source_name="UL FSRI", language="en", tags=["训练"])

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].video_id, "abc123")
        self.assertEqual(items[0].status, "discovered")
        self.assertGreaterEqual(items[0].relevance_score, 2)

    def test_missing_subtitle_marks_item_for_local_transcription(self):
        item = parse_youtube_rss(
            """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry><yt:videoId>abc123</yt:videoId><title>Firefighter mayday</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=abc123"/>
  <published>2026-07-05T00:00:00+00:00</published></entry>
</feed>""",
            source_name="UL FSRI",
            language="en",
            tags=[],
        )[0]

        updated = apply_subtitle_status(item, SubtitleResult(found=False, text="", source="none"))

        self.assertEqual(updated.status, "needs_transcription")
        self.assertEqual(updated.subtitle_source, "none")


if __name__ == "__main__":
    unittest.main()
