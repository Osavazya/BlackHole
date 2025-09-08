from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

class Settings(BaseSettings):
    secret_key: str
    database_url: str = "sqlite:///./data.db"
    allowed_origins_raw: str | None = None
    env: str = "dev"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_origins(self) -> List[str]:
        return _split_csv(self.allowed_origins_raw)

settings = Settings()
