"""Combined backend + frontend development server launcher.

Starts both uvicorn (backend) and npm dev (frontend) in a single terminal,
with prefixed output for clarity. Press Ctrl+C to stop both servers.
"""

import os
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"


def _find_npm() -> str:
    """Return the npm executable name, accounting for Windows."""
    # On Windows, npm is typically npm.cmd
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
        # Stream closed
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
            # Use taskkill for reliable Windows process tree termination
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

    stop_event = threading.Event()
    env = os.environ.copy()

    # Force unbuffered Python output for the backend subprocess
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
            "8100",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    # Wait for backend to be ready before starting frontend
    print("[dev] Waiting for backend to be ready...")
    backend_ready = False
    for _attempt in range(60):  # 30 seconds max (60 * 0.5s)
        if backend_proc.poll() is not None:
            print(f"[dev] Backend exited unexpectedly with code {backend_proc.returncode}.")
            sys.exit(1)
        try:
            urllib.request.urlopen("http://localhost:8100/api/health", timeout=1)
            backend_ready = True
            print("[dev] Backend ready.")
            break
        except Exception:
            threading.Event().wait(0.5)

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
        # Wait for either process to exit
        while True:
            backend_rc = backend_proc.poll()
            frontend_rc = frontend_proc.poll()

            if backend_rc is not None:
                print(f"\n[dev] Backend exited with code {backend_rc}.")
                break
            if frontend_rc is not None:
                print(f"\n[dev] Frontend exited with code {frontend_rc}.")
                break

            # Brief sleep to avoid busy-waiting
            threading.Event().wait(0.5)

    except KeyboardInterrupt:
        print("\n[dev] Ctrl+C received. Stopping servers...")

    # Clean up
    stop_event.set()
    _terminate_process(backend_proc)
    _terminate_process(frontend_proc)

    print("[dev] Both servers stopped.")


if __name__ == "__main__":
    main()
