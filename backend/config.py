import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_USER = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "rifa_online")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")
        if origin.strip()
    ]

    @classmethod
    def validate(cls):
        if len(cls.SECRET_KEY) < 32 or cls.SECRET_KEY.lower() in {"change-me", "secret", "rifa-secret-key"}:
            raise RuntimeError("Configure SECRET_KEY com pelo menos 32 caracteres aleatórios.")
        if not cls.MYSQL_USER or not cls.MYSQL_PASSWORD:
            raise RuntimeError("Configure MYSQL_USER e MYSQL_PASSWORD no ambiente.")
        if not cls.MYSQL_DATABASE:
            raise RuntimeError("Configure MYSQL_DATABASE no ambiente.")
