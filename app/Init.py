import uuid

import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.mysql import LONGTEXT

# db연결 및 객체 베이스 생성
# 'mysql_pymysql://db_id:db_password@dp_ip/dp_port'
# engine = create_engine('mysql+pymysql://root:seaturtle@localhost/test4', echo=False)
engine = create_engine('mysql+pymysql://root:gusdn4818@localhost/ossp', echo=False)
Base = sqlalchemy.orm.declarative_base()

# Session 선언. Session을 이용하여 db를 조작 가능
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gmail = Column(String(255), primary_key=True)
    name = Column(String(255))
    experience = Column(Integer)
    riddle_ticket = Column(Integer)
    game_ticket = Column(Integer)


class User_Game(Base):
    __tablename__ = 'user_games'

    ug_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'))
    game_id = Column(String(36), ForeignKey('games.game_id'))

    user = relationship("User")
    game = relationship("Game", uselist=False)


class Total_Feedback(Base):
    __tablename__ = "total_feedbacks"

    total_feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.user_id'))
    content = Column(String(255))

    user = relationship("User", uselist=False)


class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator = Column(String(255))
    title = Column(String(255))
    problem = Column(String(255))
    situation = Column(String(3000))
    answer = Column(String(255))
    progress_sentences = Column(String(3000))
    hit_ratio = Column(Float)
    point_1 = Column(Integer)
    point_2 = Column(Integer)
    point_3 = Column(Integer)
    point_4 = Column(Integer)
    point_5 = Column(Integer)
    problem_embedding_str = Column(LONGTEXT)
    situation_embedding_str = Column(LONGTEXT)
    answer_embedding_str = Column(LONGTEXT)


class Riddle_Prompting(Base):
    __tablename__ = 'riddle_prompting'

    riddle_prompting_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    user_query = Column(String(255))
    assistant_response = Column(String(255))

    riddle = relationship('Riddle', uselist=False)


class Ranking(Base):
    __tablename__ = 'ranking'

    rank_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    rank = Column(Integer)
    user_id = Column(String(36), ForeignKey('users.user_id'))
    user_name = Column(String(255))
    correct_time = Column(Time)

    user = relationship('User')
    riddle = relationship('Riddle')


class Query(Base):
    __tablename__ = "queries"

    query_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(String(255))
    response = Column(String(255))
    createdAt = Column(DateTime)
    is_correct = Column(Boolean)

    feedback = relationship('Feedback', uselist=False)


class Game_Query(Base):
    __tablename__ = "game_queries"

    gq_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String(36), ForeignKey('games.game_id'))
    query_id = Column(String(36), ForeignKey('queries.query_id'))

    game = relationship('Game')
    query = relationship('Query', uselist=False)


class Game(Base):
    __tablename__ = 'games'

    game_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    riddle_id = Column(String(36), ForeignKey('riddles.riddle_id'))
    title = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    is_first = Column(Boolean)
    progress = Column(Integer)
    query_ticket = Column(Integer)
    correct_time = Column(Time)
    play_time = Column(Time)
    query_length = Column(Integer)
    hit = Column(Boolean)

    riddle = relationship('Riddle')


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey('queries.query_id'))
    content = Column(String(255))


Base.metadata.create_all(engine)
