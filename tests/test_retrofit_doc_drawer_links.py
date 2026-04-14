"""Unit tests for scripts/retrofit_doc_drawer_links.py (T-P0-196).

Verifies:
- Plain 'LC 123' / 'LC123' rewrite.
- 'LeetCode 456' / 'LeetCode #456' rewrite preserves literal casing.
- Custom-title rewrite via CustomMapping.
- Idempotence: a second pass produces zero additional replacements.
- Already-linked markdown is left untouched (no double-wrapping).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "retrofit_doc_drawer_links",
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "retrofit_doc_drawer_links.py",
)
assert _SPEC and _SPEC.loader
retrofit = importlib.util.module_from_spec(_SPEC)
sys.modules["retrofit_doc_drawer_links"] = retrofit
_SPEC.loader.exec_module(retrofit)


class TestRewriteLC:
    def test_simple(self) -> None:
        new, n = retrofit.rewrite_lc("See LC 207 for topo sort.")
        assert new == "See [LC 207](lc://207) for topo sort."
        assert n == 1

    def test_no_space(self) -> None:
        new, n = retrofit.rewrite_lc("Check LC207 maybe.")
        assert new == "Check [LC 207](lc://207) maybe."
        assert n == 1

    def test_multiple(self) -> None:
        new, n = retrofit.rewrite_lc("LC 1 and LC 2 and LC 42.")
        assert n == 3
        assert "[LC 1](lc://1)" in new
        assert "[LC 42](lc://42)" in new

    def test_idempotent_on_existing_link(self) -> None:
        src = "Already linked: [LC 207](lc://207) done."
        new, n = retrofit.rewrite_lc(src)
        assert new == src
        assert n == 0

    def test_second_pass_is_noop(self) -> None:
        src = "LC 380 and LC 207 problems."
        once, n1 = retrofit.rewrite_lc(src)
        twice, n2 = retrofit.rewrite_lc(once)
        assert once == twice
        assert n1 == 2
        assert n2 == 0

    def test_no_false_match_inside_word(self) -> None:
        # 'CALCULATION' contains 'LC' but not as a token -- must not match.
        src = "CALCULATION 5 is fine."
        new, n = retrofit.rewrite_lc(src)
        assert new == src
        assert n == 0


class TestRewriteLeetCode:
    def test_preserves_casing(self) -> None:
        new, n = retrofit.rewrite_leetcode("See LeetCode 456 tomorrow.")
        assert new == "See [LeetCode 456](lc://456) tomorrow."
        assert n == 1

    def test_lowercase_and_hash(self) -> None:
        new, n = retrofit.rewrite_leetcode("leetcode #789 here.")
        assert "[leetcode #789](lc://789)" in new
        assert n == 1

    def test_idempotent(self) -> None:
        src = "[LeetCode 456](lc://456) done."
        new, n = retrofit.rewrite_leetcode(src)
        assert new == src
        assert n == 0


class TestRewriteCustom:
    def test_simple(self) -> None:
        mappings = [
            retrofit.CustomMapping(
                pattern=r"\bRound by precision p\b",
                db_id=1074,
                display="Round by precision p",
            )
        ]
        new, n = retrofit.rewrite_custom(
            "Do Round by precision p next.", mappings
        )
        assert new == "Do [Round by precision p](db://1074) next."
        assert n == 1

    def test_idempotent(self) -> None:
        mappings = [
            retrofit.CustomMapping(
                pattern=r"\bRound by precision p\b", db_id=1074
            )
        ]
        src = "Already [Round by precision p](db://1074) linked."
        new, n = retrofit.rewrite_custom(src, mappings)
        assert new == src
        assert n == 0

    def test_does_not_touch_different_db_id(self) -> None:
        # If the same title was previously linked to a different db_id, we still
        # skip (conservative: never overwrite a human-chosen link).
        mappings = [
            retrofit.CustomMapping(
                pattern=r"\bFoo\b", db_id=99
            )
        ]
        src = "[Foo](db://99) stays."
        new, n = retrofit.rewrite_custom(src, mappings)
        assert new == src
        assert n == 0


class TestRetrofitDoc:
    def test_full_pass_idempotent(self) -> None:
        doc = (
            "## Intro\n"
            "- LC 207 (topo sort)\n"
            "- LeetCode 994 (BFS)\n"
            "- Custom: Round by precision p here.\n"
        )
        mappings = [
            retrofit.CustomMapping(
                pattern=r"\bRound by precision p\b",
                db_id=1074,
                display="Round by precision p",
            )
        ]
        once, s1 = retrofit.retrofit_doc(doc, mappings)
        twice, s2 = retrofit.retrofit_doc(once, mappings)
        assert once == twice
        assert s1 == {"lc": 1, "leetcode": 1, "custom": 1}
        assert s2 == {"lc": 0, "leetcode": 0, "custom": 0}
        assert "[LC 207](lc://207)" in once
        assert "[LeetCode 994](lc://994)" in once
        assert "[Round by precision p](db://1074)" in once


class TestFuzzyFindProblemId:
    def test_match(self, tmp_path: Path) -> None:
        import sqlite3

        db = tmp_path / "t.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE problems (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute(
            "INSERT INTO problems (id, title) VALUES (?, ?)",
            (1074, "Round by Precision p (string s, precision p)"),
        )
        conn.execute(
            "INSERT INTO problems (id, title) VALUES (?, ?)",
            (42, "Two Sum"),
        )
        conn.commit()
        got = retrofit.fuzzy_find_problem_id(conn, "round by precision p")
        assert got == 1074
        conn.close()

    def test_below_threshold_returns_none(self, tmp_path: Path) -> None:
        import sqlite3

        db = tmp_path / "t.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE problems (id INTEGER PRIMARY KEY, title TEXT)")
        conn.execute(
            "INSERT INTO problems (id, title) VALUES (?, ?)", (1, "Two Sum")
        )
        conn.commit()
        assert (
            retrofit.fuzzy_find_problem_id(
                conn, "something completely unrelated", threshold=0.8
            )
            is None
        )
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
