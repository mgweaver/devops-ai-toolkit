# System Design — [Platform Name]

> **AI context file.** Fill this in once per platform and keep it checked in. Claude reads it automatically when you invoke any slash command in this repo.

---

## Overview

**Platform:** [e.g., "PropertyTrack SaaS — multi-tenant property management platform"]
**Revenue model:** [e.g., "transaction-scrape — fee per payment processed"]
**Tenancy model:** [single-tenant / multi-tenant / tenant-per-database / tenant-per-schema / row-level isolation]
**Environments:** dev | staging | prod  *(Terraform workspaces)*

---

## Architecture Diagram (text)

```
[Internet]
    |
[Route53] → [CloudFront + ACM]
                   |
              [ALB (HTTPS:443)]
               /         \
        [ECS Fargate]  [ECS Fargate]
        [API Service]  [Worker Service]
             |                |
        [RDS Aurora]    [SQS Queue]
        [PostgreSQL]         |
             |          [RDS Aurora]
        [S3 Bucket]    [PostgreSQL]
        (uploads)
             |
      [Secrets Manager]
      (DB creds, API keys)
```

*Replace with your actual topology. Include load balancers, queues, caches, CDN, and data stores.*

---

## AWS Services in Use

| Service | Purpose | Notes |
|---|---|---|
| ECS Fargate | Container runtime | No EC2 instances to manage |
| ECR | Container registry | One repo per service |
| RDS PostgreSQL | Primary database | Multi-AZ in prod, single-AZ in dev/staging |
| S3 | Object storage | [bucket names / purposes] |
| CloudFront | CDN + TLS termination | WAF enabled in prod |
| Route53 | DNS | Hosted zone: [example.com] |
| ACM | TLS certificates | Auto-renewed, attached to ALB + CloudFront |
| ALB | HTTP(S) load balancer | Target groups per service |
| Secrets Manager | Credentials + API keys | Rotation enabled for DB passwords |
| SQS | Async job queue | [queue names] |
| SNS | Alerting / fan-out | [topics] |
| IAM | Auth + authz | OIDC for GHA, task roles for ECS |
| KMS | Encryption at rest | RDS, S3, Secrets Manager |

---

## Services

### [service-name]

**Purpose:** [one sentence]
**Repo:** `github.com/[org]/[repo]`
**Language / Framework:** [e.g., Python 3.12 / FastAPI]
**ECS Cluster:** `[cluster-name]`
**ECS Service:** `[service-name]-[env]`
**Task CPU / Memory:** 512 / 1024 (dev) · 1024 / 2048 (prod)
**Desired count:** 2 (prod) · 1 (dev/staging)
**Autoscaling:** target tracking on CPU 60% · min 2 / max 10 (prod)
**Port:** 8000

**Upstream dependencies:**
- [service or system this calls]

**Downstream consumers:**
- [services that call this]

**Database:** `[db-identifier]` — schema `[schema_name]`
**S3 buckets accessed:** `[bucket-name]` (read/write)
**Secrets:** `[secret-path]` (DB password), `[secret-path]` (API key)

---

### [service-name-2]

*(repeat block per service)*

---

## Networking

**VPC:** `[vpc-id or name]`
**CIDR:** `10.0.0.0/16`

| Subnet | CIDR | AZ | Purpose |
|---|---|---|---|
| public-a | 10.0.1.0/24 | us-east-1a | ALB, NAT GW |
| public-b | 10.0.2.0/24 | us-east-1b | ALB, NAT GW |
| private-a | 10.0.10.0/24 | us-east-1a | ECS tasks, RDS |
| private-b | 10.0.11.0/24 | us-east-1b | ECS tasks, RDS |

**Security group philosophy:** deny by default, allow per named SG. No `0.0.0.0/0` ingress except on ALB port 443.

---

## Data Architecture

**Multi-tenancy strategy:** [row-level isolation with `tenant_id` FK / separate schemas / separate databases]
**Tenant identifier in DB:** `tenant_id UUID NOT NULL` on every tenant-scoped table
**PII fields:** [list tables/columns containing PII]
**Encryption at rest:** RDS storage encryption (KMS), S3 SSE-S3, Secrets Manager (KMS)
**Encryption in transit:** TLS 1.2+ enforced on ALB, RDS parameter group requires SSL

---

## CI/CD

**Workflow engine:** GitHub Actions
**Auth to AWS:** OIDC — no long-lived access keys stored in GitHub Secrets
**Pipeline stages:** lint → unit tests → build Docker image → push to ECR → deploy to ECS (dev) → smoke test → promote to staging → promote to prod (manual approval)
**IaC deploys:** Terraform via GHA on push to `main`, plan on PR
**ArgoCD:** [used / not used — if used, describe app names and sync policy]

---

## Terraform Layout

```
infrastructure/
├── modules/
│   ├── ecs-service/
│   ├── rds/
│   ├── s3-bucket/
│   └── iam-role/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── global/
    └── iam/
```

**Remote state:** S3 bucket `[tf-state-bucket]`, DynamoDB table `[tf-lock-table]`
**Workspace convention:** workspace name = environment name (`dev`, `staging`, `prod`)

---

## Observability

**Metrics / Dashboards:** Grafana ([URL or internal name])
**Alerting:** Grafana Alerting → PagerDuty (prod) / Slack #alerts-dev (non-prod)
**Logs:** CloudWatch Logs → [optional: Loki / OpenSearch]
**Traces:** [X-Ray / Jaeger / none]
**Key SLOs:**

| Service | SLO | Alert threshold |
|---|---|---|
| API | p99 latency < 500ms | alert at 400ms |
| API | error rate < 1% | alert at 0.5% |
| Worker | job success rate > 99% | alert at 98% |

---

## Secrets Inventory

| Secret path | Contents | Rotation |
|---|---|---|
| `[env]/db/[service]` | DB username + password | 30 days (auto) |
| `[env]/api/[third-party]` | Third-party API key | Manual |
| `[env]/jwt/secret` | JWT signing key | Manual |

---

## Known Constraints + Gotchas

- [e.g., "RDS is in a private subnet — migration jobs must run from ECS, not locally"]
- [e.g., "CloudFront has a 30s cache TTL on `/api/` — cache invalidation required after deploys that change API responses"]
- [e.g., "SQS FIFO queue used for payment events — do not switch to standard queue without audit"]
- [e.g., "Tenant IDs are UUIDs generated at signup — never reuse or reassign"]
