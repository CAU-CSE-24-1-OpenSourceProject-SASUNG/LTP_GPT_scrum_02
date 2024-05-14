import datetime

from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError

from .Init import session, engine
from .Service.FeedbackService import FeedbackService
from .Service.GameService import GameService
from .Service.QueryService import QueryService
from .Service.RiddleService import RiddleService
from .Service.TotalFeedbackService import TotalFeedbackService
from .Service.UserService import UserService
from .Service.RankingService import RankingService
from .Service.UserGameService import UserGameService
from .Service.GameQueryService import GameQueryService

from sqlalchemy import text

from .config import CLIENT_ID, CLIENT_SECRET, SECRET_KEY
from fastapi.staticfiles import StaticFiles
import app.ltp_gpt as ltp_gpt
import secrets

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
                game_end_time = datetime.datetime.now()
                game_start_time_str = request.session.get('game_start_time')
                if game_start_time_str:
                    game_start_time = datetime.datetime.strptime(game_start_time_str, "%Y-%m-%d %H:%M:%S")
                    play_time = game_end_time - game_start_time
                    gameService.end_game(game_id, play_time, False, True)  # Game tuple 데이터 업데이트
                    game = gameService.get_game(game_id)
                    if game:
                        rankingService.update_ranking(game)  # 랭킹 업데이트
                    userService.level_up(user_id)
            # 정답이 아니라 game을 중간에 나갔다면.. controller 다른 곳에 작성

        return JSONResponse(content={"response": response})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
