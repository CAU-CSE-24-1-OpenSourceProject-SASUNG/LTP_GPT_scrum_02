#######################
# google.routes.py

from app.configs import Configs
from httpx_oauth.clients.google import GoogleOAuth2

from .libs import fastapi_users, auth_backend   # 이메일 연동할 때 쓰던 변수

google_oauth_client = GoogleOAuth2(
    client_id=Configs.GOOGLE_CLIENT_ID,
    client_secret=Configs.GOOGLE_CLIENT_SECRET,
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile", # 구글 클라우드에서 설정한 scope
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
)

google_oauth_router = fastapi_users.get_oauth_router(
    oauth_client=google_oauth_client,
    backend=auth_backend,
    state_secret=Configs.SECRET_KEY,
    redirect_url="http://localhost:3000/login/google",  # 구글 로그인 이후 돌아갈 URL
    associate_by_email=True,
)

#######################
# main.py

app = FastAPI()
app.include_router(google_oauth_router, prefix="/auth/google", tags=["auth"])