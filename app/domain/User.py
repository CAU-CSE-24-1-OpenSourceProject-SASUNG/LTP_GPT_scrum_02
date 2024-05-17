from sqlalchemy import Column, Integer, String, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    gmail = Column(String(255), primary_key=True)
    name = Column(String(255))
    experience = Column(Integer)

    total_feedback = relationship("Total_Feedback", uselist=False)
