# BlackHole — Full‑stack MVP (FastAPI + React)

**Production‑style portfolio project.** Frontend is React/Vite, backend is FastAPI. Production hosting is cost‑efficient, serverless: **S3 + CloudFront** for static frontend, **API Gateway + Lambda** for the API, **DynamoDB** for persistence, **SSM Parameter Store** for secrets. Domain: `app.blackhole.bond`.

> Why serverless? Near‑zero monthly cost when idle. The classic ECS + ALB + RDS option is also sketched below for interviews.

---

## Repository layout

```
.
├─ backend/            # FastAPI
├─ frontend/           # React + Vite
├─ docker-compose.yml  # Dev: run both locally
├─ .env.example        # env template (never commit real .env)
└─ README.md
```

---

## Quick start (local)

### A) Docker Compose (recommended for dev)
1. Copy env templates:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
2. Run:
   ```bash
   docker compose up -d --build
   ```
3. Open:
   - Frontend: http://localhost:8080
   - Backend Swagger: http://localhost:8000/docs

> If you keep a local-only override file, run: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`.

### B) NPM + Uvicorn (no Docker)
Frontend:
```bash
cd frontend
npm ci
VITE_API_URL=/api npm run dev
```
Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Production architecture (serverless)

```
User ─▶ CloudFront (TLS) ─┬─▶ Origin #1: S3 (static frontend)
                          └─▶ Origin #2: API Gateway (HTTP API) ─▶ Lambda (FastAPI via Mangum)

Secrets: SSM Parameter Store (SecureString)
Storage: DynamoDB (on‑demand / free tier)
Logs: CloudWatch Logs
DNS: Cloudflare (or your DNS provider)
```

**Why this design**
- **S3 + CloudFront**: fast global CDN, HTTPS, pennies per month.
- **API Gateway + Lambda**: pay per request, no idle cost.
- **DynamoDB**: generous always‑free tier for small apps.
- **SSM**: free secret storage (standard tier).

---

## Environment variables

### Backend (FastAPI)
| Name | Purpose | Example |
|---|---|---|
| `ENV` | runtime mode | `dev` / `prod` |
| `SECRET_KEY` | app secret | long random string |
| `ALLOWED_ORIGINS_RAW` | CORS allowlist | `https://app.blackhole.bond` |
| `DB_URL` *(if used)* | DB connection string | `dynamodb://` or `postgresql+psycopg2://...` |

In production these values live in **SSM Parameter Store**: `/blackhole/SECRET_KEY`, `/blackhole/ALLOWED_ORIGINS_RAW`, `/blackhole/DB_URL`.

### Frontend (Vite)
| Name | Purpose | Example |
|---|---|---|
| `VITE_API_URL` | base API URL (baked at build time) | `/api`

> For production **build the frontend with `VITE_API_URL=/api`** so all requests go via CloudFront → API Gateway.

---

## Build the frontend for production
```bash
cd frontend
npm ci
VITE_API_URL=/api npm run build
# output in frontend/dist/
```
Upload the **contents** of `dist/` to S3 (bucket root).

---

## Deployment (serverless, AWS Console)

### 1) Frontend: S3 + CloudFront + custom domain
1. **S3**: create bucket (e.g., `app.blackhole.bond`), *Block public access = ON*, SSE‑S3. Upload `dist/` contents.
2. **ACM (us‑east‑1)**: request public cert for `app.blackhole.bond` (DNS validation).
3. **DNS**: add the **CNAME** from ACM in your DNS (Cloudflare/Hostinger/Route 53) until the cert is **Issued**.
4. **CloudFront**: create distribution
   - Origin: S3 with **OAC** (click *Update bucket policy*)
   - Default root object: `index.html`
   - Behavior: Redirect HTTP→HTTPS, GET/HEAD, Compression ON
   - Alternate domain: `app.blackhole.bond`
   - SSL cert: the ACM certificate from us‑east‑1
5. **DNS**: add `CNAME app → dxxxx.cloudfront.net`.
6. **SPA routing** (if needed): CloudFront → *Error pages*: 403→200 `/index.html`, 404→200 `/index.html` (TTL 0).

### 2) Backend: API Gateway + Lambda
1. **Lambda**: package FastAPI for Lambda (see entrypoint below), runtime Python 3.11, env/SSM parameters.
2. **API Gateway (HTTP API)**: create API, integration **Lambda proxy**, route `ANY /{proxy+}`.
3. **CloudFront**: add a second behavior for the API:
   - Path pattern: `/api/*`
   - Origin: API Gateway endpoint
   - Allowed methods: `GET, HEAD, OPTIONS, POST, PUT, DELETE, PATCH`
   - Cache policy: **CachingDisabled**
4. **CORS**: backend uses `ALLOWED_ORIGINS_RAW=https://app.blackhole.bond`.

#### Lambda entrypoint (FastAPI + Mangum)
`backend/lambda_app.py`:
```python
from mangum import Mangum
from app.main import app  # your FastAPI app

handler = Mangum(app)
```
Build & upload example:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -t ./package
cp -r app package/
cd package && zip -r ../lambda.zip . && cd ..
# upload lambda.zip in AWS Lambda Console
```

---

## API endpoints (examples)
- `GET /api/health` → `{ "status": "ok" }`
- `GET /api/version` → `{ "version": "x.y.z" }`
- `GET /api/ping` → `{ "status": "ok", "message": "pong" }`

The UI has a **Ping API** button that calls the backend.

---

## Cost & operating modes
- **Live demo:** CloudFront active, Lambda/API GW active → you only pay for requests; S3 costs cents.
- **Hibernate:** nothing to stop in serverless — no hourly cost anyway.
- **Parked:** remove `app` CNAME if you don’t want it publicly reachable; infra stays in place.

> For interview purposes you can also discuss an ECS + ALB + RDS variant (see below) and the start/stop strategy.

---

## Alternative for interviews: ECS Fargate + ALB + RDS (short sketch)
- **VPC**: 2 public + 2 private subnets, IGW, (NAT optional to save cost), SGs: `alb-sg`, `ecs-sg`, `rds-sg`.
- **RDS PostgreSQL**: private subnets, SG `rds-sg` (ingress from `ecs-sg`).
- **SSM**: `/blackhole/SECRET_KEY`, `/blackhole/ALLOWED_ORIGINS_RAW`, `/blackhole/DATABASE_URL`.
- **ECS Fargate**: two services (frontend:80, backend:8000) in public subnets (AssignPublicIp=ENABLED), CloudWatch logs.
- **ALB + HTTPS**: :80→redirect→:443, :443 with ACM; rules: `/api*` → backend TG(8000), default → frontend TG(80).
- **DNS**: `app.blackhole.bond` → ALB (CNAME).

This stack is recognizable on interviews but costs ≈ $50+/mo if left running 24/7.

---

## CI/CD (sketches)

### Frontend → S3 + CloudFront (GitHub Actions)
```yaml
name: Deploy frontend to S3+CloudFront
on:
  workflow_dispatch:
  push:
    branches: [ main ]
    paths: [ 'frontend/**' ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 18 }
      - run: |
          cd frontend
          npm ci
          VITE_API_URL=/api npm run build
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::<ACCOUNT_ID>:role/gh-oidc-blackhole-deploy
          aws-region: eu-south-2
      - name: Sync to S3
        run: aws s3 sync frontend/dist s3://app.blackhole.bond/ --delete
      - name: Invalidate CloudFront cache
        run: aws cloudfront create-invalidation --distribution-id ${{ secrets.CF_DIST_ID }} --paths '/*'
```

### Backend → Lambda (idea)
Build `lambda.zip` in CI, upload to S3, and update Lambda with `aws lambda update-function-code`.

---

## Security
- **Never commit** real `.env` files; keep only `*.example` templates.
- Secrets live in **SSM Parameter Store (SecureString)**.
- CORS restricted to `https://app.blackhole.bond`.
- HTTPS everywhere (ACM + CloudFront).

---

## Tech stack
- **Frontend**: React, Vite
- **Backend**: FastAPI (Python 3.11), Uvicorn, Mangum
- **Infra (prod)**: S3, CloudFront, API Gateway (HTTP API), Lambda, DynamoDB, SSM, CloudWatch
- **Dev**: Docker Compose

---

## License
MIT (or update to your preferred license).

---

## Contact
- Author: Oleksii / BlackHole
- Demo: https://app.blackhole.bond (after CloudFront is configured)
