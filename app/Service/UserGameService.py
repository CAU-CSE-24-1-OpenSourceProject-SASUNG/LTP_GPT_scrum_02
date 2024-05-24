from sqlalchemy import desc

from app.domain.Game import Game
from app.domain.User_Game import User_Game


class UserGameService:
    def __init__(self, session):
        self.session = session

    def create_user_game(self, user_id, game_id):
        user_game = User_Game(user_id=user_id, game_id=game_id)
        self.session.add(user_game)
        self.session.commit()

    def get_recent_game(self, user_id):
        user_games = self.session.query(User_Game).filter_by(user_id=user_id).all()
        game_ids = [user_game.game_id for user_game in user_games]
        game = self.session.query(Game) \
            .filter(Game.game_id.in_(game_ids)) \
            .order_by(desc(Game.updatedAt)) \
            .first()
        return game

    def get_recent_games(self, user_id):
        user_games = self.session.query(User_Game).filter_by(user_id=user_id).all()
        game_ids = [user_game.game_id for user_game in user_games]
        games = self.session.query(Game) \
            .filter(Game.game_id.in_(game_ids)) \
            .order_by(desc(Game.updatedAt)) \
            .limit(20) \
            .all()
        return games
