# devops-ai-toolkit — Master Context

This repo is a Claude Code slash command + subagent toolkit for DevOps engineers on the property management SaaS platform. Drop it in your project or use it standalone.

## Stack

| Layer | Technology |
|---|---|
| Cloud | AWS |
| IaC | Terraform |
| CI/CD | GitHub Actions + ArgoCD |
| Containers | ECS Fargate |
| Registry | ECR |
| Observability | Grafana |
| Databases | RDS (PostgreSQL) |
| Storage | S3 |
| CDN | CloudFront + Route53 + ACM |
| Load balancing | ALB |
| Secrets | AWS Secrets Manager |
| Methodology | Shape Up (Basecamp) |

## Team

- **Mason** — DevOps engineer (primary user of this toolkit)
- **Eric** — DevOps Director

## Application Context

Multi-tenant property management SaaS. Revenue model: transaction-scrape. Each tenant is isolated at the data layer. All infrastructure is multi-environment (dev / staging / prod) using Terraform workspaces.

---

## Agent Index

Agents live in `agents/`. Slash commands invoke them via the Agent tool when they need specialized, multi-step reasoning.

| Agent | File | Purpose |
|---|---|---|
| IAM Reviewer | `agents/iam-reviewer.md` | Least-privilege auditor — called automatically when `.tf` files touch IAM |
| Terraform Reviewer | `agents/terraform-reviewer.md` | Multi-pass IaC review: security, cost, drift, module hygiene |
| PR Reviewer | `agents/pr-reviewer.md` | Orchestrator — routes to iam-reviewer / terraform-reviewer based on diff |
| Incident Responder | `agents/incident-responder.md` | Triage → RCA → remediation workflow |
| Deploy Debugger | `agents/deploy-debugger.md` | ECS / ArgoCD failure investigator |

---

## Slash Command Index

Commands live in `.claude/commands/`. Claude Code picks them up automatically.

### Infrastructure (`/infra/`)
| Command | Description |
|---|---|
| `/terraform-review` | Multi-pass Terraform review (invokes terraform-reviewer agent) |
| `/terraform-security` | Security-focused scan: SGs, IAM, encryption, public exposure |
| `/iam-audit` | Standalone IAM least-privilege audit |
| `/ecs-task-def` | Generate or review ECS task definitions |
| `/ecs-debug` | Debug ECS / ArgoCD deployment failures (invokes deploy-debugger agent) |
| `/dockerfile-review` | Dockerfile security + best-practices review |

### CI/CD (`/cicd/`)
| Command | Description |
|---|---|
| `/generate-workflow` | Generate a GitHub Actions workflow from requirements |
| `/review-workflow` | Security + best practices audit of an existing workflow |
| `/debug-pipeline` | Diagnose a failed GHA run from logs |

### Observability (`/observability/`)
| Command | Description |
|---|---|
| `/generate-alerts` | Generate Grafana alert rules from SLOs / service description |
| `/write-runbook` | Generate a structured runbook |

### Incidents (`/incidents/`)
| Command | Description |
|---|---|
| `/incident-triage` | Structured triage → RCA → remediation (invokes incident-responder agent) |

### Shape Up (`/shape-up/`)
| Command | Description |
|---|---|
| `/write-pitch` | Problem → appetite → solution → rabbit holes → no-gos |
| `/scope-hammer` | What to cut to fit a fixed cycle |
| `/shape-work` | Raw idea → fully shaped pitch |

### App Development (`/app-dev/`)
| Command | Description |
|---|---|
| `/pr-review` | Full PR review, auto-invokes iam-reviewer when `.tf` files detected |
| `/api-design` | Design or review a REST / GraphQL API |
| `/schema-review` | DB schema review: normalization, indexes, multi-tenancy |
| `/implement-story` | Shaped task → implementation plan + code |

---

## Design Conventions

### How Commands Call Agents

Slash commands are markdown prompt files. When a command needs deep specialized review it ends with an instruction like:

```
Invoke the Agent tool with subagent definition from `agents/iam-reviewer.md` and pass the diff above as context.
```

The agent runs in a fresh context window so it doesn't pollute the caller's context with verbose analysis.

### IAM Philosophy

- No shared IAM users; all service-to-service auth via IAM roles
- Least privilege from day one — no `*` actions without explicit justification
- OIDC for GitHub Actions → AWS auth (no long-lived access keys in CI)
- Each ECS task gets a dedicated task role scoped to what it needs

### Terraform Style

- Modules over root configs — reusable, versioned modules
- Remote state: S3 bucket + DynamoDB lock table
- Workspaces for environment separation (dev / staging / prod)
- All resources tagged: `Environment`, `Service`, `Owner`, `ManagedBy=terraform`
- No hardcoded account IDs or region strings — use data sources

### GitHub Actions Conventions

- Reusable workflows in `.github/workflows/` with `workflow_call` trigger
- OIDC auth to AWS — never store `AWS_ACCESS_KEY_ID` in secrets
- Environment protection rules on staging and prod deployments
- Pinned action versions (SHA, not tag) for supply chain security

### Shape Up Vocabulary

- **Appetite**: Fixed time budget (small = 2 weeks, large = 6 weeks) — scope is variable
- **Pitch**: Proposal doc: problem, appetite, solution sketch, rabbit holes, no-gos
- **Scope hammer**: Cutting work to fit the appetite without slipping the cycle
- **Betting table**: Where pitches are selected for the next cycle
- **Cooldown**: 2-week buffer between cycles for bugs, exploration, and polish

---

## Context Templates

Drop these into service repos to give Claude rich context about the service:

- `context/system-design-template.md` — AI-readable architecture doc
- `context/service-context-template.md` — Per-service context
- `context/runbook-template.md` — Standard runbook structure
