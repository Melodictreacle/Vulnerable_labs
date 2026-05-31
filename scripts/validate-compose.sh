#!/usr/bin/env bash
#
# Validate every docker-compose.yml in the repository with `docker compose config`.
# This parses and resolves each file (including build contexts and env interpolation)
# without pulling images or starting containers, so it is fast and side-effect free.
#
# Usage: scripts/validate-compose.sh
# Exit status: 0 if all compose files are valid, 1 otherwise.

set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root" || exit 1

fail=0
count=0

# NUL-delimited to be safe against any odd paths.
while IFS= read -r -d '' file; do
  count=$((count + 1))
  # `config -q` validates and is quiet on success; the obsolete `version:`
  # warning is emitted on stderr with exit 0 and does not count as a failure.
  if docker compose -f "$file" config -q; then
    printf '  [OK]   %s\n' "$file"
  else
    printf '  [FAIL] %s\n' "$file"
    fail=1
  fi
done < <(find . -type f -name 'docker-compose.yml' -print0 | sort -z)

echo "----------------------------------------"
echo "Validated $count compose file(s)."

if [ "$fail" -ne 0 ]; then
  echo "One or more compose files are invalid." >&2
  exit 1
fi
echo "All compose files are valid."
