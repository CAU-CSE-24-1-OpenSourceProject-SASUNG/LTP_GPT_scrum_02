from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base

class User_Game(Base):
    __tablename__ = 'user_games'

    ug_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'))
    game_id = Column(String(36), ForeignKey('games.game_id'))

    user = relationship("User")
    game = relationship("Game", uselist=False)
