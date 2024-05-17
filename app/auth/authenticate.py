from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

# 토큰을 인수로 받아 유효한 토큰인지 검사한 뒤 payload의 사용자 필드를 리턴함
async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        print("error token")
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sign in for access"
                )

    decode_token = verify_access_token(token)
    return decode_token["user"]
