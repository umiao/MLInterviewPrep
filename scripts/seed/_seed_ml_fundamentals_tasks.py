#!/usr/bin/env python3
# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""One-off: add 13 ML-fundamentals portal tasks into MLInterviewPrep tasks.db.

Chain: alpha -> beta -> gamma -> gamma.5 (barrier) -> delta -> epsilon ->
       zeta1 (barrier) -> zeta2 -> zeta3 -> zeta4 -> eta -> theta -> iota ->
       kappa -> lambda

After creation, tasks list should show all in `pending`, with each task blocked
on its predecessor.  The autonomous runner picks one at a time (serial, per
workspace rule).

Re-run safe: if a task with the exact title already exists, skip; don't dup.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DB = REPO_ROOT / ".claude" / "hooks" / "task_db.py"
MLIP = REPO_ROOT / "MLInterviewPrep"


def run_task_db(args: list[str], cwd: Path) -> dict:
    """Invoke task_db.py inside MLInterviewPrep and return parsed JSON."""
    cmd = ["python", str(TASK_DB), *args]
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        print(f"[seed] task_db.py failed: {proc.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def list_existing_titles(cwd: Path) -> set[str]:
    cmd = ["python", str(TASK_DB), "list"]
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", check=False,
    )
    if proc.returncode != 0:
        return set()
    try:
        rows = json.loads(proc.stdout)
        return {r["title"] for r in rows}
    except Exception:
        return set()


TASKS: list[dict] = [
    {
        "key": "alpha",
        "title": "[T-MLF-01] Parse attachment -> ml_fundamentals_inventory.yaml (27 Q, tier + interview_freq columns)",
        "priority": "P0", "complexity": "S",
        "description": (
            "Parse the 85KB 'ML high-freq' attachment at "
            "C:/Users/Shenghui Xu/.claude/channels/discord/inbox/1776657806963-1495635943351128184.txt "
            "(lines 22-1796) into data/ml_fundamentals_inventory.yaml.\n\n"
            "Schema per item:\n"
            "  - id: 1..27\n"
            "  - slug: kebab-case\n"
            "  - category: classical_ml | eval_data | unsupervised | dl_training | attention_transformer | llm_stats\n"
            "  - tier: T1 | T2 | T3  (cleanup workload)\n"
            "  - interview_freq: high | mid | low\n"
            "  - line_range: [start, end]\n"
            "  - title_zh: ...\n"
            "  - title_en: ...\n"
            "  - acronyms_to_expand: [GELU, ...]\n"
            "  - cleanup_notes: str\n\n"
            "AC: yaml file committed; 27 items; CE/KL is in classical_ml (not eval_data); interview_freq present on every row."
        ),
    },
    {
        "key": "beta",
        "title": "[T-MLF-02] seed_ml_fundamentals_skeleton.py: root + 6 category + 27 leaf stubs",
        "priority": "P0", "complexity": "S",
        "description": (
            "Create scripts/seed_ml_fundamentals_skeleton.py (idempotent, Python 3.11+, encoding=utf-8).\n\n"
            "Inserts into framework_nodes:\n"
            "  - 1 root: path='ml-fundamentals', depth=0, title='ML 八股文 · Fundamentals'\n"
            "  - 6 category children (depth=1): classical_ml, eval_data, unsupervised, dl_training, attention_transformer, llm_stats\n"
            "  - 27 leaf grandchildren (depth=2), description='TODO[MLF-<slug>]' placeholder, path '<cat>/<slug>'\n\n"
            "Reads from data/ml_fundamentals_inventory.yaml (from alpha).\n"
            "Guards: sha256 of pre/post, refuses to run if existing path conflicts with a different title.\n"
            "Second run is a no-op (updates=0 skipped=34).\n\n"
            "AC: both runs pass; framework_nodes WHERE path LIKE 'ml-fundamentals%' returns exactly 34 rows (1+6+27)."
        ),
        "depends_on_key": "alpha",
    },
    {
        "key": "gamma",
        "title": "[T-MLF-03] T1 content fill Cat 1-2 (7 Q: Classical ML & Losses + Eval/Data)",
        "priority": "P0", "complexity": "M",
        "description": (
            "Write description markdown for 7 leaves:\n"
            "  Cat 1 (Classical ML & Losses): #1 Bias-Variance, #2 L1 vs L2 (+OLS), #3 Logistic Loss, #4 GBDT/RF/XGB, #7 CE vs KL\n"
            "  Cat 2 (Eval & Data Issues): #5 Class Imbalance, #6 AUC vs PR\n\n"
            "T1 = verbatim cleanup: dedupe the 3-line LaTeX repetition artifact from the attachment; "
            "first-occurrence terms as **English** (缩写, 中文); preserve all derivations and 追问预判 sections.\n\n"
            "Write via scripts/seed_ml_fundamentals_content_cat12.py (idempotent).\n"
            "AC: 7 framework_nodes.description updated; each has KaTeX math; each has section headers; seed re-run is no-op."
        ),
        "depends_on_key": "beta",
    },
    {
        "key": "gamma_barrier",
        "title": "[T-MLF-03.5] [BARRIER] Template lock checkpoint: dev server review + canonical snippet",
        "priority": "P0", "complexity": "S",
        "description": (
            "BARRIER TASK: autonomous runner stops here; user must manually review before proceeding.\n\n"
            "Steps (performed by runner):\n"
            "  1. Start frontend dev server (npm run dev under src/frontend/)\n"
            "  2. For each of the 7 Cat 1-2 leaves, open the drawer and capture rendered-state notes (KaTeX OK? bold terms? section breaks?)\n"
            "  3. Produce docs/ml_fundamentals_template.md — canonical markdown template snippet (5 sections: 问题设定 / 推导 / 物理意义 / 常见追问 / 参考), with formatting rules explicit\n"
            "  4. Append to PROGRESS.md with status [BARRIER-AWAITING-USER]\n\n"
            "AC: template file exists; PROGRESS entry written. Runner STOPS after this task even if further tasks are unblocked (manual re-launch required)."
        ),
        "depends_on_key": "gamma",
    },
    {
        "key": "delta",
        "title": "[T-MLF-04] T1 content fill Cat 3-4 (7 Q: Unsupervised + DL Training)",
        "priority": "P0", "complexity": "M",
        "description": (
            "Write description markdown for 7 leaves per the canonical template (from gamma_barrier):\n"
            "  Cat 3 (Unsupervised): #8 K-means, #9 EM+GMM\n"
            "  Cat 4 (DL Training): #10 BN vs LN, #11 Adam/SGD/AdamW, #12 Gradient Vanish/Explode, #13 Dropout, #14 Activation Evolution\n\n"
            "T1 = verbatim cleanup; #10/#11/#14 have non-trivial acronym expansion (BN/LN/GELU/GLU/SwiGLU).\n"
            "Via scripts/seed_ml_fundamentals_content_cat34.py (idempotent)."
        ),
        "depends_on_key": "gamma_barrier",
    },
    {
        "key": "epsilon",
        "title": "[T-MLF-05] T2 content fill Cat 5 (6 Q: Attention & Transformer)",
        "priority": "P0", "complexity": "L",
        "description": (
            "Write description markdown for 6 leaves:\n"
            "  #15 Self-Attention Complexity (merge with its linear-attention deep-dive subsection)\n"
            "  #16 Scaled Dot-Product (why /√d)\n"
            "  #17 MHA/MQA/GQA — REBUILD the comparison table (original is collapsed in attachment)\n"
            "  #18 Position Encoding (Sinusoidal/Learned/RoPE/ALiBi)\n"
            "  #19 KV Cache — FIX the LLaMA-2-7B memory formula (original is mis-formatted)\n"
            "  #20 Pre-norm vs Post-norm\n\n"
            "T2 = polish: full acronym expansion (SSM, HBM, SRAM, RoPE, ALiBi, NTK, YaRN, QK-Norm, µP) + format-bug fixes.\n"
            "Via scripts/seed_ml_fundamentals_content_cat5.py (idempotent)."
        ),
        "depends_on_key": "delta",
    },
    {
        "key": "zeta1",
        "title": "[T-MLF-06a] [BARRIER] T3 Y-depth #21 SFT/RLHF/DPO (calibration session)",
        "priority": "P0", "complexity": "M",
        "description": (
            "CALIBRATION BARRIER: runner stops after this task so user can review the Y-depth standard.\n\n"
            "Write a full Y-depth golden answer for #21 (SFT / RLHF / DPO):\n"
            "  Section 1: 问题设定 (three objective types defined rigorously)\n"
            "  Section 2: 推导 — Bradley-Terry RM loss; PPO with KL-constraint; DPO closed-form derivation showing Z(x) cancellation\n"
            "  Section 3: 物理意义 — why ref model stays, why KL anchor, reward hacking\n"
            "  Section 4: 常见追问预判 (5+ items)\n\n"
            "Full acronyms: SFT=Supervised Fine-Tuning, RLHF=Reinforcement Learning from Human Feedback, DPO=Direct Preference Optimization, PPO=Proximal Policy Optimization, RM=Reward Model, KL=Kullback-Leibler.\n\n"
            "Via scripts/seed_ml_fundamentals_content_q21.py (idempotent).\n"
            "AC: node.description written; PROGRESS.md updated with status [BARRIER-AWAITING-USER-CALIBRATION]."
        ),
        "depends_on_key": "epsilon",
    },
    {
        "key": "zeta2",
        "title": "[T-MLF-06b] T3 Y-depth #22 MoE routing + load balancing (template from zeta1)",
        "priority": "P0", "complexity": "M",
        "description": (
            "Apply the calibrated Y-depth template (from zeta1 review) to #22 MoE.\n\n"
            "Four sections with: top-k routing math, load-balancing aux loss derivation (f_i, P_i), "
            "expert collapse definition, capacity factor definition, Switch (k=1) vs Mixtral (k=2) examples, "
            "drop-token behavior.\n\n"
            "Full acronyms: MoE=Mixture of Experts.\n"
            "Via scripts/seed_ml_fundamentals_content_q22.py (idempotent)."
        ),
        "depends_on_key": "zeta1",
    },
    {
        "key": "zeta3",
        "title": "[T-MLF-06c] T3 Y-depth #25 MLE vs MAP (upgraded from X to Y)",
        "priority": "P0", "complexity": "M",
        "description": (
            "Upgrade #25 from original X-depth (acronym-only) to full Y-depth.\n\n"
            "Original covers ~60% already (Gaussian→L2 and Laplace→L1 derivations present). Add:\n"
            "  Section 1: Frequentist vs Bayesian framing\n"
            "  Section 2: Full MLE/MAP derivation + prior-as-regularizer equivalence (keep existing)\n"
            "  Section 3: Physical meaning — prior 'sharpness' σ or b controls λ\n"
            "  Section 4: 常见追问 (conjugate priors, n→∞ limit, when to prefer MAP, credible vs confidence intervals)\n\n"
            "Full acronyms: MLE=Maximum Likelihood Estimation, MAP=Maximum A Posteriori, KKT=Karush-Kuhn-Tucker.\n"
            "Via scripts/seed_ml_fundamentals_content_q25.py (idempotent)."
        ),
        "depends_on_key": "zeta2",
    },
    {
        "key": "zeta4",
        "title": "[T-MLF-06d] T3 X-depth batch #23/#24/#26/#27 (Tokenization, Chinchilla, CLT/LLN, A/B test)",
        "priority": "P0", "complexity": "M",
        "description": (
            "X-depth: keep original structure, expand all acronyms on first use, fix formula context holes.\n\n"
            "  #23 Tokenization — BPE=Byte Pair Encoding, PMI=Pointwise Mutual Information; preserve BPE/WordPiece/SentencePiece comparison\n"
            "  #24 Chinchilla scaling — add Kaplan 2020 / Hoffmann 2022 paper refs; formalize '~20 tokens/param' rule; add inference-cost note\n"
            "  #26 CLT vs LLN — CLT=Central Limit Theorem, LLN=Law of Large Numbers; define iid, a.s., →_P, →_d symbols\n"
            "  #27 A/B test — FWER=Family-Wise Error Rate, FDR=False Discovery Rate, MDE=Minimum Detectable Effect, BH=Benjamini-Hochberg; add power=1-β intuition\n\n"
            "Via scripts/seed_ml_fundamentals_content_q2324_2627.py (idempotent)."
        ),
        "depends_on_key": "zeta3",
    },
    {
        "key": "eta",
        "title": "[T-MLF-07] MLFundamentals.tsx page + ?cat=&slug= deep-link",
        "priority": "P0", "complexity": "M",
        "description": (
            "Create src/frontend/src/pages/MLFundamentals.tsx modeled on QuickIndex.tsx:\n"
            "  - Top tab bar: 6 categories (classical_ml, eval_data, unsupervised, dl_training, attention_transformer, llm_stats)\n"
            "  - URL state: ?cat=<cat_slug>&slug=<question_slug>\n"
            "  - Each category: grid of cards (title_zh / title_en / interview_freq badge)\n"
            "  - Card click → FrameworkNodeDrawer opens with that leaf's description\n"
            "  - Deep-link behavior: on page load, if ?slug= present, auto-open drawer; closing drawer clears slug from URL; changing tab preserves slug if valid in new cat else clears\n"
            "  - Footer cross-link: '延伸: MLSD pillar' + '/quick-index?section=ml'\n\n"
            "Route added in App.tsx: '/ml-fundamentals'.\n"
            "AC: build passes (npm run build); all 27 drawers open; URL deep-link shared across reload."
        ),
        "depends_on_key": "zeta4",
    },
    {
        "key": "theta",
        "title": "[T-MLF-08] Sidebar navItem + route wiring",
        "priority": "P0", "complexity": "S",
        "description": (
            "Edit src/frontend/src/components/Sidebar.tsx:\n"
            "  add { to: '/ml-fundamentals', label: 'ML 八股文' } between Quick Index and Framework in navItems.\n\n"
            "AC: sidebar shows new item at correct position; clicking navigates to /ml-fundamentals; no TS errors."
        ),
        "depends_on_key": "eta",
    },
    {
        "key": "iota",
        "title": "[T-MLF-09] KaTeX/drawer smoke test — all 27 drawers",
        "priority": "P1", "complexity": "S",
        "description": (
            "Run npm run dev; manually open every one of the 27 question drawers; record rendering status in docs/ml_fundamentals_smoke.md.\n\n"
            "Per drawer: {slug, KaTeX OK y/n, GFM table OK y/n, callout render OK y/n, notes}.\n\n"
            "If anything broken: file follow-up task via task_db.py add; do NOT fix silently.\n"
            "AC: smoke report committed; each of 27 has a row."
        ),
        "depends_on_key": "theta",
    },
    {
        "key": "kappa",
        "title": "[T-MLF-10] Content QA pass — acronyms, formula context, term definitions",
        "priority": "P1", "complexity": "M",
        "description": (
            "Walk each of 27 leaf descriptions and verify:\n"
            "  (1) every acronym has first-occurrence full expansion in **English** (缩写, 中文) format\n"
            "  (2) every standalone formula has surrounding prose context\n"
            "  (3) any jargon (expert collapse, FWER, MDE, ...) has inline definition\n"
            "Any issue found: update the corresponding seed_ml_fundamentals_content_*.py and re-run; do NOT edit DB directly.\n\n"
            "AC: diffs committed; sha256 of affected rows changed; seed re-run is no-op."
        ),
        "depends_on_key": "iota",
    },
    {
        "key": "lambda",
        "title": "[T-MLF-11] Google Prep Hub id=53 cross-link to /ml-fundamentals",
        "priority": "P2", "complexity": "S",
        "description": (
            "Via scripts/seed_google_hub_mlf_crosslink.py (idempotent with sha256 guard):\n"
            "  append to company_documents.content id=53 a new '系统性八股文复习' bucket above the Fundamentals bucket, linking to '/ml-fundamentals'.\n"
            "Preserve all existing Tier-2/3 buckets byte-identical (sha256 guarded).\n\n"
            "AC: id=53 has new bucket; runs twice: 1 update / 0 updates."
        ),
        "depends_on_key": "kappa",
    },
]


def main() -> None:
    if not MLIP.is_dir():
        print(f"[seed] MLInterviewPrep not found at {MLIP}", file=sys.stderr)
        sys.exit(1)

    existing = list_existing_titles(MLIP)

    key_to_id: dict[str, str] = {}
    created = 0
    skipped = 0

    for spec in TASKS:
        title = spec["title"]
        if title in existing:
            print(f"[seed] skip (exists): {title}")
            # Try to recover ID from list for downstream depends_on
            proc = subprocess.run(
                ["python", str(TASK_DB), "list"],
                cwd=str(MLIP), capture_output=True, text=True,
                encoding="utf-8", check=False,
            )
            if proc.returncode == 0:
                for row in json.loads(proc.stdout):
                    if row["title"] == title:
                        key_to_id[spec["key"]] = row["id"]
                        break
            skipped += 1
            continue

        args = [
            "add",
            "--title", title,
            "--priority", spec["priority"],
            "--complexity", spec["complexity"],
            "--description", spec["description"],
        ]
        dep_key = spec.get("depends_on_key")
        if dep_key:
            dep_id = key_to_id.get(dep_key)
            if not dep_id:
                print(f"[seed] ERROR: dep {dep_key} not resolved for {spec['key']}", file=sys.stderr)
                sys.exit(1)
            args += ["--depends-on", dep_id]

        result = run_task_db(args, MLIP)
        new_id = result["id"]
        key_to_id[spec["key"]] = new_id
        print(f"[seed] created {new_id}: {title[:80]}")
        created += 1

    print(f"\n[seed] DONE: {created} created, {skipped} skipped")
    print("[seed] chain:")
    for spec in TASKS:
        tid = key_to_id.get(spec["key"], "?")
        dep = spec.get("depends_on_key", "-")
        dep_id = key_to_id.get(dep, "-") if dep != "-" else "-"
        print(f"  {spec['key']:15s} -> {tid}  (depends on {dep}:{dep_id})")


if __name__ == "__main__":
    main()
