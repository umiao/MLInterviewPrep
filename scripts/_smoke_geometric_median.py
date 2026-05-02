"""Smoke test: extract the Weiszfeld code from problems.id=1108 notes and
exercise it on three scenarios.

1. Symmetric points around origin -> result must be near origin
   (sanity check; no degeneracy).
2. Single dominant outlier -> centroid is pulled away while
   geometric median stays near the inlier mass (robustness check).
3. Iterate exactly hits a sample point on the first step (init at a
   sample) -> Vardi-Zhang correction must engage AND not crash.

Run: /c/Anaconda/python.exe -X utf8 scripts/_smoke_geometric_median.py
"""
from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import numpy as np

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
PROBLEM_ID = 1108


def _extract_weiszfeld_source() -> str:
    conn = sqlite3.connect(str(DB_PATH))
    conn.text_factory = str
    try:
        row = conn.execute(
            "SELECT notes FROM problems WHERE id = ?", (PROBLEM_ID,)
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RuntimeError(f"problems.id={PROBLEM_ID} not found")
    notes = row[0] or ""
    blocks = re.findall(r"```python\n(.*?)```", notes, re.DOTALL)
    if not blocks:
        raise RuntimeError("no python code block in notes")
    src = blocks[0]
    if "def geometric_median" not in src:
        raise RuntimeError("geometric_median not in extracted block")
    return src


def main() -> int:
    src = _extract_weiszfeld_source()
    namespace: dict[str, object] = {"np": np}
    exec(src, namespace)
    geometric_median = namespace["geometric_median"]

    print("[1] Symmetric points around origin")
    pts = np.array(
        [[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]],
        dtype=float,
    )
    gm = geometric_median(pts)
    print(f"    geometric median = {gm} (expect ~origin)")
    assert np.linalg.norm(gm) < 1e-4, "symmetric case must be near origin"

    print("[2] Outlier robustness (centroid vs geometric median)")
    rng = np.random.default_rng(seed=42)
    inliers = rng.normal(scale=1.0, size=(99, 2))
    outlier = np.array([[1e6, 1e6]])
    pts = np.vstack([inliers, outlier])
    centroid = pts.mean(axis=0)
    gm = geometric_median(pts)
    print(f"    centroid          = {centroid} (pulled far)")
    print(f"    geometric median  = {gm} (near inlier mass)")
    assert np.linalg.norm(centroid) > 1e3, "centroid must be pulled by outlier"
    assert np.linalg.norm(gm) < 5.0, "geometric median must stay near inlier mass"

    print("[3] Vardi-Zhang degeneracy: 5 copies of one point + 1 stray")
    # When init=centroid lands extremely close to the dominant cluster, and
    # later iterates may hit it, the singular_mask branch must not crash.
    pts = np.array(
        [[0.0, 0.0]] * 5 + [[10.0, 0.0]],
        dtype=float,
    )
    gm = geometric_median(pts)
    print(f"    geometric median = {gm} (expect at or very near origin: "
          f"5 of 6 weight pulls it to (0,0))")
    # With the dominant point repeated 5 times, the geometric median is
    # exactly (0, 0) -- subgradient norm at origin equals 1 (unit vector
    # pointing at the stray) which is <= eta_j = 5, certifying optimality
    # via Vardi-Zhang Theorem 2.1.
    assert np.linalg.norm(gm) < 1e-6, (
        f"Vardi-Zhang must certify origin as optimum; got {gm}"
    )

    print("[4] 1D degenerate case = ordinary median")
    pts = np.array([[1.0], [2.0], [3.0], [4.0], [100.0]])  # outlier at 100
    gm = geometric_median(pts)
    print(f"    geometric median = {gm} (expect near the median = 3.0)")
    # 1D geometric median IS the median; with one outlier the median is 3.0.
    assert abs(float(gm[0]) - 3.0) < 1e-3, (
        f"1D geometric median must equal the ordinary median; got {gm}"
    )

    print("\n[OK] All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
