#!/usr/bin/env bash
# Shared helpers for NotebookLM pipeline scripts.
# shellcheck shell=bash

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "error: required command not found: $cmd" >&2
    exit 2
  fi
}

slugify() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g; s/--*/-/g; s/^-//; s/-$//'
}

validate_format() {
  case "$1" in
    brief|explainer) return 0 ;;
    *)
      echo "error: format must be brief or explainer (got: $1)" >&2
      exit 2
      ;;
  esac
}

validate_style() {
  case "$1" in
    whiteboard|classic|watercolor|retro_print|heritage|paper_craft|kawaii|anime) return 0 ;;
    *)
      echo "error: unknown style: $1" >&2
      exit 2
      ;;
  esac
}

# Escape text for ffmpeg drawtext=text='...'
ffmpeg_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//:/\\:}"
  s="${s//\'/\'\\\'\'}"
  printf '%s' "$s"
}
