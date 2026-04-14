"""Tests for T-P0-214: tag models + migration 19/20/21 + doc_kind."""
import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from src.backend.database import init_db
from src.backend.models import (
    BehavioralExample,
    BehavioralExampleCompanyTag,
    Company,
    CompanyDocument,
    FrameworkNode,
    NodeCompanyTag,
    Problem,
    ProblemCompanyTag,
)


@pytest.fixture
def db_session(tmp_path):
    """Create a fresh SQLite DB with all migrations applied."""
    db_path = tmp_path / "test_tags.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    init_db(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    engine.dispose()


def test_schema_version_at_least_21(db_session: Session):
    """AC2: init_db advances schema_versions to >= 21."""
    rows = db_session.execute(
        text("SELECT version FROM schema_versions")
    ).fetchall()
    versions = {r[0] for r in rows}
    assert 19 in versions
    assert 20 in versions
    assert 21 in versions


def test_company_documents_doc_kind_default(db_session: Session):
    """Migration 19: doc_kind column exists with default 'prep_note'."""
    company = Company(name="TestCo")
    db_session.add(company)
    db_session.flush()
    doc = CompanyDocument(company_id=company.id, title="x", content="y")
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    assert doc.doc_kind == "prep_note"


def test_problem_company_tag_crud_and_unique(db_session: Session):
    """AC3+AC4: CRUD works; UNIQUE(problem_id, company_id) enforced."""
    company = Company(name="Google")
    problem = Problem(title="Two Sum")
    db_session.add_all([company, problem])
    db_session.flush()

    tag = ProblemCompanyTag(
        problem_id=problem.id,
        company_id=company.id,
        relevance="core",
        source="manual",
        notes="n",
    )
    db_session.add(tag)
    db_session.commit()

    fetched = (
        db_session.query(ProblemCompanyTag).filter_by(problem_id=problem.id).one()
    )
    fetched.notes = "updated"
    db_session.commit()

    dup = ProblemCompanyTag(
        problem_id=problem.id, company_id=company.id, relevance="likely"
    )
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_node_company_tag_crud(db_session: Session):
    """AC3: NodeCompanyTag CRUD works."""
    company = Company(name="Meta")
    node = FrameworkNode(path="root.x", depth=0, title="X")
    db_session.add_all([company, node])
    db_session.flush()
    tag = NodeCompanyTag(
        node_id=node.id, company_id=company.id, relevance="likely"
    )
    db_session.add(tag)
    db_session.commit()
    assert db_session.query(NodeCompanyTag).count() == 1


def test_behavioral_example_company_tag_with_attribute(db_session: Session):
    """AC3: BehavioralExampleCompanyTag stores company_attribute."""
    company = Company(name="Google")
    ex = BehavioralExample(example_id="EX-1", title="t")
    db_session.add_all([company, ex])
    db_session.flush()
    tag = BehavioralExampleCompanyTag(
        example_id=ex.id,
        company_id=company.id,
        relevance="core",
        company_attribute="Googleyness",
    )
    db_session.add(tag)
    db_session.commit()
    fetched = db_session.query(BehavioralExampleCompanyTag).one()
    assert fetched.company_attribute == "Googleyness"


def test_cascade_delete_on_company(db_session: Session):
    """AC5: deleting company cascades through all 3 tag tables."""
    company = Company(name="Uber")
    problem = Problem(title="P")
    node = FrameworkNode(path="root.y", depth=0, title="Y")
    ex = BehavioralExample(example_id="EX-2", title="t")
    db_session.add_all([company, problem, node, ex])
    db_session.flush()
    db_session.add_all([
        ProblemCompanyTag(problem_id=problem.id, company_id=company.id),
        NodeCompanyTag(node_id=node.id, company_id=company.id),
        BehavioralExampleCompanyTag(example_id=ex.id, company_id=company.id),
    ])
    db_session.commit()

    # SQLite requires FK pragma to enforce cascade
    db_session.execute(text("PRAGMA foreign_keys=ON"))
    db_session.delete(company)
    db_session.commit()

    assert db_session.query(ProblemCompanyTag).count() == 0
    assert db_session.query(NodeCompanyTag).count() == 0
    assert db_session.query(BehavioralExampleCompanyTag).count() == 0


def test_relevance_check_constraint(db_session: Session):
    """AC4: relevance CHECK constraint rejects invalid values."""
    company = Company(name="Z")
    problem = Problem(title="P2")
    db_session.add_all([company, problem])
    db_session.flush()
    db_session.execute(text("PRAGMA foreign_keys=ON"))
    bad = ProblemCompanyTag(
        problem_id=problem.id, company_id=company.id, relevance="bogus"
    )
    db_session.add(bad)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
