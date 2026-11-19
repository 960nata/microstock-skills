#!/usr/bin/env bash
# Check every skill: frontmatter present, name matches folder, description long enough,
# file not too long, and no obvious secrets.
set -uo pipefail
cd "$(dirname "$0")/../skills"
fail=0
for dir in */; do
  name="${dir%/}"; f="$dir/SKILL.md"
  [ -f "$f" ] || { echo "✗ $name: missing SKILL.md"; fail=1; continue; }
  [ "$(head -1 "$f")" = "---" ] || { echo "✗ $name: no frontmatter"; fail=1; }
  fm_name="$(sed -n '2,/^---$/p' "$f" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//')"
  [ "$fm_name" = "$name" ] || { echo "✗ $name: name '$fm_name' != folder"; fail=1; }
  desc="$(sed -n '2,/^---$/p' "$f" | grep -m1 '^description:' | sed 's/^description:[[:space:]]*//')"
  [ ${#desc} -ge 80 ] || { echo "✗ $name: description too short (${#desc} chars)"; fail=1; }
  [ ${#desc} -le 1024 ] || { echo "✗ $name: description over 1024 chars"; fail=1; }
  lines=$(wc -l < "$f"); [ "$lines" -le 200 ] || echo "! $name: $lines lines, consider references/"
  if grep -nEq '(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY)' "$f"; then
    echo "✗ $name: looks like a secret"; fail=1
  fi
done
[ $fail -eq 0 ] && echo "✓ all skills valid"
exit $fail
