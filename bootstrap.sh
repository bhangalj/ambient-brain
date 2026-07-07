#!/usr/bin/env bash
set -euo pipefail

# Resolve the vault dir = directory containing this script (works wherever cloned)
VAULT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
GLOBAL_MD="$CLAUDE_DIR/CLAUDE.md"
MARKER_BEGIN="<!-- BEGIN ambient-brain -->"

mkdir -p "$SKILLS_DIR"

# 1. Symlink each skill into ~/.claude/skills/ (idempotent)
for src in "$VAULT_DIR"/install/skills/*/; do
  src="${src%/}"
  name="$(basename "$src")"
  target="$SKILLS_DIR/$name"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then
    echo "skill '$name' already linked"
  elif [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "WARN: $target exists and is not a symlink; leaving it alone" >&2
  else
    ln -sfn "$src" "$target"
    echo "linked skill '$name' -> $src"
  fi
done

# 2. Append the global CLAUDE.md snippet (idempotent, path-interpolated)
if [ -f "$GLOBAL_MD" ] && grep -qF "$MARKER_BEGIN" "$GLOBAL_MD"; then
  echo "global CLAUDE.md snippet already present; leaving it (edit manually to change path)"
else
  {
    echo ""
    sed "s#__VAULT_DIR__#$VAULT_DIR#g" "$VAULT_DIR/install/claude-md-snippet.md"
  } >> "$GLOBAL_MD"
  echo "appended ambient-brain snippet to $GLOBAL_MD"
fi

echo ""
echo "Bootstrap complete. Next:"
echo "  1. Personalize $VAULT_DIR/people/me.md"
echo "  2. Open a NEW Claude Code session (any directory) and try: /recall  or  /remember <a fact>"
