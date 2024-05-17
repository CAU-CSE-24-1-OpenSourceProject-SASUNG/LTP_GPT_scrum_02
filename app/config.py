import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get('CLIENT_ID', None)
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', None)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
SECRET_KEY = os.getenv("SECRET_KEY", None)
