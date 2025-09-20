from typing import List, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

class Settings(BaseSettings):
    # --- базовые ---
    env: str = "dev"  # dev | prod
    secret_key: Optional[str] = None

    # --- БД ---
    database_url: str = "sqlite:///./data.db"

    # --- CORS ---
    allowed_origins_raw: Optional[str] = None  # CSV
    allowed_origin_regex: Optional[str] = None 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="BACKEND_",
    )

    
    @property
    def allowed_origins(self) -> List[str]:
        items = _split_csv(self.allowed_origins_raw)
        if items:
            return items
        # дефолты, если env не задан
        return [
            "http://localhost:5173",
            "http://localhost:8000",
            "https://app.blackhole.bond",
        ]

    
    @property
    def effective_secret_key(self) -> str:
        if self.env == "prod":
            if not self.secret_key:
                raise ValueError("BACKEND_SECRET_KEY is required in prod")
            return self.secret_key
        # dev — мягко генерим
        return self.secret_key or secrets.token_urlsafe(32)

   
    @property
    def safe_database_url(self) -> str:
        url = self.database_url
        parsed = urlparse(url)
        if parsed.scheme.startswith("postgres"):
            qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
            if "sslmode" not in qs:
                qs["sslmode"] = "require"
                new_qs = urlencode(qs)
                url = urlunparse(parsed._replace(query=new_qs))
        return url

settings = Settings()
