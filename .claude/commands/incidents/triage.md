# /incident-triage

Structured triage → RCA → remediation for production incidents. Invokes the incident-responder agent to run the full workflow.

## Usage

```
/incident-triage
Service: <affected service or services>
[Cluster: <ECS cluster name>]
[Alert: <alert name or description that fired>]
[Impact: <what users are experiencing>]
[Logs: <paste any relevant log lines, error messages, or metrics>]
[Last change: <recent deploy, config change, or infra change>]
```

Minimal invocation (agent will ask for more if needed):

```
/incident-triage
Service: payment-api
Alert: payment-api availability critical — 98.2% success rate, SLO is 99.95%
```

## What Happens

1. Collects available context (service, alert, logs, recent changes)
2. Fetches live ECS service status and recent CloudWatch logs if AWS CLI is available
3. Invokes the `incident-responder` agent with all context for structured triage
4. Returns: TRIAGE REPORT → ROOT CAUSE ANALYSIS → REMEDIATION PLAN
5. Produces stakeholder communication drafts and a postmortem stub

---

## Steps

### Step 1: Gather live context (if AWS CLI available)

```bash
# ECS service health
aws ecs describe-services \
  --cluster <cluster> \
  --services <service> \
  --query 'services[0].{status:status,runningCount:runningCount,desiredCount:desiredCount,events:events[0:10]}'
```

```bash
# Stopped tasks (if tasks are failing)
aws ecs list-tasks \
  --cluster <cluster> \
  --service-name <service> \
  --desired-status STOPPED \
  --query 'taskArns[0:3]'
```

If stopped tasks found:
```bash
aws ecs describe-tasks \
  --cluster <cluster> \
  --tasks <task-arn> \
  --query 'tasks[*].{stoppedReason:stoppedReason,containers:containers[*].{name:name,exitCode:exitCode,reason:reason}}'
```

```bash
# Recent logs
aws logs tail /ecs/<service> --since 30m
```

```bash
# ALB target health
aws elbv2 describe-target-health --target-group-arn <arn>
```

If the user did not provide a cluster or ARN, prompt for them or proceed with whatever context is available.

### Step 2: Invoke the Incident Responder agent

Invoke the Agent tool with the subagent definition from `agents/incident-responder.md`, passing all gathered context:

> Run the full incident response workflow for the following production incident. Work through Triage → RCA → Remediation. Produce a TRIAGE REPORT, ROOT CAUSE ANALYSIS, REMEDIATION PLAN, stakeholder communication drafts, and a postmortem stub.
>
> **Service:** <service>
> **Cluster:** <cluster>
> **Alert:** <alert name and condition>
> **Impact:** <user-facing impact>
> **ECS service events:** [paste output]
> **Stopped task details:** [paste output]
> **Recent logs:** [paste output]
> **Last known change:** <deploy, config change, or "unknown">
> **Additional context:** [user-provided context]

### Step 3: Present findings

Return the full structured report from the agent:

1. **TRIAGE REPORT** — severity, blast radius, immediate mitigation available?
2. **ROOT CAUSE ANALYSIS** — precise root cause with evidence
3. **REMEDIATION PLAN** — immediate restoration steps + root cause fix
4. **Stakeholder messages** — ready to paste into Slack/email
5. **Postmortem stub** — ready to paste into Confluence or Notion

If the agent requests additional diagnostic data, fetch it and re-invoke.

---

## Severity Reference

| SEV | Criteria | Do this |
|---|---|---|
| SEV-1 | Revenue impact, data loss risk, all tenants affected | Page Eric immediately. 15-min response. |
| SEV-2 | Partial outage, degraded service, subset of tenants | Notify Eric async. 1-hour response. |
| SEV-3 | Non-critical degradation, no direct user impact | Best-effort. Next business day. |

---

## Quick Diagnostic Commands

If you need to investigate before invoking the agent:

```bash
# Is it the app or the infra?
aws ecs describe-services --cluster <cluster> --services <service> \
  --query 'services[0].{running:runningCount,desired:desiredCount}'

# Is AWS having problems?
# Check: https://health.aws.amazon.com

# Recent logs
aws logs tail /ecs/<service> --since 15m

# Database status
aws rds describe-db-instances --db-instance-identifier <db-id> \
  --query 'DBInstances[0].DBInstanceStatus'

# Quick rollback (if last deploy is the culprit)
aws ecs update-service \
  --cluster <cluster> \
  --service <service> \
  --task-definition <service>:<previous-revision-number>
```

---

## Examples

```
/incident-triage
Service: payment-api
Cluster: prod-cluster
Alert: payment-api availability critical
Impact: Tenants reporting payment failures — cannot collect rent
Last change: Deployed image tag 3.1.0 at 14:32 UTC (30 minutes ago)
Logs:
ERROR: Connection timeout after 30000ms calling stripe.com/v1/charges
ERROR: Connection timeout after 30000ms calling stripe.com/v1/charges
FATAL: Unhandled promise rejection — payment processing failed
```

```
/incident-triage
Service: lease-processor
Alert: lease-processor availability warning — degraded for 20 minutes
Impact: Some tenants reporting slow lease signing, not all failing
Context: No recent deploys. First and 15th of the month — peak usage period.
```

```
/incident-triage
Service: tenant-api, auth-service
Impact: All tenants locked out — login returning 503
Last change: RDS security group updated by Terraform at 09:15 UTC
```
