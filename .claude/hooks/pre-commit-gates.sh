#!/usr/bin/env bash
# PreToolUse Bash(git commit *): size limit, docs coupling and provenance trailer before a commit lands.
set -uo pipefail
INPUT=$(cat)
CWD=$(jq -r '.cwd' <<<"$INPUT")
CMD=$(jq -r '.tool_input.command // empty' <<<"$INPUT")
cd "$CWD" || exit 0
PROBLEMS=""
OUT=$(scripts/change-size.sh origin/main 2>&1) || PROBLEMS+="$OUT"$'\n'
OUT=$(scripts/docs-coupling.sh origin/main 2>&1) || PROBLEMS+="$OUT"$'\n'
grep -q 'Agent:' <<<"$CMD" || PROBLEMS+='Commit message must end with the trailer "Agent: <model-id>".'$'\n'
if [ -n "$PROBLEMS" ]; then
  jq -n --arg r "$PROBLEMS" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
fi
exit 0
