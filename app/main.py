from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

# controller
from app.controller.ChatController import get_chat_router
from app.controller.GameController import get_game_router
from app.controller.RiddleController import get_riddle_router
from app.controller.UserController import get_user_router
# google login
from .config import SECRET_KEY
from .db_init import session, engine
# service
from .service.FeedbackService import FeedbackService
from .service.GameQueryService import GameQueryService
from .service.GameService import GameService
from .service.QueryService import QueryService
from .service.RankingService import RankingService
from .service.RiddlePromptingService import RiddlePromptingService
from .service.RiddleService import RiddleService
from .service.TotalFeedbackService import TotalFeedbackService
from .service.UserGameService import UserGameService
from .service.UserService import UserService

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Service
userService = UserService(session)
gameService = GameService(session)
riddleService = RiddleService(session)
queryService = QueryService(session)
feedbackService = FeedbackService(session)
totalFeedbackService = TotalFeedbackService(session)
rankingService = RankingService(session)
ugService = UserGameService(session)
gqService = GameQueryService(session)
rpService = RiddlePromptingService(session)

# 라우터 등록 (Controller)
app.include_router(get_chat_router(userService, gameService, queryService, gqService, rankingService), prefix="/chat")
app.include_router(get_game_router(userService, gameService, ugService, gqService, riddleService), prefix="/game")
app.include_router(get_riddle_router(userService, riddleService, rpService), prefix="/riddle")
app.include_router(get_user_router(userService), prefix="/user")

# DB 모든 데이터 삭제
with engine.connect() as conn:
    table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries', 'ranking']
    # table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries', 'riddles', 'riddle_prompting']
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))  # 외래 키 제약 조건을 잠시 해제
    for table_name in table_names:
        delete_query = text('TRUNCATE TABLE {};'.format(table_name))
        conn.execute(delete_query)
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))  # 외래 키 제약 조건을 다시 활성화
