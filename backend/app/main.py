from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from . import models
from .routers.blackholes import router as blackholes_router

app = FastAPI(title="BlackHole API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",  # Vite dev
        "http://localhost:8080", "http://127.0.0.1:8080"   # nginx build
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"status": "ok", "message": "pong"}


app.include_router(blackholes_router)
