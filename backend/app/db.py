# app/db.py
import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Глобальные ссылки (ленивая инициализация)
_engine = None
_SessionLocal = None


def _normalize_url() -> str:
    """
    Берём URL из ENV (DATABASE_URL или BACKEND_DATABASE_URL),
    форсим драйвер psycopg2 для Postgres и sslmode=require.
    """
    url = os.getenv("DATABASE_URL") or os.getenv("BACKEND_DATABASE_URL")
    if not url:
        return "sqlite:////tmp/app.db"

    # могли сохранить с одинарными кавычками — уберём
    if url.startswith("'") and url.endswith("'"):
        url = url[1:-1]

    p = urlparse(url)
    if p.scheme.startswith("postgres"):
        # форсим psycopg2 (совместимо с AWS Lambda)
        p = p._replace(scheme="postgresql+psycopg2")
        q = dict(parse_qsl(p.query, keep_blank_values=True))
        q.pop("channel_binding", None)   # на всякий случай
        q.setdefault("sslmode", "require")
        url = urlunparse(p._replace(query=urlencode(q)))

    return url


def get_engine():
    """Ленивая сборка Engine, чтобы импорт не падал без драйвера в момент старта."""
    global _engine, _SessionLocal
    if _engine is None:
        url = _normalize_url()
        kwargs = {"pool_pre_ping": True}
        if url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        else:
            kwargs.update(pool_size=5, max_overflow=0)

        _engine = create_engine(url, **kwargs)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    return _engine


class Base(DeclarativeBase):
    pass


def get_db():
    """Зависимость для FastAPI роутов (если понадобится)."""
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
