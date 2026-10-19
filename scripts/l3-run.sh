#!/usr/bin/env bash
# Headless L3 run for one issue: the agent works in its own worktree, then gates run OUTSIDE the agent,
# an independent reviewer checks the diff, and only then a draft PR is opened. A human merges.
# Usage: scripts/l3-run.sh <issue-number> [max-budget-usd]
set -euo pipefail
ISSUE=$1
BUDGET=${2:-10}
ROOT=$(git rev-parse --show-toplevel)
WT="$ROOT/.claude/worktrees/issue-$ISSUE"
OUT="$ROOT/out/issue-$ISSUE"
mkdir -p "$OUT"

git -C "$ROOT" fetch -q origin
git -C "$ROOT" worktree add -q -B "agent/issue-$ISSUE" "$WT" origin/main
cd "$WT"
uv sync --frozen -q
mkdir -p .claude/state && echo "$ISSUE" > .claude/state/issue

echo "[$(date -u +%FT%TZ)] implementing #$ISSUE (budget \$$BUDGET)"
claude -p "/implement-issue $ISSUE
You are running unattended. Do steps 1-7 only: do not push and do not open a PR; the runner does that.
If you must stop early, explain why in your final message." \
  --permission-mode dontAsk --max-budget-usd "$BUDGET" \
  --output-format json > "$OUT/implement.json" || true

COST=$(jq -r '.total_cost_usd // 0' "$OUT/implement.json")
echo "agent finished: $(jq -r '.subtype' "$OUT/implement.json"), cost \$$COST"

# Gates outside the agent: we do not trust the agent's own claim of done.
GATES=ok
VERIFY_BASE=origin/main scripts/verify.sh > "$OUT/verify.log" 2>&1 || GATES=fail
scripts/change-size.sh origin/main >> "$OUT/verify.log" 2>&1 || GATES=fail
scripts/docs-coupling.sh origin/main >> "$OUT/verify.log" 2>&1 || GATES=fail
scripts/check-trailers.sh origin/main >> "$OUT/verify.log" 2>&1 || GATES=fail
echo "gates: $GATES"

claude -p "Act as the spec-reviewer subagent. Issue text: $(gh issue view "$ISSUE" --json title,body --jq '.title + "\n" + .body')" \
  --agent spec-reviewer --permission-mode dontAsk --max-budget-usd 3 --output-format json > "$OUT/review.json" || true
REVIEW_COST=$(jq -r '.total_cost_usd // 0' "$OUT/review.json")
VERDICT=$(jq -r '.result' "$OUT/review.json" | grep -o '{"verdict".*}' | tail -1 | jq -r '.verdict' 2>/dev/null || echo unknown)
TOTAL=$(python3 -c "print(round($COST + $REVIEW_COST, 2))")
echo "review: $VERDICT, total cost \$$TOTAL"

if [ "$GATES" = ok ] && [ "$VERDICT" = pass ]; then
  git push -q -u origin "agent/issue-$ISSUE"
  BODY="$OUT/pr-body.md"
  {
    jq -r '.result' "$OUT/implement.json"
    printf '\n## Evidence (runner)\n```\n%s\n```\nReviewer verdict: %s\n\nCloses #%s\nCost-USD: %s\n' \
      "$(tail -15 "$OUT/verify.log")" "$VERDICT" "$ISSUE" "$TOTAL"
  } > "$BODY"
  gh pr create --draft --head "agent/issue-$ISSUE" --title "$(gh issue view "$ISSUE" --json title --jq .title)" --body-file "$BODY"
else
  echo "Not opening a PR. Logs: $OUT" >&2
  exit 1
fi
