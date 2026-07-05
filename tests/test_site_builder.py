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
            self.assertIn("UL FSRI", html)
            self.assertIn("不调用付费 API", html)
            self.assertNotIn("|---|---|", html)


if __name__ == "__main__":
    unittest.main()
