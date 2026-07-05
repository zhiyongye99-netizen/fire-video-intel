# 免费消防资料自动收集站 - Dry Run

## 已加载信息源
- UL FSRI YouTube（youtube_channel，优先级：high）
- NIST Fire Research（web，优先级：high）
- NIOSH Fire Fighter Fatality Investigation（web，优先级：high）
- U.S. Fire Administration（web，优先级：high）
- NFPA News（web，优先级：high）
- Fire Engineering（web，优先级：medium）

## 运行说明
- Dry run 不访问网络，不下载视频，不调用付费 API。
- 正式 daily 模式只抓取公开 RSS 元数据和可用字幕。
- 无字幕视频只进入 needs_transcription 队列，等待本机免费工具处理。
