#!/usr/bin/env bash
# Code under a mapped prefix changed without its documentation -> fail.
# Map format (.claude/doc-map): "<code-prefix> <doc-prefix>" per line.
set -euo pipefail
BASE=${1:-origin/main}
MAP=.claude/doc-map
[ -f "$MAP" ] || exit 0
git rev-parse --verify -q "$BASE" >/dev/null || BASE=$(git hash-object -t tree /dev/null)
CHANGED=$( { git diff "$BASE" --name-only; git ls-files --others --exclude-standard; } | sort -u)
MISSING=""
while read -r CODE DOC; do
  [ -z "${CODE:-}" ] || [ "${CODE:0:1}" = "#" ] && continue
  if grep -q "^$CODE" <<<"$CHANGED" && ! grep -q "^$DOC" <<<"$CHANGED"; then
    MISSING+="  $CODE changed, expected an update in $DOC"$'\n'
  fi
done < "$MAP"
if [ -n "$MISSING" ]; then
  printf 'Code changed without its documentation:\n%s' "$MISSING" >&2
  echo "If the docs really need no change, say so in the PR under 'Docs-unchanged:' and let the human decide." >&2
  exit 1
fi
echo "docs-coupling: ok"
