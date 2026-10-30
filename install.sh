#!/usr/bin/env bash
# Reporch installer: clones (or updates) the skill for Claude Code and/or Codex.
#   curl -fsSL https://raw.githubusercontent.com/mobo-kun/reporch/main/install.sh | bash
# It only runs `git clone` / `git pull` into your skills folders. No sudo, no packages, nothing else.
set -euo pipefail

REPO="${REPORCH_REPO:-https://github.com/mobo-kun/reporch.git}"
CLAUDE_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}/reporch"
CODEX_DIR="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}/reporch"
TARGET="${REPORCH_TARGET:-}"          # claude | codex | both (asked when empty)

say() { printf '%s\n' "$*"; }
ask() {                               # read from the terminal even when piped from curl
  local prompt="$1" default="$2" reply=""
  if [ -r /dev/tty ]; then printf '%s' "$prompt" > /dev/tty; read -r reply < /dev/tty || true; fi
  printf '%s' "${reply:-$default}"
}

command -v git >/dev/null 2>&1 || { say "Reporch needs git. Install git, then run this again."; exit 1; }
if command -v python3 >/dev/null 2>&1; then
  python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
    || say "Note: Reporch's tools need Python 3.9 or newer (found $(python3 --version 2>&1))."
else
  say "Note: Reporch's tools need Python 3.9+. Install it before using the skill."
fi

say "Reporch (Report of Research) by Mobo · Behdad Morsalpoor"
say ""
if [ -z "$TARGET" ]; then
  say "Install for:  1) Claude Code   2) Codex   3) both"
  case "$(ask 'Choose 1, 2 or 3 [3]: ' 3)" in
    1) TARGET=claude ;; 2) TARGET=codex ;; *) TARGET=both ;;
  esac
fi

install_to() {
  local dir="$1"
  if [ -d "$dir/.git" ]; then
    say "Updating $dir"
    git -C "$dir" pull --ff-only --quiet
  elif [ -e "$dir" ]; then
    say "Skipped $dir: it exists and is not a Reporch clone. Move it away and run again."
    return 1
  else
    say "Installing into $dir"
    mkdir -p "$(dirname "$dir")"
    git clone --depth 1 --quiet "$REPO" "$dir"
  fi
}

link_to() {                           # second agent shares the first clone
  local src="$1" dir="$2"
  if [ -L "$dir" ] || [ -d "$dir/.git" ]; then say "Already present: $dir"; return 0; fi
  if [ -e "$dir" ]; then say "Skipped $dir: it exists. Move it away and run again."; return 1; fi
  mkdir -p "$(dirname "$dir")"
  ln -s "$src" "$dir"
  say "Linked $dir → $src"
}

case "$TARGET" in
  claude) install_to "$CLAUDE_DIR" ;;
  codex)  install_to "$CODEX_DIR" ;;
  both)   install_to "$CLAUDE_DIR" && link_to "$CLAUDE_DIR" "$CODEX_DIR" ;;
  *) say "Unknown target '$TARGET' (use claude, codex or both)"; exit 1 ;;
esac

say ""
say "Done. Restart your agent, then say: \"Use Reporch\"."
say "Guide: https://github.com/mobo-kun/reporch/blob/main/HOW-TO-USE.md"
