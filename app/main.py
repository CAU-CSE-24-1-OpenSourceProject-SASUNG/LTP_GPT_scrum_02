import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
#from fastapi.middleware.cors import CORSMiddleware  # CORS

from .Init import session, engine
from .service.FeedbackService import FeedbackService
from .service.GameService import GameService
from .service.QueryService import QueryService
from .service.RiddleService import RiddleService
from .service.TotalFeedbackService import TotalFeedbackService
from .service.UserService import UserService
from .service.RankingService import RankingService
from .service.UserGameService import UserGameService
from .service.GameQueryService import GameQueryService

from sqlalchemy import text
from typing import List, Dict

#google login
from database.connection import conn
from routes.users import user_router

from .config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
from fastapi.staticfiles import StaticFiles
import app.ltp_gpt as ltp_gpt
import secrets

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router, prefix="/user")

## CORS
#origins = [
#    "http://localhost:3000",
#    "http://127.0.0.1:3000"
#]
#
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=origins,
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

templates = Jinja2Templates(directory="templates")

userService = UserService(session)
gameService = GameService(session)
riddleService = RiddleService(session)
queryService = QueryService(session)
feedbackService = FeedbackService(session)
totalFeedbackService = TotalFeedbackService(session)
rankingService = RankingService(session)
ugService = UserGameService(session)
gqService = GameQueryService(session)

## DB 모든 데이터 삭제
#with engine.connect() as conn:
#    table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries', 'ranking']
#    # table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries']
#    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))  # 외래 키 제약 조건을 잠시 해제
#    for table_name in table_names:
#        delete_query = text('TRUNCATE TABLE {};'.format(table_name))
#        conn.execute(delete_query)
#    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))  # 외래 키 제약 조건을 다시 활성화



recent_games = [
        {'gameId': '1', 'gameTitle': '아이는 10층에 산다 (1)'},
        {'gameId': '2', 'gameTitle': '더운 방 속 한 사람 (2)'},
        {'gameId': '3', 'gameTitle': '더운 방 속 한 사람 (1)'}
        ]

@app.get('/recentgames')
async def reaccess(request: Request):
    return JSONResponse(content=recent_games)

riddle_items = [
        {'riddleId': '1', 'riddleTitle': '아이는 10층에 산다.'},
        {'riddleId': '2', 'riddleTitle': '도청하는 사람 A'},
        {'riddleId': '3', 'riddleTitle': '더운 방 속 한 사람'}
        ]

@app.get('/riddles')
async def show_all_riddle():
    return JSONResponse(content=riddle_items)


@app.post('/newgame')
async def create_game():
    return JSONResponse(content={'newGameId': '3'})



game_info = [
        {'gameTitle' : '아이는 10층에 산다. (1)', 'problem': '어떤 아이가 아파트 10층에 살고 있다. 아이는 맑은 날 ~'},
        {'queryId' : '1', 'query' : '안녕' , 'response' : '상관 없습니다.'},
        {'queryId' : '2', 'query' : '아이는 키가 작아?' , 'response' : '맞습니다.'},
        {'queryId' : '3', 'query' : '아이는 우산을 가지고 있어?' , 'response' : '맞습니다.'},
        {'queryId' : '4', 'query' : '아이는 운동하는 걸 좋아해?' , 'response' : '아닙니다.'},
        {'queryId' : '5', 'query' : '아이는 비오는 날 우산으로 10층 버튼을 누를 수 있는거야!' , 'response' : '정확한 정답을 맞추셨습니다!'},
        ]


@app.get('/gameinfo')
async def access_game(gameid: int = Query(...)):
    return JSONResponse(content=game_info)

#@app.post("/chat")
#async def chat(request: Request):
#    try:
#        body = await request.json()
#        question = body.get("question")
#        user_id = request.session.get('user_id')
#        game_id = request.session.get('game_id')
#        riddle_id = request.session.get('riddle_id')
#
#        response = queryService.get_response(question, riddle_id)  # 메모이제이션
#        if not response:
#            response = ltp_gpt.evaluate_question(question)
#        query_id = queryService.create_query(question, response)
#        gqService.create_game_query(game_id, query_id)
#
#        game = gameService.get_game(game_id)
#        if game.is_first is True:  # 동일 게임에 대해 최초의 정답만 데이터, 랭킹 업데이트
#            if "정답" in response:  # 정답이면 game을 종료 -> 정답을 맞춘 것을 어떻게 판단?
#                game_end_time = datetime.datetime.now()
#                game_start_time_str = request.session.get('game_start_time')
#                if game_start_time_str:
#                    game_start_time = datetime.datetime.strptime(game_start_time_str, "%Y-%m-%d %H:%M:%S")
#                    play_time = game_end_time - game_start_time
#                    gameService.end_game(game_id, play_time, False, True)  # Game tuple 데이터 업데이트
#                    game = gameService.get_game(game_id)
#                    if game:
#                        rankingService.update_ranking(game)  # 랭킹 업데이트
#                    userService.level_up(user_id)
#            # 정답이 아니라 game을 중간에 나갔다면.. controller 다른 곳에 작성
#
#        return JSONResponse(content={"response": response})
#    except Exception as e:
#        print(str(e))
#        return JSONResponse(content={"error": str(e)}, status_code=500)
#
#
#@app.get('/recentgames')
#async def reaccess(request: Request):
#    #    user_id = request.session.get('user_id')
##    games = ugService.get_recent_games(user_id)
##    recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
##    return JSONResponse(content=recent_games)
#    games = gameService.get_all_game()
#    recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
#    return JSONResponse(content=recent_games)
#
#
#@app.get('/riddles')
#async def show_all_riddle():
#    riddles = riddleService.get_all_riddle()
#    all_riddles = [{'riddleId': riddle.riddle_id, 'riddleTitle': riddle.title} for riddle in riddles]
#    return JSONResponse(content=all_riddles)
#
#
#@app.post('/newgame')
#async def create_game(request: Request, riddleid: int = Query(...)):
#    user_id = request.session.get('user_id')
#    game_id = gameService.create_game(user_id, riddleid)
#    return JSONResponse(content={'newGameId': game_id})
#
#
#@app.get('/gameinfo')
#async def access_game(gameid: int = Query(...)):
#    #gameService.reaccess(gameid)
#
#    game = gameService.get_game(gameid)
#    riddle = riddleService.get_riddle(game.riddle_id)
#    game_queries = gqService.get_queries(gameid)
#
#    game_info = [
#        {'gameTitle': game.title, 'problem': riddle.problem}
#    ]
#    for game_query in game_queries:
#        query = queryService.get_query(game_query.query_id)
#        game_info.append({
#            'queryId': query.query_id,
#            'query': query.query,
#            'response': query.response
#        })
#
#    return JSONResponse(content=game_info)
#
#
#@app.get('/logout')
#def logout(request: Request):
#    request.session.pop('user')
#    request.session.clear()
#    return RedirectResponse('/')
