#!/usr/bin/env bash
# Install microstock-skills into one or more coding agents.
#
#   ./install.sh                     all agents whose config folder exists
#   ./install.sh claude codex        specific agents
#   ./install.sh --copy all          copy instead of symlink
#   ./install.sh --project DIR ...   install into a project instead of globally
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)/skills"
MODE=link
PROJECT=""
AGENTS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE=copy ;;
    --project) PROJECT="$(cd "$2" && pwd)"; shift ;;
    -h|--help) sed -n 2,8p "$0"; exit 0 ;;
    *) AGENTS+=("$1") ;;
  esac
  shift
done

global_dir() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;;
    codex) echo "${CODEX_HOME:-$HOME/.codex}/skills" ;;
    antigravity) echo "$HOME/.gemini/antigravity/skills" ;;
    gemini) echo "$HOME/.gemini/skills" ;;
    *) return 1 ;;
  esac
}

project_dir() {
  case "$1" in
    claude) echo "$PROJECT/.claude/skills" ;;
    codex) echo "$PROJECT/.agents/skills" ;;
    antigravity) echo "$PROJECT/.agent/skills" ;;
    gemini) echo "$PROJECT/.gemini/skills" ;;
    *) return 1 ;;
  esac
}

ALL=(claude codex antigravity gemini)
if [ ${#AGENTS[@]} -eq 0 ]; then
  # Default: only agents that look installed (their home folder exists).
  for a in "${ALL[@]}"; do
    base="$(dirname "$(global_dir "$a")")"
    [ -d "$base" ] && AGENTS+=("$a")
  done
  [ ${#AGENTS[@]} -eq 0 ] && { echo "No agent folders found. Pass an agent name, e.g. ./install.sh claude"; exit 1; }
elif [ "${AGENTS[0]}" = "all" ]; then
  AGENTS=("${ALL[@]}")
fi

for agent in "${AGENTS[@]}"; do
  if [ -n "$PROJECT" ]; then dest="$(project_dir "$agent")" || { echo "Unknown agent: $agent"; exit 1; }
  else dest="$(global_dir "$agent")" || { echo "Unknown agent: $agent"; exit 1; }; fi
  mkdir -p "$dest"
  for skill in "$SRC"/*/; do
    name="$(basename "$skill")"
    target="$dest/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "  skip $agent/$name (a non-symlink folder already exists at $target)"
      continue
    fi
    rm -f "$target"
    if [ "$MODE" = copy ]; then cp -R "$skill" "$target"; else ln -s "${skill%/}" "$target"; fi
  done
  echo "✓ $agent → $dest ($MODE)"
done
