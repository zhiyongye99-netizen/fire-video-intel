import html
import re
from pathlib import Path


def _read(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8")


def _markdown_to_html(markdown: str) -> str:
    lines = []
    in_table = False
    in_code = False
    code_lines = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if line.startswith("```"):
            if in_code:
                escaped = html.escape("\n".join(code_lines).strip())
                lines.append(f"<pre><code>{escaped}</code></pre>")
                code_lines = []
                in_code = False
            else:
                if in_table:
                    lines.append("</tbody></table>")
                    in_table = False
                in_code = True
            continue
        if in_code:
            code_lines.append(raw)
            continue
        if not line:
            if in_table:
                lines.append("</tbody></table>")
                in_table = False
            continue
        if line.startswith("# "):
            if in_table:
                lines.append("</tbody></table>")
                in_table = False
            lines.append(f"<h2>{html.escape(line[2:])}</h2>")
        elif line.startswith("## "):
            if in_table:
                lines.append("</tbody></table>")
                in_table = False
            lines.append(f"<h3>{html.escape(line[3:])}</h3>")
        elif line.startswith("- "):
            if in_table:
                lines.append("</tbody></table>")
                in_table = False
            lines.append(f"<p class=\"bullet\">{html.escape(line[2:])}</p>")
        elif line.startswith("|") and re.fullmatch(r"[\|\-\s:]+", line):
            continue
        elif line.startswith("|"):
            cells = [html.escape(cell.strip()) for cell in line.strip("|").split("|")]
            if not in_table:
                lines.append("<table><tbody>")
                in_table = True
            tag = "th" if all(cell in {"信息源", "类型", "状态", "详情", "URL"} for cell in cells[:1]) else "td"
            lines.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
        else:
            if in_table:
                lines.append("</tbody></table>")
                in_table = False
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_table:
        lines.append("</tbody></table>")
    if in_code:
        escaped = html.escape("\n".join(code_lines).strip())
        lines.append(f"<pre><code>{escaped}</code></pre>")
    return "\n".join(lines)


def _collect_video_links(knowledge_base: Path, site_dir: Path) -> list[tuple[str, str]]:
    videos = []
    for path in sorted((knowledge_base / "videos").glob("*/summary.zh.md")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = match.group(1) if match else path.parent.name
        rel = f"videos/{path.parent.name}/summary.html"
        output = site_dir / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_wrap_page(title, _markdown_to_html(text)), encoding="utf-8")
        videos.append((title, rel))
    return videos


def build_site(knowledge_base: Path, site_dir: Path) -> Path:
    site_dir.mkdir(parents=True, exist_ok=True)
    daily = _read(knowledge_base / "daily" / "latest.md", "# 消防专业资料自动收集日报\n\n- 本次新增：0 条\n")
    source_check = _read(knowledge_base / "source-check.md", "# 信息源体检报告\n\n- 尚未生成体检报告\n")
    video_links = _collect_video_links(knowledge_base, site_dir)
    total_count = len(video_links)
    videos_html = "\n".join(
        f"<li><a href=\"{html.escape(href)}\">{html.escape(title)}</a></li>" for title, href in video_links
    ) or "<li>暂无入库视频摘要。低相关视频会被过滤，不进入资料库。</li>"
    page = _wrap_page(
        "消防资料自动收件箱",
        f"""
  <header>
    <h1>消防资料自动收件箱</h1>
    <p>免费优先：不调用付费 API，不下载完整视频，只做公开资料收集、去重和待处理排队。</p>
  </header>
  <main>
    <section>
      {_markdown_to_html(daily)}
    </section>
    <section>
      <h2>入库资料摘要</h2>
      <p class="bullet">累计入库：{total_count} 条</p>
      <ul>{videos_html}</ul>
    </section>
    <section>
      {_markdown_to_html(source_check)}
    </section>
  </main>
""",
    )
    output = site_dir / "index.html"
    output.write_text(page, encoding="utf-8")
    return output


def _wrap_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f9;
      color: #1f2933;
    }}
    body {{ margin: 0; }}
    header {{
      background: #8f1d1d;
      color: white;
      padding: 28px max(24px, calc((100vw - 1080px) / 2));
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      gap: 18px;
    }}
    section {{
      background: white;
      border: 1px solid #d7dde5;
      border-radius: 8px;
      padding: 18px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    h2 {{ margin-top: 0; }}
    .bullet {{ margin: 8px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border: 1px solid #d7dde5; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f3f5; }}
    a {{ color: #8f1d1d; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""
