#!/usr/bin/env bash
set -euo pipefail

# Resolve the vault dir = directory containing this script (works wherever cloned)
VAULT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
GLOBAL_MD="$CLAUDE_DIR/CLAUDE.md"
MARKER_BEGIN="<!-- BEGIN ambient-brain -->"

# Optional subsystems are off by default; opt in with flags.
WITH_FATHOM=0
for arg in "$@"; do
  case "$arg" in
    --with-fathom) WITH_FATHOM=1 ;;
    *) echo "unknown option: $arg (supported: --with-fathom)" >&2; exit 2 ;;
  esac
done

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

# 4. Fathom auto-ingest: LaunchAgent + the SessionStart hook that surfaces it.
# The vault claims to be portable, so the automation that feeds it has to be
# installed from the repo rather than living only on one laptop.
# Opt-in: runs only with --with-fathom (and only when the directory exists).
AI_DIR="$VAULT_DIR/install/fathom-autoingest"
if [ "$WITH_FATHOM" = 0 ]; then
  echo "fathom auto-ingest not installed (opt in with: ./bootstrap.sh --with-fathom)"
elif [ -d "$AI_DIR" ]; then
  chmod +x "$AI_DIR"/*.sh 2>/dev/null || true

  case "$(uname -s)" in
    Darwin)
      LA_DIR="$HOME/Library/LaunchAgents"
      PLIST_LABEL="com.ambient-brain.fathom-autoingest"
      mkdir -p "$LA_DIR"
      sed -e "s#__VAULT_DIR__#$VAULT_DIR#g" -e "s#__HOME__#$HOME#g" \
        "$AI_DIR/$PLIST_LABEL.plist" >"$LA_DIR/$PLIST_LABEL.plist"
      # Reload so an edited schedule takes effect. RunAtLoad is false in the
      # plist, so this does NOT trigger an immediate ingest.
      launchctl bootout "gui/$(id -u)/$PLIST_LABEL" 2>/dev/null || true
      if launchctl bootstrap "gui/$(id -u)" "$LA_DIR/$PLIST_LABEL.plist" 2>/dev/null; then
        echo "fathom auto-ingest LaunchAgent installed + loaded (09:30 + 17:00 local)"
      else
        echo "WARN: could not load $PLIST_LABEL; load it with:" >&2
        echo "      launchctl bootstrap gui/$(id -u) $LA_DIR/$PLIST_LABEL.plist" >&2
      fi
      ;;
    *)
      echo "not macOS; skipping the fathom auto-ingest LaunchAgent (run.sh still works by hand)"
      ;;
  esac

  # SessionStart hook — the only thing that surfaces a pending ingest, so its
  # absence silently defeats the whole design. Idempotent; backs up first.
  SETTINGS="$CLAUDE_DIR/settings.json"
  HOOK_CMD="bash $AI_DIR/pending.sh"
  if command -v python3 >/dev/null 2>&1; then
    # `|| true`: bootstrap runs under `set -e`, and this step is a nice-to-have.
    # A settings.json we cannot parse must not abort the run and swallow the
    # "Bootstrap complete" instructions below — it warns and moves on.
    HOOK_CMD="$HOOK_CMD" SETTINGS="$SETTINGS" python3 - <<'PY' || true
import json, os, shutil, tempfile
settings, cmd = os.environ["SETTINGS"], os.environ["HOOK_CMD"]
data = {}
if os.path.exists(settings):
    try:
        with open(settings) as fh:
            data = json.load(fh)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"WARN: {settings} unreadable ({exc}); add the hook by hand: {cmd}")
    shutil.copy2(settings, settings + ".bak")

# Valid JSON is not the same as the shape we expect; refuse rather than crash
# with a traceback (or, worse, clobber a settings file we misread).
def bad(what):
    raise SystemExit(f"WARN: {settings} has an unexpected {what}; add the hook by hand: {cmd}")

if not isinstance(data, dict):
    bad("top level (expected an object)")
hooks = data.setdefault("hooks", {})
if not isinstance(hooks, dict):
    bad("'hooks' value (expected an object)")
groups = hooks.setdefault("SessionStart", [])
if not isinstance(groups, list):
    bad("'hooks.SessionStart' value (expected an array)")

present = any(
    h.get("command") == cmd
    for g in groups if isinstance(g, dict)
    for h in g.get("hooks", []) if isinstance(h, dict)
)
if present:
    print("fathom pending-work SessionStart hook already present")
else:
    groups.append({"hooks": [{"type": "command", "command": cmd}]})
    os.makedirs(os.path.dirname(settings) or ".", exist_ok=True)
    # Write via a temp file + rename: an interrupted write here would leave the
    # user with no usable global settings at all.
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(settings) or ".", prefix=".settings-")
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, settings)
    print("added fathom pending-work SessionStart hook to " + settings)
PY
  else
    echo "WARN: python3 not found; add a SessionStart hook by hand: $HOOK_CMD" >&2
  fi
fi

echo ""
echo "Bootstrap complete. Next:"
echo "  1. Personalize $VAULT_DIR/people/me.md"
echo "  2. Open a NEW Claude Code session (any directory) and try: /recall  or  /remember <a fact>"
