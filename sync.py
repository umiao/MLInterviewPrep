"""Sync shared hooks and CLAUDE.md content to downstream projects."""

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

HEADER = "<!-- Auto-generated: CLAUDE.md.local + shared. Do not edit directly. -->\n"
SHARED_DIR = Path(__file__).parent / "shared"


def file_hash(path: Path) -> str:
    """Return SHA-256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_hooks(target: Path, *, check: bool = False) -> bool:
    """Copy shared hooks to target/.claude/hooks/, preserving local/ dir.

    Returns True if changes were made (or would be made in check mode).
    """
    src = SHARED_DIR / "hooks"
    dst = target / ".claude" / "hooks"
    dst.mkdir(parents=True, exist_ok=True)

    changed = False
    for src_file in sorted(src.iterdir()):
        if src_file.name == "__pycache__" or src_file.is_dir():
            continue
        dst_file = dst / src_file.name
        if dst_file.exists() and file_hash(src_file) == file_hash(dst_file):
            continue
        changed = True
        if check:
            print(f"  hooks: {src_file.name} differs")
        else:
            shutil.copy2(src_file, dst_file)
            print(f"  copied: {src_file.name}")

    # Remove orphan files in target that no longer exist in shared
    shared_names = {f.name for f in src.iterdir() if f.is_file()}
    for target_file in sorted(dst.iterdir()):
        if target_file.is_dir():  # skip __pycache__, local/
            continue
        if target_file.name not in shared_names:
            changed = True
            if check:
                print(f"  hooks: {target_file.name} orphaned (not in shared)")
            else:
                target_file.unlink()
                print(f"  removed orphan: {target_file.name}")

    return changed


def sync_settings(target: Path, *, check: bool = False) -> bool:
    """Copy shared settings_base.json to target/.claude/settings.json.

    Returns True if changes were made (or would be made in check mode).
    """
    src = SHARED_DIR / "settings_base.json"
    dst = target / ".claude" / "settings.json"
    if not src.exists():
        print(f"  [SKIP] {src} not found")
        return False
    if dst.exists() and file_hash(src) == file_hash(dst):
        return False
    if check:
        print("  settings.json: differs from settings_base.json")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print("  copied: settings.json")
    return True


def compose_claude_md(target: Path, *, check: bool = False) -> bool:
    """Concatenate CLAUDE.md.local + shared content into CLAUDE.md.

    Returns True if changes were made (or would be made in check mode).
    """
    local_file = target / "CLAUDE.md.local"
    shared_file = SHARED_DIR / "claude_md_shared.md"
    output_file = target / "CLAUDE.md"

    if not local_file.exists():
        print(f"  [SKIP] {local_file} not found")
        return False
    if not shared_file.exists():
        print(f"  [SKIP] {shared_file} not found")
        return False

    local_content = local_file.read_text(encoding="utf-8")
    shared_content = shared_file.read_text(encoding="utf-8")

    # Ensure single newline between sections
    composed = HEADER + local_content.rstrip("\n") + "\n\n" + shared_content.lstrip("\n")

    if output_file.exists():
        existing = output_file.read_text(encoding="utf-8")
        if existing == composed:
            return False

    if check:
        print("  CLAUDE.md: content differs from composed result")
        return True

    output_file.write_text(composed, encoding="utf-8")
    print("  wrote: CLAUDE.md")
    return True


def main() -> None:
    """Entry point for sync script."""
    parser = argparse.ArgumentParser(description="Sync shared hooks and CLAUDE.md")
    parser.add_argument("--target", required=True, type=Path, help="Target project dir")
    parser.add_argument("--check", action="store_true", help="Dry-run: report staleness")
    parser.add_argument("--hooks-only", action="store_true", help="Only sync hooks")
    parser.add_argument("--settings-only", action="store_true", help="Only sync settings.json")
    parser.add_argument("--claude-md-only", action="store_true", help="Only compose CLAUDE.md")
    args = parser.parse_args()

    if not args.target.is_dir():
        print(f"Error: {args.target} is not a directory", file=sys.stderr)
        sys.exit(1)

    only_flags = [args.hooks_only, args.settings_only, args.claude_md_only]
    any_only = any(only_flags)
    do_hooks = args.hooks_only or not any_only
    do_settings = args.settings_only or not any_only
    do_md = args.claude_md_only or not any_only

    any_changed = False

    if do_hooks:
        print(f"Hooks -> {args.target}")
        if sync_hooks(args.target, check=args.check):
            any_changed = True
        else:
            print("  up to date")

    if do_settings:
        print(f"Settings -> {args.target}")
        if sync_settings(args.target, check=args.check):
            any_changed = True
        else:
            print("  up to date")

    if do_md:
        print(f"CLAUDE.md -> {args.target}")
        if compose_claude_md(args.target, check=args.check):
            any_changed = True
        else:
            print("  up to date")

    if args.check:
        sys.exit(1 if any_changed else 0)


if __name__ == "__main__":
    main()
