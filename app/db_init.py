from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from app.domain import Base

from app.domain.User import User
from app.domain.Game import Game
from app.domain.User_Game import User_Game
from app.domain.TotalFeedback import Total_Feedback
from app.domain.Feedback import Feedback
from app.domain.Riddle import Riddle
from app.domain.Riddle_Prompting import Riddle_Prompting
from app.domain.Query import Query
from app.domain.Game_Query import Game_Query
from app.domain.Ranking import Ranking

# db연결 및 객체 베이스 생성
# 'mysql_pymysql://db_id:db_password@dp_ip/dp_port'
# engine = create_engine('mysql+pymysql://root:seaturtle@localhost/test4', echo=False)
engine = create_engine('mysql+pymysql://root:gusdn4818@localhost/ossp', echo=False)

# Session 선언. Session을 이용하여 db를 조작 가능
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
