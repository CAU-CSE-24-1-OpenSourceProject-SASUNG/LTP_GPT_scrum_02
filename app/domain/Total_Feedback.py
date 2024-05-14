from sqlalchemy import Column, Integer, ForeignKey, String

from app.db.session import Base


class Total_Feedback(Base):
    __tablename__ = "total_feedbacks"

    total_feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(String(255))
