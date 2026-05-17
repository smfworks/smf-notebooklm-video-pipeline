# HOWTO — SMF NotebookLM Video Pipeline

> **Complete setup and usage guide.** This document is designed to be fed to an OpenClaw or Hermes AI agent for automated setup. See the "Agent Setup" section at the bottom.

## Overview

This guide walks through every step of setting up and running the NotebookLM video pipeline: installing dependencies, authenticating with Google, creating notebooks, generating videos, overlaying branding, and posting to social media.

At the end, you'll be producing 2-3 branded educational videos per day with ~20-30 minutes of human time per video.

---

## Step 1: Install Dependencies

### 1.1 Install notebooklm-py

```bash
pip install notebooklm-py
```

Verify installation:

```bash
notebooklm --version
```

### 1.2 Install ffmpeg

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

Verify installation:

```bash
ffmpeg -version
```

### 1.3 Install Fonts

The overlay pipeline uses EB Garamond and Roboto for professional typography.

```bash
# Ubuntu/Debian
sudo apt install fonts-ebgaramond fonts-roboto

# macOS — download from Google Fonts and install via Font Book
```

Verify font paths:

```bash
fc-list | grep -i "ebgaramond\|roboto"
```

Expected paths:
- Serif: `/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf`
- Sans: `/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Light.ttf`
- Sans Bold: `/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf`

If paths differ, update `FONT_SERIF`, `FONT_SANS`, and `FONT_SANS_BOLD` in `scripts/overlay.sh`.

### 1.4 Install Postiz (Optional — for Social Media Posting)

If you want to automate posting to X/Twitter, set up [Postiz](https://postiz.com) and configure API access. See the Postiz documentation for setup instructions.

Alternatively, post manually by downloading videos and uploading through the X web interface.

---

## Step 2: Authenticate with Google

### 2.1 Browser Login

```bash
notebooklm login
```

This opens a browser window. Sign in with your Google Workspace account that has NotebookLM access.

### 2.2 Verify Authentication

```bash
notebooklm notebooks list
```

If you see a list (even empty), authentication is working.

**Important:** Browser cookies expire. If you get authentication errors, re-run `notebooklm login`.

---

## Step 3: Create a Notebook and Add Sources

### 3.1 Create a Notebook

```bash
notebooklm create "My Project: Lesson Title" --use
```

The `--use` flag sets this as the active notebook for subsequent commands.

### 3.2 Add Sources

You can add URLs, local files, or pasted text:

```bash
# Add a web source
notebooklm source add "https://en.wikisource.org/wiki/Enchiridion_(Epictetus)"

# Add a local file
notebooklm source add ./sources/my-lesson-content.md

# Add pasted text
notebooklm source add --text "Your custom content here..."
```

**Source tips:**
- NotebookLM works best with 3-5 high-quality sources per notebook
- Public domain texts (Wikisource, Project Gutenberg) are excellent sources
- Include your own lesson script or outline as a source for the best results
- Sources need 30-60 seconds to index after upload

### 3.3 Verify Sources

```bash
notebooklm sources list
```

---

## Step 4: Generate a Video

### 4.1 Choose Your Format

| Format | Duration | Best For |
|--------|----------|----------|
| **Brief** | 1:30-2:00 | Quick lessons, daily content |
| **Explainer** | 3:00-5:00 | Deep dives, weekly content |

### 4.2 Generate Using a Steering Prompt

```bash
# Brief format (recommended for daily content)
notebooklm generate video \
  --prompt-file ./steering-prompts/my-lesson.md \
  --format brief \
  --style whiteboard \
  --wait

# Explainer format (for longer lessons)
notebooklm generate video \
  --prompt-file ./steering-prompts/my-lesson.md \
  --format explainer \
  --style whiteboard \
  --wait
```

Available styles: `whiteboard`, `classic`, `watercolor`, `retro_print`, `heritage`, `paper_craft`, `kawaii`, `anime`

**Generation time:** Brief takes 5-15 minutes. Explainer takes 10-20 minutes. The `--wait` flag polls until completion.

### 4.3 Download the Video

```bash
notebooklm download video ./output/my-lesson.mp4
```

### 4.4 Using the Python API (Alternative)

```python
import asyncio
from notebooklm import NotebookLMClient

async def generate_lesson():
    async with await NotebookLMClient.from_storage() as client:
        # Create notebook
        nb = await client.notebooks.create("My Project: Lesson Title")
        
        # Add sources
        await client.sources.add_url(nb.id, "https://en.wikisource.org/wiki/Enchiridion_(Epictetus)")
        await client.sources.add_file(nb.id, "./sources/my-lesson.md")
        
        # Wait for indexing
        await asyncio.sleep(30)
        
        # Generate video
        status = await client.artifacts.generate_video(
            nb.id,
            format="brief",
            style="whiteboard",
            instructions="Your steering prompt text here..."
        )
        await client.artifacts.wait_for_completion(nb.id, status.task_id, timeout=600)
        
        # Download
        await client.artifacts.download_video(nb.id, "./output/my-lesson.mp4")

asyncio.run(generate_lesson())
```

---

## Step 5: Overlay Branding

### 5.1 Run the Overlay Pipeline

```bash
./scripts/overlay.sh output/my-lesson.mp4 "Philosopher Name" "Lesson Title"
```

This produces `output/my-lesson-final.mp4` with:
- **Title card** (2.5s): Dark navy background, philosopher name in EB Garamond, lesson title in warm red, project wordmark
- **Lower-third badge**: Subtle "PROJECTNAME" watermark throughout
- **End card** (3s): Attribution, tool credit, project wordmark

### 5.2 Customize Branding

Edit `scripts/overlay.sh` to change:
- `BG_COLOR` — Background color (default: deep navy `0x1a1a2e`)
- `ACCENT_COLOR` — Accent color (default: warm red `0xe94560`)
- `TEXT_COLOR` — Primary text color (default: off-white `0xf5f5f5`)
- `SUBTITLE` — Attribution line (default: "Curated by Aiona for WisdomForge, an SMF Works project")
- Font paths — Change for your brand fonts
- Duration values — Adjust title card and end card timing

### 5.3 Verify Output

```bash
ffprobe -v quiet -show_entries format=duration -of csv=p0 output/my-lesson-final.mp4
```

Expected: Original duration + ~5.5 seconds (2.5s title + 3s end card).

---

## Step 6: Quality Check

Watch the final video end-to-end. Check for:

- [ ] Title card displays correctly (philosopher name, lesson title, wordmark)
- [ ] Watermark badge is visible throughout (bottom-right corner)
- [ ] End card shows attribution and tool credit
- [ ] Audio is clear and narration follows the steering prompt structure
- [ ] No visual glitches or artifacts
- [ ] Total duration is appropriate (1:30-2:00 for Brief, 3:00-5:00 for Explainer)

---

## Step 7: Post to Social Media

### 7.1 Using Postiz (Recommended)

If you have Postiz configured with your social accounts:

```python
from postiz_poster import create_post

result = create_post(
    content="Your intro text here\n\n#Hashtags",
    integration_id="your-integration-id",
    platform_type="x",
    scheduled_at="now",
    media_path="./output/my-lesson-final.mp4"
)
```

### 7.2 Manual Posting

1. Download the final MP4 to your local machine
2. Open X/Twitter and compose a new post
3. Attach the video
4. Write your intro text (see Intro Text Templates below)
5. Post

### 7.3 Intro Text Templates

**Template A — Direct Quote (under 280 chars):**

```
"[CLASSICAL QUOTE]"

[PHILOSOPHER] drew this line [X] years ago. [ONE-LINE APPLICATION].

Today's [PROJECT] ↓

#Hashtags
```

**Template B — Question:**

```
[APPLICATION QUESTION]?

[PHILOSOPHER] answered this [X] years ago: "[ABBREVIATED QUOTE]"

[PROJECT] ↓

#Hashtags
```

**Template C — Provocation:**

```
[COUNTERINTUITIVE QUOTE]

Most people think [COMMON ASSUMPTION]. [PHILOSOPHER] disagreed.

[PROJECT] ↓

#Hashtags
```

---

## Step 8: Batch Production (Advanced)

For producing 2-3 videos per day sustainably:

### 8.1 Sunday Prep (60-90 minutes)

```bash
# Create all notebooks for the week
for lesson in "epictetus-dichotomy" "marcus-inner-citadel" "seneca-shortness"; do
  notebooklm create "WisdomForge: $lesson" --use
  notebooklm source add "./sources/${lesson}.md"
  notebooklm source add "https://en.wikisource.org/wiki/..."
done
```

### 8.2 Daily Generation (10-15 minutes human time)

```bash
# Generate video for today's lesson
notebooklm use <notebook_id>
notebooklm generate video --prompt-file ./steering-prompts/todays-lesson.md --format brief --style whiteboard --wait
notebooklm download video ./output/todays-lesson.mp4

# Overlay branding
./scripts/overlay.sh ./output/todays-lesson.mp4 "Philosopher" "Lesson Title"
```

### 8.3 Alternative: Generate 3 Days at Once

NotebookLM supports parallel generation. Create 3 notebooks, generate all 3 videos in the morning, review and post throughout the day.

---

## Steering Prompt Template

The steering prompt is the creative lever. Here's the base template:

```markdown
This is a [PROJECT] lesson on [PHILOSOPHER]'s teaching: "[CLASSICAL QUOTE]".

Structure:
1. Open with the quote and briefly identify the philosopher and context
2. Explain the core principle in plain language — what it means and why it mattered then
3. Show 2-3 specific modern applications: work, relationships, daily decisions
4. Close with a practical challenge the viewer can try today

Tone: Warm and direct. Speak to a curious adult learner, not an academic. Use concrete examples, not abstractions. Avoid jargon. The goal is insight, not information.

Focus: Make the ancient principle feel immediately useful. The viewer should finish thinking "I can try this today."
```

**Customize per lesson:** Replace the bracketed fields with specific philosopher, quote, and context. The more specific your source material, the better the output.

---

## Troubleshooting

### Authentication Errors
```bash
notebooklm login  # Re-authenticate with browser
```

### Video Generation Timeout
- Brief format: 5-15 minutes is normal
- Explainer format: 10-20 minutes is normal
- Use `--wait` flag to poll automatically
- If timeout exceeds 30 minutes, check your Workspace tier limits

### Daily Generation Limits
- **Business Standard:** 6 video overviews/day, 6 audio overviews/day
- **Google AI Pro ($19.99/month):** 20/day each
- **Google AI Ultra ($249.99/month):** Cinematic video format available

### Font Not Found Errors
```bash
# Verify font paths
fc-list | grep -i "ebgaramond\|roboto"

# Update paths in overlay.sh if different
FONT_SERIF="/your/path/to/EBGaramond-Bold.ttf"
FONT_SANS="/your/path/to/Roboto-Light.ttf"
```

### Video Quality Issues
- Ensure source material is substantial (at least 150-200 lines of text)
- The steering prompt significantly affects output quality — iterate on it
- Brief format produces 1:30-2:00 videos; for longer content, use Explainer

---

## Agent Setup (OpenClaw / Hermes AI)

This section is specifically designed for feeding to an AI agent (OpenClaw, Hermes, or similar) for automated pipeline setup.

### Agent Instructions

```
You are setting up the SMF NotebookLM Video Pipeline. Follow these steps in order:

1. CLONE THE REPO
   - Clone https://github.com/smfworks/smf-notebooklm-video-pipeline
   - Navigate into the project directory

2. INSTALL DEPENDENCIES
   - Run: pip install notebooklm-py
   - Verify: ffmpeg is installed (install if missing)
   - Verify: EB Garamond and Roboto fonts are installed (install if missing)
   - If fonts are in different locations, update FONT_SERIF, FONT_SANS, FONT_SANS_BOLD paths in scripts/overlay.sh

3. AUTHENTICATE WITH GOOGLE
   - Run: notebooklm login
   - The user must complete browser authentication with their Google Workspace account
   - Verify: notebooklm notebooks list (should return a list, even empty)

4. CONFIGURE BRANDING
   - Edit scripts/overlay.sh:
     - Change SUBTITLE to your attribution line (e.g., "Curated by [Name] for [Project]")
     - Change BG_COLOR, ACCENT_COLOR if desired
     - Verify font paths match your system

5. CREATE YOUR FIRST NOTEBOOK
   - Run: notebooklm create "[Your Project]: [Lesson Title]" --use
   - Add 3-5 source URLs or files
   - Wait 30-60 seconds for indexing

6. WRITE YOUR STEERING PROMPT
   - Copy steering-prompts/template.md
   - Customize with your philosopher/quote/context
   - Save as a new .md file in steering-prompts/

7. GENERATE YOUR FIRST VIDEO
   - Run: notebooklm generate video --prompt-file ./steering-prompts/your-lesson.md --format brief --style whiteboard --wait
   - Download: notebooklm download video ./output/your-lesson.mp4
   - Overlay: ./scripts/overlay.sh ./output/your-lesson.mp4 "Philosopher" "Lesson Title"

8. QUALITY CHECK
   - Play output/your-lesson-final.mp4 end-to-end
   - Verify title card, watermark, and end card display correctly
   - Verify audio clarity and narration follows steering prompt structure

9. POST TO SOCIAL
   - If Postiz is configured: use postiz_poster.py with your integration ID
   - Otherwise: download and post manually

10. ITERATE
    - Adjust steering prompt based on output quality
    - Batch-create notebooks on Sunday for the week
    - Generate videos daily or in batches
    - Target 2-3 videos per day for sustainable production
```

### Agent Context File

Save this as `AGENT.md` in the project root for agent reference:

```markdown
# Agent Context — SMF NotebookLM Video Pipeline

## Project
Produces branded short-form educational videos using Google NotebookLM.

## Key Commands
- Create notebook: `notebooklm create "Title" --use`
- Add source: `notebooklm source add <url_or_file>`
- Generate video: `notebooklm generate video --prompt-file <file> --format brief --style whiteboard --wait`
- Download video: `notebooklm download video <path>`
- Overlay branding: `./scripts/overlay.sh <input.mp4> "Philosopher" "Lesson Title"`
- Post to X: `python3 postiz_poster.py --content "..." --platforms x --media-path <final.mp4>`

## Daily Workflow
1. Select today's topic and source material
2. Write/customize steering prompt
3. Generate video (5-15 min automated)
4. Run overlay pipeline (~7 sec)
5. Quality check (~2 min)
6. Write social intro text (5-10 min)
7. Post

## Weekly Workflow
- Sunday: Create 5-6 notebooks, add sources, prepare steering prompts
- Monday-Friday: Generate, overlay, review, post 2-3 videos/day
- Saturday: Single "Ember" lesson (shorter, reflective)

## Production Limits
- Business Standard: 6 video overviews/day
- Brief format: 1:30-2:00 duration
- Explainer format: 3:00-5:00 duration
- Human time per video: ~20-30 min
- Total pipeline time per video: ~25-55 min
```

---

## Attribution & Transparency

This pipeline uses Google NotebookLM to generate video content. The AI produces the narration and visuals. The human role is:

1. **Topic selection** — choosing what to teach
2. **Source curation** — selecting and preparing source material
3. **Steering prompt design** — directing the AI's output
4. **Quality review** — ensuring the content meets standards
5. **Distribution** — writing intro text, scheduling, posting

We recommend transparent attribution: **"Curated by [Name] for [Project] • Made with NotebookLM"**

This accurately represents the human creative direction while being honest about the AI's role in generating the narration and visuals.

---

## License

MIT License — use freely, adapt for your own content pipeline, attribution appreciated but not required.

---

*Built with 🔨 by [SMF Works](https://smfworks.com) — AI services, multi-agent systems, and daily Stoic wisdom.*