from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from .config import CLIENT_ID, CLIENT_SECRET
from fastapi.staticfiles import StaticFiles
import app.ltp_gpt

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="zcxvopuvczuipo")
app.mount("/static", StaticFiles(directory = "static"), name = "static")

oauth = OAuth()
oauth.register(
        name = 'google',
        server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration',
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        client_kwargs={
            'scope': 'email openid profile',
            'redirect_url' : 'http://localhost:8000/auth'
            }
        )

templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        #return RedirectResponse('welcome')
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
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
                name='error.html',
                context={'request': request, 'error': e.error}
                )
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    #return RedirectResponse('welcome')
    return RedirectResponse('quiz')


@app.get("/quiz", response_class=HTMLResponse)
async def home(request: Request):
    problem = "어떤 아이가 아파트 10층에 살고 있으며, 맑은 날에는 엘리베이터에서 6층에서 내려서 10층까지 걸어 올라간다. 그러나 날씨가 좋지 않다면 10층에서 내려서 집으로 간다. 어떤 상황일까?"
    return templates.TemplateResponse("index.html", {"request": request, "problem": problem})

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        question = body.get("question")
        response = ltp_gpt.evaluate_question(question)
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    request.session.clear()
    return RedirectResponse('/')
