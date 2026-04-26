"""Combined backend + frontend development server launcher.

Starts both uvicorn (backend) and npm dev (frontend) in a single terminal,
with prefixed output for clarity. Press Ctrl+C to stop both servers.

Pre-flight: detects and evicts a stale prior dev.py backend that still owns
port 8100. Aborts (without killing) if a non-Python process holds the port.
"""

import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"

BACKEND_PORT = 8100

EVICTABLE_PROCESS_NAMES: frozenset[str] = frozenset(
    {"python", "python.exe", "python3", "python3.exe", "pythonw.exe", "uvicorn", "uvicorn.exe"}
)


def is_evictable_process(name: str | None) -> bool:
    """Return True if `name` is a process we will auto-kill (python/uvicorn family)."""
    if not name:
        return False
    return name.strip().lower() in EVICTABLE_PROCESS_NAMES


def parse_netstat_for_port(netstat_output: str, port: int) -> list[int]:
    """Extract PIDs of LISTENING TCP sockets on `port` from `netstat -ano` output."""
    pids: list[int] = []
    suffix = f":{port}"
    for line in netstat_output.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        if not parts[0].startswith("TCP"):
            continue
        if parts[3] != "LISTENING":
            continue
        if not parts[1].endswith(suffix):
            continue
        try:
            pid = int(parts[4])
        except ValueError:
            continue
        if pid not in pids:
            pids.append(pid)
    return pids


def _get_process_name(pid: int) -> str | None:
    """Return the executable basename for `pid`, or None if it cannot be determined."""
    try:
        if sys.platform.startswith("win"):
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line.startswith('"'):
                    continue
                first = line.split('","', 1)[0].lstrip('"').rstrip('"')
                return first or None
            return None
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "comm="],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        name = result.stdout.strip()
        return name or None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def _get_pids_on_port(port: int) -> list[int]:
    """Return PIDs LISTENING on `port` (cross-platform; empty on lookup failure)."""
    try:
        if sys.platform.startswith("win"):
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            return parse_netstat_for_port(result.stdout, port)
        result = subprocess.run(
            ["lsof", "-ti", f":{port}", "-sTCP:LISTEN"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        pids: list[int] = []
        for tok in result.stdout.split():
            try:
                pids.append(int(tok))
            except ValueError:
                continue
        return pids
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _kill_pid(pid: int) -> bool:
    """Force-kill `pid`. Returns True on success."""
    try:
        if sys.platform.startswith("win"):
            result = subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            return result.returncode == 0
        import signal as _signal

        os.kill(pid, _signal.SIGKILL)
        return True
    except (FileNotFoundError, ProcessLookupError, subprocess.TimeoutExpired, OSError):
        return False


def _wait_for_port_free(port: int, timeout: float = 3.0) -> bool:
    """Poll until `port` has no LISTENING owner or `timeout` elapses. Returns True if free."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _get_pids_on_port(port):
            return True
        time.sleep(0.2)
    return not _get_pids_on_port(port)


def evict_stale_backend(port: int = BACKEND_PORT, dry_run: bool = False) -> tuple[bool, str]:
    """Auto-evict a stale dev.py backend holding `port`.

    Returns (can_proceed, message):
      - (True, "clear")                              -- port has no owner.
      - (True, "evicted: <name> PID <pid>[, ...]")   -- python/uvicorn process(es) killed.
      - (True, "would evict: <name> PID <pid>[, ...]") -- dry_run only.
      - (False, "blocked: <name> PID <pid>")         -- non-evictable holder; abort.
      - (False, "evict timeout: ...")                -- killed but port still held after 3s.
    """
    pids = _get_pids_on_port(port)
    if not pids:
        return (True, "clear")

    candidates: list[tuple[int, str]] = []
    for pid in pids:
        name = _get_process_name(pid) or "unknown"
        if not is_evictable_process(name):
            return (False, f"blocked: {name} PID {pid}")
        candidates.append((pid, name))

    label = ", ".join(f"{n} PID {p}" for p, n in candidates)
    if dry_run:
        return (True, f"would evict: {label}")

    for pid, _name in candidates:
        _kill_pid(pid)

    if not _wait_for_port_free(port, timeout=3.0):
        kept = ", ".join(str(p) for p, _ in candidates)
        return (False, f"evict timeout: PIDs [{kept}] killed but port {port} still held")

    return (True, f"evicted: {label}")


def _preflight_port(port: int = BACKEND_PORT) -> None:
    """Run pre-flight eviction; print status; exit(1) if blocked. AC1/AC2/AC3."""
    print(f"[dev] Checking port {port} for stale backend...")
    ok, msg = evict_stale_backend(port=port)
    if not ok:
        if msg.startswith("blocked: "):
            holder = msg[len("blocked: "):]
            print(
                f"[dev] Port {port} held by {holder}; not a dev.py orphan. "
                f"Free the port manually before re-running."
            )
        else:
            print(f"[dev] Pre-flight failed: {msg}")
        sys.exit(1)
    if msg == "clear":
        print(f"[dev] Port {port} clear; spawning backend...")
        return
    if msg.startswith("evicted: "):
        print(f"[dev] Found stale process on port {port}; evicting...")
        print(f"[dev] {msg}")
        print(f"[dev] Port {port} freed; spawning fresh backend...")
        return
    print(f"[dev] {msg}")


def _find_npm() -> str:
    """Return the npm executable name, accounting for Windows."""
    if sys.platform == "win32":
        npm = shutil.which("npm.cmd") or shutil.which("npm")
    else:
        npm = shutil.which("npm")
    if not npm:
        print("[dev] npm not found. Please install Node.js 18+.")
        sys.exit(1)
    return npm


def _check_node_modules() -> None:
    """Verify that frontend dependencies are installed."""
    if not (FRONTEND_DIR / "node_modules").is_dir():
        print(f"[dev] node_modules not found in {FRONTEND_DIR}")
        print("[dev] Run: cd src/frontend && npm install")
        sys.exit(1)


def _stream_output(
    process: subprocess.Popen,  # type: ignore[type-arg]
    prefix: str,
    stop_event: threading.Event,
) -> None:
    """Read lines from a process's stdout and print with a prefix."""
    assert process.stdout is not None
    try:
        for line in process.stdout:
            if stop_event.is_set():
                break
            print(f"{prefix} {line}", end="", flush=True)
    except ValueError:
        pass


def _stream_stderr(
    process: subprocess.Popen,  # type: ignore[type-arg]
    prefix: str,
    stop_event: threading.Event,
) -> None:
    """Read lines from a process's stderr and print with a prefix."""
    assert process.stderr is not None
    try:
        for line in process.stderr:
            if stop_event.is_set():
                break
            print(f"{prefix} {line}", end="", flush=True)
    except ValueError:
        pass


def _terminate_process(proc: subprocess.Popen) -> None:  # type: ignore[type-arg]
    """Terminate a subprocess, handling platform differences."""
    if proc.poll() is not None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
            )
        else:
            proc.terminate()
            proc.wait(timeout=5)
    except (subprocess.TimeoutExpired, OSError):
        proc.kill()


def main() -> None:
    """Start backend and frontend dev servers."""
    npm = _find_npm()
    _check_node_modules()

    _preflight_port(BACKEND_PORT)

    stop_event = threading.Event()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    print("[dev] Starting backend (uvicorn) and frontend (npm run dev)...")
    print("[dev] Press Ctrl+C to stop both servers.\n")

    backend_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.backend.main:app",
            "--reload",
            "--port",
            str(BACKEND_PORT),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    print("[dev] Waiting for backend to be ready...")
    backend_ready = False
    for _attempt in range(60):  # 30 seconds max (60 * 0.5s)
        if backend_proc.poll() is not None:
            print(f"[dev] Backend exited unexpectedly with code {backend_proc.returncode}.")
            sys.exit(1)
        try:
            urllib.request.urlopen(
                f"http://localhost:{BACKEND_PORT}/api/health", timeout=1
            )
            # AC6: re-verify our spawned child is still alive after the response.
            # If a foreign process won the bind race, our uvicorn parent will have
            # exited with WinError 10013 by now and the response we just got was
            # not from us.
            time.sleep(0.3)
            if backend_proc.poll() is not None:
                print(
                    f"[dev] Backend exited right after healthcheck "
                    f"(code {backend_proc.returncode})."
                )
                print(
                    f"[dev] Another process likely won the bind race for port {BACKEND_PORT}."
                )
                sys.exit(1)
            backend_ready = True
            print("[dev] Backend ready.")
            break
        except Exception:
            time.sleep(0.5)

    if not backend_ready:
        print("[dev] Backend failed to start within 30s. Aborting.")
        _terminate_process(backend_proc)
        sys.exit(1)

    frontend_proc = subprocess.Popen(
        [npm, "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        cwd=str(FRONTEND_DIR),
        env=env,
    )

    threads = [
        threading.Thread(
            target=_stream_output,
            args=(backend_proc, "[backend]", stop_event),
            daemon=True,
        ),
        threading.Thread(
            target=_stream_stderr,
            args=(backend_proc, "[backend]", stop_event),
            daemon=True,
        ),
        threading.Thread(
            target=_stream_output,
            args=(frontend_proc, "[frontend]", stop_event),
            daemon=True,
        ),
        threading.Thread(
            target=_stream_stderr,
            args=(frontend_proc, "[frontend]", stop_event),
            daemon=True,
        ),
    ]
    for t in threads:
        t.start()

    try:
        while True:
            backend_rc = backend_proc.poll()
            frontend_rc = frontend_proc.poll()

            if backend_rc is not None:
                print(f"\n[dev] Backend exited with code {backend_rc}.")
                break
            if frontend_rc is not None:
                print(f"\n[dev] Frontend exited with code {frontend_rc}.")
                break

            threading.Event().wait(0.5)

    except KeyboardInterrupt:
        print("\n[dev] Ctrl+C received. Stopping servers...")

    stop_event.set()
    _terminate_process(backend_proc)
    _terminate_process(frontend_proc)

    print("[dev] Both servers stopped.")


if __name__ == "__main__":
    main()
