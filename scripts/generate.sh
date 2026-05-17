#!/bin/bash
# NotebookLM Video Generation Script
# Creates a notebook, adds sources, and generates a video overview
#
# Usage: ./generate.sh <notebook_name> <steering_prompt_file> [format] [style]
# Example: ./generate.sh "WisdomForge: Epictetus" ./steering-prompts/epictetus-dichotomy.md brief whiteboard
#
# Format: brief (1:30-2:00) or explainer (3:00-5:00)
# Style: whiteboard, classic, watercolor, retro_print, heritage, paper_craft, kawaii, anime

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: generate.sh <notebook_name> <steering_prompt_file> [format] [style]"
  echo "Example: generate.sh 'WisdomForge: Epictetus' ./steering-prompts/epictetus-dichotomy.md brief whiteboard"
  exit 1
fi

NOTEBOOK_NAME="$1"
STEERING_PROMPT="$2"
FORMAT="${3:-brief}"
STYLE="${4:-whiteboard}"
OUTPUT_DIR="./output"

mkdir -p "$OUTPUT_DIR"

echo "=== NotebookLM Video Generation ==="
echo "Notebook: $NOTEBOOK_NAME"
echo "Prompt: $STEERING_PROMPT"
echo "Format: $FORMAT | Style: $STYLE"

# Step 1: Create notebook
echo "→ Creating notebook..."
notebooklm create "$NOTEBOOK_NAME" --use
NOTEBOOK_ID=$(notebooklm notebooks list --json 2>/dev/null | jq -r '.[0].id' 2>/dev/null || echo "active")

# Step 2: Generate video
echo "→ Generating video (this takes 5-15 minutes for Brief, 10-20 for Explainer)..."
notebooklm generate video \
  --prompt-file "$STEERING_PROMPT" \
  --format "$FORMAT" \
  --style "$STYLE" \
  --wait

# Step 3: Download video
SLUG_NAME=$(echo "$NOTEBOOK_NAME" | tr '[:upper:]' '[:lower]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
OUTPUT_FILE="${OUTPUT_DIR}/${SLUG_NAME}.mp4"

echo "→ Downloading video..."
notebooklm download video "$OUTPUT_FILE"

echo ""
echo "=== Generation Complete ==="
echo "Output: $OUTPUT_FILE"
echo ""
echo "Next step: Run the overlay pipeline:"
echo "  ./scripts/overlay.sh $OUTPUT_FILE \"Philosopher Name\" \"Lesson Title\""
