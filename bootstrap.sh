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

# 3. Pin vault git auth to the repo owner (idempotent; multi-account machines).
# The gh credential helper serves only the ACTIVE account's token, so a push from
# a session where another account is active 404s. A repo-local helper that always
# pulls the owner's token from gh's keyring makes vault pushes account-agnostic.
REMOTE_URL="$(git -C "$VAULT_DIR" remote get-url origin 2>/dev/null || true)"
case "$REMOTE_URL" in
  https://*github.com/*)
    OWNER="$(echo "$REMOTE_URL" | sed -E 's#https://([^@/]+@)?github.com/([^/]+)/.*#\2#')"
    if command -v gh >/dev/null 2>&1; then
      git -C "$VAULT_DIR" config --local --replace-all credential.helper ''
      git -C "$VAULT_DIR" config --local --add credential.helper \
        "!f() { if [ \"\$1\" = get ]; then echo \"username=$OWNER\"; echo \"password=\$(gh auth token --user $OWNER 2>/dev/null)\"; fi; }; f"
      if gh auth token --user "$OWNER" >/dev/null 2>&1; then
        echo "vault git auth pinned to '$OWNER' (repo-local credential helper)"
      else
        echo "WARN: '$OWNER' not in gh keyring; run: gh auth login (as $OWNER), then re-run bootstrap" >&2
      fi
    else
      echo "WARN: gh CLI not found; vault pushes will use default git credentials" >&2
    fi
    ;;
  *)
    echo "vault remote is not GitHub-HTTPS; skipping credential-helper pin (SSH/other auth applies)"
    ;;
esac

echo ""
echo "Bootstrap complete. Next:"
echo "  1. Personalize $VAULT_DIR/people/me.md"
echo "  2. Open a NEW Claude Code session (any directory) and try: /recall  or  /remember <a fact>"
