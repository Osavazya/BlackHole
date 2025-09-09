# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models  # чтобы таблицы точно были импортированы
from .routers.blackholes import router as blackholes_router
from .settings import settings

# 1) сначала создаём приложение
app = FastAPI(title="BlackHole API")

# 2) затем вешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) стартовые действия (миграция + сид)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        existing = conn.exec_driver_sql("SELECT COUNT(*) FROM blackholes").scalar()
        if existing == 0:
            conn.exec_driver_sql(
                """
                INSERT INTO blackholes (id, name, distance_ly, mass_solar, description) VALUES
                (1, 'Стрелец A*', 26000, 4.3e6, 'Сверхмассивная ЧД в центре Млечного Пути.'),
                (2, 'M87*', 53000000, 6.5e9, 'Первая тень ЧД, снятая EHT (2019).');
                """
            )

# 4) простые сервисные эндпоинты
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

# 5) роутеры домена
app.include_router(blackholes_router)
