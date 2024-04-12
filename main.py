from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Fetch client_id from environment variables
GOOGLE_CLIENT_ID = os.getenv("REACT_APP_GOOGLE_AUTH_CLIENT_ID")

class User(BaseModel):
    name: str

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/login/oauth2/code/google&scope=openid%20email%20profile",
    tokenUrl="https://oauth2.googleapis.com/token",
)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Welcome to Google OAuth2 Example with FastAPI"}

@app.get("/login")
async def login():
    return RedirectResponse(url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/login/oauth2/code/google&scope=openid%20email%20profile")

@app.get("/login/oauth2/code/google")
async def callback(code: str):
    # exchange the code for tokens
    # we are just printing the tokens here, but in a real application
    # you would save these tokens in a database
    print(f"Received code: {code}")
    return {"code": code}

@app.get("/profile", response_model=User)
async def profile(current_user: User = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
