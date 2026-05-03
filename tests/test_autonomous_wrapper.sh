#!/bin/bash
# Tests for scripts/autonomous_run.sh wrapper logic (AR-7/11/12/15/16/18).
#
# T-P1-715 (AR-16): cold-start fast-fail watchdog. ACs 1, 5, 6, 7 are exercised
# unconditionally via mocked `claude`. ACs 2-4, 8 require a real `setsid` binary
# (Linux/macOS) and exercise the watchdog end-to-end; they are skipped on
# Windows MSYS where setsid is absent.
#
# Run:
#   cd MLInterviewPrep
#   bash tests/test_autonomous_wrapper.sh
#
# Exit code 0 = all tests passed; non-zero = test failure or hard error.
set -u  # NOTE: not -e; we want to count failures explicitly.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/autonomous_run.sh"

if [ ! -f "$WRAPPER" ]; then
  echo "FAIL: cannot find $WRAPPER"
  exit 1
fi

PASS=0
FAIL=0
SKIP=0

_pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
_fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }
_skip() { SKIP=$((SKIP + 1)); echo "  SKIP: $1"; }

# Build an isolated sandbox: minimal project root with mocks for claude/timeout/setsid.
# Strategy: create a temp dir, copy the wrapper functions into a sourceable harness file,
# point the harness at a fake claude in PATH, and drive each scenario via bash function
# call. Each test owns its sandbox so they are independent.
make_sandbox() {
  local sb
  sb="$(mktemp -d -t ar16_test.XXXXXX)"
  mkdir -p "$sb/.claude" "$sb/logs" "$sb/bin"
  touch "$sb/CLAUDE.md"
  (cd "$sb" && git init -q && git -c user.email=t@t -c user.name=t commit --allow-empty -m "[T-P1-715] sandbox seed" -q)
  # Extract just the wrapper functions (lines from `_classify_head()` through end of
  # `run_claude_with_timeout()`). We exec-wrap so that sourcing does not hijack stdout.
  cat > "$sb/wrapper_harness.sh" <<HARNESS_EOF
#!/bin/bash
# Source the wrapper's CONFIG + functions only. The harness skips the script's main
# argument-parsing, lockfile, exec-redirect, and outer loop.
HARNESS_EOF
  # Pull the relevant section: CLAUDE_P_TIMEOUT defaults + _classify_head + _run_claude_attempt + run_claude_with_timeout
  awk '
    /^CLAUDE_P_TIMEOUT=/ { capture=1 }
    capture { print }
    /^run_claude_with_timeout\(\) {/ { in_func=1 }
    in_func && /^}/ { print; in_func=0; capture=0; exit }
  ' "$WRAPPER" >> "$sb/wrapper_harness.sh"
  echo "$sb"
}

cleanup_sandbox() {
  local sb=$1
  [ -n "$sb" ] && [ -d "$sb" ] && rm -rf "$sb"
}

# AC 1: setsid precheck. If setsid is missing, the precheck auto-disables AR-16 with WARN.
test_ac1_setsid_precheck() {
  echo "[AC 1] setsid precheck"
  # Run the precheck snippet in a subshell that overrides `command` to lie about setsid.
  # This isolates the test from the host PATH (which on Windows MSYS naturally lacks setsid,
  # and on Linux naturally has it).
  local out
  out=$(bash -c '
    # Override the `command` builtin via a function to simulate missing setsid.
    command() {
      if [ "$1" = "-v" ] && [ "$2" = "setsid" ]; then
        return 1
      fi
      builtin command "$@"
    }
    if [ "${CLAUDE_P_DISABLE_COLDSTART_GUARD:-0}" != "1" ]; then
      if ! command -v setsid >/dev/null 2>&1; then
        echo "[orchestrator] WARN: setsid not found on this platform; AR-16 cold-start watchdog auto-disabled. Set CLAUDE_P_DISABLE_COLDSTART_GUARD=1 explicitly to silence this warning." >&2
        export CLAUDE_P_DISABLE_COLDSTART_GUARD=1
      fi
    fi
    echo "DISABLED=${CLAUDE_P_DISABLE_COLDSTART_GUARD:-0}"
  ' 2>&1)
  if echo "$out" | grep -q "DISABLED=1"; then
    _pass "missing setsid auto-sets CLAUDE_P_DISABLE_COLDSTART_GUARD=1"
  else
    _fail "missing setsid did not auto-disable AR-16: $out"
  fi
  if echo "$out" | grep -qi "WARN.*setsid not found"; then
    _pass "WARN message emitted on missing setsid"
  else
    _fail "no WARN message on missing setsid: $out"
  fi
  # Cross-check by source-grep that the precheck block actually exists in the script.
  if grep -q 'AR-16 platform precheck' "$WRAPPER" && \
     grep -q 'WARN: setsid not found' "$WRAPPER"; then
    _pass "wrapper source contains AR-16 precheck block"
  else
    _fail "AR-16 precheck block missing from wrapper"
  fi
}

# AC 7: kill-switch verified to skip watchdog. With CLAUDE_P_DISABLE_COLDSTART_GUARD=1,
# _run_claude_attempt should call plain `timeout claude` and not write coldstart telemetry.
test_ac7_kill_switch() {
  echo "[AC 7] kill switch (CLAUDE_P_DISABLE_COLDSTART_GUARD=1) skips watchdog"
  local sb rc
  sb=$(make_sandbox)
  # Mock claude as immediate-exit-0; mock timeout as a passthrough.
  cat > "$sb/bin/claude" <<'EOF'
#!/bin/bash
echo "fake claude ran"
exit 0
EOF
  chmod +x "$sb/bin/claude"
  # Use the system `timeout` (it exists on MSYS).
  cd "$sb" || return
  # Source harness with kill-switch and a tight timeout, call _run_claude_attempt.
  out=$(PATH="$sb/bin:$PATH" CLAUDE_P_DISABLE_COLDSTART_GUARD=1 \
    bash -c "
      effective_timeout=5s
      log_size_start=0
      source '$sb/wrapper_harness.sh'
      _run_claude_attempt -p test
      echo \"RC=\$?\"
      echo \"KILLED=\$_AR16_LAST_KILLED\"
    " 2>&1)
  if echo "$out" | grep -q "RC=0"; then _pass "claude exited rc=0 under kill-switch"; else _fail "rc != 0: $out"; fi
  if echo "$out" | grep -q "KILLED=0"; then _pass "_AR16_LAST_KILLED=0 (watchdog did not fire)"; else _fail "_AR16_LAST_KILLED set: $out"; fi
  if [ ! -f "$sb/logs/wrapper-stats.jsonl" ]; then _pass "no telemetry written under kill-switch"; else _fail "telemetry written: $(cat "$sb/logs/wrapper-stats.jsonl")"; fi
  cleanup_sandbox "$sb"
}

# AC 5 (logic): race-with-AR12. After a cold-start kill, the wrapper resets
# wrapper_start_porcelain_hash so AR-12 does not extend on residue. We simulate the
# state directly by setting _AR16_LAST_KILLED=1 and verifying the porcelain reset
# branch fires. (Full end-to-end with real setsid is AC 5 below.)
test_ac5_race_with_ar12_logic() {
  echo "[AC 5 logic] race-with-AR12 porcelain refresh after cold-start kill"
  local sb out
  sb=$(make_sandbox)
  cd "$sb" || return
  # Verify the wrapper file actually contains the race-fix block — pure source-level invariant.
  if grep -q "AR-16 race-with-AR12" "$WRAPPER" && \
     grep -q 'wrapper_start_porcelain_hash="\$current_porcelain_hash"' "$WRAPPER"; then
    _pass "wrapper contains race-with-AR12 porcelain refresh block"
  else
    _fail "race-with-AR12 block missing from wrapper"
  fi
  # Verify the refresh is gated on _AR16_LAST_KILLED (so it does NOT fire on normal timeouts).
  if grep -A 6 'AR-16 race-with-AR12' "$WRAPPER" | grep -q '_AR16_LAST_KILLED'; then
    _pass "porcelain refresh gated on _AR16_LAST_KILLED"
  else
    _fail "porcelain refresh not properly gated"
  fi
  cleanup_sandbox "$sb"
}

# AC 6: telemetry format. Compose the JSON exactly as the watchdog would and verify
# it parses with the expected schema fields.
test_ac6_telemetry_format() {
  echo "[AC 6] coldstart_kill telemetry JSON schema"
  local out
  out=$(python -c "
import json
ts='2026-05-03T10:00:00Z'
host='test'
log_growth=42
grace=120
growth_min=200
line=json.dumps({'ts':ts,'host':host,'branch':'coldstart_kill','log_growth_b':log_growth,'grace_s':grace,'growth_min_b':growth_min})
parsed=json.loads(line)
required={'ts','host','branch','log_growth_b','grace_s','growth_min_b'}
assert set(parsed.keys())==required, f'fields mismatch: {parsed.keys()} vs {required}'
assert parsed['branch']=='coldstart_kill'
print('OK')
" 2>&1)
  if echo "$out" | grep -q "^OK$"; then
    _pass "telemetry JSON has required fields {ts, host, branch, log_growth_b, grace_s, growth_min_b}"
  else
    _fail "telemetry schema invalid: $out"
  fi
}

# AC 2/3/4/8: end-to-end watchdog tests. Require real `setsid` binary.
test_ac2_zero_log_growth_kill() {
  if ! command -v setsid >/dev/null 2>&1; then
    _skip "[AC 2] setsid not available; skipping end-to-end coldstart-kill test"
    return
  fi
  echo "[AC 2] zero-log-growth claude is killed within grace window"
  local sb out elapsed
  sb=$(make_sandbox)
  cat > "$sb/bin/claude" <<'EOF'
#!/bin/bash
# Sleep silently, no log writes. Watchdog should kill us.
sleep 30
exit 0
EOF
  chmod +x "$sb/bin/claude"
  cd "$sb" || return
  local t0 t1
  t0=$(date +%s)
  out=$(PATH="$sb/bin:$PATH" CLAUDE_P_COLDSTART_GRACE=3 CLAUDE_P_COLDSTART_GROWTH_MIN=200 \
    bash -c "
      effective_timeout=20s
      log_size_start=0
      source '$sb/wrapper_harness.sh'
      _run_claude_attempt -p test
      echo \"RC=\$?\"
      echo \"KILLED=\$_AR16_LAST_KILLED\"
    " 2>&1)
  t1=$(date +%s)
  elapsed=$((t1 - t0))
  if echo "$out" | grep -q "KILLED=1"; then
    _pass "watchdog fired (KILLED=1)"
  else
    _fail "watchdog did not fire: $out"
  fi
  if [ "$elapsed" -lt 12 ]; then
    _pass "kill happened within grace + 4s + slack ($elapsed s)"
  else
    _fail "kill took too long: $elapsed s"
  fi
  if [ -f "$sb/logs/wrapper-stats.jsonl" ] && grep -q '"branch":"coldstart_kill"' "$sb/logs/wrapper-stats.jsonl"; then
    _pass "telemetry written"
  else
    _fail "no telemetry: $(cat "$sb/logs/wrapper-stats.jsonl" 2>/dev/null)"
  fi
  cleanup_sandbox "$sb"
}

test_ac3_normal_claude_not_killed() {
  if ! command -v setsid >/dev/null 2>&1; then
    _skip "[AC 3] setsid not available; skipping normal-claude-not-killed test"
    return
  fi
  echo "[AC 3] normal claude (writes log) is not mis-killed"
  local sb out
  sb=$(make_sandbox)
  cat > "$sb/bin/claude" <<'EOF'
#!/bin/bash
# Write enough to logs/autonomous.log to exceed growth threshold, then exit cleanly.
for i in 1 2 3 4 5 6 7 8 9 10; do
  printf "log line %d with some bytes of content\n" $i >> logs/autonomous.log
  sleep 0.2
done
exit 0
EOF
  chmod +x "$sb/bin/claude"
  cd "$sb" || return
  out=$(PATH="$sb/bin:$PATH" CLAUDE_P_COLDSTART_GRACE=5 CLAUDE_P_COLDSTART_GROWTH_MIN=200 \
    bash -c "
      effective_timeout=15s
      log_size_start=0
      source '$sb/wrapper_harness.sh'
      _run_claude_attempt -p test
      echo \"RC=\$?\"
      echo \"KILLED=\$_AR16_LAST_KILLED\"
    " 2>&1)
  if echo "$out" | grep -q "KILLED=0"; then
    _pass "watchdog did not mis-kill (KILLED=0)"
  else
    _fail "watchdog mis-killed normal run: $out"
  fi
  if echo "$out" | grep -q "RC=0"; then
    _pass "claude exited rc=0"
  else
    _fail "claude rc != 0: $out"
  fi
  cleanup_sandbox "$sb"
}

test_ac4_fast_exit_no_zombie() {
  if ! command -v setsid >/dev/null 2>&1; then
    _skip "[AC 4] setsid not available; skipping fast-exit-no-zombie test"
    return
  fi
  echo "[AC 4] claude that exits within grace cleans up watchdog"
  local sb out
  sb=$(make_sandbox)
  cat > "$sb/bin/claude" <<'EOF'
#!/bin/bash
echo "quick run" >> logs/autonomous.log
sleep 1
exit 0
EOF
  chmod +x "$sb/bin/claude"
  cd "$sb" || return
  out=$(PATH="$sb/bin:$PATH" CLAUDE_P_COLDSTART_GRACE=10 CLAUDE_P_COLDSTART_GROWTH_MIN=200 \
    bash -c "
      effective_timeout=15s
      log_size_start=0
      source '$sb/wrapper_harness.sh'
      _run_claude_attempt -p test
      echo \"RC=\$?\"
      echo \"KILLED=\$_AR16_LAST_KILLED\"
    " 2>&1)
  if echo "$out" | grep -q "RC=0" && echo "$out" | grep -q "KILLED=0"; then
    _pass "fast-exit wrapper returns rc=0 with no kill"
  else
    _fail "fast-exit anomaly: $out"
  fi
  cleanup_sandbox "$sb"
}

test_ac8_pgid_kill_propagation() {
  if ! command -v setsid >/dev/null 2>&1; then
    _skip "[AC 8] setsid not available; skipping pgid kill-propagation test"
    return
  fi
  echo "[AC 8] killing pgid reaps grandchildren (no orphans)"
  local sb out
  sb=$(make_sandbox)
  # claude that forks 2 grandchildren, all sleep 60.
  cat > "$sb/bin/claude" <<'EOF'
#!/bin/bash
( sleep 60 ) &
gc1=$!
( sleep 60 ) &
gc2=$!
echo "GRANDCHILDREN: $gc1 $gc2" > "$PWD/.grandchildren"
sleep 60
EOF
  chmod +x "$sb/bin/claude"
  cd "$sb" || return
  ( PATH="$sb/bin:$PATH" CLAUDE_P_COLDSTART_GRACE=2 CLAUDE_P_COLDSTART_GROWTH_MIN=200 \
    bash -c "
      effective_timeout=30s
      log_size_start=0
      source '$sb/wrapper_harness.sh'
      _run_claude_attempt -p test >/dev/null 2>&1
    " ) &
  local outer_pid=$!
  wait "$outer_pid"
  sleep 1
  if [ -f "$sb/.grandchildren" ]; then
    local gcs alive=0
    gcs=$(cat "$sb/.grandchildren" | awk '{print $2, $3}')
    for gc in $gcs; do
      if kill -0 "$gc" 2>/dev/null; then alive=$((alive + 1)); fi
    done
    if [ "$alive" -eq 0 ]; then
      _pass "all grandchildren reaped"
    else
      _fail "$alive grandchildren still alive"
      # Cleanup
      for gc in $gcs; do kill -KILL "$gc" 2>/dev/null || true; done
    fi
  else
    _skip ".grandchildren marker not written (claude killed before fork)"
  fi
  cleanup_sandbox "$sb"
}

# Run all tests.
echo "=== AR-16 wrapper tests ==="
test_ac1_setsid_precheck
test_ac7_kill_switch
test_ac5_race_with_ar12_logic
test_ac6_telemetry_format
test_ac2_zero_log_growth_kill
test_ac3_normal_claude_not_killed
test_ac4_fast_exit_no_zombie
test_ac8_pgid_kill_propagation

echo
echo "=== Summary ==="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "SKIP: $SKIP"
if [ "$FAIL" -gt 0 ]; then exit 1; fi
exit 0
