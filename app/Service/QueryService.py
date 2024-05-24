import datetime

from app.domain.Feedback import Feedback
from app.domain.Game import Game
from app.domain.Game_Query import Game_Query
from app.domain.Query import Query


class QueryService:
    def __init__(self, session):
        self.session = session

    def create_query(self, query, response, is_correct=False):
        query = Query(query=query, response=response, createdAt=datetime.datetime.now(), is_correct=is_correct)

        self.session.add(query)
        self.session.commit()

        return query.query_id

    def get_query(self, query_id):
        return self.session.query(Query).filter_by(query_id=query_id).first()

    def get_query_by_game(self, game_id):
        return self.session.query(Game_Query).filter_by(game_id=game_id).all()

    def get_response(self, query, riddle_id):
        games = self.session.query(Game).filter_by(riddle_id=riddle_id).all()
        for game in games:
            game_queries = self.session.query(Game_Query).filter_by(game_id=game.game_id).all()
            for game_query in game_queries:
                query_object = game_query.query
                if query_object.query == query:
                    return query_object.response
                else:
                    return None

    def get_all_query(self):
        return self.session.query(Query).all()

    def update_query(self, query_id, is_correct):
        query = self.get_query(query_id)
        if query:
            query.is_correct = is_correct
            self.session.commit()

    def delete_query(self, query_id):
        query = self.get_query(query_id)
        if query:
            game_query = self.session.query(Game_Query).filter_by(query_id=query_id).first()
            feedback = self.session.query(Feedback).filter_by(query_id=query_id).first()

            if game_query:
                self.session.delete(game_query)
            if feedback:
                self.session.delete(feedback)

            self.session.delete(query)
            self.session.commit()
