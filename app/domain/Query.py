from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base

class Query(Base):
    __tablename__ = "queries"

    query_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(255))
    response = Column(String(255))
    createdAt = Column(DateTime)
    is_correct = Column(Boolean)

    feedback = relationship('Feedback', uselist=False)
