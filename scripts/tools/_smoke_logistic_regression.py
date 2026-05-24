# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
# ruff: noqa: N806
"""Smoke test for the LogisticRegression + SoftmaxRegression code embedded
in scripts/seed_logistic_regression_20260502.py NOTES.

Reproduces the exact code from the markdown notes (no copy-paste -- we
extract the code block from the seed file) and runs:
- binary LR on a separable Gaussian-blob dataset, expect train acc >= 0.95.
- softmax LR on a 3-class blob dataset, expect train acc >= 0.85.
- stable BCE on extreme logits (z = +-1000), expect finite loss + sane grad.

ruff N806 (uppercase var names) is intentionally suppressed -- this smoke
test mirrors ML notation (X, Y, P, Z) directly from the seed's markdown.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

SEED = Path(__file__).resolve().parent / "seed_logistic_regression_20260502.py"


def _extract_code_block(seed_path: Path) -> str:
    text = seed_path.read_text(encoding="utf-8")
    # The notes embed exactly one ```python ... ``` block with both classes.
    matches = re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL)
    if not matches:
        print("[FAIL] no ```python``` block found in seed")
        sys.exit(1)
    # Concatenate all python blocks (the notes have one combined block, but
    # be robust if it ever splits).
    return "\n\n".join(matches)


def main() -> int:
    code = _extract_code_block(SEED)
    namespace: dict = {"np": np}
    exec(code, namespace)
    LogisticRegression = namespace["LogisticRegression"]
    SoftmaxRegression = namespace["SoftmaxRegression"]

    rng = np.random.RandomState(0)

    # ---- Binary LR on separable Gaussian blobs ----
    n = 200
    X_pos = rng.randn(n, 2) + np.array([2.0, 2.0])
    X_neg = rng.randn(n, 2) + np.array([-2.0, -2.0])
    X = np.vstack([X_pos, X_neg])
    y = np.concatenate([np.ones(n, dtype=int), np.zeros(n, dtype=int)])

    model = LogisticRegression(learning_rate=0.1, max_iterations=500)
    model.fit(X, y.astype(float))
    train_pred = model.predict(X)
    acc = float(np.mean(train_pred == y))
    final_loss = model.training_loss_history[-1]
    print(f"[binary] train_acc={acc:.4f} final_bce={final_loss:.4f} "
          f"iters={len(model.training_loss_history)}")
    assert acc >= 0.95, f"binary train acc too low: {acc}"
    assert np.isfinite(final_loss), f"binary final loss not finite: {final_loss}"

    # Probability calibration sanity: predict_proba in [0, 1].
    probs = model.predict_proba(X)
    assert (probs >= 0).all() and (probs <= 1).all(), "probs out of range"

    # ---- Stable BCE on extreme logits ----
    z_extreme = np.array([1000.0, -1000.0, 0.0, 50.0, -50.0])
    y_extreme = np.array([1.0, 0.0, 1.0, 1.0, 0.0])
    stable_loss = LogisticRegression._stable_bce_loss(z_extreme, y_extreme)
    print(f"[stable_bce] extreme logits loss={stable_loss:.6f}")
    assert np.isfinite(stable_loss), f"stable BCE blew up: {stable_loss}"

    # ---- Stable sigmoid on extreme logits ----
    sig_out = LogisticRegression._sigmoid(z_extreme)
    print(f"[sigmoid] z=[1000, -1000, 0, 50, -50] -> {sig_out}")
    assert np.all(np.isfinite(sig_out)), "sigmoid produced non-finite values"
    assert np.all((sig_out >= 0) & (sig_out <= 1)), "sigmoid out of [0,1]"
    assert sig_out[0] > 0.99 and sig_out[1] < 0.01, "sigmoid extreme wrong"

    # ---- Softmax LR on 3-class blobs ----
    n3 = 150
    X1 = rng.randn(n3, 2) + np.array([3.0, 3.0])
    X2 = rng.randn(n3, 2) + np.array([-3.0, 3.0])
    X3 = rng.randn(n3, 2) + np.array([0.0, -3.0])
    X_mc = np.vstack([X1, X2, X3])
    y_mc = np.concatenate([
        np.zeros(n3, dtype=int),
        np.ones(n3, dtype=int),
        np.full(n3, 2, dtype=int),
    ])
    sm = SoftmaxRegression(n_classes=3, learning_rate=0.1, max_iterations=500)
    sm.fit(X_mc, y_mc)
    pred_mc = sm.predict(X_mc)
    acc_mc = float(np.mean(pred_mc == y_mc))
    print(f"[softmax] train_acc={acc_mc:.4f}")
    assert acc_mc >= 0.85, f"softmax train acc too low: {acc_mc}"

    # ---- Stable softmax on extreme logits (no overflow) ----
    Z = np.array([[1000.0, 999.0, -1000.0], [0.0, 0.0, 0.0]])
    P = SoftmaxRegression._softmax(Z)
    print(f"[softmax_stable] P={P}")
    assert np.all(np.isfinite(P)), "stable softmax produced non-finite values"
    assert np.allclose(P.sum(axis=1), 1.0), "softmax rows do not sum to 1"

    print("[OK] all smoke checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
