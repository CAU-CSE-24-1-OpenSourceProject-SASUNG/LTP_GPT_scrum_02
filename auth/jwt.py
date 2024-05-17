from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.config import SECRET_KEY

#TODO
def create_access_token(user: str, exp: int):
	payload = {
		"user": user,
		"expires": exp
	}
	token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
	return token

# 토큰을 검증하는 함수
def verify_access_token(token: str):
	try:
		data = jwt.decode(token, SECRET_KEY, algorithms="HS256")
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
		return data
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid token"
		)
