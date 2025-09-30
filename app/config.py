from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Prefer full SQLAlchemy-style URL
    database_url: Optional[str] = None
    # legacy connection string format: server=...;port=...;database=...;user=...;password=...
    connection_string: Optional[str] = None

    # JWT
    # read from ENV var SECRET_KEY (from .env)
    secret_key: str = Field("supersecret", env="SECRET_KEY")
    jwt_issuer: str = "qlnv-api"
    jwt_audience: str = "qlnv-client"
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

    
    # SMTP
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    smtp_from: Optional[str] = None
    smtp_enable_ssl: Optional[bool] = None

    debug: bool = True

    class Config:
        env_file = ".env"

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if self.connection_string:
            parts = dict(p.split('=') for p in self.connection_string.split(';') if p)
            host = parts.get('server') or parts.get('host') or 'localhost'
            port = parts.get('port') or '3306'
            db = parts.get('database') or parts.get('dbname') or ''
            user = parts.get('user') or parts.get('uid') or ''
            password = parts.get('password') or parts.get('pwd') or ''
            if user:
                return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}"

        return "sqlite+aiosqlite:///./test.db"


settings = Settings()
