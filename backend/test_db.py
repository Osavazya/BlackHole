from sqlalchemy import create_engine, text
from app.settings import settings

print("URL =", settings.safe_database_url)
engine = create_engine(settings.safe_database_url, pool_pre_ping=True)

with engine.begin() as conn:
    print("SELECT 1 ->", conn.execute(text("SELECT 1")).scalar())
