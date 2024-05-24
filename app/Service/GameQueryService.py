from app.domain.Game import Game
from app.domain.Game_Query import Game_Query


class GameQueryService:
    def __init__(self, session):
        self.session = session

    def create_game_query(self, game_id, query_id):
        game_query = Game_Query(game_id=game_id, query_id=query_id)
        game = self.session.query(Game).filter_by(game_id=game_id).first()
        game.query_ticket -= 1
        self.session.add(game_query)
        self.session.commit()

    def get_queries(self, game_id):
        return self.session.query(Game_Query).filter_by(game_id=game_id).all()
