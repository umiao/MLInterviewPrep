---
name: scrape
description: Forum scraping automation -- sync config, scrape links, fetch posts
user_invocable: true
---

# /scrape -- Forum Scraping Skill

## Usage

```
/scrape                      # Full run: sync config -> scrape links -> fetch posts
/scrape status               # Progress table for all seeds
/scrape --links-only         # Phase A only (collect links, no content fetch)
/scrape --resume             # Phase B only (fetch pending posts)
/scrape --company LinkedIn   # Filter to one company
/scrape --cron-setup         # Set up recurring cron jobs
```

## Procedure

### Step 1 -- Load & validate config

```bash
python -c "from src.backend.scraper.scrape_config import load_config; c = load_config(); print(f'{len(c.companies)} companies, {sum(len(co.seeds) for co in c.companies)} seeds')"
```

If validation fails, show the error and stop.

### Step 2 -- Sync seeds to DB

For each seed in config, check `python scripts/forum_scrape.py list-seeds`.
If a seed URL is missing from DB, add it:

```bash
python scripts/forum_scrape.py add-seed "<url>" --label "<label>" --company "<company_name>"
```

Never delete seeds from DB that are missing from config -- only add missing ones.

### Step 3 -- Phase A (link collection)

For each seed (or filtered by `--company`):

```bash
python scripts/forum_scrape.py scrape <seed_id> --pages 999
```

The scraper auto-detects max page and early-stops on 3 consecutive zero-new pages.
`last_scraped_page` is updated in DB per page.

**Resume**: Check `python scripts/forum_scrape.py batch-status` for `Last Page`.
If partially scraped, pass `--start-page <last+1>`:

```bash
python scripts/forum_scrape.py scrape <seed_id> --pages 999 --start-page <last+1>
```

Skip this step if `--resume` flag is set (Phase B only).

### Step 4 -- Phase B (content fetch)

Unless `--links-only` was specified:

```bash
python scripts/forum_scrape.py fetch <seed_id> --all --limit 50
```

The `--limit 50` prevents unbounded runs. Repeat if more pending posts remain.

### Step 5 -- Retry & report

```bash
python scripts/forum_scrape.py retry-failed <seed_id>
python scripts/forum_scrape.py batch-status
```

### Content quality escalation

After Phase B, check `batch-status`. If `failed / total > 0.3`, warn:
"High failure rate -- likely expired cookie. Update ONEPOINT3ACRES_COOKIE in .env."

### Cron setup (`--cron-setup`)

Create two recurring jobs using CronCreate:

| Job | Schedule | What it does |
|-----|----------|--------------|
| Fetch batch | `17 */4 * * *` (every 4 hours) | `/scrape --resume` -- drains pending via `fetch --limit 50` |
| Discover | `42 2 * * *` (daily 2:42 AM) | `/scrape --links-only` -- re-scans from page 1, early-stops |

**Important**: CronCreate jobs are session-only (die on exit, 7-day max).
Print this warning to the user after setup.

## Human-machine protocol

### Human does
1. Edit `config/scrape_seeds.yaml` to add/remove companies + seed URLs
2. Keep `ONEPOINT3ACRES_COOKIE` in `.env` fresh (symptom: high failure rate)
3. Optionally run Chrome with `--remote-debugging-port=9222` for CDP speed
4. Run `/scrape --cron-setup` in a Claude session to start automation
5. Run `/scrape status` anytime to check progress

### Machine does
1. Validate config (schema errors = immediate stop with clear message)
2. Sync config -> DB (add missing seeds, never delete)
3. Scrape links + fetch posts with rate limiting
4. Track `last_scraped_page` in DB for resume
5. Reject posts shorter than 50 chars (login wall detection)
6. Retry failures automatically
7. Never modify YAML. Never import to company docs without explicit ask.

### Escalation (machine -> human)
- ">30% failed fetches" -> cookie likely expired
- "0 new links on 3 consecutive discovery sweeps" -> seed may be stale
- "Playwright/CDP unavailable" -> suggest CDP mode
- "Schema validation error" -> show the offending key/field
