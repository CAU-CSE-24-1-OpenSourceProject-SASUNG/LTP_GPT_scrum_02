from sqlalchemy import Column, Integer, ForeignKey, String, Time
from sqlalchemy.orm import relationship

from app.db.session import Base

class Ranking(Base):
    __tablename__ = 'ranking'

    rank_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    rank = Column(Integer)
    user_id = Column(String(36), ForeignKey('users.user_id'))
    user_name = Column(String(255))
    play_time = Column(Time)

    user = relationship('User')
    riddle = relationship('Riddle')
