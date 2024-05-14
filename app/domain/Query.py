from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class Query(Base):
    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(255))
    response = Column(String(255))
    createdAt = Column(DateTime)
    is_correct = Column(Boolean)

    feedback = relationship('Feedback', uselist=False)


