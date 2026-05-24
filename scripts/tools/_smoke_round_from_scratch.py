# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Standalone verifier for the round()-from-scratch canonical solution.

Runs the reference implementation (copy of the snippet in the notes) against
a matrix of cases including carry propagation, leading/trailing dot forms,
explicit signs, and invalid inputs that must raise.

Usage: python scripts/_smoke_round_from_scratch.py
"""
from __future__ import annotations


def my_round(s: str) -> int:
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
        raise ValueError(f"unexpected char at {i}: {s!r}")
    if not int_part and not frac_part:
        raise ValueError(f"no digits in {s!r}")
    if not int_part:
        int_part = "0"

    round_up = len(frac_part) > 0 and frac_part[0] >= "5"
    digits = list(int_part)
    if round_up:
        j = len(digits) - 1
        carry = 1
        while j >= 0 and carry:
            d = int(digits[j]) + carry
            if d == 10:
                digits[j] = "0"
                carry = 1
            else:
                digits[j] = str(d)
                carry = 0
            j -= 1
        if carry:
            digits.insert(0, "1")

    mag = int("".join(digits))
    return -mag if (neg and mag != 0) else mag


VALID_CASES = [
    ("2.4", 2),
    ("2.5", 3),
    ("2.6", 3),
    ("-2.5", -3),
    ("-2.4", -2),
    ("9.5", 10),
    ("99.5", 100),
    ("999.9", 1000),
    ("-.2", 0),
    ("-.5", -1),
    ("-0.5", -1),
    ("0.5", 1),
    ("0.4999999999999", 0),
    ("2.", 2),
    (" +3 ", 3),
    ("  -7.5  ", -8),
    ("0.0", 0),
    ("-0.0", 0),
    ("0", 0),
    # Long input that would overflow float()
    ("1" + "0" * 400 + ".5", int("1" + "0" * 400) + 1),
]

INVALID_CASES = ["", ".", "1.2.3", "1e2", "abc", "- 2", "+-1", "--1", "1.2a"]


def main() -> None:
    for s, expected in VALID_CASES:
        got = my_round(s)
        assert got == expected, f"{s!r}: expected {expected}, got {got}"

    for s in INVALID_CASES:
        try:
            my_round(s)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {s!r}")

    print(f"OK {len(VALID_CASES)} valid + {len(INVALID_CASES)} invalid cases passed")


if __name__ == "__main__":
    main()
