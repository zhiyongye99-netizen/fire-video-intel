import unittest

from fire_video_intel.collectors.web_page import extract_article_links, parse_web_page
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

    def test_extract_article_links_filters_navigation_and_keeps_reports(self):
        source = Source(
            name="NIOSH Fire Fighter Fatality Investigation",
            type="web",
            url="https://www.cdc.gov/niosh/fire/",
            priority="high",
            language="en",
            tags=["事故调查"],
            link_keywords=["fffipp", "report", "fatality"],
        )
        html = """
<a href="#content">Skip to content</a>
<a href="/niosh/firefighters/fffipp/face2024-01.html">Career Firefighter Dies During Search Operations</a>
<a href="/niosh/firefighters/ppe/index.html">Personal Protective Equipment</a>
<a href="/niosh/firefighters/fffipp/slides.html">FFFIPP Reports and Slides</a>
"""

        links = extract_article_links(html, source, limit=3)

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].title, "Career Firefighter Dies During Search Operations")
        self.assertEqual(
            links[0].url,
            "https://www.cdc.gov/niosh/firefighters/fffipp/face2024-01.html",
        )


if __name__ == "__main__":
    unittest.main()
