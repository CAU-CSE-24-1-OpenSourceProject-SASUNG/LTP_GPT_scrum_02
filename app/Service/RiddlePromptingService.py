from app.domain.Riddle_Prompting import Riddle_Prompting


class RiddlePromptingService:
    def __init__(self, session):
        self.session = session

    def create_riddle_prompting(self, riddle_id, exQueryResponse):
        for item in exQueryResponse:
            ex_query = item.get('exQuery')
            ex_response = item.get('exResponse')
            riddle_prompting = Riddle_Prompting(riddle_id=riddle_id, user_query=ex_query,
                                                assistant_response=ex_response)
            self.session.add(riddle_prompting)
        self.session.commit()

    def get_all_prompting(self, riddle_id):
        return self.session.query(Riddle_Prompting).filter_by(riddle_id=riddle_id).all()
