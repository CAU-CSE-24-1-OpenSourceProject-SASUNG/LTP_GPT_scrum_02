import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

import app.ltp_gpt as ltp_gpt
from .Init import session, engine
from .auth.authenticate import authenticate
# google login
from .auth.jwt import create_access_token
from .config import SECRET_KEY
from .dto.QueryInfoDto import QueryInfoDto
# Dto
from .dto.UserDto import UserDto
# service logic
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


## DB 모든 데이터 삭제
# with engine.connect() as conn:
#    table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries', 'ranking']
#    # table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries']
#    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))  # 외래 키 제약 조건을 잠시 해제
#    for table_name in table_names:
#        delete_query = text('TRUNCATE TABLE {};'.format(table_name))
#        conn.execute(delete_query)
#    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))  # 외래 키 제약 조건을 다시 활성화

# riddleService.create_riddle('Umbrella', '아이는 10층에 산다',
#                            '어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?',
#                            0)

# 로그인
@app.post("/user/login")
async def login(user: UserDto):
    # 로그인 유저가 DB에 있는지 검사한뒤
    existing_user = userService.get_user_email(user.email)
    try:
        # 있다면 토큰을 발행하고 리턴
        if existing_user:
            access_token = create_access_token(user.email)
        else:
            # 없다면 DB에 저장하고 리턴
            userService.create_user(user.email, user.name)
            access_token = create_access_token(user.email)

        return JSONResponse(content={"access_token": access_token, "token_type": "Bearer"})
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=400)


# 채팅(질문)
@app.post("/chat")
async def chat(request: Request, queryInfo: QueryInfoDto):
    try:
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user_id = userService.get_user_email(user_email)
        query = queryInfo.query
        game_id = queryInfo.game_id
        riddle_id = gameService.get_game(game_id).riddle_id
        riddle = riddleService.get_riddle(riddle_id)
        game = gameService.get_game(game_id)
        if game.query_ticket > 0:  # query 개수 제한
            # response = queryService.get_response(query, riddle_id)  # 메모이제이션
            #  if not response:
            #      response = ltp_gpt.evaluate_question(query)
            # 1차 프롬프팅
            response = ltp_gpt.evaluate_question(query, riddle)
            query_id = queryService.create_query(query, response)  # query 생성
            gqService.create_game_query(game_id, query_id)  # game_query 생성 : query ticket -= 1
            # 2차 프롬프팅
            if game.is_first is True:
                if '맞습니다' in response or '그렇다고 볼 수도 있습니다' in response or '정답과 유사합니다' in response or '정확한 정답을 맞추셨습니다' in response:
                    similarity = ltp_gpt.evaluate_similarity(query, riddle)
                    gameService.set_progress(game_id, similarity)  # game 진행도 업데이트
                correct_time = datetime.datetime.now() - datetime.datetime.strptime(request.session.get('game_start_time'), "%Y-%m-%d %H:%M:%S")
                gameService.correct_game(game_id, correct_time)
                game = gameService.get_game(game_id)
                rankingService.update_ranking(game)  # 랭킹 업데이트
                userService.level_up(user_id)  # 경험치 증가
                return JSONResponse(content={"response": response})
        else:
            return JSONResponse(content={'error': "Failed to create query"}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


# 사이드바에 최근 게임 목록
@app.get('/recentgames')
async def lookup(request: Request):
    token = get_token_from_header(request)
    user_email = await authenticate(token)
    user = userService.get_user_email(user_email)
    games = ugService.get_recent_games(user.user_id)
    recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
    return JSONResponse(content=recent_games)


# 가장 최근 게임 접속
@app.get('/recentgame')
async def access(request: Request):
    token = get_token_from_header(request)
    user_email = await authenticate(token)
    user = userService.get_user_email(user_email)
    game = ugService.get_recent_game(user.user_id)
    gameService.reaccess(game.game_id)
    return JSONResponse(content={'gameId': game.game_id})


# 모든 riddle 보여주기
@app.get('/riddles')
async def show_all_riddle(request: Request):
    token = get_token_from_header(request)
    await authenticate(token)
    riddles = riddleService.get_all_riddle()
    all_riddles = [{'riddleId': riddle.riddle_id, 'riddleTitle': riddle.title} for riddle in riddles]
    return JSONResponse(content=all_riddles)


# 새로운 게임 생성
@app.post('/newgame')
async def create_game(request: Request):
    try:
        body = await request.json()
        riddle_id = body.get("riddleId")
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)

        if userService.create_game(user.user_id) is True:
            game_id = gameService.create_game(user.user_id, riddle_id)  # game 생성
            ugService.create_user_game(user.user_id, game_id)  # user_game 생성
            return JSONResponse(content={'newGameId': game_id})
        else:
            return JSONResponse(content={'error': "Failed to create game"}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)


# 새로운 riddle 생성
@app.post('/newriddle')
async def create_riddle(request: Request):
    try:
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)
        body = await request.json()
        riddleTitle = body.get('riddleTitle')
        problem = body.get('problem')
        situation = body.get('situation')
        answer = body.get('answer')
        progress_sentences = body.get('progressSentences')
        exQueryResponse = body.get('exQueryResponse')

        if userService.create_riddle(user.user_id) is True:
            riddle_id = riddleService.create_riddle(user_email, riddleTitle, problem, situation, answer, progress_sentences)
            rpService.create_riddle_prompting(riddle_id, exQueryResponse)
            return JSONResponse(content={'error': "Failed to create riddle"}, status_code=400)
        else:
            return JSONResponse(content={'riddleId': "Riddle Token Error"})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)


# 게임 진행률 조회
@app.get('/gameprogress')
async def progress(request: Request):
    try:
        body = await request.json()
        game_id = body.get('gameId')
        game = gameService.get_game(game_id)
        return JSONResponse(content={'progress': game.progress})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)


# 게임 접속하기
@app.get('/gameinfo')
async def access_game(request: Request, gameId: str = Query(...)):
    try:
        token = get_token_from_header(request)
        user_email = await authenticate(token)
        user = userService.get_user_email(user_email)
        game = gameService.get_game(gameId)
        riddle = riddleService.get_riddle(game.riddle_id)
        game_queries = gqService.get_queries(gameId)
        gameService.reaccess(gameId)  # 재접속
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
