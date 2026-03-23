"""Forum scraping CLI -- wraps forum_service for command-line use.

Subcommands:
    add-seed    Add a new ForumSeed URL
    list-seeds  List all ForumSeeds
    scrape      Phase A: collect post links from a seed page
    fetch       Phase B: fetch individual post content
    status      Show fetch progress for a seed
    import      Import a fetched post into company prep notes
    retry-failed  Re-fetch all failed links for a seed
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy.exc import IntegrityError

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backend.database import SessionLocal, init_db  # noqa: E402
from src.backend.models.company import Company  # noqa: E402
from src.backend.models.forum import ForumPostLink, ForumSeed  # noqa: E402
from src.backend.scraper.crawler import PlaywrightCrawler  # noqa: E402
from src.backend.services.forum_service import (  # noqa: E402
    fetch_next_unfetched,
    fetch_single_post,
    get_fetch_progress,
    import_post_to_document,
    retry_failed,
    scrape_seed_page,
    scrape_seed_pages,
)

# Domain -> source_site mapping
DOMAIN_TO_SITE: dict[str, str] = {
    "1point3acres.com": "1point3acres",
    "www.1point3acres.com": "1point3acres",
}


def detect_source_site(url: str) -> str:
    """Auto-detect source_site from URL domain.

    Args:
        url: The seed URL.

    Returns:
        Detected source_site string.

    Raises:
        ValueError: If domain is not recognized.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    for domain, site in DOMAIN_TO_SITE.items():
        if hostname == domain or hostname.endswith("." + domain):
            return site
    raise ValueError(
        f"Cannot detect source_site from domain '{hostname}'. "
        f"Supported domains: {list(DOMAIN_TO_SITE.keys())}"
    )


def cmd_add_seed(args: argparse.Namespace) -> None:
    """Handle the add-seed subcommand."""
    db = SessionLocal()
    try:
        source_site = detect_source_site(args.url)

        company_id = None
        if args.company:
            company = (
                db.query(Company)
                .filter(Company.name.ilike(args.company))
                .first()
            )
            if not company:
                print(f"Error: Company '{args.company}' not found", file=sys.stderr)
                sys.exit(1)
            company_id = company.id

        # Check for existing seed with same URL
        existing = db.query(ForumSeed).filter(ForumSeed.url == args.url).first()
        if existing:
            print(f"Seed already exists with id={existing.id}")
            return

        seed = ForumSeed(
            url=args.url,
            source_site=source_site,
            label=args.label,
            company_id=company_id,
        )
        db.add(seed)
        db.commit()
        db.refresh(seed)
        print(f"Created seed id={seed.id} source_site={source_site} url={seed.url}")
        if company_id:
            print(f"  company_id={company_id}")
        if args.label:
            print(f"  label={args.label}")
    finally:
        db.close()


def cmd_list_seeds(args: argparse.Namespace) -> None:
    """Handle the list-seeds subcommand."""
    db = SessionLocal()
    try:
        seeds = db.query(ForumSeed).all()
        if not seeds:
            print("No seeds found.")
            return

        for s in seeds:
            scraped = s.last_scraped_at.isoformat() if s.last_scraped_at else "never"
            company = ""
            if s.company_id:
                c = db.query(Company).filter(Company.id == s.company_id).first()
                company = f" company={c.name}" if c else f" company_id={s.company_id}"
            label = f' label="{s.label}"' if s.label else ""
            print(f"  [{s.id}] {s.url}{company}{label} (scraped: {scraped})")
    finally:
        db.close()


def cmd_scrape(args: argparse.Namespace) -> None:
    """Handle the scrape subcommand."""
    db = SessionLocal()
    try:
        seed = db.query(ForumSeed).filter(ForumSeed.id == args.seed_id).first()
        if not seed:
            print(f"Error: Seed {args.seed_id} not found", file=sys.stderr)
            sys.exit(1)

        crawler = PlaywrightCrawler()

        if args.pages > 1:
            auto_detect = not args.no_auto_detect
            stats = asyncio.run(
                scrape_seed_pages(
                    db,
                    args.seed_id,
                    crawler,
                    max_pages=args.pages,
                    auto_detect=auto_detect,
                    start_page=args.start_page,
                )
            )
            print(f"Pages scraped:      {stats['pages_scraped']}")
            print(f"Total links:        {stats['total_links']}")
            print(f"New links:          {stats['new_links']}")
            print(f"Max page detected:  {stats['max_page_detected']}")
            print(f"Stopped early:      {stats['stopped_early']}")
            print(f"Last page:          {stats['last_page']}")
        else:
            links = asyncio.run(scrape_seed_page(db, args.seed_id, crawler))
            print(f"Discovered {len(links)} links for seed {args.seed_id}")
            for link in links:
                title = link.title or "(no title)"
                print(f"  [{link.id}] {title} - {link.url}")
    finally:
        db.close()


def cmd_fetch(args: argparse.Namespace) -> None:
    """Handle the fetch subcommand."""
    db = SessionLocal()
    try:
        seed = db.query(ForumSeed).filter(ForumSeed.id == args.seed_id).first()
        if not seed:
            print(f"Error: Seed {args.seed_id} not found", file=sys.stderr)
            sys.exit(1)

        crawler = PlaywrightCrawler()

        if args.link_id:
            post = asyncio.run(fetch_single_post(db, args.link_id, crawler))
            if post:
                print(f"Fetched post id={post.id} ({len(post.raw_text)} chars)")
            else:
                print("No post fetched (already fetched or failed)")

        elif args.all:
            timeout = args.timeout_minutes
            deadline = time.monotonic() + timeout * 60 if timeout else None
            count = 0
            failures = 0
            while True:
                if deadline and time.monotonic() >= deadline:
                    print(f"Timeout reached ({timeout} min), stopping.")
                    break
                try:
                    post = asyncio.run(
                        fetch_next_unfetched(db, args.seed_id, crawler)
                    )
                except IntegrityError as exc:
                    # DB constraint violation (e.g., duplicate forum_post_link_id).
                    # Roll back and continue -- the secondary guard in fetch_single_post
                    # will fix the stale-status row on the next iteration.
                    print(f"[WARN] IntegrityError, rolling back and continuing: {exc.orig}")
                    db.rollback()
                    failures += 1
                    time.sleep(2)
                    continue
                if not post:
                    # Distinguish: no pending links remain vs single fetch failed.
                    # fetch_next_unfetched returns None both when no pending link
                    # is found AND when fetch_single_post fails (failure sets
                    # link.status='failed' before returning None). Re-query to check.
                    still_pending = (
                        db.query(ForumPostLink)
                        .filter(
                            ForumPostLink.forum_seed_id == args.seed_id,
                            ForumPostLink.status == "pending",
                        )
                        .first()
                    )
                    if still_pending:
                        # A single fetch failed; skip it and continue.
                        failures += 1
                        time.sleep(2)
                        continue
                    break
                count += 1
                failures = 0
                print(f"  [{count}] post id={post.id} ({len(post.raw_text)} chars)")
                # Rate limiting: 2 second delay between fetches
                time.sleep(2)
            print(f"Fetched {count} posts total ({failures} consecutive failures at end)")

        else:
            # Default: --next (fetch one)
            post = asyncio.run(
                fetch_next_unfetched(db, args.seed_id, crawler)
            )
            if post:
                print(f"Fetched post id={post.id} ({len(post.raw_text)} chars)")
            else:
                print("No pending posts to fetch")
    finally:
        db.close()


def cmd_status(args: argparse.Namespace) -> None:
    """Handle the status subcommand."""
    db = SessionLocal()
    try:
        seed = db.query(ForumSeed).filter(ForumSeed.id == args.seed_id).first()
        if not seed:
            print(f"Error: Seed {args.seed_id} not found", file=sys.stderr)
            sys.exit(1)

        progress = get_fetch_progress(db, args.seed_id)
        print(f"Seed {args.seed_id}: {seed.url}")
        print(f"  Total links:  {progress['total']}")
        print(f"  Pending:      {progress['pending']}")
        print(f"  Fetched:      {progress['fetched']}")
        print(f"  Failed:       {progress['failed']}")
        if progress["last_fetched_url"]:
            print(f"  Last fetched: {progress['last_fetched_url']}")
    finally:
        db.close()


def cmd_import(args: argparse.Namespace) -> None:
    """Handle the import subcommand."""
    db = SessionLocal()
    try:
        company = (
            db.query(Company)
            .filter(Company.name.ilike(args.company))
            .first()
        )
        if not company:
            print(f"Error: Company '{args.company}' not found", file=sys.stderr)
            sys.exit(1)

        doc = import_post_to_document(db, args.post_id, company.id)
        content_len = len(doc.content) if doc.content else 0
        print(
            f"Imported post {args.post_id} to '{company.name}' "
            f"document '{doc.title}' ({content_len} chars)"
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


def cmd_batch_status(args: argparse.Namespace) -> None:
    """Handle the batch-status subcommand -- show progress for all seeds."""
    db = SessionLocal()
    try:
        seeds = db.query(ForumSeed).all()
        if not seeds:
            print("No seeds found.")
            return

        # Header
        print(
            f"{'ID':>3} | {'Label':<25} | {'Total':>5} | {'Fetched':>7} "
            f"| {'Pending':>7} | {'Failed':>6} | {'Last Page':>9}"
        )
        print(
            f"{'---':>3} | {'-' * 25} | {'-----':>5} | {'-------':>7} "
            f"| {'-------':>7} | {'------':>6} | {'-' * 9}"
        )

        for s in seeds:
            progress = get_fetch_progress(db, s.id)
            label = (s.label or "")[:25]
            last_page = str(s.last_scraped_page) if s.last_scraped_page else "-"
            print(
                f"{s.id:>3} | {label:<25} | {progress['total']:>5} "
                f"| {progress['fetched']:>7} | {progress['pending']:>7} "
                f"| {progress['failed']:>6} | {last_page:>9}"
            )
    finally:
        db.close()


def cmd_retry_failed(args: argparse.Namespace) -> None:
    """Handle the retry-failed subcommand."""
    db = SessionLocal()
    try:
        seed = db.query(ForumSeed).filter(ForumSeed.id == args.seed_id).first()
        if not seed:
            print(f"Error: Seed {args.seed_id} not found", file=sys.stderr)
            sys.exit(1)

        # Count failed before retry
        failed_count = (
            db.query(ForumPostLink)
            .filter(
                ForumPostLink.forum_seed_id == args.seed_id,
                ForumPostLink.status == "failed",
            )
            .count()
        )
        if failed_count == 0:
            print("No failed links to retry")
            return

        print(f"Retrying {failed_count} failed links...")
        crawler = PlaywrightCrawler()
        results = asyncio.run(retry_failed(db, args.seed_id, crawler))
        print(f"Successfully re-fetched {len(results)} of {failed_count} posts")
        for post in results:
            print(f"  post id={post.id} ({len(post.raw_text)} chars)")
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with all subcommands.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="forum_scrape",
        description="Forum scraping CLI for interview post collection",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-seed
    p_add = subparsers.add_parser("add-seed", help="Add a new forum seed URL")
    p_add.add_argument("url", help="Seed URL to scrape")
    p_add.add_argument("--company", help="Company name to associate")
    p_add.add_argument("--label", help="Optional label for this seed")
    p_add.set_defaults(func=cmd_add_seed)

    # list-seeds
    p_list = subparsers.add_parser("list-seeds", help="List all forum seeds")
    p_list.set_defaults(func=cmd_list_seeds)

    # scrape
    p_scrape = subparsers.add_parser(
        "scrape", help="Phase A: scrape seed page for post links"
    )
    p_scrape.add_argument("seed_id", type=int, help="Seed ID to scrape")
    p_scrape.add_argument(
        "--pages", type=int, default=1,
        help="Number of pages to scrape (default: 1)"
    )
    p_scrape.add_argument(
        "--start-page", type=int, default=1,
        help="Page number to start from (default: 1, for resuming)"
    )
    p_scrape.add_argument(
        "--no-auto-detect", action="store_true",
        help="Disable auto-detection of max page from pagination"
    )
    p_scrape.set_defaults(func=cmd_scrape)

    # fetch
    p_fetch = subparsers.add_parser(
        "fetch", help="Phase B: fetch post content"
    )
    p_fetch.add_argument("seed_id", type=int, help="Seed ID")
    fetch_group = p_fetch.add_mutually_exclusive_group()
    fetch_group.add_argument(
        "--next", action="store_true", default=True,
        help="Fetch next pending post (default)"
    )
    fetch_group.add_argument(
        "--all", action="store_true",
        help="Fetch all pending posts with rate limiting"
    )
    fetch_group.add_argument(
        "--link-id", type=int,
        help="Fetch a specific link by ID"
    )
    p_fetch.add_argument(
        "--timeout-minutes", type=int, default=None,
        help="Stop fetching after this many minutes (only with --all)"
    )
    p_fetch.set_defaults(func=cmd_fetch)

    # status
    p_status = subparsers.add_parser(
        "status", help="Show fetch progress for a seed"
    )
    p_status.add_argument("seed_id", type=int, help="Seed ID")
    p_status.set_defaults(func=cmd_status)

    # import
    p_import = subparsers.add_parser(
        "import", help="Import a fetched post to company prep notes"
    )
    p_import.add_argument("post_id", type=int, help="Post ID to import")
    p_import.add_argument(
        "--company", required=True,
        help="Company name to import into"
    )
    p_import.set_defaults(func=cmd_import)

    # batch-status
    p_batch = subparsers.add_parser(
        "batch-status", help="Show progress for all seeds"
    )
    p_batch.set_defaults(func=cmd_batch_status)

    # retry-failed
    p_retry = subparsers.add_parser(
        "retry-failed", help="Re-fetch all failed links for a seed"
    )
    p_retry.add_argument("seed_id", type=int, help="Seed ID")
    p_retry.set_defaults(func=cmd_retry_failed)

    return parser


def main() -> None:
    """Entry point for the forum scraping CLI."""
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
