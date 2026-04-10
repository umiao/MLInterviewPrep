"""Stop hook: run tests and frontend production build before allowing Claude to exit.

<!-- CUSTOMIZE: Update TEST_COMMAND and TEST_PATHS for your project -->
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_utils import run_hook  # noqa: E402

# <!-- CUSTOMIZE: Set your test command and paths -->
TEST_COMMAND = ["python", "-m", "pytest"]
TEST_PATHS = ["tests/"]
TEST_FLAGS = ["-x", "-q", "--tb=short", "--maxfail=1", "-m", "not integration and not slow"]

# Frontend build check (production path: tsc -b && vite build)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "frontend"


def run_frontend_build() -> bool:
    """Run npm run build in the frontend directory. Returns True if passed."""
    if not (FRONTEND_DIR / "package.json").exists():
        return True  # No frontend, skip

    npm_path = shutil.which("npm")
    if npm_path is None:
        print("[BUILD GUARD] npm not found, skipping frontend build check", file=sys.stderr)
        return True

    try:
        result = subprocess.run(
            [npm_path, "run", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        print("[BUILD GUARD] Frontend build timed out after 120s", file=sys.stderr)
        return False

    if result.returncode != 0:
        output_lines = (result.stdout + result.stderr).strip().splitlines()
        summary = "\n".join(output_lines[-30:])
        print(
            f"[BUILD GUARD] Frontend build failed (npm run build). Fix before stopping:\n{summary}",
            file=sys.stderr,
        )
        return False

    return True


def main(hook_input: dict) -> None:
    """Run tests and frontend build, blocking exit if either fails."""
    blocked = False

    # --- Frontend production build check ---
    if not run_frontend_build():
        blocked = True

    # --- Python test suite ---
    try:
        result = subprocess.run(
            TEST_COMMAND + TEST_PATHS + TEST_FLAGS,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("[TEST GUARD] Tests timed out after 300s", file=sys.stderr)
        sys.exit(2)

    if result.returncode not in (0, 5):  # 0 = pass, 5 = no tests collected
        # Show last 30 lines of output to keep it concise
        output_lines = (result.stdout + result.stderr).strip().splitlines()
        summary = "\n".join(output_lines[-30:])
        print(
            f"[TEST GUARD] Tests failed. Fix them before stopping:\n{summary}",
            file=sys.stderr,
        )
        blocked = True

    sys.exit(2 if blocked else 0)


if __name__ == "__main__":
    run_hook("test_check", main)
