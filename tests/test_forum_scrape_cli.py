"""Tests for the forum_scrape CLI script."""

import importlib
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the module directly by path (scripts/ is not a package)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

_spec = importlib.util.spec_from_file_location(
    "forum_scrape",
    PROJECT_ROOT / "scripts" / "forum_scrape.py",
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["forum_scrape"] = _mod
_spec.loader.exec_module(_mod)

build_parser = _mod.build_parser
cmd_add_seed = _mod.cmd_add_seed
cmd_list_seeds = _mod.cmd_list_seeds
cmd_status = _mod.cmd_status
cmd_import = _mod.cmd_import
detect_source_site = _mod.detect_source_site

MODULE_PATH = "forum_scrape"


class TestDetectSourceSite:
    """Tests for auto-detection of source_site from URL."""

    def test_1point3acres_www(self) -> None:
        """Detect 1point3acres from www subdomain."""
        assert detect_source_site("https://www.1point3acres.com/bbs/tag-123.html") == "1point3acres"

    def test_1point3acres_bare(self) -> None:
        """Detect 1point3acres from bare domain."""
        assert detect_source_site("https://1point3acres.com/bbs/tag-123.html") == "1point3acres"

    def test_1point3acres_subdomain(self) -> None:
        """Detect 1point3acres from arbitrary subdomain."""
        assert detect_source_site("https://forums.1point3acres.com/page") == "1point3acres"

    def test_unknown_domain_raises(self) -> None:
        """Raise ValueError for unsupported domains."""
        with pytest.raises(ValueError, match="Cannot detect source_site"):
            detect_source_site("https://reddit.com/r/cscareerquestions")


class TestBuildParser:
    """Tests for argparse subcommand parsing."""

    def test_add_seed_basic(self) -> None:
        """Parse add-seed with URL only."""
        parser = build_parser()
        args = parser.parse_args(["add-seed", "https://www.1point3acres.com/bbs/tag-1.html"])
        assert args.command == "add-seed"
        assert args.url == "https://www.1point3acres.com/bbs/tag-1.html"
        assert args.company is None
        assert args.label is None

    def test_add_seed_with_company_and_label(self) -> None:
        """Parse add-seed with --company and --label."""
        parser = build_parser()
        args = parser.parse_args([
            "add-seed", "https://www.1point3acres.com/bbs/tag-1.html",
            "--company", "Google", "--label", "SWE posts",
        ])
        assert args.company == "Google"
        assert args.label == "SWE posts"

    def test_list_seeds(self) -> None:
        """Parse list-seeds."""
        parser = build_parser()
        args = parser.parse_args(["list-seeds"])
        assert args.command == "list-seeds"

    def test_scrape(self) -> None:
        """Parse scrape with seed_id."""
        parser = build_parser()
        args = parser.parse_args(["scrape", "42"])
        assert args.command == "scrape"
        assert args.seed_id == 42

    def test_fetch_next(self) -> None:
        """Parse fetch with --next (default)."""
        parser = build_parser()
        args = parser.parse_args(["fetch", "1"])
        assert args.command == "fetch"
        assert args.seed_id == 1
        assert args.link_id is None

    def test_fetch_all(self) -> None:
        """Parse fetch with --all."""
        parser = build_parser()
        args = parser.parse_args(["fetch", "1", "--all"])
        assert args.all is True

    def test_fetch_link_id(self) -> None:
        """Parse fetch with --link-id."""
        parser = build_parser()
        args = parser.parse_args(["fetch", "1", "--link-id", "99"])
        assert args.link_id == 99

    def test_status(self) -> None:
        """Parse status with seed_id."""
        parser = build_parser()
        args = parser.parse_args(["status", "5"])
        assert args.command == "status"
        assert args.seed_id == 5

    def test_import(self) -> None:
        """Parse import with post_id and --company."""
        parser = build_parser()
        args = parser.parse_args(["import", "10", "--company", "Meta"])
        assert args.command == "import"
        assert args.post_id == 10
        assert args.company == "Meta"

    def test_retry_failed(self) -> None:
        """Parse retry-failed with seed_id."""
        parser = build_parser()
        args = parser.parse_args(["retry-failed", "3"])
        assert args.command == "retry-failed"
        assert args.seed_id == 3


class TestCmdAddSeed:
    """Tests for the add-seed command with DB interaction."""

    def test_add_seed_creates_record(self, db_session) -> None:
        """add-seed creates a ForumSeed in the database."""
        from src.backend.models.forum import ForumSeed

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.url = "https://www.1point3acres.com/bbs/tag-123.html"
            args.company = None
            args.label = "test label"

            cmd_add_seed(args)

        seed = db_session.query(ForumSeed).first()
        assert seed is not None
        assert seed.url == "https://www.1point3acres.com/bbs/tag-123.html"
        assert seed.source_site == "1point3acres"
        assert seed.label == "test label"
        assert seed.company_id is None

    def test_add_seed_with_company(self, db_session) -> None:
        """add-seed resolves company name to company_id."""
        from src.backend.models.company import Company
        from src.backend.models.forum import ForumSeed

        company = Company(name="Google")
        db_session.add(company)
        db_session.commit()
        company_id = company.id

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.url = "https://www.1point3acres.com/bbs/tag-456.html"
            args.company = "Google"
            args.label = None

            cmd_add_seed(args)

        seed = db_session.query(ForumSeed).first()
        assert seed is not None
        assert seed.company_id == company_id

    def test_add_seed_duplicate_skips(self, db_session, capsys) -> None:
        """add-seed with duplicate URL prints message without creating."""
        from src.backend.models.forum import ForumSeed

        existing = ForumSeed(
            url="https://www.1point3acres.com/bbs/tag-789.html",
            source_site="1point3acres",
        )
        db_session.add(existing)
        db_session.commit()

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.url = "https://www.1point3acres.com/bbs/tag-789.html"
            args.company = None
            args.label = None

            cmd_add_seed(args)

        captured = capsys.readouterr()
        assert "already exists" in captured.out
        assert db_session.query(ForumSeed).count() == 1

    def test_add_seed_unknown_company_exits(self, db_session) -> None:
        """add-seed with nonexistent company exits with code 1."""
        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.url = "https://www.1point3acres.com/bbs/tag-100.html"
            args.company = "NonExistentCorp"
            args.label = None

            with pytest.raises(SystemExit) as exc_info:
                cmd_add_seed(args)
            assert exc_info.value.code == 1


class TestCmdListSeeds:
    """Tests for the list-seeds command."""

    def test_list_seeds_empty(self, db_session, capsys) -> None:
        """list-seeds with no seeds prints message."""
        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            cmd_list_seeds(MagicMock())

        captured = capsys.readouterr()
        assert "No seeds found" in captured.out

    def test_list_seeds_shows_entries(self, db_session, capsys) -> None:
        """list-seeds prints seed details."""
        from src.backend.models.forum import ForumSeed

        seed = ForumSeed(
            url="https://www.1point3acres.com/bbs/tag-1.html",
            source_site="1point3acres",
            label="Test",
        )
        db_session.add(seed)
        db_session.commit()

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            cmd_list_seeds(MagicMock())

        captured = capsys.readouterr()
        assert "tag-1.html" in captured.out


class TestCmdStatus:
    """Tests for the status command."""

    def test_status_shows_progress(self, db_session, capsys) -> None:
        """status prints progress summary."""
        from src.backend.models.forum import ForumPostLink, ForumSeed

        seed = ForumSeed(
            url="https://www.1point3acres.com/bbs/tag-1.html",
            source_site="1point3acres",
        )
        db_session.add(seed)
        db_session.commit()
        db_session.refresh(seed)

        # Add links with different statuses
        for i, status in enumerate(["pending", "fetched", "failed"]):
            link = ForumPostLink(
                forum_seed_id=seed.id,
                url=f"https://www.1point3acres.com/thread-{i}",
                status=status,
                fetch_order=i,
            )
            db_session.add(link)
        db_session.commit()

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.seed_id = seed.id
            cmd_status(args)

        captured = capsys.readouterr()
        assert "Total links:  3" in captured.out
        assert "Pending:      1" in captured.out
        assert "Fetched:      1" in captured.out
        assert "Failed:       1" in captured.out

    def test_status_seed_not_found(self, db_session) -> None:
        """status with invalid seed_id exits with code 1."""
        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.seed_id = 999

            with pytest.raises(SystemExit) as exc_info:
                cmd_status(args)
            assert exc_info.value.code == 1


class TestCmdImport:
    """Tests for the import command."""

    def test_import_success(self, db_session, capsys) -> None:
        """import appends post to company prep_notes."""
        from src.backend.models.company import Company
        from src.backend.models.forum import ForumPost, ForumPostLink, ForumSeed

        company = Company(name="TestCo")
        db_session.add(company)
        db_session.commit()

        seed = ForumSeed(
            url="https://www.1point3acres.com/bbs/tag-1.html",
            source_site="1point3acres",
        )
        db_session.add(seed)
        db_session.commit()

        link = ForumPostLink(
            forum_seed_id=seed.id,
            url="https://www.1point3acres.com/thread-100",
            title="Test Post",
            status="fetched",
        )
        db_session.add(link)
        db_session.commit()

        post = ForumPost(
            forum_post_link_id=link.id,
            raw_text="Interview experience content",
            content_hash="abc123",
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)

        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.post_id = post.id
            args.company = "TestCo"
            cmd_import(args)

        captured = capsys.readouterr()
        assert "Imported post" in captured.out
        updated = db_session.query(Company).filter(Company.id == company.id).first()
        assert "Interview experience content" in updated.prep_notes

    def test_import_company_not_found(self, db_session) -> None:
        """import with nonexistent company exits with code 1."""
        with patch(f"{MODULE_PATH}.SessionLocal", return_value=db_session):
            args = MagicMock()
            args.post_id = 1
            args.company = "NoSuchCo"

            with pytest.raises(SystemExit) as exc_info:
                cmd_import(args)
            assert exc_info.value.code == 1
