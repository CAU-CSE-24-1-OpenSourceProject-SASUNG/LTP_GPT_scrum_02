from app.Init import *


class UserService:
    def __init__(self, session):
        self.session = session

    def create_user(self, gmail, name):
        user = User(gmail=gmail, name=name, experience=0)
        self.session.add(user)
        self.session.commit()

        return user.user_id

    def get_user(self, user_id):
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_user_email(self, gmail):
        return self.session.query(User).filter_by(gmail=gmail).first()

    def get_all_user(self):
        return self.session.query(User).all()

    def level_up(self, user_id):
        user = self.get_user(user_id)
        if user:
            user.experience += 20
            self.session.commit()

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            user_games = self.session.query(User_Game).filter_by(user_id=user.user_id).all()
            total_feedback = self.session.query(Total_Feedback).filter_by(user_id=user.user_id).first()
            rankings = self.session.query(Ranking).filter_by(user_id=user.user_id).all()

            if user_games:
                for user_game in user_games:
                    self.session.delete(user_game)
            if total_feedback:
                self.session.delete(total_feedback)
            if rankings:
                for ranking in rankings:
                    self.session.delete(ranking)

            self.session.delete(user)
            self.session.commit()
