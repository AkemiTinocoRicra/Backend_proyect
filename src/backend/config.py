from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:8080"

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_name: str = "Booki"

    jwt_secret_key: str = "change-me-to-a-long-random-secret-32-bytes-min"
    jwt_expire_min: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
