#!/bin/bash
# Unit test for _classify_head function in scripts/autonomous_run.sh
# Validates AR-11 + AR-18 attribution logic across all branches.
#
# Run from MLInterviewPrep root: bash logs/_test_wrapper_classify.sh
# Expected: all PASS, exit 0.
#
# Note: extracts only the function definition (not the side-effects from sourcing the full
# script) by piping the function body through bash. Avoids touching .claude/autonomous.lock.

set -uo pipefail

cd "$(dirname "$0")/.."

# Source just the _classify_head function by extracting its definition.
# The function spans from `_classify_head() {` to the next standalone `}` at column 0.
eval "$(sed -n '/^_classify_head() {$/,/^}$/p' scripts/autonomous_run.sh)"

# Test counter
total=0
passed=0
failed=()

run_test() {
  local name=$1 expected=$2
  local start=$3 cur=$4 msg=$5
  shift 5
  # Optional env overrides per test
  local got
  total=$((total + 1))
  got=$(_classify_head "$start" "$cur" "$msg")
  if [ "$got" = "$expected" ]; then
    passed=$((passed + 1))
    echo "PASS: $name (got $got)"
  else
    failed+=("$name: expected=$expected got=$got")
    echo "FAIL: $name expected=$expected got=$got"
  fi
}

# Reset env to clean state
unset EXPECTED_TASK_PREFIX
unset CLAUDE_P_DISABLE_ATTRIBUTION
unset CLAUDE_P_DISABLE_PROGRESS_SIGNAL

echo "=== Group 1: head_unchanged (HEAD not moved) ==="
run_test "1a HEAD unchanged any msg" "head_unchanged" "abc123" "abc123" "[T-P0-100] anything"

echo ""
echo "=== Group 2: head_external (sanity regex rejects lowercase/non-task) ==="
run_test "2a lowercase ad-hoc" "head_external" "abc" "def" "[T-adhoc-ar-plan] PROGRESS entry"
run_test "2b no brackets" "head_external" "abc" "def" "Random commit message"
run_test "2c lowercase t-" "head_external" "abc" "def" "[t-P0-100] lowercase t"
run_test "2d adhoc style" "head_external" "abc" "def" "[T-adhoc] Quick note"

echo ""
echo "=== Group 3: head_legit (no EXPECTED_TASK_PREFIX, valid task-ID shape) ==="
run_test "3a P0 task" "head_legit" "abc" "def" "[T-P0-100] Implement feature"
run_test "3b P1 task with description" "head_legit" "abc" "def" "[T-P1-999] Long detailed description"
run_test "3c hyphenated suffix" "head_legit" "abc" "def" "[T-ADHOC-RECOVER] Recovery"

echo ""
echo "=== Group 4: head_wip (WIP suffix) ==="
run_test "4a WIP unset prefix" "head_wip" "abc" "def" "[T-P0-100 WIP] partial progress"
run_test "4b WIP P1 task" "head_wip" "abc" "def" "[T-P1-200 WIP] checkpoint"

echo ""
echo "=== Group 5: head_legit with EXPECTED_TASK_PREFIX strict match ==="
EXPECTED_TASK_PREFIX="T-P0-711"
run_test "5a strict match" "head_legit" "abc" "def" "[T-P0-711] GeoMed second pass"
EXPECTED_TASK_PREFIX="T-P0-100"
run_test "5b strict mismatch -> legit_unexpected" "head_legit_unexpected" "abc" "def" "[T-P0-200] Different task"
run_test "5c strict mismatch + WIP -> wip" "head_wip" "abc" "def" "[T-P0-200 WIP] Different task WIP"
unset EXPECTED_TASK_PREFIX

echo ""
echo "=== Group 6: kill switches ==="
CLAUDE_P_DISABLE_ATTRIBUTION=1
run_test "6a kill switch lowercase still legit" "head_legit" "abc" "def" "[T-adhoc-ar-plan] external"
run_test "6b kill switch random msg legit" "head_legit" "abc" "def" "Random commit"
unset CLAUDE_P_DISABLE_ATTRIBUTION

echo ""
echo "=== Summary ==="
echo "Total: $total, Passed: $passed, Failed: $((total - passed))"
if [ ${#failed[@]} -ne 0 ]; then
  echo "FAILED tests:"
  for f in "${failed[@]}"; do echo "  - $f"; done
  exit 1
fi
echo "ALL PASS"
exit 0
