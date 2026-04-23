# Runbook — [Service Name]: [Alert or Scenario Name]

> **Template.** Copy this file, fill in the blanks, and commit it to your service repo at `runbooks/[alert-name].md`. The `/write-runbook` command uses this structure automatically.

---

## Metadata

| Field | Value |
|---|---|
| **Service** | [service-name] |
| **Alert / Scenario** | [e.g., "High 5xx Error Rate", "RDS Connection Pool Exhausted", "ECS Task Crash Loop"] |
| **Severity** | P1 — Critical / P2 — High / P3 — Medium *(delete as appropriate)* |
| **SLO impact** | [e.g., "Breaches error-rate SLO if sustained > 5 minutes"] |
| **Last reviewed** | [YYYY-MM-DD] |
| **Owner** | [team or on-call rotation] |
| **Escalation contact** | [name / PagerDuty policy / Slack handle] |

---

## Alert Definition

**Grafana alert name:** `[alert-name]`
**Condition:** [e.g., "5xx rate > 1% over a 5-minute window"]
**Firing threshold:** [metric value that triggers the alert]
**Evaluation interval:** [e.g., every 1 minute, 3 consecutive failures]
**Notification channel:** PagerDuty (prod) · Slack `#alerts-[env]` (non-prod)

---

## Quick Reference

**Useful links (fill in before an incident, not during):**

- Grafana dashboard: [URL]
- CloudWatch logs: [URL or log group path]
- ECS service console: [URL]
- RDS console: [URL]
- Runbook for upstream service: [URL]

**Key commands (fill in ahead of time):**

```bash
# Tail logs for this service
aws logs tail /ecs/[service-name] --follow --region [region]

# Check ECS service status
aws ecs describe-services \
  --cluster [cluster-name] \
  --services [service-name]-prod \
  --region [region]

# List running tasks
aws ecs list-tasks \
  --cluster [cluster-name] \
  --service-name [service-name]-prod \
  --region [region]

# Describe a specific task (replace TASK_ARN)
aws ecs describe-tasks \
  --cluster [cluster-name] \
  --tasks TASK_ARN \
  --region [region]

# Force new deployment (rolling restart)
aws ecs update-service \
  --cluster [cluster-name] \
  --service [service-name]-prod \
  --force-new-deployment \
  --region [region]
```

---

## Triage Steps

*Run these in order. Stop when you find the root cause.*

### Step 1 — Confirm the alert is real

- [ ] Check Grafana dashboard — is the metric actually elevated or is this a flapping alert?
- [ ] Confirm the alert fired in prod (not staging/dev noise)
- [ ] Check if a deploy happened in the last 30 minutes (`git log --oneline -10` or check GHA)
- [ ] Check `#deploys` Slack channel for recent activity

**If a deploy is the likely cause → go to [Rollback](#rollback)**

---

### Step 2 — Check ECS task health

- [ ] Are all desired tasks running?
  ```bash
  aws ecs describe-services --cluster [cluster] --services [service]-prod --region [region] \
    --query 'services[0].{desired:desiredCount,running:runningCount,pending:pendingCount}'
  ```
- [ ] Are tasks crash-looping? (Look for `STOPPED` tasks with `stoppedReason`)
  ```bash
  aws ecs list-tasks --cluster [cluster] --service-name [service]-prod --desired-status STOPPED --region [region]
  ```
- [ ] What is the stop reason?
  ```bash
  aws ecs describe-tasks --cluster [cluster] --tasks TASK_ARN --region [region] \
    --query 'tasks[0].stoppedReason'
  ```

---

### Step 3 — Check logs

- [ ] Open CloudWatch Logs for the service:
  ```bash
  aws logs tail /ecs/[service-name] --follow --since 10m --region [region]
  ```
- [ ] Look for: panic / exception stack traces, OOM messages, timeout errors, dependency failures
- [ ] Note the first error timestamp — compare to alert firing time

**Common log patterns and their meaning:**

| Log pattern | Likely cause |
|---|---|
| `connection refused` / `dial tcp` | Downstream service unavailable or SG misconfigured |
| `context deadline exceeded` | DB or external API timeout |
| `too many connections` | DB connection pool exhausted |
| `OOMKilled` | Task memory limit too low |
| `secret not found` | Secrets Manager ARN wrong or IAM permission missing |
| `FATAL: password authentication failed` | DB credentials rotated but task not restarted |

---

### Step 4 — Check the database

- [ ] Are DB connections near the limit?
  ```sql
  SELECT count(*) FROM pg_stat_activity WHERE datname = '[db_name]';
  SELECT setting::int AS max_connections FROM pg_settings WHERE name = 'max_connections';
  ```
- [ ] Are there long-running queries blocking others?
  ```sql
  SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
  FROM pg_stat_activity
  WHERE (now() - pg_stat_activity.query_start) > interval '30 seconds'
  ORDER BY duration DESC;
  ```
- [ ] Kill a blocking query if needed (get approval before running in prod):
  ```sql
  SELECT pg_terminate_backend([pid]);
  ```

---

### Step 5 — Check upstream / downstream dependencies

- [ ] Is the ALB returning errors? (Check ALB target group health in AWS console or Grafana)
- [ ] Is [upstream service] healthy? (Check its runbook or dashboard)
- [ ] Are external API calls failing? (Check logs for 4xx/5xx from third-party APIs)
- [ ] Is SQS queue depth spiking? (Check `ApproximateNumberOfMessagesNotVisible` metric)

---

## Remediation

### Fix: Restart the ECS service (rolling restart)

Use when: tasks are crash-looping or stuck with stale state.

```bash
aws ecs update-service \
  --cluster [cluster-name] \
  --service [service-name]-prod \
  --force-new-deployment \
  --region [region]
```

Monitor: watch task count stabilize at desired count before closing the incident.

---

### Fix: Scale up ECS service

Use when: CPU/memory is saturated and autoscaling hasn't kicked in fast enough.

```bash
aws ecs update-service \
  --cluster [cluster-name] \
  --service [service-name]-prod \
  --desired-count [n] \
  --region [region]
```

**Remember to scale back down after the incident.** Autoscaling will not reduce below the desired count you set manually — update it back to `2` (or whatever the baseline is) when load normalizes.

---

### Fix: Kill long-running DB queries

Use when: connection pool exhausted due to blocked/long queries.

1. Identify the blocking query (Step 4 above)
2. Get approval from [team lead / DBA]
3. `SELECT pg_terminate_backend([pid]);`
4. Monitor connection count — should drop within 30 seconds

---

### Fix: Rotate and re-inject secrets

Use when: `password authentication failed` or `secret not found` in logs after a secret rotation.

1. Confirm the secret was rotated: AWS Console → Secrets Manager → `[secret-path]`
2. Force a new ECS deployment to pick up the new secret value:
   ```bash
   aws ecs update-service --cluster [cluster] --service [service]-prod --force-new-deployment --region [region]
   ```
3. New tasks will pull the latest secret at startup

---

### Rollback

Use when: the incident started within 30 minutes of a deploy.

**Option A — Redeploy previous image:**
1. Find the previous task definition revision:
   ```bash
   aws ecs describe-task-definition --task-definition [service-name] --region [region]
   ```
   *(the current revision minus 1 is the previous deploy)*
2. Update the service to the previous revision:
   ```bash
   aws ecs update-service \
     --cluster [cluster-name] \
     --service [service-name]-prod \
     --task-definition [service-name]:[previous-revision] \
     --region [region]
   ```

**Option B — Revert in GitHub Actions:**
1. Find the last good commit SHA: `git log --oneline`
2. Revert: `git revert [bad-sha]` and push → triggers deploy pipeline

---

## Escalation

If the issue is not resolved within [X minutes], escalate:

| When | Who | How |
|---|---|---|
| > 15 min, P1 unresolved | [name] | PagerDuty / phone |
| DB corruption suspected | [DBA or senior eng] | Slack DM + phone |
| Data breach suspected | [security contact] | Incident bridge + legal protocol |
| Third-party API outage | [vendor support] | [support URL / status page] |

---

## Post-Incident

After the incident is resolved:

- [ ] Update the incident record in [Linear / Jira / PagerDuty]
- [ ] Write an incident timeline (when did it start, when detected, when resolved)
- [ ] Identify contributing causes (not root cause — use 5 Whys)
- [ ] File follow-up tasks: alert threshold tuning, runbook gaps, missing monitoring
- [ ] Schedule a blameless post-mortem if P1 or if the same issue recurred

---

## Runbook Changelog

| Date | Author | Change |
|---|---|---|
| [YYYY-MM-DD] | [name] | Initial version |
| [YYYY-MM-DD] | [name] | [what changed and why] |
