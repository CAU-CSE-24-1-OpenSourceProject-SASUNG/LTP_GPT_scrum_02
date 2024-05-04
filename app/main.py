import uuid

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

# DB 모든 데이터 삭제
with engine.connect() as conn:
    table_names = ['user_games', 'total_feedbacks', 'users', 'game_queries', 'games', 'riddles', 'feedbacks', 'queries']
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))  # 외래 키 제약 조건을 잠시 해제
    for table_name in table_names:
        delete_query = text('TRUNCATE TABLE {};'.format(table_name))
        conn.execute(delete_query)
    conn.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))  # 외래 키 제약 조건을 다시 활성화

# 게임의 종류를 선택
riddleService.create_riddle('Umbrella', 0)


@app.get("/")
def index(request: Request):
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
        user = userService.get_user(email)
        if user is None:
            userService.create_user(email)
        request.session['user_id'] = email
        # user_id = str(uuid.uuid4())

        return RedirectResponse('quiz')
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )


@app.get("/quiz", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get('user')
    # Game 생성
    user_id = request.session.get('user_id')  # 세션에서 user_id 가져오기
    if not user_id:
        # user_id가 세션에 없는 경우 로그인 페이지로 리다이렉트
        return RedirectResponse('/login')

    game_id = str(uuid.uuid4())
    gameService.create_game(user_id, game_id, 'Umbrella', 0, 0, 0, False)
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
        response = ltp_gpt.evaluate_question(question)

        game_id = request.session.get('game_id')  # 세션에서 game_id 가져오기
        query_id = str(uuid.uuid4())
        queryService.create_query(game_id, query_id, question, response, False)

        return JSONResponse(content={"response": response})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
