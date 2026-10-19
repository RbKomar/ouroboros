#!/usr/bin/env bash
# Every commit in BASE..HEAD must carry an "Agent:" trailer (model id, or "none" for human-only work).
# This is the provenance signal the metrics depend on.
set -euo pipefail
BASE=${1:-origin/main}
BAD=""
for SHA in $(git rev-list "$BASE"..HEAD); do
  if ! git log -1 --format='%(trailers:key=Agent,valueonly)' "$SHA" | grep -q .; then
    BAD+="  $(git log -1 --format='%h %s' "$SHA")"$'\n'
  fi
done
if [ -n "$BAD" ]; then
  printf 'Commits without an "Agent:" trailer:\n%s' "$BAD" >&2
  exit 1
fi
echo "trailers: ok"
