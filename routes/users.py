from fastapi import APIRouter, Depends, HTTPException, status
from auth.jwt import create_access_token
from database.connection import get_session
from app.Init import User

user_router = APIRouter(
	tags=["User"],
)

# Response를 TokenResponse 모델로 지정
@user_router.post("/login", response_model=TokenResponse)
async def login(body: User, session=Depends(get_session)) -> dict:
	# 로그인 유저가 DB에 있는지 검사한뒤
	existing_user = session.get(User , body.email)
	try:
	    # 있다면 토큰을 발행하고 리턴
		if existing_user:
			access_token = create_access_token(body.email, body.exp)
		else:
        # 없다면 DB에 저장하고 리턴
			session.add(body)
			session.commit()
			session.refresh(body)
			access_token = create_access_token(body.email, body.exp)
		return {
				"access_token": access_token,
				"token_type": "Bearer"
			}
	except:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Bad Parameter",
		)
