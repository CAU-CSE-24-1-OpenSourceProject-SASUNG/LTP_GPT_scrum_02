from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.config import SECRET_KEY

def create_access_token(user: str):
    #future_time = datetime.utcnow() + timedelta(seconds=60)
    future_time = datetime.utcnow() + timedelta(days=1)
    expires = int((future_time - datetime(1970, 1, 1)).total_seconds())
    payload = {
            "user": user,
            "expires": expires
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
