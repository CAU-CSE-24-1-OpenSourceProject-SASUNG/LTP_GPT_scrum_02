import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship, sessionmaker

# db연결 및 객체 베이스 생성
# 'mysql_pymysql://db_id:db_password@dp_ip/dp_port'
engine = create_engine('mysql+pymysql://root:gusdn4818@localhost/ossp', echo=False)
Base = sqlalchemy.orm.declarative_base()
3
# Session 선언. Session을 이용하여 db를 조작 가능
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(255), primary_key=True)
    # email = Column(String(255), primary_key=True)

    user_games = relationship("User_Game")
    total_feedback = relationship("Total_Feedback", uselist=False)


class User_Game(Base):
    __tablename__ = 'user_games'

    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    game_id = Column(String(255), ForeignKey('games.game_id'), primary_key=True)


class Total_Feedback(Base):
    __tablename__ = "total_feedbacks"

    user_id = Column(String(255), ForeignKey('users.user_id'), primary_key=True)
    content = Column(String(255))


class Riddle(Base):
    __tablename__ = 'riddles'

    riddle_id = Column(String(255), primary_key=True)
    hit_ratio = Column(Float)

    games = relationship("Game", back_populates="riddle")


class Query(Base):
    __tablename__ = "queries"

    query_id = Column(String(255), primary_key=True)
    query = Column(String(255))
    response = Column(String(255))
    is_correct = Column(Boolean)

    game_query = relationship('Game_Query', uselist=False)
    feedback = relationship('Feedback', uselist=False, back_populates='query')


class Game_Query(Base):
    __tablename__ = "game_queries"

    game_id = Column(String(255), ForeignKey('games.game_id'), primary_key=True)
    query_id = Column(String(255), ForeignKey('queries.query_id'), primary_key=True)


class Game(Base):
    __tablename__ = 'games'

    game_id = Column(String(255), primary_key=True)
    riddle_id = Column(String(255), ForeignKey('riddles.riddle_id'))
    query_count = Column(Integer)
    play_time = Column(Time)
    query_length = Column(Integer)
    hit = Column(Boolean)

    game_queries = relationship("Game_Query")
    user_game = relationship('User_Game', uselist=False)
    riddle = relationship("Riddle", back_populates="games")


class Feedback(Base):
    __tablename__ = "feedbacks"

    query_id = Column(String(255), ForeignKey('queries.query_id'), primary_key=True)
    content = Column(String(255))

    query = relationship("Query", uselist=False, back_populates="feedback")


Base.metadata.create_all(engine)
