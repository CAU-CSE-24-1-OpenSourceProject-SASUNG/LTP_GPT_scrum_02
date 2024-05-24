from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.auth.jwt import *
from app.dto.UserDto import UserDto
from app.service.UserService import UserService


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

    return router
