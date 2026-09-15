#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../scripts/lib.sh
source "${ROOT}/scripts/lib.sh"

fail=0
expect() {
  local got="$1" want="$2" name="$3"
  if [[ "$got" != "$want" ]]; then
    echo "FAIL $name: got '$got' want '$want'"
    fail=1
  else
    echo "ok   $name"
  fi
}

expect "$(slugify 'WisdomForge: Epictetus')" "wisdomforge-epictetus" "slugify notebook name"
expect "$(slugify '---Hello---World---')" "hello-world" "slugify strips edges"
expect "$(slugify '!!!')" "untitled" "slugify empty fallback"
expect "$(ffmpeg_escape 'A:B')" 'A\:B' "ffmpeg colon escape"
expect "$(ffmpeg_escape '100%')" '100\%' "ffmpeg percent escape"

tmpf="$(mktemp)"
if got="$(pick_font /no/such.ttf "$tmpf")"; then
  expect "$got" "$tmpf" "pick_font first existing"
else
  echo "FAIL pick_font"
  fail=1
fi
rm -f "$tmpf"
if pick_font /no/such.ttf >/dev/null; then
  echo "FAIL pick_font should miss"
  fail=1
else
  echo "ok   pick_font miss"
fi

if validate_format brief && validate_format explainer; then
  echo "ok   format allowlist"
else
  echo "FAIL format allowlist"
  fail=1
fi

if ( validate_format nope ); then
  echo "FAIL format should reject nope"
  fail=1
else
  echo "ok   format rejects unknown"
fi

bash -n "${ROOT}/scripts/generate.sh"
bash -n "${ROOT}/scripts/overlay.sh"
bash -n "${ROOT}/scripts/lib.sh"
bash -n "${ROOT}/scripts/run-local-explainer.sh"
echo "ok   bash -n scripts"

exit "$fail"
