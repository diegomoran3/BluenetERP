#!/bin/bash
# Strip CRLF line endings from text files in a git checkout.
# Fixes corruption caused by Windows git (core.autocrlf) on clones.
# Usage: ./scripts/fix-crlf.sh [directory]   (default: current dir)
set -e

DIR="${1:-.}"
FIXED=0

find "$DIR" \( -name '*.sh' -o -name '*.py' -o -name '*.conf' -o -name '*.yaml' \
  -o -name '*.yml' -o -name '*.json' -o -name '*.env' -o -name '*.md' \
  -o -name '*.txt' -o -name '*.toml' -o -name '*.ini' \) \
  -not -path '*/.git/*' \
  -exec sh -c 'for f; do
    if grep -q "$(printf "\r")" "$f" 2>/dev/null; then
      sed "s/\r$//" "$f" > "$f.tmp" && mv -f "$f.tmp" "$f" && echo "fixed: $f"
    fi
  done' sh {} +

echo "Done."
