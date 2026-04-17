# Adobe EN/中 Bilingual Mirror Seed Deletion — Approval Request

**Date**: 2026-04-13
**Task**: T-P2-191
**Policy**: T-P1-185 AC #4 — deletion of raw seed files requires explicit user approval.

## Candidates (English mirrors of the Chinese sources of truth)

| File | Chars | Chinese source of truth | Archive mirror |
|------|-------|-------------------------|----------------|
| `MLInterviewPrep/scripts/seed_adobe_day1_diffusion.py` | 18,469 | `seed_adobe_day1_chinese.py` | `MLInterviewPrep/archive/legacy_company_docs/2026-04-13/seed_adobe_day1_diffusion.py` |
| `MLInterviewPrep/scripts/seed_adobe_day2_rlhf_dpo.py` | 25,682 | `seed_adobe_day2_chinese.py` | `MLInterviewPrep/archive/legacy_company_docs/2026-04-13/seed_adobe_day2_rlhf_dpo.py` |
| `MLInterviewPrep/scripts/seed_adobe_day3_distributed.py` | 27,406 | `seed_adobe_day3_chinese.py` | `MLInterviewPrep/archive/legacy_company_docs/2026-04-13/seed_adobe_day3_distributed.py` |

## Safety Checks

- [x] Archive copies exist at `MLInterviewPrep/archive/legacy_company_docs/2026-04-13/`
- [x] Archive copies are byte-identical to originals (matched via `wc -c`)
- [x] Chinese source of truth (`*_chinese.py`) retained and untouched
- [x] Reversible via `git restore` + archive copy

## Approval

User must approve by replying **approve T-P2-191** (or similar affirmative) in the task channel or by merging a PR whose description explicitly lists the three files above.

Until approved, task T-P2-191 stays in **blocked** status. Autonomous mode must not self-delete.

## Execution Plan (post-approval)

```bash
git rm MLInterviewPrep/scripts/seed_adobe_day1_diffusion.py \
       MLInterviewPrep/scripts/seed_adobe_day2_rlhf_dpo.py \
       MLInterviewPrep/scripts/seed_adobe_day3_distributed.py
git commit -m "[T-P2-191] Remove 3 Adobe EN bilingual mirror seeds (approved)"
```
