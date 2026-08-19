from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import Session

from app.db.base import Base


class DummyModel(Base):
    __tablename__ = "dummy_test_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


def test_database_session_and_execution(db_session: Session) -> None:
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_database_table_creation_and_crud(db_session: Session) -> None:
    # Verify table schema works on db session
    item = DummyModel(id=1, name="Test Item")
    db_session.add(item)
    db_session.commit()

    retrieved = db_session.query(DummyModel).filter_by(id=1).first()
    assert retrieved is not None
    assert retrieved.name == "Test Item"
