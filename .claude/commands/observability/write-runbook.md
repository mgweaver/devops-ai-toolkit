# /write-runbook

Generate a structured, actionable runbook for a service, alert, or incident type. Output is ready to paste into Confluence, Notion, or a wiki.

## Usage

```
/write-runbook
Service: <service name>
Alert: <alert name or condition that triggers this runbook>
[Severity: critical | warning]
[Context: <architecture details, dependencies, common failure modes>]
[Template: incident | alert | deployment | maintenance]
```

Or describe what you need:

```
/write-runbook
Alert: lease-processor availability critical
Context: ECS Fargate service backed by RDS PostgreSQL and SQS. Calls Stripe and Docusign. On-call is woken up when this fires.
```

## What Happens

1. Identifies the runbook type (alert response, incident, deployment, maintenance)
2. Generates a structured runbook with triage steps ordered from fastest-to-check to most invasive
3. Includes exact AWS CLI commands and dashboard links (parameterized for the service)
4. Adds an escalation path and resolution checklist

---

## Runbook Structure

Every runbook follows this structure:

### Header

```markdown
# Runbook: <Alert or Procedure Name>
**Service:** <service>
**Severity:** critical | warning
**Last updated:** YYYY-MM-DD
**Owner:** DevOps
**Escalation:** @devops-oncall → Eric (DevOps Director)
```

### Overview

- What this service does (1-2 sentences)
- Why this alert exists and what user impact looks like
- SLO at stake (if applicable)

### Alert Context

- Alert name and expression
- What threshold triggers it
- Typical time-of-day / traffic patterns that affect it
- Known false positive conditions

### Immediate Triage (< 5 minutes)

Ordered from fastest to check to most invasive:

1. **Check service health dashboard** — link to Grafana dashboard
2. **Check ECS service status**:
   ```bash
   aws ecs describe-services \
     --cluster <cluster> \
     --services <service> \
     --query 'services[0].{status:status,runningCount:runningCount,desiredCount:desiredCount,events:events[0:5]}'
   ```
3. **Check recent logs**:
   ```bash
   aws logs tail /ecs/<service> --since 10m
   ```
4. **Check downstream dependencies** — list of external services to check (RDS, Stripe, SQS, etc.)

### Diagnosis Decision Tree

```
Is runningCount < desiredCount?
├── YES → Task launch failure (see Task Failures section)
└── NO → Tasks running but unhealthy
    ├── ALB health checks failing? → App not responding (see App Health section)
    ├── High error rate in logs? → Application error (see Error Analysis section)
    └── Latency spike? → Downstream dependency slow (see Dependencies section)
```

### Common Failure Modes

For each known failure mode:

#### <Failure Mode Name>

**Symptoms:** what you see in logs/metrics
**Cause:** root cause
**Fix:**
```bash
# exact command to resolve
```
**Verification:** how to confirm it's fixed

### Escalation

| Condition | Action |
|---|---|
| Unable to diagnose within 15 minutes | Page Eric (@devops-director) |
| Data loss suspected | Page Eric + notify engineering lead immediately |
| SLO breach confirmed (error budget exhausted) | Open incident, notify stakeholders |

### Resolution Checklist

- [ ] Alert resolved in Grafana
- [ ] Root cause identified and documented
- [ ] Postmortem ticket created (if critical)
- [ ] Fix deployed or workaround in place
- [ ] Runbook updated if steps were missing or wrong

### Related Resources

- Grafana dashboard: `https://grafana.internal/d/<dashboard-uid>`
- ECS service: AWS Console → ECS → Clusters → `<cluster>` → Services → `<service>`
- CloudWatch logs: `/ecs/<service>`
- Terraform source: `infra/modules/<service>/`
- Related runbooks: [list]

---

## Runbook Types

### `alert` (default)
Response steps for a specific Grafana alert firing on-call. Focused on triage speed.

### `incident`
Full incident response: detection → triage → communication → remediation → postmortem. Includes stakeholder communication templates.

### `deployment`
Step-by-step deployment procedure for the service, including rollback steps.

### `maintenance`
Scheduled maintenance window procedure (e.g., RDS upgrade, certificate rotation, schema migration).

---

## Output Format

Produce the complete runbook in Markdown, ready to paste into a wiki. Do not summarize or truncate — a runbook is only useful if it is complete.

Include:
- All AWS CLI commands parameterized for the specific service/cluster
- Decision trees for the most common failure paths
- Escalation contacts and SLA expectations
- Exact resolution checklist

---

## Examples

```
/write-runbook
Service: payment-api
Alert: payment-api availability critical
Severity: critical
Context: Stripe integration. P99 > 1s or error rate > 1% triggers this. On-call is woken up. Failure means tenants cannot pay rent.
```

```
/write-runbook
Service: tenant-db
Template: maintenance
Context: RDS PostgreSQL 14 → 15 upgrade. Multi-tenant, cannot tolerate data loss. Maintenance window is Sunday 2–4am ET.
```

```
/write-runbook
Template: incident
Context: General incident response runbook for any production outage affecting tenant-facing services.
```
