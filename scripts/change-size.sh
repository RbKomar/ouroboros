#!/usr/bin/env bash
# Fails when the non-test change against BASE exceeds MAX changed lines.
# Usage: change-size.sh [BASE] [MAX]. Tests, fixtures and lockfiles are excluded: the limit protects
# reviewability of production code and must not penalise writing tests first.
# Why a limit at all: unmerged agent PRs are larger and touch more files (Ehsani et al., MSR 2026,
# https://arxiv.org/abs/2601.15195); large PRs carry far more review findings (Anthropic Code Review,
# https://claude.com/blog/code-review). The number 400 is our own starting point, not from a study.
set -euo pipefail
BASE=${1:-origin/main}
MAX=${2:-${OUROBOROS_MAX_CHANGE_LINES:-400}}
git rev-parse --verify -q "$BASE" >/dev/null || BASE=$(git hash-object -t tree /dev/null)
EXCLUDES=(':(exclude)uv.lock' ':(exclude)tests/**')
TRACKED=$(git diff "$BASE" --numstat -- . "${EXCLUDES[@]}" | awk '{s+=$1+$2} END {print s+0}')
UNTRACKED=$(git ls-files --others --exclude-standard -- . "${EXCLUDES[@]}" | xargs -r cat 2>/dev/null | wc -l)
TOTAL=$((TRACKED + UNTRACKED))
if [ "$TOTAL" -gt "$MAX" ]; then
  echo "Change has $TOTAL changed non-test lines against $BASE (limit $MAX). Split it into smaller PRs, one concern each." >&2
  exit 1
fi
echo "change-size: $TOTAL/$MAX lines"
