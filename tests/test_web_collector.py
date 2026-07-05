import unittest

from fire_video_intel.collectors.web_page import parse_web_page
from fire_video_intel.config import Source


class WebCollectorTest(unittest.TestCase):
    def test_parse_web_page_uses_title_and_meta_description(self):
        source = Source(
            name="NIST Fire Research",
            type="web",
            url="https://www.nist.gov/fire",
            priority="high",
            language="en",
            tags=["火灾实验", "建筑火灾"],
        )
        html = """
<!doctype html>
<html>
<head>
  <title>Fire Research Division | NIST</title>
  <meta name="description" content="Research on fire dynamics, structures, smoke and wildland urban interface fires.">
</head>
<body></body>
</html>
"""

        item, excerpt = parse_web_page(html, source)

        self.assertEqual(item.source, "NIST Fire Research")
        self.assertEqual(item.title, "Fire Research Division | NIST")
        self.assertEqual(item.status, "needs_review")
        self.assertGreaterEqual(item.relevance_score, 2)
        self.assertIn("fire dynamics", excerpt)


if __name__ == "__main__":
    unittest.main()
