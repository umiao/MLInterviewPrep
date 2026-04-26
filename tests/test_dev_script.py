"""Unit tests for scripts/dev.py port-eviction helpers (T-P0-617 AC7)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

# scripts/ is not a Python package and the workspace contains other scripts/
# directories on sys.path; load dev.py directly by file path to avoid collisions.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEV_PATH = PROJECT_ROOT / "scripts" / "dev.py"
_spec = importlib.util.spec_from_file_location("mlinterviewprep_dev_script", _DEV_PATH)
assert _spec is not None and _spec.loader is not None
dev_script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dev_script)


# ---------------------------------------------------------------------------
# parse_netstat_for_port
# ---------------------------------------------------------------------------


SAMPLE_NETSTAT = """\
Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1692
  TCP    0.0.0.0:8100           0.0.0.0:0              LISTENING       12345
  TCP    127.0.0.1:8100         0.0.0.0:0              LISTENING       12345
  TCP    [::]:8100              [::]:0                 LISTENING       12345
  TCP    127.0.0.1:54321        127.0.0.1:8100         ESTABLISHED     6789
  TCP    0.0.0.0:8101           0.0.0.0:0              LISTENING       9999
  TCP    0.0.0.0:81000          0.0.0.0:0              LISTENING       8888
  UDP    0.0.0.0:8100           *:*                                    7777
"""


def test_parse_netstat_for_port_returns_listening_pids():
    pids = dev_script.parse_netstat_for_port(SAMPLE_NETSTAT, 8100)
    assert pids == [12345], f"Expected only PID 12345 (LISTENING TCP on :8100), got {pids}"


def test_parse_netstat_for_port_excludes_other_ports():
    assert dev_script.parse_netstat_for_port(SAMPLE_NETSTAT, 8101) == [9999]
    assert dev_script.parse_netstat_for_port(SAMPLE_NETSTAT, 81000) == [8888]


def test_parse_netstat_for_port_excludes_substring_collisions():
    """`:8100` must NOT match `:81000` or `:81` etc. (suffix match on the full port token)."""
    netstat = (
        "  TCP    0.0.0.0:81000          0.0.0.0:0              LISTENING       111\n"
        "  TCP    0.0.0.0:81             0.0.0.0:0              LISTENING       222\n"
        "  TCP    0.0.0.0:8100           0.0.0.0:0              LISTENING       333\n"
    )
    assert dev_script.parse_netstat_for_port(netstat, 8100) == [333]


def test_parse_netstat_for_port_empty_output_returns_empty_list():
    assert dev_script.parse_netstat_for_port("", 8100) == []


def test_parse_netstat_for_port_skips_established_state():
    netstat = "  TCP    127.0.0.1:8100         127.0.0.1:54321        ESTABLISHED     6789\n"
    assert dev_script.parse_netstat_for_port(netstat, 8100) == []


def test_parse_netstat_for_port_dedupes_pids():
    """The same PID listening on multiple addresses (0.0.0.0 + ::) is returned once."""
    pids = dev_script.parse_netstat_for_port(SAMPLE_NETSTAT, 8100)
    assert len(pids) == len(set(pids))


# ---------------------------------------------------------------------------
# is_evictable_process
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["python.exe", "python3.exe", "python", "python3", "uvicorn", "uvicorn.exe", "PYTHON.EXE"],
)
def test_is_evictable_process_accepts_python_family(name):
    assert dev_script.is_evictable_process(name) is True


@pytest.mark.parametrize(
    "name",
    ["chrome.exe", "node.exe", "code.exe", "explorer.exe", "nginx", "redis-server", ""],
)
def test_is_evictable_process_rejects_other_processes(name):
    assert dev_script.is_evictable_process(name) is False


def test_is_evictable_process_handles_none():
    assert dev_script.is_evictable_process(None) is False


def test_is_evictable_process_strips_whitespace():
    assert dev_script.is_evictable_process("  python.exe\n") is True


# ---------------------------------------------------------------------------
# evict_stale_backend (dry_run path)
# ---------------------------------------------------------------------------


def test_evict_stale_backend_clear_when_no_owner():
    with patch.object(dev_script, "_get_pids_on_port", return_value=[]):
        ok, msg = dev_script.evict_stale_backend(port=8100, dry_run=True)
    assert ok is True
    assert msg == "clear"


def test_evict_stale_backend_dry_run_lists_candidate_without_killing():
    """AC7: evict_stale_backend(port=8100, dry_run=True) returns the candidate without killing."""
    with patch.object(dev_script, "_get_pids_on_port", return_value=[12345]), patch.object(
        dev_script, "_get_process_name", return_value="python.exe"
    ), patch.object(dev_script, "_kill_pid") as kill_mock:
        ok, msg = dev_script.evict_stale_backend(port=8100, dry_run=True)
    assert ok is True
    assert msg.startswith("would evict: ")
    assert "12345" in msg
    assert "python.exe" in msg
    kill_mock.assert_not_called()


def test_evict_stale_backend_blocks_non_python_holder():
    """AC2: a non-python process holding the port -> abort, no kill."""
    with patch.object(dev_script, "_get_pids_on_port", return_value=[4242]), patch.object(
        dev_script, "_get_process_name", return_value="chrome.exe"
    ), patch.object(dev_script, "_kill_pid") as kill_mock:
        ok, msg = dev_script.evict_stale_backend(port=8100, dry_run=False)
    assert ok is False
    assert msg.startswith("blocked: chrome.exe")
    assert "4242" in msg
    kill_mock.assert_not_called()


def test_evict_stale_backend_kills_python_then_waits_for_release():
    """AC1 happy path: python holder is killed and we report success."""
    pid_seq = iter([[12345], []])  # first call sees the orphan; after kill the port is free
    with patch.object(dev_script, "_get_pids_on_port", side_effect=lambda port: next(pid_seq)), patch.object(
        dev_script, "_get_process_name", return_value="python.exe"
    ), patch.object(dev_script, "_kill_pid", return_value=True) as kill_mock, patch.object(
        dev_script, "_wait_for_port_free", return_value=True
    ):
        ok, msg = dev_script.evict_stale_backend(port=8100, dry_run=False)
    assert ok is True
    assert msg.startswith("evicted: python.exe")
    assert "12345" in msg
    kill_mock.assert_called_once_with(12345)


def test_evict_stale_backend_reports_timeout_when_port_still_held():
    """If the kill succeeds but the port stays held within 3s, surface the timeout."""
    with patch.object(dev_script, "_get_pids_on_port", return_value=[12345]), patch.object(
        dev_script, "_get_process_name", return_value="python.exe"
    ), patch.object(dev_script, "_kill_pid", return_value=True), patch.object(
        dev_script, "_wait_for_port_free", return_value=False
    ):
        ok, msg = dev_script.evict_stale_backend(port=8100, dry_run=False)
    assert ok is False
    assert "evict timeout" in msg
    assert "12345" in msg


def test_evict_stale_backend_idempotent_when_port_already_free():
    """AC5: calling twice with no holder -> both calls return ('clear')."""
    with patch.object(dev_script, "_get_pids_on_port", return_value=[]):
        first = dev_script.evict_stale_backend(port=8100)
        second = dev_script.evict_stale_backend(port=8100)
    assert first == (True, "clear")
    assert second == (True, "clear")


def test_evict_stale_backend_blocks_if_any_pid_is_non_evictable():
    """If ONE of multiple PIDs is non-python, the whole eviction is refused (no partial kill)."""
    with patch.object(dev_script, "_get_pids_on_port", return_value=[111, 222]), patch.object(
        dev_script, "_get_process_name", side_effect=lambda pid: "python.exe" if pid == 111 else "chrome.exe"
    ), patch.object(dev_script, "_kill_pid") as kill_mock:
        ok, msg = dev_script.evict_stale_backend(port=8100)
    assert ok is False
    assert "blocked: chrome.exe" in msg
    kill_mock.assert_not_called()


# ---------------------------------------------------------------------------
# Integration smoke: dry_run against the live OS without killing anything
# ---------------------------------------------------------------------------


def test_evict_stale_backend_live_dry_run_does_not_kill_anything():
    """End-to-end smoke: invoke against the live OS in dry_run; assert no kill API was called."""
    with patch.object(dev_script, "_kill_pid") as kill_mock:
        ok, msg = dev_script.evict_stale_backend(port=BACKEND_PORT_FOR_SMOKE, dry_run=True)
    assert ok in (True, False)
    assert isinstance(msg, str)
    kill_mock.assert_not_called()


# Use a port unlikely to be bound during CI runs.
BACKEND_PORT_FOR_SMOKE = 59123
