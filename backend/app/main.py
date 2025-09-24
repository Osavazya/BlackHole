# app/main.py
from contextlib import asynccontextmanager
from datetime import datetime
from importlib.util import find_spec

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .db import Base, get_engine                 # 👈 только так
from .routers.blackholes import router as blackholes_router
from .settings import settings

ALLOWED_ORIGINS = settings.allowed_origins or [
    "https://app.blackhole.bond",
    "http://localhost:5173",
    "http://localhost:8000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            count = conn.exec_driver_sql("SELECT COUNT(*) FROM blackholes").scalar()
            if count == 0:
                conn.execute(text("""
                    INSERT INTO blackholes (id, name, distance_ly, mass_solar, description)
                    VALUES
                      (1, 'Стрелец A*', 26000, 4.3e6, 'Сверхмассивная ЧД в центре Млечного Пути.'),
                      (2, 'M87*', 53000000, 6.5e9, 'Первая тень ЧД, снятая EHT (2019).')
                    ON CONFLICT (id) DO NOTHING
                """))
    except Exception:
        pass
    yield

app = FastAPI(title="BlackHole API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","Accept","X-Requested-With"],
)

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
def ping(request: Request):
    return JSONResponse(
        {"ok": True, "ts": datetime.utcnow().isoformat() + "Z"},
        headers={"X-Debug-Handler": "fastapi"},
    )

# Диагностика БД
@app.get("/db-ping")
def db_ping():
    engine = get_engine()
    driver = "psycopg2" if find_spec("psycopg2") else ("psycopg" if find_spec("psycopg") else "none")
    try:
        with engine.connect() as conn:
            one = conn.execute(text("SELECT 1")).scalar_one()
        return {"db": "ok", "select1": one, "driver": driver}
    except Exception as e:
        return JSONResponse({"db": "error", "driver": driver, "error": str(e)}, status_code=500)

app.include_router(blackholes_router)
