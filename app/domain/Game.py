import uuid

from sqlalchemy import *
from sqlalchemy.orm import relationship

from . import Base


class Game(Base):
    __tablename__ = 'games'

    game_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    title = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    is_first = Column(Boolean)
    progress = Column(Integer)
    query_ticket = Column(Integer)
    correct_time = Column(Time)
    play_time = Column(Time)
    query_length = Column(Integer)
    hit = Column(Boolean)

    riddle = relationship('Riddle')
