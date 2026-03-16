"""Schema audit test: verify all ORM model columns exist in the database.

Uses subset assertion (model_columns <= db_columns) rather than strict
equality, since the DB may have extra columns the ORM doesn't map.
The important invariant is: every column the ORM expects must exist.
"""
from sqlalchemy import inspect

from src.backend.database import Base


def test_all_model_columns_exist_in_db(db_engine):
    """Every column in every SQLAlchemy model must exist in the DB table."""
    inspector = inspect(db_engine)
    for mapper in Base.registry.mappers:
        table = mapper.persist_selectable
        table_name = table.name
        db_columns = {col["name"] for col in inspector.get_columns(table_name)}
        model_columns = {col.name for col in table.columns}
        missing = model_columns - db_columns
        assert not missing, (
            f"Table '{table_name}': columns in model but not DB: {missing}"
        )
