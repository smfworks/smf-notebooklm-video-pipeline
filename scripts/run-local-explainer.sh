#!/usr/bin/env bash
# Local explainer (no NotebookLM, no Spark): Grok 4.6 → Kokoro af_heart → Ken Burns → overlay.
# Usage: ./scripts/run-local-explainer.sh --source booklet.md --title "Lesson title"
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/local_explainer.py" "$@"
