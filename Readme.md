# BlackHole

Serverless web app: React/Vite frontend on S3 + CloudFront and FastAPI backend on AWS Lambda behind API Gateway. PostgreSQL database on Neon. Automated deployments via GitHub Actions.

## Links

- App: https://app.blackhole.bond
- API: https://api.blackhole.bond

## Architecture

```
Browser (app.blackhole.bond)
        │
        ▼
CloudFront → S3 (static frontend)
        │
        └── API requests ──► API Gateway (api.blackhole.bond)
                               │
                               ▼
                           AWS Lambda (FastAPI + Mangum)
                               │
                               ▼
                           Neon Postgres (TLS, sslmode=require)
```

**Why this design**
- No servers to maintain; low cost at low/medium traffic.
- Automatic scaling via Lambda.
- Static hosting + global CDN with CloudFront.
- Managed Postgres (Neon) with branches/environments and TLS by default.

## Tech Stack

- **Frontend:** React, Vite, TypeScript (optional), deployed to **S3 + CloudFront**
- **Backend:** **FastAPI** packaged for **AWS Lambda** (via Mangum), exposed through **API Gateway (HTTP API, payload v2)**
- **Database:** **Neon Postgres**
- **CI/CD:** **GitHub Actions** (frontend & backend workflows)
- **Region:** `eu-south-2` (Madrid)
- **Domains & TLS:** ACM certificates in the same region; custom domains `app.blackhole.bond` and `api.blackhole.bond`

## Requirements

- Node.js 18+
- Python 3.11+
- AWS account with IAM permissions to update Lambda, API Gateway, S3, CloudFront, ACM
- Neon Postgres database (free tier is fine)
- GitHub repository with Actions enabled

## Local Development

### Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000
```

Create `.env` (local):
```
DATABASE_URL=postgresql+psycopg://user:pass@host/dbname?sslmode=require
CORS_ALLOWED_ORIGINS=https://app.blackhole.bond,http://localhost:5173
STAGE=dev
```

Health check:
```bash
curl -i http://localhost:8000/health
```

**Notes for Lambda compatibility**
- Keep DB connections short-lived; enable SQLAlchemy `pool_pre_ping=True` to avoid stale connections.
- File system is ephemeral; persist data in the DB or S3.
- Expect a small cold-start delay on the first request after idle.

### Frontend (Vite)

```bash
npm install
npm run dev    # usually http://localhost:5173
```

Create `.env` (frontend):
```
VITE_API_BASE=https://api.blackhole.bond
```

## Deployment

### Frontend (S3 + CloudFront)

- Build: `npm run build`
- Upload the `dist/` artifacts to S3 bucket
- Invalidate CloudFront distribution to publish the new version
- Cache best practices: long max-age for hashed assets, short for HTML

### Backend (Lambda + API Gateway)

- Package FastAPI with dependencies for Lambda (zip or Lambda layer)
- Update Lambda function code
- HTTP API in API Gateway with route `ANY /{proxy+}` (payload format 2.0)
- **CORS:** disabled in API Gateway; CORS headers are returned by the app (middleware)

Environment variables (Lambda):
```
DATABASE_URL=postgresql+psycopg://...sslmode=require
CORS_ALLOWED_ORIGINS=https://app.blackhole.bond
STAGE=prod
```

### Custom Domains & TLS

- Request a public certificate in **ACM** in `eu-south-2`
- Validate via DNS (CNAMEs)
- Attach to API Gateway custom domain: `api.blackhole.bond`
- Point DNS (A/AAAA/ALIAS) to API Gateway domain name
- Frontend domain `app.blackhole.bond` points to CloudFront

## CI/CD (GitHub Actions)

Recommended setup:
- **backend.yml** — build package/layer, update Lambda code; assume AWS role via GitHub **OIDC** (no long-lived keys)
- **frontend.yml** — build and upload to S3, then CloudFront invalidation
- Branch strategy: `main` → production, `dev` → staging (optional separate stacks)

Secrets / variables to configure in GitHub:
- `AWS_ROLE_TO_ASSUME` (for OIDC), `AWS_REGION=eu-south-2`
- `S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`
- `NEON_DATABASE_URL` (or use AWS Secrets Manager and fetch at deploy/runtime)

## API (Draft)

- `GET /health` — liveness check
- `GET /blackholes` — list items
- `GET /blackholes/{id}` — item details
- `POST /auth/signup` — user registration (passwords are stored **only as hashes**)
- `POST /auth/login` — login, return JWT
- `GET /me` — current user profile (JWT required)

**Auth & Passwords**
- Use `bcrypt` or `argon2` for hashing (never store plain text)
- Issue short-lived access tokens (JWT) + optional refresh tokens
- Store only necessary claims in JWT

## Observability

- **CloudWatch Logs** for Lambda (review tracebacks and performance)
- **CloudWatch Metrics/Alarms**: 5xx errors, duration, throttles, cold starts
- (Optional) **AWS X-Ray** for distributed tracing
- (Optional) Structured logging (JSON) for easier parsing

## Security

- CORS: allow only trusted origins (e.g., `https://app.blackhole.bond`)
- Rate limiting / throttling at API Gateway
- Store secrets in **AWS Secrets Manager** or Lambda env vars (encrypted)
- Use IAM roles with least privilege
- Enforce TLS: `sslmode=require` for Postgres

## Common Pitfalls

- **CORS blocked:** ensure backend returns `Access-Control-Allow-Origin` with the exact frontend origin; keep CORS disabled in API Gateway if the app handles it.
- **502/500:** check CloudWatch Logs for stack traces.
- **DB connection errors:** include `sslmode=require`; enable `pool_pre_ping=True`.
- **Slow first request:** likely Lambda cold start; subsequent calls are faster.

## Roadmap

- Auth flows (signup/login), roles/permissions
- API versioning & OpenAPI docs
- E2E tests (Playwright/Cypress)
- Infrastructure as Code (Terraform) for full reproducibility
- Staging environment with separate Neon branch
- Caching & performance tuning

---

**Status:** production-ready baseline with room for iteration.
