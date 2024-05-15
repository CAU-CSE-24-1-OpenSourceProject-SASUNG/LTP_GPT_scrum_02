import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker

# db연결 및 객체 베이스 생성
# 'mysql_pymysql://db_id:db_password@dp_ip/dp_port'
engine = create_engine('mysql+pymysql://root:seaturtle@localhost/test', echo=False)
Base = sqlalchemy.orm.declarative_base()

# Session 선언. Session을 이용하여 db를 조작 가능
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    gmail = Column(String(255), primary_key=True)
    name = Column(String(255))
    experience = Column(Integer)

    total_feedback = relationship("Total_Feedback", uselist=False)


class User_Game(Base):
    __tablename__ = 'user_games'

    ug_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    game_id = Column(Integer, ForeignKey('games.game_id'))

    user = relationship("User")
    game = relationship("Game", uselist=False)


class Total_Feedback(Base):
    __tablename__ = "total_feedbacks"

    total_feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(String(255))


class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    problem = Column(String(255))
    title = Column(String(255))
    hit_ratio = Column(Float)


class Ranking(Base):
    __tablename__ = 'ranking'

    rank_id = Column(Integer, primary_key=True, autoincrement=True)
    riddle_id = Column(Integer, ForeignKey('riddles.riddle_id'))
    rank = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user_name = Column(String(255))
    play_time = Column(Time)

    user = relationship('User')
    riddle = relationship('Riddle')


class Query(Base):
    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(255))
    response = Column(String(255))
    createdAt = Column(DateTime)
    is_correct = Column(Boolean)

    feedback = relationship('Feedback', uselist=False)


class Game_Query(Base):
    __tablename__ = "game_queries"

    gq_id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.game_id'))
    query_id = Column(Integer, ForeignKey('queries.query_id'))

    game = relationship('Game')
    query = relationship('Query', uselist=False)


class Game(Base):
    __tablename__ = 'games'

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    riddle_id = Column(Integer, ForeignKey('riddles.riddle_id'))
    title = Column(String(255))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    is_first = Column(Boolean)
    progress = Column(Integer)
    query_count = Column(Integer)
    play_time = Column(Time)
    query_length = Column(Integer)
    hit = Column(Boolean)

    riddle = relationship('Riddle')


class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey('queries.query_id'))
    content = Column(String(255))


Base.metadata.create_all(engine)
