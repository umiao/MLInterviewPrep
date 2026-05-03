"""Smoke test the shift-based reuse refactor for 1074 (user proposal 2026-04-15)."""
from __future__ import annotations


def my_round(s: str) -> int:
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
    pi, _, pf = p.partition(".")
    if pf:
        return -len(pf)
    return len(pi) - len(pi.rstrip("0") or "0")


def _shift_decimal(int_s: str, frac_s: str, shift: int) -> tuple[str, str]:
    """Move decimal point right by `shift` (negative = move left)."""
    if shift >= 0:
        borrowed = frac_s[:shift].ljust(shift, "0")
        return int_s + borrowed, frac_s[shift:]
    n = -shift
    if n >= len(int_s):
        return "0", "0" * (n - len(int_s)) + int_s + frac_s
    return int_s[:-n], int_s[-n:] + frac_s


def round_by_precision(s: str, p: str) -> str:
    s = s.strip()
    neg = s.startswith("-")
    if s[:1] in "+-":
        s = s[1:]
    int_s, _, frac_s = s.partition(".")
    int_s = int_s or "0"
    k = _precision_exponent(p)

    shifted_int, shifted_frac = _shift_decimal(int_s, frac_s, -k)

    digits = list(shifted_int)
    if shifted_frac[:1] >= "5":
        i, carry = len(digits) - 1, 1
        while i >= 0 and carry:
            d = int(digits[i]) + carry
            digits[i], carry = str(d % 10), d // 10
            i -= 1
        if carry:
            digits.insert(0, "1")
    rounded = "".join(digits)

    if k >= 0:
        out = rounded + "0" * k
    else:
        n = -k
        if n >= len(rounded):
            out = "0." + "0" * (n - len(rounded)) + rounded
        else:
            out = rounded[:-n] + "." + rounded[-n:]

    left, _, right = out.partition(".")
    left = left.lstrip("0") or "0"
    out = f"{left}.{right}" if right else left
    return "-" + out if neg and out != "0" else out


if __name__ == "__main__":
    cases_1073 = [
        ("2.4", 2), ("2.5", 3), ("-2.5", -3), ("9.5", 10), ("99.5", 100),
        ("-.2", 0), ("-.5", -1), ("-0.5", -1), ("2.", 2), (" +3 ", 3),
        ("0.0", 0), ("0", 0), ("-0", 0),
    ]
    for s, expected in cases_1073:
        got = my_round(s)
        assert got == expected, f"my_round({s!r}) = {got}, expected {expected}"
    print(f"[PASS] 1073: {len(cases_1073)} cases")

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
        # extras: p='1' must match my_round exactly
        ("2.5", "1", "3"),
        ("-2.5", "1", "-3"),
        ("99.5", "1", "100"),
        # deep shift both directions
        ("7", "1000", "0"),
        ("500", "1000", "1000"),
        ("0.00049", "0.0001", "0.0005"),
    ]
    for s, p, expected in cases_1074:
        got = round_by_precision(s, p)
        assert got == expected, f"round_by_precision({s!r}, {p!r}) = {got!r}, expected {expected!r}"
    print(f"[PASS] 1074: {len(cases_1074)} cases")
