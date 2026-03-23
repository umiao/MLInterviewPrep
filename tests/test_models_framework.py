"""Tests for FrameworkNode, StudyLog, Company, CompanyTopicWeight models."""
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.company import Company, CompanyTopicWeight
from src.backend.models.framework import FrameworkNode, StudyLog

# --- FrameworkNode tests ---


def test_framework_parent_child(db_session):
    """Root + child insert, verify parent-child relationship."""
    root = FrameworkNode(path="pillar1", depth=0, title="Coding")
    db_session.add(root)
    db_session.flush()

    child = FrameworkNode(
        parent_id=root.id, path="pillar1.dp", depth=1, title="DP"
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(root)

    assert len(root.children) == 1
    assert root.children[0].title == "DP"
    assert child.parent.title == "Coding"


def test_framework_unique_path(db_session):
    """Duplicate path raises IntegrityError."""
    n1 = FrameworkNode(path="pillar1", depth=0, title="A")
    n2 = FrameworkNode(path="pillar1", depth=0, title="B")
    db_session.add(n1)
    db_session.commit()
    db_session.add(n2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_defaults(db_session):
    """FrameworkNode defaults: status, progress, confidence, importance."""
    node = FrameworkNode(path="p1", depth=0, title="Test")
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    assert node.status == "not_started"
    assert node.progress_pct == 0.0
    assert node.confidence_level == 0
    assert node.importance == 1.0
    assert node.priority == "P1"
    assert node.created_at is not None
    assert node.parent_id is None
    assert node.description is None
    assert node.estimated_hours is None
    assert node.started_at is None
    assert node.completed_at is None
    assert node.last_studied_at is None


def test_framework_all_valid_statuses(db_session):
    """All valid status values are accepted."""
    for i, status in enumerate(["not_started", "in_progress", "review", "mastered"]):
        node = FrameworkNode(
            path=f"status_{i}", depth=0, title=f"Status {status}", status=status
        )
        db_session.add(node)
    db_session.commit()
    assert db_session.query(FrameworkNode).count() == 4


def test_framework_invalid_status(db_session):
    """Invalid status raises IntegrityError."""
    node = FrameworkNode(path="bad", depth=0, title="Bad", status="invalid")
    db_session.add(node)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_progress_pct_range(db_session):
    """progress_pct must be between 0 and 100."""
    node = FrameworkNode(path="p1", depth=0, title="T", progress_pct=101)
    db_session.add(node)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_progress_pct_negative(db_session):
    """progress_pct cannot be negative."""
    node = FrameworkNode(path="p1", depth=0, title="T", progress_pct=-1)
    db_session.add(node)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_confidence_too_high(db_session):
    """confidence_level must be between 0 and 5."""
    node = FrameworkNode(path="p1", depth=0, title="T", confidence_level=6)
    db_session.add(node)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_confidence_negative(db_session):
    """confidence_level cannot be negative."""
    node = FrameworkNode(path="p1", depth=0, title="T", confidence_level=-1)
    db_session.add(node)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_framework_relevant_companies_property(db_session):
    """relevant_companies_list getter/setter works."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    node.relevant_companies_list = ["Google", "Meta"]
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    assert node.relevant_companies_list == ["Google", "Meta"]


def test_framework_relevant_companies_empty(db_session):
    """Empty relevant_companies returns []."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    assert node.relevant_companies_list == []


def test_framework_cascade_delete_children(db_session):
    """Deleting parent cascades to children."""
    root = FrameworkNode(path="root", depth=0, title="Root")
    db_session.add(root)
    db_session.flush()

    child = FrameworkNode(parent_id=root.id, path="root.child", depth=1, title="Child")
    db_session.add(child)
    db_session.commit()

    db_session.delete(root)
    db_session.commit()
    assert db_session.query(FrameworkNode).count() == 0


def test_framework_cascade_delete_study_logs(db_session):
    """Deleting node cascades to its study logs."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add(node)
    db_session.flush()

    log = StudyLog(
        framework_node_id=node.id, date=date(2024, 1, 1), duration_minutes=30
    )
    db_session.add(log)
    db_session.commit()

    db_session.delete(node)
    db_session.commit()
    assert db_session.query(StudyLog).count() == 0


def test_framework_study_logs_relationship(db_session):
    """Node.study_logs relationship works."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add(node)
    db_session.flush()

    log1 = StudyLog(
        framework_node_id=node.id, date=date(2024, 1, 1), duration_minutes=30
    )
    log2 = StudyLog(
        framework_node_id=node.id, date=date(2024, 1, 2), duration_minutes=60
    )
    db_session.add_all([log1, log2])
    db_session.commit()
    db_session.refresh(node)

    assert len(node.study_logs) == 2


# --- StudyLog tests ---


def test_study_log_creation(db_session):
    """StudyLog links to FrameworkNode."""
    n = FrameworkNode(path="p1", depth=0, title="Test")
    db_session.add(n)
    db_session.flush()

    log = StudyLog(
        framework_node_id=n.id,
        date=date(2024, 1, 15),
        duration_minutes=30,
        activity_type="practice",
    )
    db_session.add(log)
    db_session.commit()
    assert log.id is not None
    assert log.framework_node.title == "Test"


def test_study_log_defaults(db_session):
    """StudyLog defaults: created_at set, optional fields null."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add(node)
    db_session.flush()

    log = StudyLog(
        framework_node_id=node.id, date=date(2024, 6, 1), duration_minutes=45
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    assert log.created_at is not None
    assert log.activity_type is None
    assert log.notes is None


def test_study_log_with_notes(db_session):
    """StudyLog stores activity_type and notes."""
    node = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add(node)
    db_session.flush()

    log = StudyLog(
        framework_node_id=node.id,
        date=date(2024, 3, 15),
        duration_minutes=90,
        activity_type="video",
        notes="Watched lecture on DP",
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    assert log.activity_type == "video"
    assert log.notes == "Watched lecture on DP"
    assert log.duration_minutes == 90


# --- Company tests ---


def test_company_duplicate_name(db_session):
    """Duplicate company name raises IntegrityError."""
    c1 = Company(name="Google")
    c2 = Company(name="Google")
    db_session.add(c1)
    db_session.commit()
    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_company_defaults(db_session):
    """Company defaults: status=applied, optional fields null."""
    c = Company(name="TestCo")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    assert c.status == "applied"
    assert c.group_tag is None
    assert c.notes is None
    assert c.applied_at is None
    assert c.interview_stages is None


def test_company_all_valid_statuses(db_session):
    """All valid company statuses are accepted."""
    statuses = ["applied", "phone_screen", "onsite", "offer", "rejected"]
    for i, s in enumerate(statuses):
        c = Company(name=f"Co{i}", status=s)
        db_session.add(c)
    db_session.commit()
    assert db_session.query(Company).count() == 5


def test_company_invalid_status(db_session):
    """Invalid company status raises IntegrityError."""
    c = Company(name="Bad", status="interviewing")
    db_session.add(c)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_company_interview_stages_property(db_session):
    """interview_stages_list getter/setter works."""
    c = Company(name="Google")
    c.interview_stages_list = [
        {"name": "Phone", "type": "technical"},
        {"name": "Onsite", "type": "system_design"},
    ]
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    stages = c.interview_stages_list
    assert len(stages) == 2
    assert stages[0]["name"] == "Phone"
    assert stages[1]["type"] == "system_design"


def test_company_interview_stages_empty(db_session):
    """Empty interview_stages returns []."""
    c = Company(name="Empty")
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)

    assert c.interview_stages_list == []


def test_company_cascade_delete_weights(db_session):
    """Deleting company cascades to topic weights."""
    c = Company(name="Google")
    n = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add_all([c, n])
    db_session.flush()

    w = CompanyTopicWeight(company_id=c.id, framework_node_id=n.id, weight=3.0)
    db_session.add(w)
    db_session.commit()

    db_session.delete(c)
    db_session.commit()
    assert db_session.query(CompanyTopicWeight).count() == 0


# --- CompanyTopicWeight tests ---


def test_company_topic_weight_composite_pk(db_session):
    """CompanyTopicWeight composite PK prevents duplicates."""
    c = Company(name="Google")
    n = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add_all([c, n])
    db_session.flush()

    w1 = CompanyTopicWeight(company_id=c.id, framework_node_id=n.id, weight=3.0)
    db_session.add(w1)
    db_session.commit()

    db_session.expunge(w1)
    w2 = CompanyTopicWeight(company_id=c.id, framework_node_id=n.id, weight=4.0)
    db_session.add(w2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_company_topic_weight_default(db_session):
    """CompanyTopicWeight default weight is 1.0."""
    c = Company(name="Meta")
    n = FrameworkNode(path="p1", depth=0, title="T")
    db_session.add_all([c, n])
    db_session.flush()

    w = CompanyTopicWeight(company_id=c.id, framework_node_id=n.id)
    db_session.add(w)
    db_session.commit()

    result = db_session.query(CompanyTopicWeight).first()
    assert result.weight == 1.0


def test_company_topic_weight_relationship(db_session):
    """CompanyTopicWeight relationships to company and node work."""
    c = Company(name="Google")
    n = FrameworkNode(path="p1", depth=0, title="Coding")
    db_session.add_all([c, n])
    db_session.flush()

    w = CompanyTopicWeight(company_id=c.id, framework_node_id=n.id, weight=4.5)
    db_session.add(w)
    db_session.commit()
    db_session.refresh(w)

    assert w.company.name == "Google"
    assert w.framework_node.title == "Coding"


def test_company_topic_weight_via_company_relationship(db_session):
    """Company.topic_weights relationship returns weights."""
    c = Company(name="Google")
    n1 = FrameworkNode(path="p1", depth=0, title="Coding")
    n2 = FrameworkNode(path="p2", depth=0, title="ML")
    db_session.add_all([c, n1, n2])
    db_session.flush()

    w1 = CompanyTopicWeight(company_id=c.id, framework_node_id=n1.id, weight=4.0)
    w2 = CompanyTopicWeight(company_id=c.id, framework_node_id=n2.id, weight=2.0)
    db_session.add_all([w1, w2])
    db_session.commit()
    db_session.refresh(c)

    assert len(c.topic_weights) == 2
    weights = {tw.framework_node.title: tw.weight for tw in c.topic_weights}
    assert weights["Coding"] == 4.0
    assert weights["ML"] == 2.0
