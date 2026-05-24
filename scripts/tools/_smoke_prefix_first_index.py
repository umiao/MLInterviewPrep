# SAFE_DELETE_AFTER: 2026-08-21  (T-P2-353 scripts/ lifecycle migration; one-shot already run)
"""Standalone smoke verifier for the prefix-first-index solutions.

Task: T-P1-399. Validates both the Trie and bisect solutions against the
self-test cases embedded in the notes before seeding the DB row.
"""
from __future__ import annotations

from bisect import bisect_left


class TrieNode:
    __slots__ = ("children", "min_index")

    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.min_index: int = -1


class PrefixIndex:
    def __init__(self, words: list[str]) -> None:
        self.root = TrieNode()
        for i, w in enumerate(words):
            node = self.root
            # Also update root.min_index so empty-prefix query returns 0.
            if self.root.min_index == -1 or i < self.root.min_index:
                self.root.min_index = i
            for ch in w:
                nxt = node.children.get(ch)
                if nxt is None:
                    nxt = TrieNode()
                    node.children[ch] = nxt
                node = nxt
                if node.min_index == -1 or i < node.min_index:
                    node.min_index = i

    def first_index(self, prefix: str) -> int:
        node = self.root
        for ch in prefix:
            node = node.children.get(ch)
            if node is None:
                return -1
        return node.min_index


def solve(words: list[str], prefixes: list[str]) -> list[int]:
    idx = PrefixIndex(words)
    return [idx.first_index(p) for p in prefixes]


def solve_sorted(words: list[str], prefixes: list[str]) -> list[int]:
    out = []
    for p in prefixes:
        i = bisect_left(words, p)
        out.append(i if i < len(words) and words[i].startswith(p) else -1)
    return out


def main() -> None:
    words = ["a", "apple", "appz", "b"]
    assert solve(words, ["ap"]) == [1], solve(words, ["ap"])
    assert solve(words, ["b"]) == [3]
    assert solve(words, ["c"]) == [-1]
    assert solve(words, [""]) == [0]
    assert solve(words, ["app"]) == [1]
    assert solve(words, ["appz"]) == [2]

    words2 = ["banana", "apple", "appz", "ant"]
    assert solve(words2, ["ap"]) == [1]
    assert solve(words2, ["an"]) == [3]

    # bisect vs trie parity on sorted input
    sw = sorted(words)
    for p in ["", "a", "ap", "app", "appz", "b", "c", "z"]:
        t = solve(sw, [p])[0]
        b = solve_sorted(sw, [p])[0]
        assert t == b, f"mismatch on {p!r}: trie={t} bisect={b}"

    # Trap: bisect_left lands on a non-matching word.
    assert solve_sorted(["a", "az", "b"], ["ap"]) == [-1]

    print("OK all smoke tests passed")


if __name__ == "__main__":
    main()
