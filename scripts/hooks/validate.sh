#!/bin/sh
# Stop hook: a turn cannot end while a story fails validation or the suite is red.
# Exit 2 returns the failure to the model; stop_hook_active prevents a loop.
set -u
input=$(cat)
case "$input" in
  *'"stop_hook_active": true'*|*'"stop_hook_active":true'*) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
out=$(python3 -m scripts.check_stories 2>&1)
status=$?
if [ "$status" -ne 0 ]; then
  printf 'Story validation failed; fix before finishing:\n%s\n' "$out" >&2
  exit 2
fi
out=$(python3 -m unittest discover -s tests 2>&1 | tail -5)
case "$out" in
  *OK*) exit 0 ;;
  *) printf 'Unit tests failed; fix before finishing:\n%s\n' "$out" >&2; exit 2 ;;
esac
