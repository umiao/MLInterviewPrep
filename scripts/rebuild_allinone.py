"""Rebuild the All-in-One document (company_documents id=19) from source docs 12-18, 20.

Merges the prep script header with all 8 day documents in chronological order.
"""

import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"

# Day order: Doc 18 is Day1, Doc 12 is Day2, ..., Doc 20 is Day8
DAY_ORDER = [
    (18, "Day 1"),
    (12, "Day 2"),
    (13, "Day 3"),
    (14, "Day 4"),
    (15, "Day 5"),
    (16, "Day 6"),
    (17, "Day 7"),
    (20, "Day 8"),
]

# Prep script header - the top section of the All-in-One doc
PREP_HEADER = r"""# Adobe Senior MLE (Generative AI) - Complete Prep Notes
> {doc_count} documents merged | Generated {date}

---

# Phone Screen Prep Script

# Adobe Senior MLE -- Phone Screen Prep

> **Week of March 30 - April 3, 2026 | Phone Screen | Exact time TBD**

---

## JD Key Highlights (Senior MLE -- Generative AI)

**Role focus**: Turn research breakthroughs into product features. Domains: **NLP, Image/Video generation, editing, multimodal AI**.

**Core responsibilities**:
- Transform research -> practical Generative AI / LLM / RL / Reasoning / Evaluation applications
- Rapid prototyping, demonstrate feasibility + business impact
- GPU-accelerated pipelines for model training & inference (performance, scalability, reliability)
- Collaborate with researchers + ML engineers, publish at top venues

**Must-have qualifications**:
- PhD/MS + **7+ years** professional experience (or equivalent)
- Research/industry experience in: **multimodal LLMs, Image, Video** (at least one)
- Large-scale model training: **data curation, distributed training, memory-efficient strategies**
- Post-training: **fine-tuning, alignment, distillation**
- **PyTorch** proficiency, GPU/TPU cluster scaling

**Preferred (high-signal differentiators)**:
- Large-scale generative model training experience
- **Synthetic data generation**
- Product team technology transfer experience
- Large-scale datasets experience
- 4-7 years in relevant fields

**Key JD keywords to weave into answers**: Generative AI, multimodal LLM, distributed training, inference optimization, alignment, distillation, GPU pipeline, research-to-production, Adobe Firefly

---

## Pre-Interview Checklist

- [x] Review this JD, highlight 3-5 requirement keywords to weave into self-intro
- [ ] Research Adobe AI products: **Firefly** (image gen), **Acrobat AI** (document), **Express** (design), **Experience Platform** (personalization)
- [ ] Prepare self-introduction (60-90s): emphasize research-to-production, large-scale training, generative AI
- [ ] Prepare 2 project stories mapped to JD: (1) large-scale model training/serving (2) research -> product deployment
- [ ] Practice 3 LC mediums: array/string, dynamic programming, tree
- [ ] Prepare 2-3 behavioral stories (STAR format): innovation, collaboration, moving fast
- [ ] Prepare reverse questions: team structure, Firefly tech stack, research vs production balance, publication culture
- [ ] Set up quiet environment + phone/video tested

## Coding Prep

- [ ] Array/String (LC 1 Two Sum, LC 3 Longest Substring, LC 56 Merge Intervals)
- [ ] Dynamic Programming (LC 124 Max Path Sum, LC 322 Coin Change, LC 300 LIS)
- [ ] Tree/Graph (LC 200 Number of Islands, LC 236 LCA, LC 994 Rotting Oranges)
- [ ] Design (LC 146 LRU Cache, LC 380 Insert Delete GetRandom)
- [ ] Binary Search (LC 33 Search in Rotated, LC 875 Koko Eating Bananas)

## ML / Technical Prep

- [ ] Generative AI: diffusion models (DDPM, latent diffusion, classifier-free guidance), how Firefly likely works
- [ ] LLM: transformer architecture, attention mechanism, KV cache, inference optimization (quantization, speculative decoding)
- [ ] Distributed training: data parallelism, model parallelism (tensor/pipeline), DeepSpeed ZeRO, FSDP
- [ ] Post-training: SFT, RLHF/DPO alignment, knowledge distillation, LoRA/QLoRA fine-tuning
- [ ] Multimodal: CLIP, LLaVA-style vision-language models, cross-attention fusion
- [ ] Inference optimization: batching, KV cache, quantization (INT8/INT4), TensorRT, vLLM

## Behavioral Prep (mapped to JD signals)

- [ ] "Research to production" story: took a paper/idea and shipped it as a product feature
- [ ] "Moving fast with innovation" story: rapid prototype that demonstrated business impact
- [ ] "Collaboration with researchers" story: cross-functional teamwork between research and engineering
- [ ] "Technical excellence" story: optimized a system for performance/scalability

---
"""


def _setup_utf8() -> None:
    """Ensure stdout uses UTF-8 on Windows."""
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def rebuild() -> None:
    """Rebuild doc 19 from source documents."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    # Collect source docs
    sections = []
    total_source_chars = 0
    for doc_id, day_label in DAY_ORDER:
        row = conn.execute(
            "SELECT title, content FROM company_documents WHERE id=?", (doc_id,)
        ).fetchone()
        if row is None:
            print(f"[WARN] Doc {doc_id} ({day_label}) not found, skipping")
            continue
        title, content = row
        total_source_chars += len(content)
        sections.append((doc_id, day_label, title, content))
        print(f"  [{day_label}] Doc {doc_id}: {title} ({len(content)} chars)")

    # Build the merged document
    today = datetime.now().strftime("%Y-%m-%d")
    header = PREP_HEADER.format(doc_count=len(sections), date=today)

    parts = [header.strip(), ""]  # header + blank line

    for doc_id, day_label, title, content in sections:
        # Add day separator
        parts.append("")
        parts.append("---")
        parts.append("")
        # Add the content (strip leading/trailing whitespace)
        parts.append(content.strip())

    merged = "\n".join(parts) + "\n"

    # Validate: check no formulas in code blocks
    code_blocks = re.findall(r"```[\s\S]*?```", merged)
    formula_in_code = 0
    for block in code_blocks:
        if "$$" in block:
            formula_in_code += 1
    if formula_in_code > 0:
        print(f"[WARN] {formula_in_code} code blocks contain $$ formulas")

    # Check Chinese content
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", merged))

    # Update doc 19
    conn.execute(
        "UPDATE company_documents SET content=? WHERE id=19",
        (merged,),
    )
    conn.commit()

    # Verify
    new_len = conn.execute(
        "SELECT LENGTH(content) FROM company_documents WHERE id=19"
    ).fetchone()[0]

    print("\n[DONE] Rebuilt doc 19:")
    print(f"  Source docs: {len(sections)}")
    print(f"  Total source chars: {total_source_chars}")
    print(f"  Merged doc size: {new_len} chars")
    print(f"  Chinese characters: {chinese_chars}")
    print("  Previous size: 121556 chars")
    if formula_in_code > 0:
        print(f"  [WARN] Formulas in code blocks: {formula_in_code}")
    else:
        print("  Formulas in code blocks: 0 (clean)")

    conn.close()


if __name__ == "__main__":
    _setup_utf8()
    rebuild()
