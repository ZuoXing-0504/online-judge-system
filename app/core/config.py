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

    max_code_length: int = 65536
    max_output_length: int = 1_048_576
    concurrent_judge_jobs: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
