# app/db.py
from pathlib import Path

from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .settings import settings

# 1) Берём URL из настроек (по умолчанию — sqlite:///./data.db)
DATABASE_URL = settings.safe_database_url  # добавит sslmode=require для PG, если его нет

# 2) Определяем тип БД
parsed = urlparse(DATABASE_URL)
is_sqlite = parsed.scheme.startswith("sqlite")

# 3) Параметры движка
engine_kwargs = {
    "pool_pre_ping": True,  # чинит «висящие» коннекты
}

if is_sqlite:
    # Для SQLite (файл). Разрешаем многопоточность.
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Для Postgres/др. — небольшой пул без перелива
    engine_kwargs.update(pool_size=5, max_overflow=0)

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
