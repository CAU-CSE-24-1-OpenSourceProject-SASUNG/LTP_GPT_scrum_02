from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import EmailStr
from database.connection import Settings

# Settings 클래스를 인스턴스화 해서 .env 값을 가져온다.
settings = Settings()

# 토큰을 생성하는 함수
def create_access_token(user: EmailStr, exp: int):
	# 토큰을 생성할 때 user 이메일과 exp(만료시간)을 받아온다
	# 받아온 정보를 기반으로 payload를 작성한다. 필요한 정보만큼 저장하면 된다.
	payload = {
		"user": user,
		"expires": exp
	}
	# 작성된 payload와 secrets키, 암호화 알고리즘을 지정해준다.
	token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
	# 만들어진 토큰을 리턴한다.
	return token

# 토큰을 검증하는 함수
def verify_access_token(token: str):
	try:
	    # 토큰을 decode한 값을 data에 저장한다.
        # 이 단계에서 decode되지 않으면 당연히 검증된 토큰이 아니다.
		data = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        # 여기서부터 인증된 사용자의 토큰이 만료되었는지 체크한다.
		expires = data.get("expires")
		if expires is None:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="No access token supplied"
			)
		if datetime.utcnow() > datetime.utcfromtimestamp(expires):
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Token expired!"
			)
        # 정상 토큰이라면 사용자 데이터를 리턴한다.
		return data
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid token"
		)
