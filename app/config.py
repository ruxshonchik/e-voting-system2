from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Production CORS — vergul bilan ajratilgan domainlar
    # Misol: "https://mydomain.com,https://www.mydomain.com"
    ALLOWED_ORIGINS: str = "*"

    # PostgreSQL alohida (docker-compose uchun)
    POSTGRES_DB: str = "evoting_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
