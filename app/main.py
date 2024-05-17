import datetime
import secrets

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware  # CORS

import app.ltp_gpt as ltp_gpt
from .Init import session, engine
from .config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
from .service.FeedbackService import FeedbackService
from .service.GameQueryService import GameQueryService
from .service.GameService import GameService
from .service.QueryService import QueryService
from .service.RankingService import RankingService
from .service.RiddleService import RiddleService
from .service.TotalFeedbackService import TotalFeedbackService
from .service.UserService import UserService
from .service.UserGameService import UserGameService

from sqlalchemy import text

#google login
from .auth.jwt import create_access_token
from .auth.authenticate import authenticate

from .config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
import app.ltp_gpt as ltp_gpt
import secrets

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

#riddleService.create_riddle('Umbrella', '아이는 10층에 산다',
#                            '어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?',
#                            0)


from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

@app.post("/user/login")
async def login(user: User):
    # 로그인 유저가 DB에 있는지 검사한뒤
#    print(user.email)
#    print(user.name)
    existing_user = userService.get_user_email(user.email)
    try:
        # 있다면 토큰을 발행하고 리턴
        if existing_user:
            access_token = create_access_token(user.email)
        else:
            # 없다면 DB에 저장하고 리턴
            userService.create_user(user.email, user.name)
            access_token = create_access_token(user.email)

        return JSONResponse(content={ "access_token": access_token, "token_type": "Bearer"})
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=400)


class QueryInfo(BaseModel):
    game_id: str
    query: str


@app.post("/chat")
async def chat(request: Request, queryInfo: QueryInfo):
    try:
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user_id = userService.get_user_email(user_email)
        query = queryInfo.query
        game_id = queryInfo.game_id
        riddle_id = gameService.get_game(game_id).riddle_id
#       response = queryService.get_response(query, riddle_id)  # 메모이제이션
#        if not response:
#            response = ltp_gpt.evaluate_question(query)
        response = ltp_gpt.evaluate_question(query)

        similarity = "0%"
        print(response)

        # 2차
#        if(response == '맞습니다.' or response == '그렇다고 볼 수도 있습니다.') or response == '정답과 유사합니다.' or response == '정확한 정답을 맞추셨습니다.':
#            similarity = ltp_gpt.evaluate_similarity(question)

        # 쿼리 id 할당
        query_id = queryService.create_query(query, response)
        # game_id - query_id 연결
        gqService.create_game_query(game_id, query_id)


        # 랭킹과 정답 등의 처리
        game = gameService.get_game(game_id)
        if game.is_first is True:  # 동일 게임에 대해 최초의 정답만 데이터, 랭킹 업데이트
            if "정답" in response:  # 정답이면 game을 종료 -> 정답을 맞춘 것을 어떻게 판단?
                game_correct_time = datetime.datetime.now()
                game_start_time_str = request.session.get('game_start_time')
                if game_start_time_str:
                    game_start_time = datetime.datetime.strptime(game_start_time_str, "%Y-%m-%d %H:%M:%S")
                    correct_time = game_correct_time - game_start_time
                    gameService.correct_game(game_id, correct_time, False, True)  # Game 데이터 업데이트
                    game = gameService.get_game(game_id)
                    rankingService.update_ranking(game)  # 랭킹 업데이트
                    userService.level_up(user_id)  # 경험치 증가

        # game = gameService.get_game(game_id)
        # gameService.set_progress(game_id, result) # TF 리스트를 result로 전달
        # if game.is_first is True:  # 동일 게임에 대해 최초의 정답만 데이터, 랭킹 업데이트
        #     if game.progress == 100:  # 정답이면 game을 종료 -> 정답을 맞춘 것을 어떻게 판단?
        #         game_correct_time = datetime.datetime.now()
        #         game_start_time_str = request.session.get('game_start_time')
        #         if game_start_time_str:
        #             game_start_time = datetime.datetime.strptime(game_start_time_str, "%Y-%m-%d %H:%M:%S")
        #             correct_time = game_correct_time - game_start_time
        #             gameService.correct_game(game_id, correct_time, False, True)  # Game 데이터 업데이트
        #             game = gameService.get_game(game_id)
        #             rankingService.update_ranking(game)  # 랭킹 업데이트
        #             userService.level_up(user_id)  # 경험치 증가

        return JSONResponse(content={"response": response})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get('/recentgames')
async def lookup(request: Request):
    token = get_token_from_header(request)
    user_email = await authenticate(token)
    print(user_email)
    user = userService.get_user_email(user_email)
    games = ugService.get_recent_games(user.user_id)
    recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
    print(recent_games)
    return JSONResponse(content=recent_games)


@app.get('/recentgame')
async def access(request: Request):
    token = get_token_from_header(request)
    user_email = await authenticate(token)
    user = userService.get_user_email(user_email)
    game = ugService.get_recent_game(user.user_id)
    gameService.reaccess(game.game_id)
    return JSONResponse(content={'gameId': game.game_id})


def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Authorization header must start with Bearer")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

@app.get('/riddles')
async def show_all_riddle(request: Request):
    token = get_token_from_header(request)
    await authenticate(token)
    riddles = riddleService.get_all_riddle()
    all_riddles = [{'riddleId' : riddle.riddle_id, 'riddleTitle': riddle.title} for riddle in riddles]
    return JSONResponse(content=all_riddles)

@app.post('/newgame')
async def create_game(request: Request):
    try:
        body = await request.json()
        riddle_id = body.get("riddleId")
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)
        game_id = gameService.create_game(user.user_id, riddle_id)
        # user id - game_id 관계 설정
        ugService.create_user_game(user.user_id, game_id)
        return JSONResponse(content={'newGameId': game_id})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)


@app.get('/gameinfo')
async def access_game(request: Request, gameid: str = Query(...)):
    try:
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)

        gameService.reaccess(gameid)
        game = gameService.get_game(gameid)
        riddle = riddleService.get_riddle(game.riddle_id)
        game_queries = gqService.get_queries(gameid)
        game_info = [{'gameTitle': game.title, 'problem': riddle.problem}]
        for game_query in game_queries:
            query = queryService.get_query(game_query.query_id)
            game_info.append({
                'queryId': query.query_id,
                'query': query.query,
                'response': query.response
                })
        return JSONResponse(content=game_info)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)
