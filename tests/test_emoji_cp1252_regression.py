"""Regression test: scripts/check_emoji.py must survive cp1252 stdout environment.

Prior bug: on Windows, sys.stdout defaults to cp1252 which cannot encode emoji
chars above U+00FF. When the script found an emoji and tried to print the
diagnostic, print() raised UnicodeEncodeError. The fix reconfigures stdout/stderr
to utf-8 at module load. This test forces the failure mode on any platform via
PYTHONIOENCODING=cp1252 and asserts no traceback.

We embed U+1F600 (grinning face) — it is inside the narrow _EMOJI_RE (emoticons
range) AND outside cp1252's encodable set, so it exercises both the match path
and the unprintable-in-cp1252 path simultaneously.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_check_emoji_survives_cp1252_stdout(tmp_path):
    # Seed a fake project with a .py file containing an emoji that cp1252 cannot
    # encode. Code-extension so it lands in code_hits and triggers the stdout print path.
    fake_root = tmp_path / "fake_proj"
    (fake_root / "src").mkdir(parents=True)
    (fake_root / "src" / "bad.py").write_text("marker = '\U0001f600'\n", encoding="utf-8")

    # Copy the real script into the fake tree so its __file__-based project-root
    # walk stays inside tmp_path (otherwise it would scan the real repo).
    (fake_root / "scripts").mkdir()
    real_script = (REPO_ROOT / "scripts" / "check_emoji.py").read_text(encoding="utf-8")
    (fake_root / "scripts" / "check_emoji.py").write_text(real_script, encoding="utf-8")

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    proc = subprocess.run(
        [sys.executable, str(fake_root / "scripts" / "check_emoji.py")],
        capture_output=True,
        env=env,
        timeout=30,
    )
    stderr = proc.stderr.decode("utf-8", errors="replace")
    stdout = proc.stdout.decode("utf-8", errors="replace")

    assert "UnicodeEncodeError" not in stderr, (
        f"cp1252 regression: check_emoji.py crashed with UnicodeEncodeError.\nstderr:\n{stderr}"
    )
    assert "Traceback" not in stderr, (
        f"cp1252 regression: check_emoji.py unexpected crash.\nstderr:\n{stderr}\nstdout:\n{stdout}"
    )
    assert proc.returncode == 1, (
        f"Expected rc=1 (emoji found) after regex scan, got {proc.returncode}."
        f"\nstderr:\n{stderr}\nstdout:\n{stdout}"
    )
