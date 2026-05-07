from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Online Judge"
    debug: bool = False
    secret_key: str = "dev-secret-change-in-production"

    database_url: str = "postgresql+asyncpg://judge:judge_pass@localhost:5432/online_judge"

    redis_host: str = "localhost"
    redis_port: int = 6379

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    max_code_length: int = 65536
    max_output_length: int = 1_048_576
    concurrent_judge_jobs: int = 2
    cors_origins_raw: str = (
        "http://localhost:8000,"
        "http://127.0.0.1:8000,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


settings = Settings()
