# devops-ai-toolkit

A Claude Code slash command + subagent toolkit for DevOps engineers. Built for real daily use on AWS + Terraform + GitHub Actions + ECS stacks. Drop it into any project and get a full AI-powered DevOps co-pilot.

## What This Is

A collection of Claude Code slash commands and subagent definitions that encode real DevOps expertise:

- **Slash commands** — invoke specialized workflows from any project that includes this toolkit
- **Subagents** — specialist agents invoked by commands when they need deep, focused analysis (IAM auditing, incident triage, deploy debugging)
- **Context templates** — drop into service repos to give Claude rich context about your architecture

Designed around Shape Up methodology, AWS best practices, and least-privilege IAM from day one.

## Stack

AWS · Terraform · GitHub Actions · ArgoCD · ECS Fargate · Grafana · RDS · PostgreSQL

---

## Quick Start

```bash
git clone https://github.com/mgweaver/devops-ai-toolkit ~/.claude-toolkit
```

Copy the commands into your project:

```bash
cp -r ~/.claude-toolkit/.claude/commands .claude/commands
cp ~/.claude-toolkit/CLAUDE.md CLAUDE.md   # gives Claude stack context
```

Then in any Claude Code session:

```
/pr-review
/terraform-review
/incident-triage
```

---

## Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed
- AWS CLI configured (for commands that read live infra)
- `terraform`, `gh`, `argocd` CLIs available as needed per command

---

## Installation

### Option 1: Clone into your project

```bash
git clone https://github.com/mgweaver/devops-ai-toolkit .claude-toolkit
ln -s .claude-toolkit/.claude/commands .claude/commands
```

### Option 2: Global installation

```bash
git clone https://github.com/mgweaver/devops-ai-toolkit ~/.claude-toolkit
```

Add to your global Claude Code settings (`~/.claude/settings.json`):

```json
{
  "commandPaths": ["~/.claude-toolkit/.claude/commands"]
}
```

### Option 3: Copy commands you want

Browse `.claude/commands/` and copy individual files into your project's `.claude/commands/`.

---

## Command Reference

### Infrastructure

| Command | Description |
|---|---|
| `/terraform-review` | Multi-pass Terraform plan/config review: security, cost flags, drift risks, module hygiene |
| `/terraform-security` | Security-focused scan: open SGs, IAM wildcards, unencrypted resources, public exposure |
| `/iam-audit` | Least-privilege IAM audit of roles, policies, and trust relationships |
| `/ecs-task-def` | Generate or review ECS task definitions against best practices |
| `/ecs-debug` | Debug ECS or ArgoCD deployment failures — invokes the deploy-debugger agent |
| `/dockerfile-review` | Dockerfile security + layer efficiency review |

**Examples:**

```
/terraform-review
Plan file: terraform.plan.txt
Focus on the new RDS module and any cost changes.
```

```
/terraform-security
Scan the modules/ecs directory.
Flag anything that touches public ingress or IAM.
```

```
/iam-audit
Role: arn:aws:iam::123456789012:role/payment-service-task-role
Policy: (paste policy JSON)
```

```
/ecs-debug
Service: payment-api  Environment: prod
Last deployment started at 14:45 UTC. Tasks failing health checks.
ECS events: (paste events)
```

```
/dockerfile-review
(paste Dockerfile)
```

---

### CI/CD

| Command | Description |
|---|---|
| `/generate-workflow` | Generate a GitHub Actions workflow from a plain-English description |
| `/review-workflow` | Security + best practices audit of an existing workflow file |
| `/debug-pipeline` | Diagnose a failed GitHub Actions run from logs |

**Examples:**

```
/generate-workflow
Build and push a Docker image to ECR on merge to main.
Use OIDC auth to AWS. Deploy to ECS Fargate after push.
Run tests before build. Environment: prod. Region: us-east-1.
```

```
/review-workflow
(paste .github/workflows/deploy.yml)
```

```
/debug-pipeline
Run ID: 9823741022
Failure step: "Deploy to ECS"
Logs: (paste failed step logs)
```

---

### Observability

| Command | Description |
|---|---|
| `/generate-alerts` | Generate Grafana alert rules from SLOs or a service description |
| `/write-runbook` | Generate a structured runbook for a service or incident type |

**Examples:**

```
/generate-alerts
Service: payment-api
SLOs: p99 latency < 500ms, error rate < 0.5%, availability > 99.9%
Datasource: Prometheus. Alert via PagerDuty.
```

```
/write-runbook
Service: tenant-sync-worker
Common failure: worker falls behind on message queue under high transaction volume.
On-call contacts: #infra-oncall Slack channel.
```

---

### Incidents

| Command | Description |
|---|---|
| `/incident-triage` | Structured triage → root cause analysis → remediation steps. Invokes the incident-responder agent. |

**Example:**

```
/incident-triage
P1 — payment service returning 503s since 14:32 UTC.
ECS task count dropped from 3 to 1. RDS CPU at 95%.
Recent deploy: v2.4.1 at 14:15 UTC.
```

---

### Shape Up

| Command | Description |
|---|---|
| `/write-pitch` | Turn a problem into a full Shape Up pitch: problem, appetite, solution, rabbit holes, no-gos |
| `/scope-hammer` | Given a pitch and remaining time, decide what to cut |
| `/shape-work` | Raw idea → fully shaped pitch ready for the betting table |

**Examples:**

```
/write-pitch
Problem: Tenants can't export their transaction history. We keep getting support tickets.
Appetite: Small batch (2 weeks).
```

```
/scope-hammer
Pitch: Multi-tenant audit log export feature.
Time remaining: 4 days. What do we cut?
Must-haves: CSV export, date range filter.
```

```
/shape-work
Idea: Add webhook support so tenants can push transaction events to their own systems.
```

---

### App Development

| Command | Description |
|---|---|
| `/pr-review` | Full PR review. Automatically invokes the IAM reviewer when `.tf` files are detected in the diff. |
| `/api-design` | Design or review a REST / GraphQL API |
| `/schema-review` | Database schema review: normalization, indexes, multi-tenancy isolation |
| `/implement-story` | Shaped task → implementation plan + working code |

**Examples:**

```
/pr-review
PR: https://github.com/org/repo/pull/142
```

```
/api-design
Design a REST API for tenant-scoped webhook subscriptions.
Auth: JWT. Must support CRUD + replay. Multi-tenant: row-level isolation in RDS.
```

```
/schema-review
(paste CREATE TABLE statements)
Flag any missing indexes, missing tenant_id isolation, or normalization issues.
```

```
/implement-story
Shaped task: Add CSV export endpoint for tenant transaction history.
Stack: Python / FastAPI, RDS PostgreSQL, S3 for file storage.
Appetite: 2 days.
```

---

## Agents

These run as subagents invoked by commands — you don't call them directly.

| Agent | Invoked By | Role |
|---|---|---|
| `iam-reviewer` | `/pr-review`, `/iam-audit` | Least-privilege IAM auditor |
| `terraform-reviewer` | `/terraform-review`, `/pr-review` | Multi-pass IaC reviewer |
| `pr-reviewer` | `/pr-review` | Orchestrator — routes to specialist agents based on changed files |
| `incident-responder` | `/incident-triage` | Triage → RCA → remediation |
| `deploy-debugger` | `/ecs-debug` | ECS / ArgoCD failure investigator |

Agents run in a fresh context window so verbose analysis stays isolated from the calling command's context.

---

## Context Templates

Drop these into service repos to give Claude rich context about your architecture:

| Template | Purpose |
|---|---|
| `context/system-design-template.md` | AI-readable system architecture doc |
| `context/service-context-template.md` | Per-service context: ports, dependencies, env vars, on-call notes |
| `context/runbook-template.md` | Standard runbook structure |

Fill in the templates and commit them alongside your service code. Every Claude Code command you run in that repo will have full architectural context automatically.

---

## How It Works

1. You invoke a slash command (e.g. `/pr-review`)
2. Claude Code loads the command file from `.claude/commands/`
3. The command prompt instructs Claude to gather context (diff, plan file, logs, etc.)
4. For deep analysis, the command invokes a specialist subagent via the Agent tool
5. The subagent runs in a fresh context, produces a focused report, and returns it to the command
6. You get a structured, actionable output

The subagent pattern means commands stay fast and focused while specialist analysis stays thorough.

---

## Design Philosophy

- **Least privilege, always** — IAM review is automatic on any PR touching `.tf` files
- **No long-lived credentials** — OIDC for CI/CD, IAM roles for services
- **Shape Up native** — pitches, appetite, scope hammer are first-class concepts
- **Real tool output** — commands reference actual CLI tools (`terraform`, `aws`, `gh`, `argocd`)
- **Agents isolate context** — subagents get a fresh window so verbose analysis doesn't pollute command context

---

## License

MIT
