# Free Fire Video Intel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-new-cost firefighting video intelligence collector that discovers sources, fetches available subtitles, deduplicates records, and produces Markdown review queues.

**Architecture:** GitHub Actions performs free scheduled collection and archival. Local Codex Skills and open-source local tools handle later professional translation, review, and transcription without paid API calls.

**Tech Stack:** Python 3.11 standard library core, optional `youtube-transcript-api`, SQLite, Markdown, GitHub Actions, Codex Skills.

---

### Task 1: Core Records, Relevance, Storage, Markdown

**Files:**
- Create: `src/fire_video_intel/models.py`
- Create: `src/fire_video_intel/relevance.py`
- Create: `src/fire_video_intel/storage/database.py`
- Create: `src/fire_video_intel/storage/markdown_writer.py`
- Test: `tests/test_core_pipeline.py`

- [ ] **Step 1: Write failing tests** for firefighting relevance, SQLite deduplication, and Markdown output.
- [ ] **Step 2: Run tests** with `python -m unittest discover -s tests`.
- [ ] **Step 3: Implement minimal modules** that satisfy the tests.
- [ ] **Step 4: Re-run tests** with `python -m unittest discover -s tests`.

### Task 2: Free Collectors and CLI

**Files:**
- Create: `src/fire_video_intel/config.py`
- Create: `src/fire_video_intel/collectors/youtube_rss.py`
- Create: `src/fire_video_intel/processors/subtitle_fetcher.py`
- Create: `src/fire_video_intel/main.py`
- Test: `tests/test_collectors.py`

- [ ] **Step 1: Write failing tests** for config parsing, YouTube RSS parsing, and no-subtitle queue status.
- [ ] **Step 2: Run targeted tests** with `python -m unittest tests.test_collectors`.
- [ ] **Step 3: Implement collectors** using standard library XML parsing and optional subtitle dependency.
- [ ] **Step 4: Re-run all tests** with `python -m unittest discover -s tests`.

### Task 3: Repo Operations and Free Automation

**Files:**
- Create: `sources.yaml`
- Create: `fire_terms.yaml`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.github/workflows/daily_free_fire_video_intel.yml`
- Create: `.agents/skills/fire-video-intake/SKILL.md`
- Create: `.agents/skills/fire-translation/SKILL.md`
- Create: `.agents/skills/fire-report/SKILL.md`
- Create: `README.md`

- [ ] **Step 1: Add default source and terminology files** focused on high-authority fire sources.
- [ ] **Step 2: Add GitHub Actions** that runs daily and commits generated metadata/reports.
- [ ] **Step 3: Add Codex Skills** that enforce firefighting review, translation, and reporting rules.
- [ ] **Step 4: Add README** explaining zero-cost operation and upgrade path.

### Task 4: Verification

**Files:**
- Modify: project files as needed.

- [ ] **Step 1: Run unit tests** with `python -m unittest discover -s tests`.
- [ ] **Step 2: Run CLI dry run** with `python -m fire_video_intel.main --mode dry-run --sources sources.yaml --output knowledge_base`.
- [ ] **Step 3: Inspect generated files** with `find knowledge_base -maxdepth 3 -type f`.
