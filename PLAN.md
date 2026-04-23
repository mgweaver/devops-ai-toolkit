# devops-ai-toolkit — Build Plan

A Claude Code slash commands + subagent toolkit for DevOps engineers. Public GitHub repo, resume-oriented but built for real daily use.

## Stack Context
- Cloud: AWS
- IaC: Terraform
- CI/CD: GitHub Actions + ArgoCD
- Containers: ECS
- Observability: Grafana
- Methodology: Shape Up (Basecamp)
- Primary users: Mason (DevOps engineer) + Eric (DevOps Director)
- App being built: property management SaaS (multi-tenant, transaction-scrape revenue model)

## Repo Layout (target state)
```
devops-ai-toolkit/
├── CLAUDE.md
├── README.md
├── PLAN.md                            (this file)
├── .claude/
│   ├── settings.json
│   └── commands/
│       ├── infra/
│       │   ├── terraform-review.md
│       │   ├── terraform-security.md
│       │   ├── iam-audit.md
│       │   ├── ecs-task-def.md
│       │   ├── ecs-debug.md
│       │   └── dockerfile-review.md
│       ├── cicd/
│       │   ├── generate-workflow.md
│       │   ├── debug-pipeline.md
│       │   └── review-workflow.md
│       ├── observability/
│       │   ├── generate-alerts.md
│       │   └── write-runbook.md
│       ├── incidents/
│       │   └── triage.md
│       ├── shape-up/
│       │   ├── write-pitch.md
│       │   ├── scope-hammer.md
│       │   └── shape-work.md
│       └── app-dev/
│           ├── pr-review.md
│           ├── api-design.md
│           ├── schema-review.md
│           └── implement-story.md
├── agents/
│   ├── iam-reviewer.md
│   ├── terraform-reviewer.md
│   ├── pr-reviewer.md
│   ├── incident-responder.md
│   └── deploy-debugger.md
└── context/
    ├── system-design-template.md
    ├── service-context-template.md
    └── runbook-template.md
```

---

## Tasks

### PHASE 1 — Foundation
- [x] **1.1** Create `CLAUDE.md` — master context file: stack, conventions, agent index, how commands call agents
- [x] **1.2** Create `.claude/settings.json` — tool permissions for common DevOps operations
- [x] **1.3** Create `README.md` — public-facing: what this is, how to install, command index

### PHASE 2 — Flagship: PR Review Pipeline
*Most impressive on resume. `/pr-review` orchestrates the full review and auto-invokes `iam-reviewer` when `.tf` files are detected in the diff.*

- [x] **2.1** Create `agents/iam-reviewer.md` — least-privilege IAM auditor subagent
- [x] **2.2** Create `agents/pr-reviewer.md` — orchestrator: routes to iam-reviewer, terraform-reviewer based on changed files
- [x] **2.3** Create `.claude/commands/app-dev/pr-review.md` — `/pr-review` slash command that invokes pr-reviewer agent

### PHASE 3 — Terraform Commands + Agent
- [x] **3.1** Create `agents/terraform-reviewer.md` — multi-pass IaC reviewer (security, cost flags, drift, module hygiene)
- [x] **3.2** Create `.claude/commands/infra/terraform-review.md` — `/terraform-review` command
- [x] **3.3** Create `.claude/commands/infra/terraform-security.md` — `/terraform-security` command (SGs, IAM, encryption, public exposure)
- [x] **3.4** Create `.claude/commands/infra/iam-audit.md` — `/iam-audit` standalone command

### PHASE 4 — Shape Up Commands
*Most differentiated vs. every other DevOps AI toolkit. Encodes Shape Up methodology: pitches, appetite, scope hammer.*

- [x] **4.1** Create `.claude/commands/shape-up/write-pitch.md` — `/write-pitch` (problem → appetite → solution → rabbit holes → no-gos)
- [x] **4.2** Create `.claude/commands/shape-up/scope-hammer.md` — `/scope-hammer` (what to cut to fit a fixed cycle)
- [x] **4.3** Create `.claude/commands/shape-up/shape-work.md` — `/shape-work` (raw idea → fully shaped pitch)

### PHASE 5 — ECS / Container Commands
- [x] **5.1** Create `.claude/commands/infra/ecs-task-def.md` — `/ecs-task-def` (generate/review ECS task definitions)
- [x] **5.2** Create `agents/deploy-debugger.md` — ECS/ArgoCD failure investigator subagent
- [x] **5.3** Create `.claude/commands/infra/ecs-debug.md` — `/ecs-debug` command (invokes deploy-debugger agent)
- [x] **5.4** Create `.claude/commands/infra/dockerfile-review.md` — `/dockerfile-review`

### PHASE 6 — CI/CD Commands
- [x] **6.1** Create `.claude/commands/cicd/generate-workflow.md` — `/generate-workflow` (GHA workflow from requirements)
- [x] **6.2** Create `.claude/commands/cicd/review-workflow.md` — `/review-workflow` (security + best practices audit)
- [x] **6.3** Create `.claude/commands/cicd/debug-pipeline.md` — `/debug-pipeline` (diagnose failed GHA run from logs)

### PHASE 7 — Observability + Incident Commands
- [x] **7.1** Create `.claude/commands/observability/generate-alerts.md` — `/generate-alerts` (Grafana alert rules from SLOs/service description)
- [x] **7.2** Create `.claude/commands/observability/write-runbook.md` — `/write-runbook`
- [x] **7.3** Create `agents/incident-responder.md` — triage → RCA → remediation workflow agent
- [x] **7.4** Create `.claude/commands/incidents/triage.md` — `/incident-triage` (invokes incident-responder agent)

### PHASE 8 — App Dev Commands
- [x] **8.1** Create `.claude/commands/app-dev/api-design.md` — `/api-design` (design or review a REST/GraphQL API)
- [x] **8.2** Create `.claude/commands/app-dev/schema-review.md` — `/schema-review` (DB schema review: normalization, indexes, multi-tenancy)
- [x] **8.3** Create `.claude/commands/app-dev/implement-story.md` — `/implement-story` (scoped shape-up task → implementation plan + code)

### PHASE 9 — Context Templates
- [x] **9.1** Create `context/system-design-template.md` — AI-readable architecture doc template
- [x] **9.2** Create `context/service-context-template.md` — per-service context template (drop into any service repo)
- [x] **9.3** Create `context/runbook-template.md` — standard runbook structure

### PHASE 10 — Polish + Ship
- [x] **10.1** Update `README.md` with full command index, installation instructions, example usage
- [x] **10.2** Git init, initial commit, push to GitHub (mgweaver/devops-ai-toolkit)
- [x] **10.3** Review all files for consistency, cross-references, and quality

---

## How to Resume After Clearing Context

Tell Claude:
> "We're building devops-ai-toolkit. Read PLAN.md at C:\Code\devops-ai-toolkit\PLAN.md and continue from the next unchecked task."

Mark tasks complete by changing `- [ ]` to `- [x]` as you finish them.

---

## Design Decisions (for Claude to reference)

- **Slash commands** live in `.claude/commands/` — Claude Code picks them up automatically in any project that includes this repo
- **Agents** are subagent definitions in `agents/` — commands invoke them via the Agent tool
- **`/pr-review`** auto-detects `.tf` file changes and routes to `iam-reviewer` — engineers never forget the IAM check
- **Shape Up vocabulary**: appetite (fixed time/variable scope), pitch (proposal doc), scope hammer (cutting to fit), betting table (cycle planning)
- **IAM philosophy**: no shared accounts, least-privilege from day one, service-to-service auth via IAM roles not keys
- **Target AWS services**: ECS Fargate, ECR, RDS, S3, CloudFront, Route53, ACM, ALB, Secrets Manager
- **Terraform style**: modules over root configs, remote state in S3+DynamoDB, workspaces for env separation
- **GHA conventions**: reusable workflows, OIDC auth to AWS (no long-lived keys), environment protection rules
