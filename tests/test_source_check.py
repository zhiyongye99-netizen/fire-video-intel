import unittest

from fire_video_intel.config import Source
from fire_video_intel.source_check import SourceCheck, check_source


class SourceCheckTest(unittest.TestCase):
    def test_checks_web_source_with_injected_probe(self):
        source = Source(
            name="NIST Fire Research",
            type="web",
            url="https://www.nist.gov/fire",
            priority="high",
            language="en",
            tags=["火灾实验"],
        )

        result = check_source(source, web_probe=lambda url, timeout: 200)

        self.assertEqual(
            result,
            SourceCheck(
                name="NIST Fire Research",
                source_type="web",
                url="https://www.nist.gov/fire",
                ok=True,
                detail="HTTP 200",
            ),
        )

    def test_checks_youtube_source_by_resolving_channel_id(self):
        source = Source(
            name="UL FSRI YouTube",
            type="youtube_channel",
            url="https://www.youtube.com/@ULFSRI",
            priority="high",
            language="en",
            tags=["轰燃"],
        )

        result = check_source(
            source,
            web_probe=lambda url, timeout: 200,
            channel_resolver=lambda url, timeout: "UC123",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.detail, "channel_id=UC123")

    def test_marks_youtube_source_unhealthy_when_channel_id_missing(self):
        source = Source(
            name="Unknown YouTube",
            type="youtube_channel",
            url="https://www.youtube.com/@unknown",
            priority="medium",
            language="en",
            tags=[],
        )

        result = check_source(
            source,
            web_probe=lambda url, timeout: 200,
            channel_resolver=lambda url, timeout: "",
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.detail, "channel_id_not_found")


if __name__ == "__main__":
    unittest.main()
