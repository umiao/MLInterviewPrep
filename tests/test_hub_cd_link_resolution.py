"""T-P0-675 (c): integration test that every cd://N link inside a hub doc
resolves to a real, non-empty company_documents row via the
GET /company-documents/{N} resolver endpoint.

Replaces the original "manual screenshot smoke test" gate per design review.
The reusable `assert_hub_cd_links_resolve` fixture below lets follow-up tasks
(T-P0-676 for Uber id=37/81 + Google id=51/53) add one-line cases.
"""
from __future__ import annotations

import re

import pytest

from src.backend.models.company import Company, CompanyDocument

CD_LINK_RE = re.compile(r"cd://(\d+)")


@pytest.fixture()
def meta_hub_with_subdocs(db_session):
    """Seed a Meta hub with 4 sub-docs and a hub body that links to all 4 via cd://."""
    company = Company(name="MetaHubFixture")
    db_session.add(company)
    db_session.flush()

    sub_titles = (
        "[Meta] Code-Pad LLM Prompt + 3-Step Playbook",
        "[Meta] AI-Native Domain Breadth -- 5 Talking Points",
        "[Meta] AI-Native Behavioral 5-Pack",
        "[Meta] AI-Native -- 临场 Prompt 写作 Best Practices",
    )
    sub_docs: list[CompanyDocument] = []
    for title in sub_titles:
        d = CompanyDocument(
            company_id=company.id,
            title=title,
            content=f"# {title}\n\nbody for {title}",
            source_type="manual",
            doc_kind="prep_note",
        )
        db_session.add(d)
        sub_docs.append(d)
    db_session.flush()

    t1, t2, t3, t4bp = (d.id for d in sub_docs)
    hub_body = (
        "<!-- META_AI_NATIVE_HUB_TEST -->\n"
        "# Meta AI-Native Hub\n\n"
        f"- [T1 playbook](cd://{t1})\n"
        f"- [T2 breadth](cd://{t2})\n"
        f"- [T3 behavioral](cd://{t3})\n"
        f"- [T4-bp prompt](cd://{t4bp})\n"
        f"- schedule: also [T1 again](cd://{t1}) and [T4-bp again](cd://{t4bp})\n"
    )
    hub = CompanyDocument(
        company_id=company.id,
        title="[Meta] AI-Native Hub (test)",
        content=hub_body,
        source_type="manual",
        doc_kind="prep_note",
    )
    db_session.add(hub)
    db_session.commit()
    db_session.refresh(hub)
    for d in sub_docs:
        db_session.refresh(d)
    return hub, sub_docs


def assert_hub_cd_links_resolve(test_client, hub: CompanyDocument) -> list[int]:
    """Reusable assertion: every cd://N in `hub.content` resolves to 200 with
    a non-empty content payload via GET /api/company-documents/{N}.

    Returns the list of unique cd:// targets that were checked, so callers
    can additionally assert on counts.
    """
    targets = sorted({int(m.group(1)) for m in CD_LINK_RE.finditer(hub.content)})
    assert targets, "hub body contains no cd:// links -- regression"
    for n in targets:
        resp = test_client.get(f"/api/company-documents/{n}")
        assert resp.status_code == 200, (
            f"cd://{n} from doc id={hub.id} returned {resp.status_code}: "
            f"{resp.text[:200]}"
        )
        body = resp.json()
        assert body["id"] == n
        assert body["content"], f"cd://{n} resolved but content is empty"
    return targets


def test_meta_hub_all_cd_links_resolve_to_real_docs(
    test_client, meta_hub_with_subdocs
):
    """Every cd://N in the Meta hub body resolves to its sub-doc."""
    hub, sub_docs = meta_hub_with_subdocs
    expected_ids = sorted(d.id for d in sub_docs)
    resolved_ids = assert_hub_cd_links_resolve(test_client, hub)
    assert resolved_ids == expected_ids, (
        f"hub linked {resolved_ids} but seeded sub-docs are {expected_ids}"
    )


def test_meta_hub_resolver_returns_correct_titles(
    test_client, meta_hub_with_subdocs
):
    """Each cd:// target returns the matching sub-doc title (not a sibling)."""
    hub, sub_docs = meta_hub_with_subdocs
    title_by_id = {d.id: d.title for d in sub_docs}
    for n in {int(m.group(1)) for m in CD_LINK_RE.finditer(hub.content)}:
        resp = test_client.get(f"/api/company-documents/{n}")
        assert resp.status_code == 200
        assert resp.json()["title"] == title_by_id[n]


def test_dangling_cd_link_returns_404(test_client, meta_hub_with_subdocs):
    """A cd:// pointing at a missing id returns 404 (the contract that lets
    CompanyDocDrawer render its explicit not-found UI from T-P0-673)."""
    resp = test_client.get("/api/company-documents/9999999")
    assert resp.status_code == 404


def test_hub_body_uses_cd_scheme_not_db_for_subdocs(meta_hub_with_subdocs):
    """Regression guard: hub body must NOT use db:// for company-doc targets.

    db://N would route through ProblemDrawer and -- because problem.id and
    company_document.id share the same auto-increment space -- might silently
    open an unrelated LeetCode problem instead of the sub-doc (T-P0-675
    cross-table-corruption fix).
    """
    hub, _ = meta_hub_with_subdocs
    assert "db://" not in hub.content, (
        "hub body should use cd:// for sub-doc links, never db://"
    )
    assert "cd://" in hub.content
