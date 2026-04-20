"""Audit: T-P1-550 [T-MLF-10] content QA pass for 27 ml-fundamentals leaves.

Read-only. Scans every `ml-fundamentals/<cat>/<slug>` description and flags:

  (1) ACRONYMS: any all-caps token (2-5 letters, optionally with hyphens/digits)
      whose first occurrence lacks a canonical expansion pattern of the form
      `**English Full Name** (ACRO, 中文)`. Whitelists common non-acronym
      all-caps strings (e.g. `MUST`, `NOTE`, `PASS`, etc.) and LaTeX/math
      tokens inside $..$ or $$..$$.
  (2) STANDALONE FORMULA: a `$$..$$` display block preceded AND followed by
      a blank line with no Chinese/English prose sentence in the next
      non-blank, non-heading line (i.e. the formula has no explanation).
  (3) JARGON: occurrences of known interview jargon (`expert collapse`,
      `FWER`, `MDE`, `power`, `p-value`, `Type I`, etc.) whose first
      appearance lacks a surrounding inline definition (parenthesized
      Chinese gloss or a colon-led explanation within the same sentence).

Output: a Markdown report `logs/mlf_content_qa_audit.md` (one table per
category, plus a summary at the bottom). Exits 0 regardless of findings
(read-only audit). Writer (update_ml_fundamentals_content_qa.py) uses the
report to drive seed-script edits.
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
from collections import OrderedDict

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"
OUT_PATH = REPO_ROOT / "logs" / "mlf_content_qa_audit.md"


ACRONYM_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,5}(?:-[A-Z0-9]+)?)\b")

# Tokens that look like acronyms but are either English words/labels or math
# tokens that don't need Chinese expansion. Keep conservative.
NON_ACRONYM_WHITELIST = {
    # Logger / doc markers (won't appear in body text unless quoted)
    "TODO", "NOTE", "PASS", "FAIL", "WARN", "MUST", "BUG",
    # Label tokens commonly embedded in notes
    "GOOD", "BAD", "OK", "N", "A", "I", "II", "III", "IV", "V", "VI",
    # Common English words caps'd for emphasis
    "AND", "OR", "NOT", "IF", "ELSE", "THEN",
    # HTTP methods / status labels (not typically in ml content)
    "GET", "POST", "PUT", "DELETE",
    # Common doc headings already in English per style guide
    "TL", "DR",
    # Model / architecture names per style guide (do NOT translate)
    "BERT", "GPT", "GPT-2", "GPT-3", "GPT-4", "GPT-3.5", "T5", "BART",
    "CLIP", "ViT", "CNN", "RNN", "LSTM", "GRU", "ResNet", "Transformer",
    "ALBERT", "RoBERTa", "ELECTRA", "DeBERTa", "CANINE", "ByT5",
    "Llama", "LLaMA", "DeepSeek", "Mistral", "Qwen", "Gemma",
    # Hardware model numbers
    "GPU", "TPU", "CPU", "HBM", "SRAM", "DRAM", "NVMe",
    "H100", "A100", "V100", "H800", "A800", "B100", "B200", "MI300",
    # Optimizer / attention variant names treated as proper nouns
    "Adam", "AdamW", "SGD", "RMSProp", "LAMB", "LARS",
    "FA-2", "FA-3", "FAVOR", "ISTA", "GOSS",
    # Version / index labels
    "V2", "V3", "V4", "V5", "B2", "B3", "B4",
    # Regularization names (L1/L2 already explained in context as 范数)
    "L1", "L2", "L3", "L4",
    # Statistical / loss abbreviations treated as standard English jargon
    "JS", "JSD", "LM", "NN",
    # Publication / benchmark labels
    "BDA3", "MLF-05", "MLF-06", "MLF-01", "MLF-15", "MLF-18",
    # Math operator abbreviations (rarely expanded)
    "QK", "QKV", "CLS", "SEP",
    # F1 is standard ML metric, treat as proper noun; FP/FN/TP/TN similar
    "F1", "FP", "FN", "TP", "TN",
    # CV/NLP/ML domain abbreviations — treat as standard
    "CV", "NLP", "ML", "DL", "AI", "IR", "RL",
    # Common OS/system acronyms treated as standard English
    "OS", "IO",
}

# Canonical acronym -> English full name (for quick cross-check). When an
# acronym from this list appears, we know the expected expansion to look for.
CANONICAL = {
    "IID": "Independent and Identically Distributed",
    "MSE": "Mean Squared Error",
    "MAE": "Mean Absolute Error",
    "OLS": "Ordinary Least Squares",
    "MAP": "Maximum A Posteriori",
    "MLE": "Maximum Likelihood Estimation",
    "KL": "Kullback-Leibler Divergence",
    "CE": "Cross-Entropy",
    "SGD": "Stochastic Gradient Descent",
    "BN": "Batch Normalization",
    "LN": "Layer Normalization",
    "RN": "RMS Normalization",
    "GN": "Group Normalization",
    "MHA": "Multi-Head Attention",
    "MQA": "Multi-Query Attention",
    "GQA": "Grouped-Query Attention",
    "MoE": "Mixture of Experts",
    "KV": "Key-Value",
    "RoPE": "Rotary Position Embedding",
    "ALiBi": "Attention with Linear Biases",
    "LoRA": "Low-Rank Adaptation",
    "QLoRA": "Quantized LoRA",
    "PEFT": "Parameter-Efficient Fine-Tuning",
    "RLHF": "Reinforcement Learning from Human Feedback",
    "DPO": "Direct Preference Optimization",
    "PPO": "Proximal Policy Optimization",
    "SFT": "Supervised Fine-Tuning",
    "FFN": "Feed-Forward Network",
    "FFW": "Feed-Forward",
    "RAG": "Retrieval-Augmented Generation",
    "SVM": "Support Vector Machine",
    "GBDT": "Gradient Boosted Decision Trees",
    "RF": "Random Forest",
    "CTR": "Click-Through Rate",
    "AUC": "Area Under the Curve",
    "NDCG": "Normalized Discounted Cumulative Gain",
    "PR": "Precision-Recall",
    "ROC": "Receiver Operating Characteristic",
    "FPR": "False Positive Rate",
    "TPR": "True Positive Rate",
    "FWER": "Family-Wise Error Rate",
    "FDR": "False Discovery Rate",
    "MDE": "Minimum Detectable Effect",
    "CLT": "Central Limit Theorem",
    "LLN": "Law of Large Numbers",
    "BPE": "Byte-Pair Encoding",
    "EM": "Expectation-Maximization",
    "GMM": "Gaussian Mixture Model",
    "KKT": "Karush-Kuhn-Tucker",
    "LR": "Learning Rate",
    "AdamW": "Adam with Decoupled Weight Decay",
    "A/B": "A/B (对照组/实验组)",
}

# Interview jargon strings (Chinese or English) whose first appearance should
# have an inline gloss. Store as (needle, hint).
JARGON_PATTERNS = [
    ("expert collapse", "专家坍缩 / 路由坍缩 — few experts dominate routing"),
    ("FWER", "family-wise error rate 族误差率"),
    ("MDE", "minimum detectable effect 最小可检测效应"),
    ("Type I", "一类错误 / false positive"),
    ("Type II", "二类错误 / false negative"),
    ("p-value", "p 值 / 在原假设下观测到至少此极端统计量的概率"),
    ("power", "统计功效 / 1 - β"),
]


def load_descriptions(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """Return [(path, slug, description)] for every ml-fundamentals leaf."""
    rows = conn.execute(
        """
        SELECT path, description FROM framework_nodes
        WHERE path LIKE 'ml-fundamentals/%/%' AND description IS NOT NULL
        ORDER BY path
        """
    ).fetchall()
    out = []
    for path, desc in rows:
        # leaf slugs are the trailing path segment
        parts = path.split("/")
        if len(parts) != 3:
            continue
        slug = parts[2]
        out.append((path, slug, desc or ""))
    return out


def strip_code_and_math(text: str) -> str:
    """Remove fenced code blocks and math blocks so acronym detection doesn't
    match LaTeX macros like \\mathrm{MSE} or python identifiers.
    """
    # fenced code blocks
    text = re.sub(r"```[\s\S]*?```", " ", text)
    # display math
    text = re.sub(r"\$\$[\s\S]*?\$\$", " ", text)
    # inline math
    text = re.sub(r"(?<!\\)\$[^\n\$]+\$", " ", text)
    return text


def first_occurrence_index(text: str, token: str) -> int:
    """Index of first whole-word occurrence of token; -1 if absent."""
    m = re.search(r"\b" + re.escape(token) + r"\b", text)
    return m.start() if m else -1


def has_canonical_expansion(text: str, acronym: str, first_idx: int) -> bool:
    """True iff near the first occurrence of acronym there is some form of
    expansion (English full name, Chinese gloss, or inline definition).
    Window is [-200, +80] characters around first_idx.
    """
    window_start = max(0, first_idx - 200)
    window = text[window_start: first_idx + len(acronym) + 80]

    # Pattern A: **Full Name** (ACRO, 中文) or full-width variants
    pat_a = re.compile(
        r"\*\*[^*]+\*\*\s*[(（]\s*" + re.escape(acronym)
        + r"\s*[,，]\s*[^)）]+?[)）]"
    )
    if pat_a.search(window):
        return True

    # Pattern B: inline `(ACRO, 中文)` or （ACRO，中文）
    pat_b = re.compile(
        r"[(（]\s*" + re.escape(acronym) + r"\s*[,，]\s*[^)）]+?[)）]"
    )
    if pat_b.search(window):
        return True

    # Pattern C: `ACRO = English (中文)` or `ACRO = English（中文）`
    pat_c = re.compile(
        re.escape(acronym)
        + r"\s*=\s*[A-Za-z][A-Za-z\s\-]+\s*[(（][^)）]+?[)）]"
    )
    if pat_c.search(window):
        return True

    # Pattern D: `**English Full**（中文）ACRO` — Chinese paren style
    pat_d = re.compile(
        r"\*\*[A-Za-z][A-Za-z\s\-]+\*\*\s*[(（][\u4e00-\u9fff][^)）]+?[)）]"
        r"[^A-Z]{0,30}" + re.escape(acronym)
    )
    if pat_d.search(window):
        return True

    # Pattern D2: `ACRO（**English Full**，ACRO，中文）` — my q_a pass style
    # for some entries (e.g. KTO, DPMM) using full-width parens + bold English
    pat_d2 = re.compile(
        re.escape(acronym)
        + r"\s*[(（]\s*\*\*[A-Za-z][A-Za-z\s\-]+\*\*[^)）]*?[)）]"
    )
    if pat_d2.search(window):
        return True

    # Pattern F: `ACRO（English Full Name, 中文）` with inline English gloss
    # (no bolding) — accepted by audit as sufficient context
    pat_f = re.compile(
        re.escape(acronym)
        + r"\s*[(（][A-Za-z][A-Za-z\s\-]{4,}[^)）]*?[)）]"
    )
    if pat_f.search(window):
        return True

    # Pattern G: `English Full Name (ACRO)` — English-first form commonly used
    # with half-width parens (e.g. `TensorFlow (TF)`)
    pat_g = re.compile(
        r"[A-Za-z][A-Za-z\s\-]{4,}\s*[(（]\s*" + re.escape(acronym)
        + r"\s*[)）]"
    )
    if pat_g.search(window):
        return True

    # Pattern E: acronym immediately adjacent to its bolded English expansion
    # e.g. `**OLS**` … `Ordinary Least Squares` or `ACRO **English Full**`
    pat_e = re.compile(
        r"\*\*" + re.escape(acronym) + r"\*\*\s*[(（]?\s*"
        r"[A-Za-z][A-Za-z\s\-]{4,}"
    )
    if pat_e.search(window):
        return True

    return False


def strip_h1_title(text: str) -> str:
    """Remove the leading `# ...` title line so first-occurrence detection
    starts in the body prose (where the `**English** (ACRO, 中文)` intro is
    expected to appear).
    """
    lines = text.split("\n")
    if lines and lines[0].lstrip().startswith("# "):
        lines[0] = ""
    return "\n".join(lines)


def scan_acronyms(text: str) -> list[tuple[str, str]]:
    """Return [(acronym, excerpt)] for first-occurrence acronyms lacking
    canonical expansion. One finding per acronym per document.
    """
    cleaned = strip_code_and_math(strip_h1_title(text))
    # track seen to only check FIRST occurrence per acronym
    seen: dict[str, int] = OrderedDict()
    for m in ACRONYM_RE.finditer(cleaned):
        acro = m.group(1)
        if acro in seen:
            continue
        if acro in NON_ACRONYM_WHITELIST:
            continue
        # Skip any acronym starting with a digit-prefixed model number
        if re.match(r"^[A-Z]\d{2,3}$", acro):  # e.g. H100, A100
            continue
        # Skip pure model-family names with digit suffix (GPT-4, T5, V100)
        if re.match(r"^[A-Z]{1,4}-?\d+$", acro):
            continue
        seen[acro] = m.start()

    findings: list[tuple[str, str]] = []
    for acro, idx in seen.items():
        if has_canonical_expansion(cleaned, acro, idx):
            continue
        # Some acronyms like AC, P0 etc. are task-markers; filter
        # (length 2 + purely letters + very high freq across English is OK
        # if the document doesn't otherwise introduce it; heuristic: accept
        # very short acronyms if appearing only once and inside parentheses
        # `(IID)` — already matched by pat_b). Here we just report.
        start = max(0, idx - 40)
        end = min(len(cleaned), idx + 60)
        excerpt = cleaned[start:end].replace("\n", " ").strip()
        findings.append((acro, excerpt))
    return findings


def _has_prose(line: str) -> bool:
    """True iff line looks like natural-language prose (>=2 CJK chars OR
    >=3 English words). Headings, bare labels, and formula markers excluded."""
    line = line.strip()
    if not line:
        return False
    if line.startswith("#"):
        return False
    if line.startswith("$$") or line.startswith("$"):
        return False
    if line.startswith("|"):  # table row
        return False
    chinese_chars = sum(1 for c in line if "\u4e00" <= c <= "\u9fff")
    english_words = len(re.findall(r"[A-Za-z]{2,}", line))
    return chinese_chars >= 2 or english_words >= 3


def scan_standalone_formulas(text: str) -> list[tuple[str, str]]:
    """Find $$..$$ blocks that have NO prose on either side (both before AND
    after lack meaningful prose). Returns [(snippet, reason)]."""
    findings: list[tuple[str, str]] = []
    for m in re.finditer(r"\n\s*\n\$\$([\s\S]*?)\$\$\s*\n(?=\n|$)", text):
        snippet = m.group(1).strip().split("\n", 1)[0][:60]
        # Look BEFORE the formula (up to 6 non-blank lines backward)
        before_text = text[: m.start()]
        before_lines = [ln for ln in before_text.splitlines() if ln.strip()]
        before_window = before_lines[-6:]
        has_before = any(_has_prose(ln) for ln in before_window)

        # Look AFTER the formula (up to 6 non-blank lines forward)
        tail = text[m.end(): m.end() + 600]
        tail_lines = [ln for ln in tail.splitlines() if ln.strip()]
        after_window = tail_lines[:6]
        has_after = any(_has_prose(ln) for ln in after_window)

        # Only flag if BOTH sides lack prose (truly orphan formula)
        if not has_before and not has_after:
            findings.append((snippet, "no prose context before or after"))
    return findings


def scan_jargon(text: str) -> list[tuple[str, str]]:
    """Return [(jargon, context)] for first-occurrence jargon lacking gloss."""
    findings: list[tuple[str, str]] = []
    for needle, hint in JARGON_PATTERNS:
        idx = text.find(needle)
        if idx < 0:
            continue
        # Look backwards 120 chars and forwards 120 chars; accept if a Chinese
        # gloss or an English explanation within 200 chars.
        window = text[max(0, idx - 120): idx + 200]
        # Presence of at least one of: parenthesized Chinese, colon explanation
        has_cn_paren = bool(
            re.search(r"\([^)]*[\u4e00-\u9fff][^)]*\)", window)
        )
        has_colon_explain = bool(
            re.search(r"(?:[:：])[^\n]{8,}", window)
        )
        has_chinese_nearby = bool(re.search(r"[\u4e00-\u9fff]{3,}", window))
        if has_cn_paren or (has_colon_explain and has_chinese_nearby):
            continue
        ctx_start = max(0, idx - 40)
        ctx_end = min(len(text), idx + len(needle) + 60)
        findings.append(
            (needle, text[ctx_start:ctx_end].replace("\n", " ").strip())
        )
    return findings


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        leaves = load_descriptions(conn)
    finally:
        conn.close()

    if len(leaves) != 27:
        print(f"[WARN] expected 27 leaves, got {len(leaves)}")

    report: list[str] = []
    report.append("# ML-Fundamentals Content QA Audit")
    report.append("")
    report.append(
        "**Task**: T-P1-550 [T-MLF-10] content QA pass -- acronym expansions, "
        "formula context, jargon definitions"
    )
    report.append("")
    report.append(
        "Audit categories: **A** = acronym lacks first-occurrence expansion "
        "(`**English** (ACRO, 中文)`). **F** = standalone display formula with "
        "no adjacent prose. **J** = jargon lacks inline definition."
    )
    report.append("")
    report.append("| # | Slug | A | F | J | Top findings |")
    report.append("|---|------|---|---|---|--------------|")

    grand = {"A": 0, "F": 0, "J": 0}
    per_leaf: list[tuple[str, str, list, list, list]] = []

    for i, (path, slug, desc) in enumerate(leaves, 1):
        a = scan_acronyms(desc)
        f = scan_standalone_formulas(desc)
        j = scan_jargon(desc)
        grand["A"] += len(a)
        grand["F"] += len(f)
        grand["J"] += len(j)
        per_leaf.append((path, slug, a, f, j))
        top: list[str] = []
        if a:
            top.append("A: " + ", ".join(sorted({x[0] for x in a})[:6]))
        if f:
            top.append(f"F: {len(f)}")
        if j:
            top.append("J: " + ", ".join(sorted({x[0] for x in j})[:4]))
        top_s = "; ".join(top) if top else "(clean)"
        report.append(
            f"| {i} | `{slug}` | {len(a)} | {len(f)} | {len(j)} | {top_s} |"
        )

    report.append("")
    report.append(
        f"## Totals -- A={grand['A']} F={grand['F']} J={grand['J']}"
    )
    report.append("")

    # per-leaf details (only leaves with findings)
    report.append("## Per-leaf Details")
    for path, slug, a, f, j in per_leaf:
        if not (a or f or j):
            continue
        report.append(f"\n### {slug}  (`{path}`)\n")
        if a:
            report.append("**Acronyms (first-occurrence expansion missing):**\n")
            for acro, excerpt in a:
                canon = CANONICAL.get(acro, "")
                hint = f" -- canonical: {canon}" if canon else ""
                report.append(f"- `{acro}`{hint}\n    - excerpt: `{excerpt}`")
            report.append("")
        if f:
            report.append("**Standalone formulas (no adjacent prose):**\n")
            for snippet, reason in f:
                report.append(f"- `$${snippet}...$$` -- {reason}")
            report.append("")
        if j:
            report.append("**Jargon (first occurrence lacks inline gloss):**\n")
            for needle, context in j:
                report.append(f"- `{needle}`\n    - excerpt: `{context}`")
            report.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print(f"[DONE] wrote {OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"[SUMMARY] A={grand['A']} F={grand['F']} J={grand['J']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
