# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Standalone verifier for the round-by-precision solution (T-P1-403).

Runs the canonical reference implementation against an edge-case suite and
cross-checks against `Decimal.quantize(..., ROUND_HALF_UP)` for sanity.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def round_by_precision(s: str, p: str) -> str:
    # ---- determine k from p ----
    if "." in p:
        _, pfrac = p.split(".", 1)
        k = -len(pfrac)
    else:
        k = len(p) - 1

    # ---- parse s ----
    s = s.strip()
    if not s:
        raise ValueError("empty string")
    i, n = 0, len(s)
    neg = False
    if s[i] in "+-":
        neg = s[i] == "-"
        i += 1
    int_part = ""
    while i < n and s[i].isdigit():
        int_part += s[i]
        i += 1
    frac_part = ""
    if i < n and s[i] == ".":
        i += 1
        while i < n and s[i].isdigit():
            frac_part += s[i]
            i += 1
    if i != n:
        raise ValueError(f"bad char at {i}: {s!r}")
    if not int_part and not frac_part:
        raise ValueError(f"no digits in {s!r}")
    if not int_part:
        int_part = "0"

    # ---- split at position k ----
    if k >= 0:
        if len(int_part) <= k:
            int_part = "0" * (k + 1 - len(int_part)) + int_part
        keep_len = len(int_part) - k
        kept_int = list(int_part[:keep_len])
        if keep_len < len(int_part):
            round_digit = int_part[keep_len]
        else:
            round_digit = frac_part[0] if frac_part else "0"
        kept_frac: list[str] = []
    else:
        want_frac = -k
        if len(frac_part) < want_frac + 1:
            frac_part = frac_part + "0" * (want_frac + 1 - len(frac_part))
        kept_int = list(int_part)
        kept_frac = list(frac_part[:want_frac])
        round_digit = frac_part[want_frac]

    # ---- half-up carry ----
    if round_digit >= "5":
        carry = 1
        j = len(kept_frac) - 1
        while j >= 0 and carry:
            d = int(kept_frac[j]) + carry
            if d == 10:
                kept_frac[j] = "0"
                carry = 1
            else:
                kept_frac[j] = str(d)
                carry = 0
            j -= 1
        j = len(kept_int) - 1
        while j >= 0 and carry:
            d = int(kept_int[j]) + carry
            if d == 10:
                kept_int[j] = "0"
                carry = 1
            else:
                kept_int[j] = str(d)
                carry = 0
            j -= 1
        if carry:
            kept_int.insert(0, "1")

    int_str = "".join(kept_int).lstrip("0") or "0"
    magnitude = int_str + "0" * k if k >= 0 else int_str + "." + "".join(kept_frac)

    if all(c in "0." for c in magnitude):
        if "." in magnitude:
            return magnitude
        return "0"
    return ("-" + magnitude) if neg else magnitude


VALID_CASES: list[tuple[str, str, str]] = [
    ("12567",    "100",  "12600"),
    ("12549",    "100",  "12500"),
    ("12550",    "100",  "12600"),
    ("49",       "100",  "0"),
    ("50",       "100",  "100"),
    ("1234.678", "0.1",  "1234.7"),
    ("1234.678", "0.01", "1234.68"),
    ("9.99",     "0.1",  "10.0"),
    ("99.95",    "0.1",  "100.0"),
    ("-0.05",    "0.1",  "-0.1"),
    ("0.04",     "0.1",  "0.0"),
    ("2.5",      "1",    "3"),
    ("-2.5",     "1",    "-3"),
    ("  +3 ",    "1",    "3"),
    ("0",        "100",  "0"),
    ("500",      "1000", "1000"),
    ("499",      "1000", "0"),
    ("1",        "0.001","1.000"),
]

INVALID_CASES: list[str] = ["", ".", "1.2.3", "abc", "1e2", "+-1"]


def _decimal_half_up(s: str, p: str) -> str:
    """Reference using Decimal.quantize. Preserves trailing zeros.
    Note: `Decimal('100')` has exponent 0, so quantize to it == quantize to
    ones. To quantize to hundreds we must use `Decimal('1E2')`. Build the
    exponent explicitly from k."""
    k = -len(p.split(".", 1)[1]) if "." in p else len(p) - 1
    target = Decimal(1).scaleb(k)  # 10**k with exponent=k
    d = Decimal(s.strip()).quantize(target, rounding=ROUND_HALF_UP)
    out = format(d, "f")
    # Our contract strips +0 -> 0 and preserves requested decimal places.
    if "." in p:
        want = len(p.split(".", 1)[1])
        if "." not in out:
            out = out + "." + "0" * want
        else:
            head, tail = out.split(".", 1)
            tail = (tail + "0" * want)[:want]
            out = f"{head}.{tail}"
    else:
        if "." in out:
            out = out.split(".", 1)[0]
    # Normalize -0 / -0.0...
    if out.lstrip("-").replace(".", "").replace("0", "") == "":
        out = out.lstrip("-")
    return out


def main() -> int:
    failures: list[str] = []
    for s, p, expected in VALID_CASES:
        got = round_by_precision(s, p)
        if got != expected:
            failures.append(f"case({s!r},{p!r}) got={got!r} want={expected!r}")
            continue
        # Cross-check vs Decimal
        ref = _decimal_half_up(s, p)
        if ref != expected:
            failures.append(f"Decimal-ref drift for ({s!r},{p!r}): ref={ref!r}, expected={expected!r}")

    for bad in INVALID_CASES:
        try:
            round_by_precision(bad, "1")
        except ValueError:
            continue
        failures.append(f"invalid input {bad!r} did not raise ValueError")

    if failures:
        print("[FAIL]")
        for f in failures:
            print("  -", f)
        return 1
    print(f"[OK] {len(VALID_CASES)} valid + {len(INVALID_CASES)} invalid cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
