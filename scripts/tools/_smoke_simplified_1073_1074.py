# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Smoke test the simplified my_round / round_by_precision before seeding."""
from __future__ import annotations


def my_round(s: str) -> int:
    """Round decimal string to nearest int, half-away-from-zero."""
    s = s.strip()
    neg = s.startswith("-")
    if s[:1] in "+-":
        s = s[1:]
    int_s, _, frac_s = s.partition(".")
    digits = list(int_s or "0")
    if frac_s[:1] >= "5":
        i, carry = len(digits) - 1, 1
        while i >= 0 and carry:
            d = int(digits[i]) + carry
            digits[i], carry = str(d % 10), d // 10
            i -= 1
        if carry:
            digits.insert(0, "1")
    mag = int("".join(digits))
    return -mag if (neg and mag) else mag


def _precision_exponent(p: str) -> int:
    """p is a power of 10 as string. Returns k where p = 10**k."""
    pi, _, pf = p.partition(".")
    if pf:
        return -len(pf)
    return len(pi) - len(pi.rstrip("0") or "0")


def round_by_precision(s: str, p: str) -> str:
    """Round decimal string s to nearest multiple of p (p = 10**k)."""
    s = s.strip()
    neg = s.startswith("-")
    if s[:1] in "+-":
        s = s[1:]
    int_s, _, frac_s = s.partition(".")
    k = _precision_exponent(p)

    digits = list((int_s or "0") + frac_s)
    dot = len(int_s or "0")
    cut = dot - k

    if cut < 0:
        return "0"

    kept = digits[:cut]
    if cut < len(digits) and digits[cut] >= "5":
        if not kept:
            kept = ["1"]
        else:
            i, carry = len(kept) - 1, 1
            while i >= 0 and carry:
                d = int(kept[i]) + carry
                kept[i], carry = str(d % 10), d // 10
                i -= 1
            if carry:
                kept.insert(0, "1")
                cut += 1

    if k >= 0:
        out = "".join(kept) + "0" * k
    else:
        head = "".join(kept[: cut + k]) or "0"
        tail = "".join(kept[cut + k :]).ljust(-k, "0")
        out = head + "." + tail

    if "." in out:
        left, right = out.split(".")
        left = left.lstrip("0") or "0"
        out = f"{left}.{right}"
    else:
        out = out.lstrip("0") or "0"

    return "-" + out if (neg and out != "0" and set(out) != {"0", "."}) else out


if __name__ == "__main__":
    # 1073 tests
    cases_1073 = [
        ("2.4", 2), ("2.5", 3), ("-2.5", -3), ("9.5", 10), ("99.5", 100),
        ("-.2", 0), ("-.5", -1), ("-0.5", -1), ("2.", 2), (" +3 ", 3),
        ("0.0", 0), ("0", 0), ("-0", 0),
    ]
    for s, expected in cases_1073:
        got = my_round(s)
        assert got == expected, f"my_round({s!r}) = {got}, expected {expected}"
    print(f"[PASS] 1073: {len(cases_1073)} cases")

    # 1074 tests
    cases_1074 = [
        ("12567", "100", "12600"),
        ("1234.678", "0.1", "1234.7"),
        ("1234.678", "0.01", "1234.68"),
        ("99.5", "1", "100"),
        ("-0.05", "0.1", "-0.1"),
        ("49", "100", "0"),
        ("50", "100", "100"),
        ("9.99", "0.1", "10.0"),
        ("0.005", "0.01", "0.01"),
        ("0", "1", "0"),
    ]
    for s, p, expected in cases_1074:
        got = round_by_precision(s, p)
        assert got == expected, f"round_by_precision({s!r}, {p!r}) = {got!r}, expected {expected!r}"
    print(f"[PASS] 1074: {len(cases_1074)} cases")
