#!/bin/bash
# Autonomous task runner.
# Runs Claude Code sessions in a loop. Each session starts with a FRESH context
# and picks up state from .claude/session_state.json + SessionStart hook.
# Each completed task gets a git commit. When a session ends (context full,
# max turns, or no more tasks), a new session starts clean.
#
# Usage: bash scripts/autonomous_run.sh [max_sessions]
# Default: 5 sessions. Each session gets up to 200 agent turns.
# Ctrl+C to stop at any time. Progress is saved in PROGRESS.md and git history.

set -euo pipefail

# --- AR-1: arg validation (workspace-wide invariant INV-AUTORUN-2) ---
# Reject non-integer first arg before main loop. Without this, MAX_SESSIONS=$1
# silently accepts strings like a project name; the script reaches the
# `[ $session_count -lt $MAX_SESSIONS ]` test and crashes deep with
# "integer expression expected". See docs/investigations/autorun_hang_2026-05-02.md.
if [ $# -ge 1 ] && ! [[ "$1" =~ ^[0-9]+$ ]]; then
  echo "[orchestrator] ERROR: max_sessions must be a positive integer; got '$1'" >&2
  echo "[orchestrator] Usage: bash $(basename "$0") [max_sessions]" >&2
  exit 2
fi

# --- AR-2: cwd-sentinel guard (workspace-wide invariant INV-AUTORUN-3) ---
# Refuse to run if the caller's cwd is not the project root. The historical
# script silently `cd`s to the project root regardless of caller cwd, which
# masks misuse (running from /tmp, from a different sub-project, etc.) and
# enables the cross-project drift class we are hardening against.
_AR2_ORIG_PWD="$PWD"
_AR2_SCRIPT_DIR="$(basename "$(dirname "$0")")"
_AR2_SCRIPT_NAME="$(basename "$0")"
_AR2_EXPECTED_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ "$_AR2_ORIG_PWD" != "$_AR2_EXPECTED_ROOT" ]; then
  echo "[orchestrator] ERROR: must be invoked from project root" >&2
  echo "[orchestrator]   expected cwd: $_AR2_EXPECTED_ROOT" >&2
  echo "[orchestrator]   current  cwd: $_AR2_ORIG_PWD" >&2
  echo "[orchestrator] Run: cd \"$_AR2_EXPECTED_ROOT\" && bash $_AR2_SCRIPT_DIR/$_AR2_SCRIPT_NAME [max_sessions]" >&2
  exit 2
fi
cd "$_AR2_EXPECTED_ROOT"
if [ ! -f "CLAUDE.md" ]; then
  echo "[orchestrator] ERROR: project root ($PWD) has no CLAUDE.md (sentinel missing)" >&2
  exit 2
fi

# --- Robustness: ignore SIGPIPE, always log to a file ---
# Previously, launching this script via a Claude Code background subprocess
# capture could kill the orchestrator after the first inner `claude -p`
# session returned: any `echo` to stdout after that point would hit a
# closed fd, SIGPIPE would fire, and `set -e` would terminate the parent
# bash silently. Symptom: one commit landed, then nothing.
#
# Fix: trap and ignore SIGPIPE, AND tee all output to logs/autonomous.log
# so progress is preserved regardless of which fd the parent harness
# captures. The log file is append-only per run.
trap '' PIPE
mkdir -p logs
exec > >(tee -a logs/autonomous.log) 2>&1

# --- PID lockfile for concurrent run protection ---
LOCKFILE=".claude/autonomous.lock"
if [ -f "$LOCKFILE" ] && kill -0 "$(cat "$LOCKFILE")" 2>/dev/null; then
  echo "[orchestrator] Another instance is running (PID $(cat "$LOCKFILE")). Exiting."
  exit 1
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

MAX_SESSIONS=${1:-5}

# Reset stale all_done at orchestrator startup (T-P1-257).
# A previous run may have legitimately drained the queue and set all_done=true,
# but new tasks may have been added since. Inner Claude sessions trust
# session_state and will no-op without re-checking task_db. So: if task_db.py
# reports unblocked work AND state has all_done=true, force all_done=false.
# If task_db is genuinely empty, leave the flag alone (loop will no-op once
# and exit, preserving existing behavior).
STATE_FILE=".claude/session_state.json"
if [ -f "$STATE_FILE" ]; then
  if python .claude/hooks/task_db.py has-unblocked > /dev/null 2>&1; then
    python -c "
import json
with open('$STATE_FILE', encoding='utf-8') as f:
    state = json.load(f)
if state.get('all_done', False):
    state['all_done'] = False
    state['note'] = 'Reset by orchestrator: task_db has unblocked work'
    with open('$STATE_FILE', 'w', encoding='utf-8') as f2:
        json.dump(state, f2, indent=2)
    print('[orchestrator] Reset stale all_done=true (task_db has unblocked tasks)')
" 2>/dev/null || true
  fi
fi

# --- AR-7 + AR-11 + AR-12 + AR-15 + AR-18: timeout+retry wrapper around claude -p ---
# AR-7  (2026-05-02): wrap each invocation with CLAUDE_P_TIMEOUT-second timeout, retry once on hang.
# AR-11 (2026-05-03): distinguish exit-time hang via HEAD diff (non-WIP commit during window -> success).
# AR-12 (2026-05-03): working-tree porcelain hash signal. If WT changed during the window but no commit
#                     landed, extend by CLAUDE_P_TIMEOUT_EXT (default 300s) ONCE within the same attempt.
#                     Catches the "edited files but didn't commit yet" failure mode that AR-11's HEAD-only
#                     signal mis-classifies as no-progress.
# AR-15 (2026-05-03): bump default CLAUDE_P_TIMEOUT 600s -> 900s. AR-12 extension caps worst-case per
#                     attempt at 1200s. Override via env var for L-complexity tasks if needed.
# AR-18 (2026-05-03): attribution check on AR-11 INFO branch. The outer loop sets EXPECTED_TASK_PREFIX
#                     env var (the task ID it expects this session to handle); AR-11 INFO success only
#                     fires when the new commit's [T-XX-N] prefix matches. Closes the 2026-05-03 incident
#                     where a main-thread external commit was credited to the inner session.
#                     Kill switches: CLAUDE_P_DISABLE_PROGRESS_SIGNAL=1 disables AR-12,
#                                    CLAUDE_P_DISABLE_ATTRIBUTION=1     disables AR-18.
# See docs/investigations/autorun_hang_2026-05-02.md and LESSONS.md 2026-05-03 entry.
CLAUDE_P_TIMEOUT="${CLAUDE_P_TIMEOUT:-900}"
CLAUDE_P_TIMEOUT_EXT="${CLAUDE_P_TIMEOUT_EXT:-300}"

# Helper: classify HEAD outcome with AR-18 attribution. Echoes one of:
#   head_legit   — non-WIP commit AND attribution OK (or unset/disabled)
#   head_wip     — WIP-shaped commit (attribution treated as OK because outer loop's expected
#                  prefix matches the WIP task) — caller decides retry vs abort
#   head_external — HEAD moved but commit prefix does NOT match expected (AR-18 rejection)
#   head_unchanged — no commit landed
_classify_head() {
  local start_sha=$1 cur_sha=$2 msg=$3
  if [ "$cur_sha" = "$start_sha" ]; then
    echo "head_unchanged"
    return
  fi
  # AR-18 mandatory sanity: commit must have task-ID shape [T-XXX-NNN] (uppercase letters/digits/hyphens
  # in the prefix portion). Filters out ad-hoc external commits like `[T-adhoc-ar-plan]` (lowercase).
  # Without this gate, ANY non-WIP commit on HEAD would be credited (the 2026-05-03 incident class).
  if [ "${CLAUDE_P_DISABLE_ATTRIBUTION:-0}" != "1" ] && \
     ! [[ "$msg" =~ ^\[T-[A-Z0-9-]+(\ WIP)?\] ]]; then
    echo "head_external"
    return
  fi
  # AR-18 optional tight check: if the outer loop set EXPECTED_TASK_PREFIX, prefer exact match.
  # Mismatch is logged as `head_legit_unexpected` and still credited (relaxed: the inner Claude may
  # have picked a different unblocked task than the peek predicted). Hard rejection happens only at
  # the sanity-regex layer above.
  if [ "${CLAUDE_P_DISABLE_ATTRIBUTION:-0}" != "1" ] && [ -n "${EXPECTED_TASK_PREFIX:-}" ]; then
    if ! [[ "$msg" =~ ^\[${EXPECTED_TASK_PREFIX}[\]\ ] ]]; then
      if [[ "$msg" =~ ^\[T-[A-Z0-9-]+\ WIP\] ]]; then
        echo "head_wip"
      else
        echo "head_legit_unexpected"
      fi
      return
    fi
  fi
  if [[ "$msg" =~ ^\[T-[A-Z0-9-]+\ WIP\] ]]; then
    echo "head_wip"
  else
    echo "head_legit"
  fi
}

run_claude_with_timeout() {
  local attempt rc ts host wrapper_start_sha current_sha latest_msg outcome
  local wrapper_start_porcelain_hash current_porcelain_hash porcelain_dump
  local extended_once=0
  local effective_timeout="${CLAUDE_P_TIMEOUT}s"

  wrapper_start_sha=$(git rev-parse HEAD 2>/dev/null || echo "none")
  wrapper_start_porcelain_hash=$(git status --porcelain 2>/dev/null | sha256sum 2>/dev/null | cut -d' ' -f1)

  for attempt in 1 2; do
    timeout --foreground --kill-after=10s "$effective_timeout" claude "$@"
    rc=$?
    if [ "$rc" -ne 124 ] && [ "$rc" -ne 137 ]; then
      return "$rc"
    fi
    current_sha=$(git rev-parse HEAD 2>/dev/null || echo "none")
    latest_msg=$(git log -1 --pretty=%s 2>/dev/null || echo "")
    current_porcelain_hash=$(git status --porcelain 2>/dev/null | sha256sum 2>/dev/null | cut -d' ' -f1)
    ts="$(date -u +%FT%TZ)"
    host="$(hostname 2>/dev/null || echo unknown)"
    outcome=$(_classify_head "$wrapper_start_sha" "$current_sha" "$latest_msg")

    case "$outcome" in
      head_legit)
        echo "[orchestrator] INFO: claude -p timed out at exit but task committed ($wrapper_start_sha -> $current_sha, msg='${latest_msg:0:80}'). Treating as success. ts=$ts host=$host" >&2
        return 0
        ;;
      head_legit_unexpected)
        echo "[orchestrator] INFO: claude -p committed a different task than peek predicted (expected=$EXPECTED_TASK_PREFIX, msg='${latest_msg:0:80}'). Crediting as success (AR-18 soft attribution). ts=$ts host=$host" >&2
        return 0
        ;;
      head_wip)
        echo "[orchestrator] WARN: claude -p timed out; WIP checkpoint landed but task incomplete (attempt $attempt/2, msg='${latest_msg:0:80}'). ts=$ts host=$host" >&2
        if [ "$attempt" -eq 2 ]; then
          echo "[orchestrator] ERROR: claude -p hung 2x; abort. Task left in WIP state (outer loop will detect new commits). ts=$ts host=$host" >&2
          return 124
        fi
        effective_timeout="${CLAUDE_P_TIMEOUT}s"
        continue
        ;;
      head_external)
        echo "[orchestrator] WARN: HEAD moved but commit prefix does not match expected task ($wrapper_start_sha -> $current_sha, msg='${latest_msg:0:80}', expected=$EXPECTED_TASK_PREFIX). Treating as external commit (AR-18). ts=$ts host=$host" >&2
        # Fall through to AR-12 / AR-7 logic (working-tree may still indicate inner-session progress)
        ;;
      head_unchanged)
        :  # Fall through to AR-12 / AR-7 logic
        ;;
    esac

    # AR-12: if working tree changed but HEAD did not commit attributable progress, extend once.
    if [ "${CLAUDE_P_DISABLE_PROGRESS_SIGNAL:-0}" != "1" ] && \
       [ "$current_porcelain_hash" != "$wrapper_start_porcelain_hash" ] && \
       [ "$extended_once" -eq 0 ]; then
      porcelain_dump=$(git status --porcelain 2>/dev/null | head -5 | tr '\n' '|')
      echo "[orchestrator] INFO: working tree changed during ${effective_timeout} window (AR-12); extending +${CLAUDE_P_TIMEOUT_EXT}s once. porcelain_peek='${porcelain_dump:0:200}'. ts=$ts host=$host" >&2
      extended_once=1
      effective_timeout="${CLAUDE_P_TIMEOUT_EXT}s"
      timeout --foreground --kill-after=10s "$effective_timeout" claude "$@"
      rc=$?
      if [ "$rc" -ne 124 ] && [ "$rc" -ne 137 ]; then
        return "$rc"
      fi
      current_sha=$(git rev-parse HEAD 2>/dev/null || echo "none")
      latest_msg=$(git log -1 --pretty=%s 2>/dev/null || echo "")
      ts="$(date -u +%FT%TZ)"
      outcome=$(_classify_head "$wrapper_start_sha" "$current_sha" "$latest_msg")
      if [ "$outcome" = "head_legit" ] || [ "$outcome" = "head_legit_unexpected" ]; then
        echo "[orchestrator] INFO: claude -p committed during AR-12 extension window ($wrapper_start_sha -> $current_sha, msg='${latest_msg:0:80}', outcome=$outcome). Treating as success. ts=$ts host=$host" >&2
        return 0
      fi
      if [ "$outcome" = "head_wip" ]; then
        echo "[orchestrator] WARN: AR-12 extension landed only WIP commit (attempt $attempt/2, msg='${latest_msg:0:80}'). ts=$ts host=$host" >&2
        if [ "$attempt" -eq 2 ]; then
          echo "[orchestrator] ERROR: claude -p hung 2x; abort. Task left in WIP state. ts=$ts host=$host" >&2
          return 124
        fi
        effective_timeout="${CLAUDE_P_TIMEOUT}s"
        continue
      fi
      # outcome ∈ {head_external, head_unchanged}: extension exhausted, fall through to AR-7
    fi

    # AR-7: no progress (or extension exhausted). Retry once, abort on second hang.
    if [ "$attempt" -eq 1 ]; then
      echo "[orchestrator] WARN: claude -p timed out with no attributable progress (attempt 1/2). Retrying. ts=$ts host=$host" >&2
      effective_timeout="${CLAUDE_P_TIMEOUT}s"
    else
      echo "[orchestrator] ERROR: claude -p hung 2x; abort. Likely transient API/MCP issue or external-commit interference -- try again later. ts=$ts host=$host" >&2
      return 124
    fi
  done
}

session_count=0
consecutive_failures=0
MAX_CONSECUTIVE_FAILURES=2

echo "[orchestrator] Starting autonomous run (max $MAX_SESSIONS sessions)"
echo "[orchestrator] Progress: check git log, PROGRESS.md, TASKS.md"
echo "[orchestrator] Press Ctrl+C to stop. Work is saved after each task."
echo ""

while [ $session_count -lt $MAX_SESSIONS ]; do
  session_count=$((session_count + 1))
  echo "--- Session $session_count/$MAX_SESSIONS ---"

  # Capture commit SHA before session for progress detection
  start_sha=$(git rev-parse HEAD)

  # AR-18: peek the highest-priority unblocked task ID and export as EXPECTED_TASK_PREFIX
  # so the wrapper can verify any new commit during the window matches the inner session's
  # expected task (defends against external commit attribution-poisoning). Best-effort: if
  # inner Claude picks a different unblocked task than peek predicts, the wrapper falls back
  # to "head_legit_unexpected" and still credits the commit (sanity regex still applies).
  EXPECTED_TASK_PREFIX=""
  _peek_id=$(python .claude/hooks/task_db.py list --status active 2>/dev/null | python -c "
import json, sys
try:
    tasks = json.load(sys.stdin)
    if tasks:
        # task_db.py list orders by priority/sort_order; first item is the likely pick.
        print(tasks[0]['id'])
except Exception:
    pass
" 2>/dev/null || true)
  if [ -n "$_peek_id" ]; then
    EXPECTED_TASK_PREFIX="$_peek_id"
    export EXPECTED_TASK_PREFIX
    echo "[orchestrator] AR-18: EXPECTED_TASK_PREFIX=$EXPECTED_TASK_PREFIX (peeked from task_db)"
  else
    unset EXPECTED_TASK_PREFIX
  fi

  exit_code=0
  run_claude_with_timeout -p "Autonomous mode. Read TASKS.md, pick ONE highest-priority unblocked task, \
    and complete it. After completing the task: \
    1) run tests, 2) update PROGRESS.md and TASKS.md, 3) git commit with message \
    format '[T-XX-N] description', 4) update .claude/session_state.json, then stop. \
    If no unblocked tasks remain, set all_done=true in session_state.json and stop." \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep,Task" \
    --max-turns 200 || exit_code=$?

  if [ $exit_code -eq 0 ]; then
    consecutive_failures=0
    # Check if all tasks done
    # Note: use `python`, not `python3`. On Windows git-bash, `python3` may
    # resolve to AppData/Local/Microsoft/WindowsApps/python3 (the Windows
    # Store stub) which exits with code 49 and never runs the script. That
    # would silently always take the "not all done" branch, which is at
    # least benign here but masks real failures. Project convention per
    # CLAUDE.md: never use bare `python3` in scripts on this machine.
    if python -c "
import json, sys
try:
    with open('.claude/session_state.json', encoding='utf-8') as f:
        state = json.load(f)
    if state.get('all_done', False):
        sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
      echo "[orchestrator] All tasks complete!"
      break
    fi
    echo "[orchestrator] Session ended. Continuing in next session..."
  else
    # Git stash on failed session
    git stash push -m "auto-stash: failed session $session_count" 2>/dev/null || true

    # Distinguish context exhaustion from real failure
    current_sha=$(git rev-parse HEAD)
    if [ "$current_sha" != "$start_sha" ]; then
      # New commits were made -- task is progressing (context exhaustion, not failure)
      echo "[orchestrator] Session made progress (new commits). Not counting as failure."
      consecutive_failures=0
    else
      consecutive_failures=$((consecutive_failures + 1))
      echo "[orchestrator] Session failed ($consecutive_failures/$MAX_CONSECUTIVE_FAILURES)"
      if [ $consecutive_failures -ge $MAX_CONSECUTIVE_FAILURES ]; then
        echo "[orchestrator] Too many consecutive failures. Stopping."
        break
      fi
    fi
  fi
  echo ""
done

echo ""
echo "[orchestrator] Finished after $session_count session(s)"
echo "[orchestrator] Review: git log --oneline -20"
echo "[orchestrator] Status: cat TASKS.md"
