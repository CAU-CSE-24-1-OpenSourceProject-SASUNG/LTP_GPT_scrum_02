from sqlalchemy import asc

from app.domain.Ranking import Ranking
from app.domain.User_Game import User_Game


class RankingService:
    def __init__(self, session):
        self.session = session

    # 랭킹 업데이트
    def update_ranking(self, game):
        if game:
            user_game = self.session.query(User_Game).filter_by(game_id=game.game_id).first()
            user = user_game.user
            rankings = self.get_all_ranking(game.riddle_id)

            rank = 1
            if rankings:
                for ranking in rankings:
                    if game.correct_time > ranking.correct_time:
                        rank += 1
                new_ranking = Ranking(riddle_id=game.riddle_id, rank=rank, user_id=user.user_id, user_name=user.name,
                                      correct_time=game.correct_time)
            else:
                new_ranking = Ranking(riddle_id=game.riddle_id, rank=rank, user_id=user.user_id, user_name=user.name,
                                      correct_time=game.correct_time)

            for old_ranking in self.session.query(Ranking).filter(Ranking.rank >= rank).all():
                old_ranking.rank += 1

            self.session.add(new_ranking)
            self.session.commit()

    # 상위 3명의 랭킹을 가져옴
    def get_top_ranking(self, riddle_id):
        rankings = self.get_all_ranking(riddle_id)
        return sorted(rankings, key=lambda x: x.play_time)[:3]

    def get_all_ranking(self, riddle_id):
        return self.session.query(Ranking).filter_by(riddle_id=riddle_id).order_by(asc(Ranking.play_time)).all()

    def show_all_ranking(self, riddle_id):
        rankings = self.get_all_ranking(riddle_id)
        for ranking in rankings:
            print(ranking)
