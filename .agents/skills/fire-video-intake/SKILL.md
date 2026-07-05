---
name: fire-video-intake
description: Use this skill when collecting, filtering, deduplicating, or triaging firefighting-related videos, channels, RSS feeds, or web pages without paid services.
---

# Fire Video Intake Skill

You maintain a zero-new-cost firefighting video intelligence pipeline.

## Main Rules
1. Prefer official, high-authority sources: UL FSRI, NIST, NFPA, USFA, NIOSH, IAFF, and government fire agencies.
2. Do not download full videos in the default workflow.
3. Prefer YouTube RSS and available subtitles.
4. If no subtitle exists, mark `needs_transcription`; do not call paid transcription APIs.
5. Preserve evidence: source, URL, published time, fetched time, subtitle source, status, and review state.

## High Relevance Signals
- firefighter
- fireground
- incident command
- flashover
- backdraft
- ventilation
- flow path
- structure fire
- high-rise fire
- wildland fire
- hazmat
- rescue
- SCBA
- mayday
- RIT / RIC
- 消防
- 灭火救援
- 火灾
- 指挥
- 内攻
- 轰燃
- 回燃
- 排烟
- 搜救
- 危化品

## Reject Or Deprioritize
- Entertainment-only videos
- Political commentary unrelated to fire service operations
- Duplicates
- Shorts under 60 seconds unless from a high-authority source
- Videos without operational, research, investigation, training, standard, or equipment value

