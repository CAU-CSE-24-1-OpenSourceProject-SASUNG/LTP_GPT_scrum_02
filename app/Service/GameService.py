import datetime

from app.Init import *


class GameService:
    def __init__(self, session):
        self.session = session

    def create_game(self, user_id, riddle_id, is_first=True, progress=0, query_count=0, correct_time=0, play_time=0,
                    query_length=0,
                    hit=False):
        count = 1
        user_games = self.session.query(User_Game).filter_by(user_id=user_id).all()
        for user_game in user_games:
            count += self.session.query(Game).filter_by(game_id=user_game.game_id, riddle_id=riddle_id).count()
        riddle_title = self.session.query(Riddle).filter_by(riddle_id=riddle_id).first().title
        title = f"{riddle_title} ({count})"
        createdAt = datetime.datetime.now()
        updatedAt = datetime.datetime.now()
        game = Game(riddle_id=riddle_id, title=title, createdAt=createdAt, updatedAt=updatedAt, is_first=is_first,
                    progress=progress, query_count=query_count, correct_time=correct_time, play_time=play_time,
                    query_length=query_length, hit=hit)
        self.session.add(game)
        self.session.commit()

        return game.game_id

    def get_game(self, game_id):
        return self.session.query(Game).filter_by(game_id=game_id).first()

    def get_game_by_user(self, user_id):
        return self.session.query(User_Game).filter_by(user_id=user_id).limit(20).all()

    def get_all_game(self):
        return self.session.query(Game).all()

    def get_game_count(self, riddle_id):
        return self.session.query(Game).filter_by(riddle_id=riddle_id).count()

    # 게임에 재접속
    def reaccess(self, game_id):
        game = self.get_game(game_id)
        game.is_first = False
        game.updatedAt = datetime.datetime.now()

    # 게임에서 정답을 맞췄을 때
    def correct_game(self, game_id, correct_time, is_first, hit):
        game = self.get_game(game_id)
        if game:
            game_queries = self.session.query(Game_Query).filter_by(game_id=game_id).all()
            query_length = 0
            for game_query in game_queries:
                query_length += len(game_query.query.query)
            query_count = len(game_queries)
            game.query_count = query_count
            game.query_length = query_length
            game.correct_time = correct_time
            game.is_first = is_first
            game.hit = hit
        self.session.commit()

    # 게임에서 나갔을 때
    def end_game(self, game_id, play_time):
        game = self.get_game(game_id)
        if game:
            game_queries = self.session.query(Game_Query).filter_by(game_id=game_id).all()
            query_length = 0
            for game_query in game_queries:
                query_length += len(game_query.query.query)
            query_count = len(game_queries)
            game.query_count = query_count
            game.query_length = query_length
            game.play_time += play_time
        self.session.commit()

    # 진행률 저장.. result는 True,False 리스트
    def set_progress(self, game_id, result):
        game = self.get_game(game_id)
        for i, tf in enumerate(result):
            if tf is True:
                if i == 0:
                    game.progress = 20
                elif i == 1:
                    game.progress = 40
                elif i == 2:
                    game.progress = 60
                elif i == 3:
                    game.progress = 80
                elif i == 4:
                    game.progress = 100
                break

    def delete_game(self, game_id):
        game = self.get_game(game_id)
        if game:
            user_game = self.session.query(User_Game).filter_by(game_id=game.game_id).first()
            game_queries = self.session.query(Game_Query).filter_by(game_id=game.game_id).all()

            if user_game:
                self.session.delete(user_game)
            if game_queries:
                for game_query in game_queries:
                    self.session.delete(game_query)

            self.session.delete(game)
            self.session.commit()
