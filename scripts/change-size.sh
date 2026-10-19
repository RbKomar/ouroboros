#!/usr/bin/env bash
# Fails when the change against BASE exceeds MAX changed lines.
# Usage: change-size.sh [BASE] [MAX]. Lockfiles and test fixtures are excluded.
set -euo pipefail
BASE=${1:-origin/main}
MAX=${2:-${OUROBOROS_MAX_CHANGE_LINES:-400}}
git rev-parse --verify -q "$BASE" >/dev/null || BASE=$(git hash-object -t tree /dev/null)
EXCLUDES=(':(exclude)uv.lock' ':(exclude)tests/fixtures/**')
TRACKED=$(git diff "$BASE" --numstat -- . "${EXCLUDES[@]}" | awk '{s+=$1+$2} END {print s+0}')
UNTRACKED=$(git ls-files --others --exclude-standard -- . "${EXCLUDES[@]}" | xargs -r cat 2>/dev/null | wc -l)
TOTAL=$((TRACKED + UNTRACKED))
if [ "$TOTAL" -gt "$MAX" ]; then
  echo "Change has $TOTAL changed lines against $BASE (limit $MAX). Split it into smaller PRs, one concern each." >&2
  exit 1
fi
echo "change-size: $TOTAL/$MAX lines"
