import uuid

from sqlalchemy import *

from . import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey('queries.query_id'))
    content = Column(String(255))
