import sqlalchemy
import sys, os
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from core.config import settings

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:gusdn4818@localhost/ossp'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
