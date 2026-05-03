#!/bin/bash
# AR-11 wrapper test driver. Sources run_claude_with_timeout from autonomous_run.sh
# and exercises 4 scenarios in isolated temp git repos with stubbed `claude` binary.
# Usage: bash scripts/_test_ar11_wrapper.sh
# Exit 0 = all 4 tests pass. Non-zero = at least one assertion failed.

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUTONOMOUS_SCRIPT="$SCRIPT_DIR/autonomous_run.sh"

if [ ! -f "$AUTONOMOUS_SCRIPT" ]; then
  echo "FAIL: $AUTONOMOUS_SCRIPT not found"
  exit 2
fi

# Extract just the run_claude_with_timeout function definition + its CLAUDE_P_TIMEOUT
# default. Use sed range from the line containing 'CLAUDE_P_TIMEOUT="${CLAUDE_P_TIMEOUT'
# to the closing brace of run_claude_with_timeout. The function ends with `}` on its
# own line followed by the next blank line.
WRAPPER_DEF=$(sed -n '/^CLAUDE_P_TIMEOUT="\${CLAUDE_P_TIMEOUT/,/^}$/p' "$AUTONOMOUS_SCRIPT")
if ! echo "$WRAPPER_DEF" | grep -q "timed out at exit but task committed"; then
  echo "FAIL: extracted wrapper missing AR-11 INFO line. Extraction regex stale?"
  echo "----- extracted -----"
  echo "$WRAPPER_DEF"
  echo "---------------------"
  exit 2
fi

PASS=0
FAIL=0
FAILED_TESTS=()

# --- helpers ---

setup_sandbox() {
  local sandbox
  sandbox=$(mktemp -d)
  (
    cd "$sandbox"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test"
    echo "init" > README
    git add README
    git commit -q -m "init"
  )
  echo "$sandbox"
}

# Build a stub `claude` script. Args: <stub_dir> <behavior>
# behaviors:
#   exit-hang-with-completion: commit a file then sleep 999 (simulate exit hang after work done)
#   zero-progress: just sleep 999
#   wip-only: commit with [T-XXXX WIP] message then sleep 999
#   happy: commit + exit 0 cleanly
build_stub() {
  local stub_dir="$1"
  local behavior="$2"
  local sandbox="$3"
  mkdir -p "$stub_dir"
  case "$behavior" in
    exit-hang-with-completion)
      cat > "$stub_dir/claude" <<EOF
#!/bin/bash
cd "$sandbox"
echo "stub: simulating completed work" >&2
echo "done" > work.txt
git add work.txt
git commit -q -m "[T-P0-9999] real task completion"
echo "stub: now hanging at exit" >&2
sleep 999
EOF
      ;;
    zero-progress)
      cat > "$stub_dir/claude" <<EOF
#!/bin/bash
echo "stub: hanging from start, no progress" >&2
sleep 999
EOF
      ;;
    wip-only)
      cat > "$stub_dir/claude" <<EOF
#!/bin/bash
cd "$sandbox"
echo "stub: making WIP checkpoint then hanging" >&2
echo "wip" > wip.txt
git add wip.txt
git commit -q -m "[T-P0-9999 WIP] partial progress"
echo "stub: now hanging" >&2
sleep 999
EOF
      ;;
    happy)
      cat > "$stub_dir/claude" <<EOF
#!/bin/bash
cd "$sandbox"
echo "stub: completing normally" >&2
echo "happy" > happy.txt
git add happy.txt
git commit -q -m "[T-P0-9999] happy completion"
exit 0
EOF
      ;;
  esac
  chmod +x "$stub_dir/claude"
}

# Run wrapper in a subshell with PATH overridden so our stub `claude` wins.
# Returns: rc on stdout line 1, log content on subsequent lines.
# Args: <sandbox> <stub_dir> <timeout_s>
run_wrapper() {
  local sandbox="$1"
  local stub_dir="$2"
  local timeout_s="$3"
  local logfile
  logfile=$(mktemp)
  local rc
  (
    cd "$sandbox"
    export CLAUDE_P_TIMEOUT="$timeout_s"
    export PATH="$stub_dir:$PATH"
    eval "$WRAPPER_DEF"
    set +e
    run_claude_with_timeout -p "test"
    echo "WRAPPER_RC=$?"
  ) > "$logfile" 2>&1
  rc=$?
  cat "$logfile"
  rm -f "$logfile"
  return $rc
}

assert() {
  local name="$1"
  local cond="$2"
  if [ "$cond" = "true" ] || [ "$cond" = "0" ]; then
    PASS=$((PASS + 1))
    echo "  PASS: $name"
  else
    FAIL=$((FAIL + 1))
    FAILED_TESTS+=("$name")
    echo "  FAIL: $name"
  fi
}

# --- Test 1: exit-hang-with-completion ---
echo ""
echo "=== Test 1: exit-hang-with-completion (the bug we are fixing) ==="
SANDBOX=$(setup_sandbox)
STUB=$(mktemp -d)
build_stub "$STUB" "exit-hang-with-completion" "$SANDBOX"
OUT=$(run_wrapper "$SANDBOX" "$STUB" 5)
echo "----- output -----"
echo "$OUT"
echo "------------------"

INFO_COUNT=$(echo "$OUT" | grep -c "timed out at exit but task committed")
RETRY_COUNT=$(echo "$OUT" | grep -c "Retrying")
WRAPPER_RC=$(echo "$OUT" | grep -oE 'WRAPPER_RC=[0-9]+' | sed 's/WRAPPER_RC=//')

if [ "$INFO_COUNT" -eq 1 ]; then assert "1 INFO line" "true"; else assert "1 INFO line (got $INFO_COUNT)" "false"; fi
if [ "$RETRY_COUNT" -eq 0 ]; then assert "no Retrying" "true"; else assert "no Retrying (got $RETRY_COUNT)" "false"; fi
if [ "$WRAPPER_RC" = "0" ]; then assert "wrapper rc=0" "true"; else assert "wrapper rc=0 (got $WRAPPER_RC)" "false"; fi
rm -rf "$SANDBOX" "$STUB"

# --- Test 2: zero-progress hang ---
echo ""
echo "=== Test 2: zero-progress hang (regression check) ==="
SANDBOX=$(setup_sandbox)
STUB=$(mktemp -d)
build_stub "$STUB" "zero-progress" "$SANDBOX"
OUT=$(run_wrapper "$SANDBOX" "$STUB" 3)
echo "----- output -----"
echo "$OUT"
echo "------------------"

WARN1=$(echo "$OUT" | grep -c "no progress (attempt 1/2)")
ERROR_COUNT=$(echo "$OUT" | grep -c "hung 2x; abort")
WRAPPER_RC=$(echo "$OUT" | grep -oE 'WRAPPER_RC=[0-9]+' | sed 's/WRAPPER_RC=//')

if [ "$WARN1" -eq 1 ]; then assert "WARN attempt 1/2" "true"; else assert "WARN attempt 1/2 (got $WARN1)" "false"; fi
if [ "$ERROR_COUNT" -eq 1 ]; then assert "ERROR hung 2x" "true"; else assert "ERROR hung 2x (got $ERROR_COUNT)" "false"; fi
if [ "$WRAPPER_RC" = "124" ]; then assert "wrapper rc=124" "true"; else assert "wrapper rc=124 (got $WRAPPER_RC)" "false"; fi
rm -rf "$SANDBOX" "$STUB"

# --- Test 3: WIP-only commit then hang ---
echo ""
echo "=== Test 3: WIP-only commit (false-positive guard) ==="
SANDBOX=$(setup_sandbox)
STUB=$(mktemp -d)
build_stub "$STUB" "wip-only" "$SANDBOX"
OUT=$(run_wrapper "$SANDBOX" "$STUB" 3)
echo "----- output -----"
echo "$OUT"
echo "------------------"

WIP_WARN=$(echo "$OUT" | grep -c "WIP checkpoint landed but task incomplete")
INFO_COUNT=$(echo "$OUT" | grep -c "timed out at exit but task committed")
WRAPPER_RC=$(echo "$OUT" | grep -oE 'WRAPPER_RC=[0-9]+' | sed 's/WRAPPER_RC=//')

if [ "$WIP_WARN" -ge 1 ]; then assert "WIP-incomplete WARN appears" "true"; else assert "WIP-incomplete WARN (got $WIP_WARN)" "false"; fi
if [ "$INFO_COUNT" -eq 0 ]; then assert "no false-positive INFO" "true"; else assert "no false-positive INFO (got $INFO_COUNT)" "false"; fi
if [ "$WRAPPER_RC" = "124" ]; then assert "wrapper rc=124 (retry exhausted)" "true"; else assert "wrapper rc=124 (got $WRAPPER_RC)" "false"; fi
rm -rf "$SANDBOX" "$STUB"

# --- Test 4: happy path ---
echo ""
echo "=== Test 4: happy path (no timeout fires) ==="
SANDBOX=$(setup_sandbox)
STUB=$(mktemp -d)
build_stub "$STUB" "happy" "$SANDBOX"
OUT=$(run_wrapper "$SANDBOX" "$STUB" 30)
echo "----- output -----"
echo "$OUT"
echo "------------------"

INFO_COUNT=$(echo "$OUT" | grep -c "timed out at exit")
WARN_COUNT=$(echo "$OUT" | grep -c "WARN:")
ERROR_COUNT=$(echo "$OUT" | grep -c "ERROR:")
WRAPPER_RC=$(echo "$OUT" | grep -oE 'WRAPPER_RC=[0-9]+' | sed 's/WRAPPER_RC=//')

if [ "$INFO_COUNT" -eq 0 ]; then assert "no INFO line" "true"; else assert "no INFO line (got $INFO_COUNT)" "false"; fi
if [ "$WARN_COUNT" -eq 0 ]; then assert "no WARN line" "true"; else assert "no WARN line (got $WARN_COUNT)" "false"; fi
if [ "$ERROR_COUNT" -eq 0 ]; then assert "no ERROR line" "true"; else assert "no ERROR line (got $ERROR_COUNT)" "false"; fi
if [ "$WRAPPER_RC" = "0" ]; then assert "wrapper rc=0" "true"; else assert "wrapper rc=0 (got $WRAPPER_RC)" "false"; fi
rm -rf "$SANDBOX" "$STUB"

# --- Summary ---
echo ""
echo "============================================="
echo "AR-11 wrapper tests: PASS=$PASS  FAIL=$FAIL"
if [ "$FAIL" -gt 0 ]; then
  echo "Failed assertions:"
  for t in "${FAILED_TESTS[@]}"; do
    echo "  - $t"
  done
  exit 1
fi
echo "All tests passed."
exit 0
