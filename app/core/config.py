class Settings:
    DB_USERNAME = "root"
    DB_PASSWORD = "gusdn4818"
    DB_HOST = "localhost"
    DB_DATABASE = "ossp"

    DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"


settings = Settings()
