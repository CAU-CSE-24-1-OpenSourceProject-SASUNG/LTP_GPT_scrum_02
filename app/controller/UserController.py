from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.auth.authenticate import authenticate
from app.auth.jwt import *
from app.domain.dto.UserDto import UserDto
from app.service.UserService import UserService
from app.util.util import *


def get_user_router(userService: UserService):
    router = APIRouter()

    # 로그인
    @router.post("/login")
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

    @router.get("/info")
    async def info(request: Request):
        try:
            token = get_token_from_header(request)
            user_email = await authenticate(token)
            user = userService.get_user_email(user_email)

            return JSONResponse(content={"riddleTicket": user.riddle_ticket, "gameTicket": user.game_ticket})
        except Exception as e:
            print(e)
            return JSONResponse(content={"error": str(e)}, status_code=404)

    return router
