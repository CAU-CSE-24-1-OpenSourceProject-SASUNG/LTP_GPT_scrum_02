from sqlalchemy import Column, Integer, ForeignKey, String

from app.db.session import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey('queries.query_id'))
    content = Column(String(255))
