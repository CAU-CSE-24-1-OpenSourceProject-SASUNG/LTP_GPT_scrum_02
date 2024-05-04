from Init import *


class UserService:
    def __init__(self, session):
        self.session = session

    def create_user(self, user_id, email):
        user = User(user_id=user_id, email=email)
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_id):
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_all_user(self):
        return self.session.query(User).all()

    # def update_user(self, user_id, email):
    #     user = self.get_user(user_id)
    #     if user:
    #         user.username = email
    #         self.session.commit()

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            user_games = self.session.query(User_Game).filter_by(user_id=user.user_id).all()
            total_feedback = self.session.query(Total_Feedback).filter_by(user_id=user.user_id).first()

            if user_games:
                for user_game in user_games:
                    self.session.delete(user_game)
            if total_feedback:
                self.session.delete(total_feedback)

            self.session.delete(user)
            self.session.commit()
