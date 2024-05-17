import datetime
import secrets

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

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
from .service.UserGameService import UserGameService
from .service.UserService import UserService

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        # 'redirect_url' : 'https://seaturtle.newpotatoes.org/auth'
        'redirect_url': 'http://localhost:8000/auth'
    }
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

# DB 모든 데이터 삭제
with engine.connect() as conn:
    table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries', 'ranking']
    # table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'feedbacks', 'queries']
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))  # 외래 키 제약 조건을 잠시 해제
    for table_name in table_names:
        delete_query = text('TRUNCATE TABLE {};'.format(table_name))
        conn.execute(delete_query)
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))  # 외래 키 제약 조건을 다시 활성화

riddleService.create_riddle('Umbrella', '아이는 10층에 산다',
                            '어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?',
                            0)


@app.get("/")
def index(request: Request):
    request.session.clear()
    user = request.session.get('user')
    if user:
        return RedirectResponse('quiz')

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )


@app.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe()
    request.session['state'] = state
    # print(f"Saved state: {request.session['state']}")  # 디버깅용 로그
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url, state=state)


@app.get('/auth')
async def auth(request: Request):
    try:
        state = request.query_params.get('state')
        expected_state = request.session.pop('state', None)
        if not state or state != expected_state:
            raise HTTPException(status_code=400, detail="State mismatch error")

        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)

        # 로그인 성공
        email = user.get('email')
        name = user.get('name')
        user = userService.get_user_email(email)
        if user is None:
            user_id = userService.create_user(email, name)
            request.session['user_id'] = user_id
        else:
            request.session['user_id'] = user.user_id

        return RedirectResponse('quiz')
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )


@app.get("/quiz", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get('user')
    user_id = request.session.get('user_id')
    if not user_id:
        # user_id가 세션에 없는 경우 로그인 페이지로 리다이렉트
        return RedirectResponse('/login')

    # Game 생성
    game_start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    riddle_id = riddleService.get_riddle_by_name('Umbrella').riddle_id
    game_id = gameService.create_game(user_id, riddle_id)
    ugService.create_user_game(user_id, game_id)

    request.session['game_start_time'] = game_start_time_str
    request.session['riddle_id'] = riddle_id
    request.session['game_id'] = game_id

    if not user:
        return RedirectResponse('/')
    problem = "어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?"
    return templates.TemplateResponse(
        name='index.html',
        context={'request': request, 'problem': problem, 'user': user}
    )


@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        question = body.get("question")
        user_id = request.session.get('user_id')
        game_id = request.session.get('game_id')
        riddle_id = request.session.get('riddle_id')

        response = queryService.get_response(question, riddle_id)  # 메모이제이션
        if not response:
            response = ltp_gpt.evaluate_question(question)
        query_id = queryService.create_query(question, response)
        gqService.create_game_query(game_id, query_id)

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
    user_id = request.session.get('user_id')
    games = ugService.get_recent_games(user_id)
    recent_games = [{'gameId': game.game_id, 'gameTitle': game.title} for game in games]
    return JSONResponse(content=recent_games)


@app.get('/recentgame')
async def access(request: Request):
    user_id = request.session.get('user_id')
    game = ugService.get_recent_game(user_id)
    gameService.reaccess(game.game_id)
    return JSONResponse(content={'gameId': game.game_id})


@app.get('/riddles')
async def show_all_riddle():
    riddles = riddleService.get_all_riddle()
    all_riddles = [{'riddleId': riddle.riddle_id, 'riddleTitle': riddle.title} for riddle in riddles]
    return JSONResponse(content=all_riddles)


@app.post('/newgame')
async def create_game(request: Request, riddleid: int = Query(...)):
    try:
        user_id = request.session.get('user_id')
        game_id = gameService.create_game(user_id, riddleid)
        return JSONResponse(content={'newGameId': game_id})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=404)


@app.get('/gameinfo')
async def access_game(gameid: int = Query(...)):
    try:
        gameService.reaccess(gameid)

        game = gameService.get_game(gameid)
        riddle = riddleService.get_riddle(game.riddle_id)
        game_queries = gqService.get_queries(gameid)

        game_info = [
            {'gameTitle': game.title, 'problem': riddle.problem, 'progress': game.progress}
        ]
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


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
