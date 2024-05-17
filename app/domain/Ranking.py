from sqlalchemy import Column, Integer, ForeignKey, String, Time
from sqlalchemy.orm import relationship

from app.db.session import Base


class Ranking(Base):
    __tablename__ = 'ranking'

    rank_id = Column(Integer, primary_key=True, autoincrement=True)
    riddle_id = Column(Integer, ForeignKey('riddles.riddle_id'))
    rank = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user_name = Column(String(255))
    play_time = Column(Time)

    user = relationship('User')
    riddle = relationship('Riddle')
