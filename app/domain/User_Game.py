from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class User_Game(Base):
    __tablename__ = 'user_games'

    ug_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    game_id = Column(Integer, ForeignKey('games.game_id'))

    user = relationship("User")
    game = relationship("Game", uselist=False)

