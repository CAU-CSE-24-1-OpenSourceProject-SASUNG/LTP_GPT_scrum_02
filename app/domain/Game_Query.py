from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Game_Query(Base):
    __tablename__ = "game_queries"

    gq_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    query_id = Column(Integer, ForeignKey('queries.query_id'))

    game = relationship('Game')
    query = relationship('Query', uselist=False)


