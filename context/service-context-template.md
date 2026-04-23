# Service Context — [service-name]

> **AI context file.** Drop this file in your service repo as `SERVICE_CONTEXT.md`. Claude reads it to give accurate, service-aware answers when you invoke slash commands from this repo.

---

## Identity

**Service name:** `[service-name]` *(must match ECS service name and ECR repo name)*
**Purpose:** [one sentence — what does this service do for the business?]
**Owner:** [team or person]
**Repo:** `github.com/[org]/[repo]`
**Slack channel:** `#[channel]`

---

## Runtime

**Language / Runtime:** [e.g., Python 3.12, Node.js 22, Go 1.23]
**Framework:** [e.g., FastAPI, Express, net/http]
**Entry point:** [e.g., `uvicorn app.main:app`, `node dist/server.js`]
**Port:** [e.g., 8000]
**Health check endpoint:** `GET /health` → `200 OK`

---

## Container

**ECR repo:** `[aws-account-id].dkr.ecr.[region].amazonaws.com/[service-name]`
**Base image:** [e.g., `python:3.12-slim-bookworm`]
**Image tag convention:** `[branch]-[git-sha-short]` (e.g., `main-a1b2c3d`)
**Non-root user:** yes / no *(should be yes — flag if no)*
**Read-only root filesystem:** yes / no

---

## ECS

**Cluster:** `[cluster-name]`
**Service name:** `[service-name]-[env]`
**Task definition family:** `[service-name]`

| Environment | CPU | Memory | Desired count | Min / Max (autoscaling) |
|---|---|---|---|---|
| dev | 256 | 512 | 1 | — |
| staging | 512 | 1024 | 1 | — |
| prod | 1024 | 2048 | 2 | 2 / 10 |

**Autoscaling policy:** target tracking, CPU utilization 60%
**Deployment type:** rolling update / blue-green *(delete whichever doesn't apply)*
**Task role ARN:** `arn:aws:iam::[account]:role/[service-name]-task-role`
**Execution role ARN:** `arn:aws:iam::[account]:role/[service-name]-execution-role`

---

## Networking

**VPC:** `[vpc-id or name]`
**Subnets:** private subnets only (tasks not directly internet-accessible)
**Security groups:**

| SG name | Inbound | Outbound |
|---|---|---|
| `[service-name]-ecs-sg` | 8000 from ALB SG | 443 to 0.0.0.0/0 (egress) |
| | 5432 to RDS SG | |

**ALB target group:** `[tg-name]` — `/health` check, 2 healthy / 3 unhealthy threshold

---

## Database

**Engine:** PostgreSQL [version]
**RDS identifier:** `[db-identifier]-[env]`
**Database name:** `[db_name]`
**Schema:** `[schema_name]` *(if not public)*
**Connection:** via `DB_SECRET_ARN` → Secrets Manager (never hardcoded credentials)
**Connection pool:** min [n] / max [n] (e.g., pgbouncer / SQLAlchemy pool)
**Migration tool:** [Alembic / Flyway / Liquibase / raw SQL]
**Migration run:** on container startup / manual / GHA step *(delete as appropriate)*

**Key tables:**

| Table | Rows (approx) | Notes |
|---|---|---|
| `tenants` | [n] | One row per tenant |
| `[table]` | [n] | [purpose] |

**Tenant isolation:** every tenant-scoped table has `tenant_id UUID NOT NULL` + index. Queries always filter by `tenant_id`.

---

## Secrets + Environment Variables

| Variable | Source | Description |
|---|---|---|
| `DB_SECRET_ARN` | ECS task definition | ARN of Secrets Manager secret containing DB creds |
| `JWT_SECRET_ARN` | ECS task definition | ARN of JWT signing key |
| `LOG_LEVEL` | ECS task definition | `INFO` in prod, `DEBUG` in dev |
| `ENVIRONMENT` | ECS task definition | `dev` / `staging` / `prod` |
| `[VAR]` | [source] | [description] |

**Never set as plaintext in task definition:** DB passwords, API keys, JWT secrets — always use `valueFrom` with Secrets Manager ARN.

---

## S3 Access

| Bucket | Access | Purpose |
|---|---|---|
| `[bucket-name]-[env]` | read/write | [e.g., user uploads] |
| `[bucket-name]` | read-only | [e.g., static assets] |

---

## External Dependencies

| Dependency | Type | Timeout | Circuit breaker? |
|---|---|---|---|
| [third-party API] | HTTP | 5s | yes / no |
| [internal service] | HTTP | 2s | yes / no |
| [SQS queue] | AWS SDK | — | n/a |

---

## API Surface

**Base path:** `/api/v[n]`
**Auth:** JWT bearer token / API key / IAM SigV4 *(delete as appropriate)*
**Docs:** `GET /docs` (Swagger) — disabled in prod / enabled in all envs

**Key endpoints:**

| Method | Path | Purpose | Auth required |
|---|---|---|---|
| GET | /health | Health check | No |
| GET | /api/v1/[resource] | [description] | Yes |
| POST | /api/v1/[resource] | [description] | Yes |

---

## Observability

**Grafana dashboard:** [URL or dashboard UID]
**CloudWatch log group:** `/ecs/[service-name]`
**Structured logging:** yes / no — JSON format with fields: `level`, `timestamp`, `request_id`, `tenant_id`, `message`

**Key metrics to watch:**

| Metric | Normal range | Alert threshold |
|---|---|---|
| p99 latency | < 200ms | > 400ms |
| Error rate (5xx) | < 0.1% | > 0.5% |
| ECS CPU utilization | < 50% | > 80% |
| ECS memory utilization | < 60% | > 85% |
| DB connections | < [n] | > [n * 0.8] |

---

## CI/CD

**GHA workflow:** `.github/workflows/[deploy.yml]`
**Trigger:** push to `main` → deploy to dev → promote to staging → manual approval → promote to prod
**Image build:** Docker buildx, multi-stage, cached layers via ECR
**Deploy method:** `aws ecs update-service --force-new-deployment` / ArgoCD image updater *(delete as appropriate)*

**Environment protection rules:**
- `staging`: no restrictions
- `prod`: requires approval from [team / person]

---

## Local Development

```bash
# Install dependencies
[language-specific install command]

# Run locally
[run command]

# Run tests
[test command]

# Build Docker image
docker build -t [service-name]:local .

# Run with Docker
docker run -p 8000:8000 --env-file .env.local [service-name]:local
```

**`.env.local` required variables:** (never commit — see `.env.example`)
```
DB_URL=postgresql://...
JWT_SECRET=...
```

---

## Known Gotchas

- [e.g., "Task role needs `secretsmanager:GetSecretValue` on the exact secret ARN — wildcard will be rejected in code review"]
- [e.g., "Database migrations must run before ECS service update — the GHA workflow enforces this order"]
- [e.g., "CloudFront in front of the ALB — requests have `X-Forwarded-For` headers; always read client IP from header, not connection IP"]
- [e.g., "SQS consumer uses long-polling (20s) — do not set ECS stop timeout below 30s or in-flight messages will be dropped"]
