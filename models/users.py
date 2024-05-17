from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
	email: EmailStr = Field(primary_key=True)
	username: str
	exp: int

class TokenResponse(BaseModel):
	access_token: str
	token_type: str
