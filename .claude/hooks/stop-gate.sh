#!/usr/bin/env bash
# Stop: Claude may not finish while the working tree has changes and the full gate is red.
set -uo pipefail
INPUT=$(cat)
CWD=$(jq -r '.cwd' <<<"$INPUT")
cd "$CWD" || exit 0
if git diff --quiet HEAD -- 2>/dev/null && [ -z "$(git ls-files --others --exclude-standard)" ] \
   && [ "$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)" = "0" ]; then
  exit 0
fi
LOG=$(mktemp)
if ! scripts/verify.sh >"$LOG" 2>&1; then
  REASON=$(printf 'scripts/verify.sh failed. Fix the root cause; do not weaken tests or gates. Last lines:\n%s' "$(tail -25 "$LOG")")
  jq -n --arg r "$REASON" '{decision: "block", reason: $r}'
fi
rm -f "$LOG"
exit 0
