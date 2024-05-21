from sqlalchemy import Column, Integer, ForeignKey, String

from app.db.session import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey('queries.query_id'))
    content = Column(String(255))
