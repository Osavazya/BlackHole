from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text

from .db import Base, engine
from . import models  # важно, чтобы таблицы были зарегистрированы
from .routers.blackholes import router as blackholes_router
from .settings import settings


# --- CORS ---
ALLOWED_ORIGINS = settings.allowed_origins or [
    "http://localhost:5173",
    "http://localhost:8000",
    "https://app.blackhole.bond",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        # если таблица пустая — засеять начальными данными
        count = conn.exec_driver_sql("SELECT COUNT(*) FROM blackholes").scalar()
        if count == 0:
            # Для SQLite/PG подойдёт такой безопасный сид
            conn.execute(text("""
                INSERT INTO blackholes (id, name, distance_ly, mass_solar, description)
                VALUES
                  (1, 'Стрелец A*', 26000, 4.3e6, 'Сверхмассивная ЧД в центре Млечного Пути.'),
                  (2, 'M87*', 53000000, 6.5e9, 'Первая тень ЧД, снятая EHT (2019).')
                ON CONFLICT (id) DO NOTHING
            """))
    yield
    # --- shutdown --- (пока ничего)


app = FastAPI(title="BlackHole API", lifespan=lifespan)

# CORS — лучше без "*", сузим методы и заголовки
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # если нужны все поддомены *.blackhole.bond — используй:
    # allow_origin_regex=r"^https://([a-z0-9-]+\.)?blackhole\.bond$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# --- сервисные эндпоинты ---
@app.get("/")
def root():
    return {"message": "Добро пожаловать в проект BlackHole 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "0.1.0"}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong", "env": settings.env}

# --- доменные роутеры ---
app.include_router(blackholes_router)
