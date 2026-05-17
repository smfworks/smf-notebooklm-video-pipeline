#!/bin/bash
# WisdomForge Video Overlay Pipeline v2.0
# Adds title card, end card, and lower-third badge watermark to NotebookLM videos
#
# Usage: ./overlay.sh <input.mp4> <philosopher> <lesson_title> [subtitle]
# Example: ./overlay.sh output/epictetus-dichotomy-of-control.mp4 "Epictetus" "The Dichotomy of Control"
#
# Output: <input_basename>-final.mp4 in same directory
#
# Design v2:
#   - Title card: 2.5s, dark navy background, EB Garamond philosopher name,
#     Roboto for lesson title in warm red accent, WISDOMFORGE wordmark
#   - End card: 3s, attribution text, fade-in/out
#   - Lower-third badge: semi-transparent dark bar with "WISDOMFORGE" text
#     bottom-right corner — visible on both light and dark backgrounds
#   - Total addition: ~5.5s per video

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: overlay.sh <input.mp4> <philosopher> <lesson_title> [subtitle]"
  echo "Example: overlay.sh output/epictetus.mp4 'Epictetus' 'The Dichotomy of Control'"
  exit 1
fi

INPUT="$1"
PHILOSOPHER="$2"
LESSON_TITLE="$3"
SUBTITLE="${4:-Curated by Aiona for WisdomForge, an SMF Works project}"

# Resolve absolute path
INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
INPUT_DIR="$(dirname "$INPUT")"
INPUT_BASE="$(basename "${INPUT%.mp4}")"
OUTPUT="${INPUT_DIR}/${INPUT_BASE}-final.mp4"

# Temp directory
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

# Font paths
FONT_SERIF="/usr/share/fonts/truetype/ebgaramond/EBGaramond12-Bold.ttf"
FONT_SANS="/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Light.ttf"
FONT_SANS_BOLD="/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Medium.ttf"

# Colors
BG_COLOR="0x1a1a2e"       # Deep navy
ACCENT_COLOR="0xe94560"     # Warm red
TEXT_COLOR="0xf5f5f5"       # Off-white
SUBTLE_COLOR="0x999999"     # Gray

# Timing
TITLE_DURATION=2.5
END_DURATION=3.0
FADE_IN=0.8
FADE_OUT=0.8

echo "=== WisdomForge Overlay Pipeline v2.0 ==="
echo "Input: $(basename "$INPUT")"
echo "Philosopher: $PHILOSOPHER"
echo "Lesson: $LESSON_TITLE"

# Get video properties
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$INPUT")
AUDIO_RATE=$(ffprobe -v quiet -show_entries stream=sample_rate -of csv=p=0 -select_streams a:0 "$INPUT")
AUDIO_CH=$(ffprobe -v quiet -show_entries stream=channels -of csv=p=0 -select_streams a:0 "$INPUT")
FPS="24/1"

echo "Duration: ${DURATION}s | Audio: ${AUDIO_RATE}Hz"

# Step 1: Title card
echo "→ Generating title card..."
ffmpeg -y -f lavfi -i "color=c=${BG_COLOR}:s=1280x720:d=${TITLE_DURATION}:r=${FPS}" \
  -vf "
    drawtext=fontfile=${FONT_SERIF}:text='${PHILOSOPHER}':
      fontsize=64:fontcolor=${TEXT_COLOR}:x=(w-tw)/2:y=(h-th)/2-50:
      enable='between(t,0.2,${TITLE_DURATION})',
    drawtext=fontfile=${FONT_SANS}:text='${LESSON_TITLE}':
      fontsize=36:fontcolor=${ACCENT_COLOR}:x=(w-tw)/2:y=(h-th)/2+20:
      enable='between(t,0.4,${TITLE_DURATION})',
    drawtext=fontfile=${FONT_SANS_BOLD}:text='WISDOMFORGE':
      fontsize=18:fontcolor=${SUBTLE_COLOR}:x=(w-tw)/2:y=(h-th)/2+70:
      enable='between(t,0.6,${TITLE_DURATION})',
    fade=t=in:st=0:d=${FADE_IN},
    fade=t=out:st=$(echo "$TITLE_DURATION - $FADE_OUT" | bc):d=${FADE_OUT}
  " \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an \
  "${TEMP_DIR}/title.mp4" 2>/dev/null

# Step 2: End card
echo "→ Generating end card..."
ffmpeg -y -f lavfi -i "color=c=${BG_COLOR}:s=1280x720:d=${END_DURATION}:r=${FPS}" \
  -vf "
    drawtext=fontfile=${FONT_SERIF}:text='${SUBTITLE}':
      fontsize=28:fontcolor=${TEXT_COLOR}:x=(w-tw)/2:y=(h-th)/2-15:
      enable='between(t,0.3,${END_DURATION})',
    drawtext=fontfile=${FONT_SANS}:text='Made with NotebookLM':
      fontsize=20:fontcolor=${SUBTLE_COLOR}:x=(w-tw)/2:y=(h-th)/2+25:
      enable='between(t,0.5,${END_DURATION})',
    drawtext=fontfile=${FONT_SANS_BOLD}:text='WISDOMFORGE':
      fontsize=22:fontcolor=${ACCENT_COLOR}:x=(w-tw)/2:y=(h-th)/2+60:
      enable='between(t,0.7,${END_DURATION})',
    fade=t=in:st=0:d=0.5,
    fade=t=out:st=$(echo "$END_DURATION - $FADE_OUT" | bc):d=${FADE_OUT}
  " \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an \
  "${TEMP_DIR}/endcard.mp4" 2>/dev/null

# Step 3: Add watermark badge to main video
# Semi-transparent dark bar with white text — visible on both light and dark backgrounds
echo "→ Adding watermark badge..."
ffmpeg -y -i "$INPUT" \
  -vf "
    drawbox=x=iw-162:y=ih-32:w=158:h=26:color=black@0.55:t=fill:enable='between(t,2,${DURATION})',
    drawtext=fontfile=${FONT_SANS_BOLD}:text='WISDOMFORGE':
      fontsize=13:fontcolor=white@0.85:x=(w-tw-10):y=(h-th-10):enable='between(t,2,${DURATION})'
  " \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a copy \
  "${TEMP_DIR}/watermarked.mp4" 2>/dev/null

# Step 4: Silent audio for cards
ffmpeg -y -f lavfi -i "anullsrc=r=${AUDIO_RATE}:cl=mono" \
  -t ${TITLE_DURATION} -c:a aac -b:a 96k \
  "${TEMP_DIR}/title_audio.m4a" 2>/dev/null
ffmpeg -y -f lavfi -i "anullsrc=r=${AUDIO_RATE}:cl=mono" \
  -t ${END_DURATION} -c:a aac -b:a 96k \
  "${TEMP_DIR}/end_audio.m4a" 2>/dev/null

# Step 5: Mux audio into cards
ffmpeg -y -i "${TEMP_DIR}/title.mp4" -i "${TEMP_DIR}/title_audio.m4a" \
  -c:v copy -c:a copy -shortest \
  "${TEMP_DIR}/title_wa.mp4" 2>/dev/null
ffmpeg -y -i "${TEMP_DIR}/endcard.mp4" -i "${TEMP_DIR}/end_audio.m4a" \
  -c:v copy -c:a copy -shortest \
  "${TEMP_DIR}/endcard_wa.mp4" 2>/dev/null

# Step 6: Concatenate
echo "→ Concatenating..."
cat > "${TEMP_DIR}/concat.txt" <<EOF
file '${TEMP_DIR}/title_wa.mp4'
file '${TEMP_DIR}/watermarked.mp4'
file '${TEMP_DIR}/endcard_wa.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "${TEMP_DIR}/concat.txt" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart \
  "$OUTPUT" 2>/dev/null

FINAL_DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
FINAL_SIZE=$(du -h "$OUTPUT" | cut -f1)

echo ""
echo "=== Done ==="
echo "Output: $(basename "$OUTPUT")"
echo "Duration: ${FINAL_DURATION}s (original: ${DURATION}s, +$(echo "$TITLE_DURATION + $END_DURATION" | bc)s overlay)"
echo "Size: $FINAL_SIZE"