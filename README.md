# BlackHole — Full‑stack MVP (FastAPI + React)

## Quick start (Docker)
```bash
docker compose build
docker compose up -d
```
Open: Frontend http://localhost:8080, Swagger http://localhost:8000/docs

## Local backend (without Docker)
```bash
cd backend
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Local frontend
```bash
cd frontend
npm i
npm run dev
```
It uses VITE_API_URL (defaults to http://localhost:8000).

Notes:
- DB: SQLite file `backend/data.db` (mounted as a volume in Docker).
- On startup, API creates tables and seeds 2 records.
- Endpoints: `/health`, `/version`, `/api/v1/blackholes` (GET/POST), `/api/v1/blackholes/{id}`.
