#!/bin/bash
# Install project git hooks into .git/hooks/.
# Usage: bash scripts/setup-hooks.sh
#
# - Copies scripts/git-hooks/* into .git/hooks/
# - Backs up any existing non-sample hooks before overwriting
# - Sets executable permission on installed hooks

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/scripts/git-hooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_SRC" ]; then
    echo "[FAIL] $HOOKS_SRC not found. Run from repo root." >&2
    exit 1
fi

if [ ! -d "$HOOKS_DST" ]; then
    echo "[FAIL] $HOOKS_DST not found. Is this a git repository?" >&2
    exit 1
fi

installed=0
for hook in "$HOOKS_SRC"/*; do
    [ -f "$hook" ] || continue
    name="$(basename "$hook")"
    dst="$HOOKS_DST/$name"

    # Back up existing hook (skip .sample files)
    if [ -f "$dst" ] && [ "${dst%.sample}" = "$dst" ]; then
        backup="$dst.backup.$(date +%Y%m%d%H%M%S)"
        cp "$dst" "$backup"
        echo "[INFO] Backed up existing $name -> $(basename "$backup")"
    fi

    cp "$hook" "$dst"
    chmod +x "$dst"
    installed=$((installed + 1))
    echo "[OK] Installed $name"
done

if [ "$installed" -eq 0 ]; then
    echo "[WARN] No hooks found in $HOOKS_SRC"
else
    echo "[DONE] Installed $installed hook(s) into .git/hooks/"
fi
