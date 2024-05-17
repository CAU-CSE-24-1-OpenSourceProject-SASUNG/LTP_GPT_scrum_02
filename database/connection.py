from typing import Optional
from pydantic import BaseSettings
from sqlmodel import SQLModel, create_engine, Session

# 데이터 베이스 파일 이름 지정
database_file = 'test.db' 
# DB 연결, MySQL의 경우 mysql://user:password@localhost/mydatabase 형식을 맞춰주면 된다.
database_connection_string = "mysql://root:seaturtle@localhost/login"
connect_args={"check_same_thread": False}
engine_url = create_engine(database_connection_string, echo=True)

# Setting config load
class Settings(BaseSettings):
	SECRET_KEY: Optional[str] = None
	DATABASE_URL: Optional[str] = None
	class Config:
		env_file = ".env"

# 데이터베이스 테이블 생성하는 함수
def conn():
	SQLModel.metadata.create_all(engine_url)

# Session 사용 후 자동으로 종료
def get_session():
	with Session(engine_url) as session:
		yield session
