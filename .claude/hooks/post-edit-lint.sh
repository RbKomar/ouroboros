#!/usr/bin/env bash
# PostToolUse Edit|Write: fast lint of the edited Python file. Exit 2 sends stderr back to Claude.
set -uo pipefail
INPUT=$(cat)
FILE=$(jq -r '.tool_input.file_path // empty' <<<"$INPUT")
CWD=$(jq -r '.cwd' <<<"$INPUT")
case "$FILE" in *.py) ;; *) exit 0 ;; esac
cd "$CWD" || exit 0
if ! OUT=$(uv run --frozen --quiet ruff check --quiet "$FILE" 2>&1); then
  printf 'ruff found problems in %s:\n%s\n' "$FILE" "$(head -30 <<<"$OUT")" >&2
  exit 2
fi
exit 0
