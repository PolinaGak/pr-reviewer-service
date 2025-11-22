from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
