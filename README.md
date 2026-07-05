# Free Fire Video Intel

这是一个“零新增费用优先”的消防专业视频资料自动收集项目。

它的第一版目标不是全自动 AI 情报系统，而是先建立稳定的“消防资料自动收件箱”：

```text
公开信息源
  -> GitHub Actions 免费定时运行
  -> 抓取 RSS / 元数据 / 可用字幕
  -> SQLite 去重
  -> Markdown 归档
  -> 无字幕内容进入 needs_transcription 队列
  -> 本机 Codex + 免费开源工具再做翻译、摘要、转写
```

## 为什么这样设计

消防资料处理像灭火救援中的分段作战：先建立水源和主干线，再铺设支线。第一版只做免费、稳定、可审计的主流程，不直接下载视频、不调用付费 API、不把 AI 结果当成训练教材。

## 免费优先边界

- 不使用 OpenAI API。
- 不使用 OpenAI Audio API。
- 不下载完整视频。
- 不在 GitHub Actions 里跑大型本地模型。
- 有字幕就归档字幕。
- 无字幕就标记 `needs_transcription`，等待本机 `whisper.cpp`、`faster-whisper` 或其他免费工具处理。

## 本地运行

```bash
python3 -m unittest discover -s tests
python3 -m fire_video_intel.main --mode dry-run --sources sources.yaml --output knowledge_base
```

检查信息源：

```bash
python3 scripts/check_sources.py --sources sources.yaml --timeout 20 --output knowledge_base/source-check.md
```

正式采集：

```bash
python3 -m fire_video_intel.main --mode daily --sources sources.yaml --output knowledge_base --database data/intel.sqlite
```

## GitHub Actions

`.github/workflows/daily_free_fire_video_intel.yml` 每天 UTC 23:00 运行一次，对应北京时间 07:00。

如果使用公开仓库，标准 GitHub-hosted runner 通常不计费。若使用私有仓库，需要注意 GitHub Free 的 Actions 免费分钟额度。

## 目录结构

```text
fire_video_intel/
  collectors/          # RSS 等免费采集器
  processors/          # 字幕状态处理
  storage/             # SQLite 和 Markdown 输出
  main.py              # CLI 入口
sources.yaml           # 信息源
fire_terms.yaml        # 消防术语
.agents/skills/        # Codex 消防工作流规则
knowledge_base/        # 自动生成资料
data/                  # SQLite 数据库
```

## 后续免费增强路径

1. 本机安装 Ollama，用开源模型做摘要和翻译。
2. 本机安装 `whisper.cpp` 或 `faster-whisper`，只处理 A/B 级高价值无字幕视频。
3. 使用 GitHub Pages 展示 `knowledge_base`。
4. 使用本地 filesystem/git/fetch MCP 辅助 Codex 维护仓库。
5. 高价值资料进入人工复核后，再沉淀为训练、授课或研究材料。
