# /ecs-debug

Diagnose a failed or stuck ECS or ArgoCD deployment. Invokes the deploy-debugger agent for systematic triage.

## Usage

```
/ecs-debug
Service: <ECS service name>
Cluster: <ECS cluster name>
[Error: <paste error message or event log snippet>]
[Logs: <paste CloudWatch log lines or describe-tasks output>]
[Context: what changed before the failure, recent deploys, etc.]
```

## What Happens

1. Collects available context (service name, cluster, error output, logs)
2. Fetches live ECS service events and stopped task details if `aws` CLI is available
3. Invokes the `deploy-debugger` agent with all gathered context for systematic triage
4. Returns a structured report: SYMPTOM → ROOT CAUSE → EVIDENCE → REMEDIATION

---

## Steps

### Step 1: Gather live context (if AWS CLI available)

Run these commands to collect diagnostic data before invoking the agent:

```bash
# Service events (first signal)
aws ecs describe-services \
  --cluster <cluster> \
  --services <service> \
  --query 'services[0].{status:status,runningCount:runningCount,desiredCount:desiredCount,events:events[0:10]}'
```

```bash
# Most recent stopped tasks
aws ecs list-tasks \
  --cluster <cluster> \
  --service-name <service> \
  --desired-status STOPPED \
  --query 'taskArns[0:3]'
```

If stopped task ARNs are returned:
```bash
aws ecs describe-tasks \
  --cluster <cluster> \
  --tasks <task-arn-1> <task-arn-2> \
  --query 'tasks[*].{stoppedReason:stoppedReason,containers:containers[*].{name:name,exitCode:exitCode,reason:reason}}'
```

```bash
# Recent CloudWatch logs
aws logs tail /ecs/<service> --since 20m
```

If no AWS CLI access, use whatever context the user provided.

### Step 2: Invoke the Deploy Debugger agent

Invoke the Agent tool with the subagent definition from `agents/deploy-debugger.md`, passing all gathered context:

> Debug the following ECS deployment failure. Use the triage methodology in your system prompt. Produce a SYMPTOM / ROOT CAUSE / EVIDENCE / REMEDIATION / FOLLOW-UP CHECKS report.
>
> **Service:** <service>
> **Cluster:** <cluster>
> **Service events:** [paste output]
> **Stopped task details:** [paste output]
> **Logs:** [paste output]
> **Additional context:** [user-provided context]

### Step 3: Present findings

Return the agent's structured report. If the agent requests additional diagnostic data (e.g., a specific log stream or security group details), fetch it and re-invoke.

---

## Common Failure Patterns (quick reference)

| Symptom | First thing to check |
|---|---|
| Tasks launch then immediately stop | `stoppedReason` on stopped tasks + CloudWatch logs |
| `CannotPullContainerError` | ECR permissions on execution role; image tag exists in ECR |
| `ResourceInitializationError` | Secrets Manager ARNs in task def; execution role `secretsmanager:GetSecretValue`; VPC endpoints |
| ELB health checks failing | Container port in task def matches ALB target group; health endpoint responds 200; `startPeriod` long enough |
| Deployment stuck at 0 running | Check if old tasks are draining; check minimum healthy percent config |
| `exec format error` | Image architecture mismatch (arm64 image on x86 Fargate) |
| ArgoCD `OutOfSync` | Manual drift in cluster; check `argocd app diff` |

---

## Examples

```
/ecs-debug
Service: payment-api
Cluster: prod-cluster
Error: (service payment-api) (port 8080) is unhealthy in (target-group arn:aws:elasticloadbalancing:...) due to (reason Health checks failed)
Context: Deployed new image tag 2.4.1 about 10 minutes ago, was working on 2.4.0
```

```
/ecs-debug
Service: lease-processor
Cluster: staging-cluster
Logs:
ResourceInitializationError: unable to pull secrets or registry auth: execution resource retrieval failed: unable to retrieve secret from asm: service call has been retried 1 time(s): failed to fetch secret arn:aws:secretsmanager:us-east-1:123456789:secret:lease-processor/db-password-abc123 from secrets manager: AccessDeniedException
```
