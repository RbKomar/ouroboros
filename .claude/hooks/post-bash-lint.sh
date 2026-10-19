#!/usr/bin/env bash
# PostToolUse Bash: files written by shell (heredocs, sed -i) bypass the Edit|Write lint hook.
# Lint every changed or new Python file after any Bash call; cheap at this repo size.
set -uo pipefail
cd "$(jq -r '.cwd' <<<"$(cat)")" || exit 0
FILES=$( { git diff --name-only HEAD 2>/dev/null; git ls-files --others --exclude-standard; } | grep '\.py$' | sort -u)
[ -z "$FILES" ] && exit 0
if ! OUT=$(xargs uv run --frozen --quiet ruff check --quiet <<<"$FILES" 2>&1); then
  printf 'ruff found problems in files changed so far (prefer the Edit/Write tools for code):\n%s\n' "$(head -30 <<<"$OUT")" >&2
  exit 2
fi
exit 0
