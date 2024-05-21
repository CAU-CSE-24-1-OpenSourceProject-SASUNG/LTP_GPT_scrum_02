from sqlalchemy import Column, Integer, ForeignKey, String

from app.db.session import Base

class Total_Feedback(Base):
    __tablename__ = "total_feedbacks"

    total_feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'))
    content = Column(String(255))
