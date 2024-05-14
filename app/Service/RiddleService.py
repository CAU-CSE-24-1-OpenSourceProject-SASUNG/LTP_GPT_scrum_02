from app.Init import *


class RiddleService:
    def __init__(self, session):
        self.session = session

    def create_riddle(self, name, title, hit_ratio):
        riddle = Riddle(name=name, title=title, hit_ratio=hit_ratio)
        self.session.add(riddle)
        self.session.commit()

        return riddle.riddle_id

    def get_riddle(self, riddle_id):
        return self.session.query(Riddle).filter_by(riddle_id=riddle_id).first()

    def get_riddle_by_name(self, name):
        return self.session.query(Riddle).filter_by(name=name).first()

    def get_all_riddle(self):
        return self.session.query(Riddle).all()

    def update_riddle(self, riddle_id, hit_ratio):
        riddle = self.get_riddle(riddle_id)
        if riddle:
            riddle.hit_ratio = hit_ratio
            self.session.commit()

    def delete_riddle(self, riddle_id):
        riddle = self.get_riddle(riddle_id)
        if riddle:
            games = self.session.query(Game).filter_by(riddle_id=riddle.riddle_id).all()
            rankings = self.session.query(Ranking).filter_by(riddle_id=riddle.riddle_id).all()
            if games:
                for game in games:
                    user_game = self.session.query(User_Game).filter_by(game_id=game.game_id).first()
                    game_queries = self.session.query(Game_Query).filter_by(game_id=game.game_id).all()
                    if user_game:
                        self.session.delete(user_game)
                    if game_queries:
                        for game_query in game_queries:
                            self.session.delete(game_query)
                    self.session.delete(game)
            if rankings:
                for ranking in rankings:
                    self.session.delete(ranking)

            self.session.delete(riddle)
            self.session.commit()
