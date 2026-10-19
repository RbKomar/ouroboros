#!/usr/bin/env bash
# SessionStart (startup|compact): re-inject the active issue and recent history.
set -uo pipefail
cd "$(jq -r '.cwd' <<<"$(cat)")" || exit 0
ISSUE=$(cat out/state/issue 2>/dev/null || true)
[ -n "$ISSUE" ] && echo "Active issue: #$ISSUE (branch $(git branch --show-current))"
echo "Recent commits:"; git log --oneline -5 2>/dev/null
