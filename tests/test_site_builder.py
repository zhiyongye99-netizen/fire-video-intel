import tempfile
import unittest
from pathlib import Path

from fire_video_intel.site_builder import build_site


class SiteBuilderTest(unittest.TestCase):
    def test_builds_index_with_daily_status_and_source_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "knowledge_base"
            site = root / "_site"
            (kb / "daily").mkdir(parents=True)
            (kb / "daily" / "latest.md").write_text(
                "# 消防专业资料自动收集日报\n\n- 本次新增：0 条\n",
                encoding="utf-8",
            )
            (kb / "source-check.md").write_text(
                "# 信息源体检报告\n\n| 信息源 | 类型 | 状态 |\n|---|---|---|\n| UL FSRI | youtube_channel | OK |\n",
                encoding="utf-8",
            )

            output = build_site(kb, site)

            html = output.read_text(encoding="utf-8")
            self.assertIn("消防资料自动收件箱", html)
            self.assertIn("本次新增：0 条", html)
            self.assertIn("累计入库：0 条", html)
            self.assertIn("UL FSRI", html)
            self.assertIn("不调用付费 API", html)
            self.assertNotIn("|---|---|", html)

    def test_builds_video_summary_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = root / "knowledge_base"
            site = root / "_site"
            summary = kb / "videos" / "web-demo" / "summary.zh.md"
            summary.parent.mkdir(parents=True)
            summary.write_text(
                "# Fire Research\n\n## 1. 基本信息\n- 来源：NIST\n\n```text\nfire dynamics\n```\n",
                encoding="utf-8",
            )

            build_site(kb, site)

            index = (site / "index.html").read_text(encoding="utf-8")
            self.assertIn("videos/web-demo/summary.html", index)
            self.assertIn("累计入库：1 条", index)
            summary_html = (site / "videos" / "web-demo" / "summary.html").read_text(encoding="utf-8")
            self.assertIn("<pre><code>fire dynamics</code></pre>", summary_html)
            self.assertNotIn("```text", summary_html)


if __name__ == "__main__":
    unittest.main()
