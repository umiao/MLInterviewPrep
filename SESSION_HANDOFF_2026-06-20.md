# Session Handoff -- 2026-06-20 (supervised)

> One-shot handoff for the NEXT session. Authoritative detail: task specs in DB
> (`task_db.py inspect <ID>`), lessons in `LESSONS.md`, surface/routing in
> `CLAUDE.md`. Supersedes SESSION_HANDOFF_2026-06-19.md (removed).

## TL;DR

This session: shipped **T-P1-643** (Uber goldens -> system_designs + Uber tab,
committed), built a reusable **DeepSeek distillation pipeline** + 1 cheat-sheet
pilot, did a **repo-wide emoji cleanup**, and -- most importantly -- **re-scoped
the whole backlog** around a strategic pivot.

## STRATEGIC PIVOT (the key context -- read first)

**There are no active interviews anymore.** The platform's purpose is now:
**distill / extract / systematize the scattered prep content into a durable,
canonical "golden" knowledge base** -- "speak one language / 同出一孔" (one
canonical KG surface, not 30+ companies' duplicated prose). Interview-specific
content is acknowledged as **time-sensitive / low long-term value**.

Consequence: the ROI ranking **flipped**. Structural/systematization work that
builds the canonical golden surface is now the **core**; interview-specific
content authoring and misc cleanup dropped.

## Backlog re-scope (done this session, user-approved)

**Deleted** (low ROI under the new goal): T-P1-644..649 (CHEATSHEET rewrites of
already-filled rows), T-P1-627, T-P2-207, T-P2-239, T-P2-636, T-P2-716, and
**T-P1-924** (Meta cheat sheets -- 作罢; the 1 pilot row `meta-yelp` is kept with
a committed seed, the other 8 dropped).

**Kept as the new core** (build the canonical golden surface):
- **KG-INT B4 cluster** (the centerpiece = "同出一孔"): B4a dry-runs 816/817/819/820,
  B4b executes 822-834, promotion **821** (active/ready), B6 cleanup 836.
- **657** (Invariant-3: ad-hoc content -> seed), **922** (content normalization:
  sections + FK cross-refs), **917** (Guard Phase B enforcer: CI fail-on-drift),
  **921** (drawer_nav extraction).
- **606** (fix the flaky emoji-scanner -- small, real bug).
- **909** (Anthropic golden seed) -- only if the user provides the golden `.md`.

## NEXT STEPS (the "后续 run" -- in order)

1. **Start KG-INT B4 from T-P1-821** (NON-destructive value extraction first):
   read `docs/archive_plans/B4a-*.md` §5 "Promotion candidates", dedup, promote
   passing ones into meta-prep KG nodes. This produces the golden convergence the
   user wants with ZERO risk. Show the effect before touching anything destructive.
2. **Then B4b hard-archives, ONE company at a time, supervised** (start with the
   most bloated + least time-sensitive company). Each: generate skeleton seed +
   7-step causal-proof per `docs/workflow/company_internalization_protocol.md`,
   verify, then next. 9 B4a plans already exist (adobe/google/lyra/meta/
   pinterest x3/slack/uber); the other companies need B4a first.
   **B4b is destructive (deletes ~270K-char prose) -- never batch, always prove.**
3. **Base-hardening, interleaved at user's pace**: 657 (Invariant-3), 922
   (normalization), 917 (enforcer).
4. **606** quick fix; **909** only when the golden `.md` is supplied.

## DeepSeek distillation infra (reusable -- built this session)

For any future "distill into golden" work:
- `scripts/lib/ds_distill.py`: `complete(system, user, ...) -> DistillResult`.
  stdlib urllib; reasoning-model empty-content escalation (doubles max_tokens
  8192->16384). Supervised-only (key absent in autorun -> FileNotFoundError).
- `scripts/lib/.env.deepseek` (gitignored): key, base_url, `deepseek-v4-pro`.
- Contract: OpenAI-compatible; read `.content` (not `reasoning_content`);
  base_url has NO `/v1`; **DeepSeek API deprecated 2026-07-24** -- use before then.
- Example generator + idempotent seed (drafts-as-source-of-truth pattern):
  `scripts/gen_cheat_sheets_meta_goldens.py` (gen) + `scripts/seed_cheat_sheets_meta_goldens.py`
  (reads `scripts/cheatsheet_drafts/*.md`, upserts by slug). The drafts `.md` are
  the git-tracked Invariant-3 source; the seed has no DeepSeek dependency.

## Current state

- `task_db.py pick` = run it; KG-INT B4 chain is mostly blocked/pending (deps).
  **821** and **836** are `active`/`ready`.
- Emoji: repo fully clean (guard: code 0, doc 0).
- dev servers: backend was on :8100; Vite (:5173) died (exit 127) -- restart with
  `cd src/frontend && npm run dev` if the app is needed.
- Working tree: committed this session (see below).

## Run-procedure reminders

- No active interviews -> prioritize durable systematization over interview content.
- DB content writes -> idempotent seed (Invariant 3) + Surface Identification table.
- Commit by explicit path, NEVER `git add .`; English `[T-XX-N]` / `[chore]` msgs.
- `system_designs` new rows: check display_order band (memory
  `reference_system_design_tab_bands.md`): <100 eBay / [100,130) Interview /
  [130,199) ML MLSD / [199,300) Pinterest / [300,400) ML Infra / [400,500) Uber.
- Read/write CJK DB content with `PYTHONIOENCODING=utf-8`.
- subprocess to call a python script: use `sys.executable`, NOT the `/c/...` MSYS path.
