import uuid

from sqlalchemy import *
from sqlalchemy.orm import relationship

from . import Base


class Game_Query(Base):
    __tablename__ = "game_queries"

    gq_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(36), ForeignKey('games.game_id'))
    query_id = Column(String(36), ForeignKey('queries.query_id'))

    game = relationship('Game')
    query = relationship('Query', uselist=False)
