from sqlalchemy import Column, Integer, String, relationship

from app.db.session import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gmail = Column(String(255), primary_key=True)
    name = Column(String(255))
    experience = Column(Integer)

    total_feedback = relationship("Total_Feedback", uselist=False)
