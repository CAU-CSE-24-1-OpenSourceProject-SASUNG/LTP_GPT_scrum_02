from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Game(Base):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    riddle_id = Column(Integer, ForeignKey('riddles.riddle_id'))
    title = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    is_first = Column(Boolean)
    query_count = Column(Integer)
    play_time = Column(Time)
    query_length = Column(Integer)
    hit = Column(Boolean)

    riddle = relationship('Riddle')
