# SMF NotebookLM Video Pipeline

> **Turn Google NotebookLM into a daily short-form video content engine.**

A complete, reproducible pipeline for generating branded educational short-form videos (2-5 minutes) using Google NotebookLM, `notebooklm-py`, and `ffmpeg`. Designed for teams who want to produce consistent, high-quality video content at scale — 2-3 videos per day with minimal human time.

Built and battle-tested by [SMF Works](https://smfworks.com) for [WisdomForge](https://smfworks.com) — our classical education project that brings Stoic philosophy to modern life through daily video lessons.

## What This Does

1. **Ingest** source material into NotebookLM notebooks
2. **Generate** short-form video overviews using NotebookLM's AI (Brief or Explainer format)
3. **Overlay** branded title cards, watermarks, and end cards with attribution
4. **Publish** to social media (X/Twitter, with extensibility for other platforms)

The entire pipeline runs from the command line. No browser needed.

## What It Produces

- **2-5 minute educational videos** with watercolor-style illustrations and two-host narration
- **Branded title card** (2.5s): Philosopher name, lesson title, project wordmark
- **Lower-third watermark**: Subtle badge throughout the video
- **End card** (3s): Attribution, tool credit, project wordmark
- **Ready to post** MP4 files (1280×720, H.264)

## Why This Exists

We needed a way to produce daily video content from our growing repository of classical philosophy texts. NotebookLM excels at synthesizing source material into accessible overviews, but its output needed branding, attribution, and a repeatable workflow. This pipeline bridges that gap.

The key insight: **NotebookLM is a research and synthesis engine, not a production engine.** Its two-host format works beautifully for educational narration, but you still need human judgment for topic selection, source curation, steering prompt design, and quality review. This pipeline automates the mechanical steps and preserves the creative ones.

## Quick Start

See [HOWTO.md](./HOWTO.md) for the complete setup and usage guide, including instructions for feeding this document to an OpenClaw or Hermes AI agent to set up the pipeline automatically.

## Requirements

- **Google Workspace** account with NotebookLM access (Business Standard or above)
- **`notebooklm-py`** — Python CLI and API client for NotebookLM ([GitHub](https://github.com/nicholasgriffintn/notebooklm-py))
- **`ffmpeg`** — for video overlay processing
- **Fonts** — EB Garamond and Roboto (for title cards and end cards)
- **Postiz** or equivalent — for social media posting (optional)

## Directory Structure

```
smf-notebooklm-video-pipeline/
├── README.md              # This file — overview and context
├── HOWTO.md               # Complete setup and usage guide
├── scripts/
│   ├── overlay.sh         # Video overlay pipeline (title card, watermark, end card)
│   └── generate.sh        # NotebookLM notebook creation and video generation
├── steering-prompts/
│   ├── template.md        # Base steering prompt template
│   └── examples/          # Example steering prompts (Epictetus, Marcus Aurelius, Seneca)
├── sources/
│   └── example/           # Example source material
└── examples/
    └── output/            # Example output videos and frames
```

## The Ember Method

Our content format follows a 5-act structure we call **The Ember Method**:

| Act | Duration | Purpose |
|-----|----------|---------|
| **The Spark** | 15s | Classical quote, full attribution |
| **The Fire** | 30s | Context — who said it, what they were facing |
| **The Forge** | 90s | Core teaching — one insight, one modern scenario, one reframing |
| **The Ember** | 60s | Personal application — one question for the viewer |
| **The Glow** | 30s | Series close — tag + next episode tease |

This structure maps directly to the steering prompt template. NotebookLM's Brief format naturally produces 1:30-2:00 videos; Explainer format extends to 3-5 minutes.

## Production Pipeline

```
Sources → NotebookLM → Video → Overlay → Quality Check → Post
```

| Step | Time | Automatable |
|------|------|------------|
| Topic + source selection | 10-20 min | No (human judgment) |
| Create notebook + add sources | 2-3 min | Yes |
| Write steering prompt | 5-10 min | Partially (template-based) |
| Video generation (Brief) | 5-15 min | Yes (automated wait) |
| Download video | <30 sec | Yes |
| Overlay pipeline | ~6.5 sec | Yes |
| Quality check (watch-through) | ~2 min | No (human judgment) |
| Write X intro text | 5-10 min | No (human voice) |
| Post to social | <1 min | Yes |

**Total human time per video: ~20-30 minutes. Total pipeline time: ~25-55 minutes.**

## Attribution

We use transparent attribution:

> **Curated by [Your Name] for [Project Name] • Made with NotebookLM**

NotebookLM's AI generates the narration. The human role is topic selection, source curation, steering prompt design, quality review, and distribution. "Curated by" accurately represents that creative direction. "Made with NotebookLM" is transparent about the tool.

## Credits

- **Pipeline design:** SMF Works team — Pamela (CCO, creative direction), Aiona (CIO, technical pipeline), Morgan (Social Media Manager, content strategy)
- **Powered by:** [Google NotebookLM](https://notebooklm.google.com), [notebooklm-py](https://github.com/nicholasgriffintn/notebooklm-py), [ffmpeg](https://ffmpeg.org)
- **Built for:** [WisdomForge](https://smfworks.com) — classical education through modern technology

## License

MIT License — use freely, adapt for your own content pipeline, attribution appreciated but not required.

---

*Built with 🔨 by [SMF Works](https://smfworks.com) — AI services, multi-agent systems, and now: daily Stoic wisdom.*