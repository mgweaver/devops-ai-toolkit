# /ecs-task-def

Generate a new ECS task definition or review an existing one for security, correctness, and Fargate best practices.

## Usage

```
/ecs-task-def
Mode: generate
Service: <service name>
Image: <ECR image URI or placeholder>
Port: <container port>
CPU: <256|512|1024|2048|4096>
Memory: <512–30720 MiB>
[Secrets: <comma-separated secret names in Secrets Manager>]
[EnvVars: <KEY=VALUE pairs>]
[Context: any additional background]
```

```
/ecs-task-def
Mode: review
<paste task definition JSON here, or provide a file path>
```

## What Happens

**Generate mode:**
1. Builds a Fargate-compatible task definition JSON with proper structure
2. Creates separate task role and execution role stubs with least-privilege policies
3. Wires Secrets Manager references for any provided secrets
4. Configures CloudWatch Logs (`awslogs` driver) with a sensible log group
5. Sets resource limits and a basic health check
6. Flags any inputs that look risky (e.g., privileged mode, `*` resource on secrets)

**Review mode:**
1. Audits the task definition for security issues
2. Checks role separation, secret handling, logging, and resource configuration
3. Produces a structured FINDINGS report with severity ratings

---

## Steps

### Step 1: Determine mode

If `Mode: generate` — proceed to Step 2.
If `Mode: review` — skip to Step 4.

---

### Step 2 (Generate): Scaffold the task definition

Produce a JSON task definition with this structure:

```json
{
  "family": "<service-name>",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "<cpu>",
  "memory": "<memory>",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/<service-name>-execution-role",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/<service-name>-task-role",
  "containerDefinitions": [
    {
      "name": "<service-name>",
      "image": "<image-uri>",
      "portMappings": [{ "containerPort": PORT, "protocol": "tcp" }],
      "essential": true,
      "environment": [],
      "secrets": [],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/<service-name>",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:PORT/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "readonlyRootFilesystem": true,
      "linuxParameters": {
        "initProcessEnabled": true
      }
    }
  ]
}
```

Fill in all provided values. For each secret in `Secrets`, add an entry to the `secrets` array:
```json
{ "name": "SECRET_NAME", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME" }
```

For each `EnvVars` entry that is NOT sensitive, add to `environment`:
```json
{ "name": "KEY", "value": "VALUE" }
```

Flag any env var that looks like a secret (contains `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PASS`, `CRED`) — these should go in Secrets Manager, not `environment`.

---

### Step 3 (Generate): Produce role policy stubs

**Execution Role** (used by ECS agent to pull image and fetch secrets):
```json
{
  "Effect": "Allow",
  "Action": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}
```

Add per-secret Secrets Manager permissions if secrets were provided:
```json
{
  "Effect": "Allow",
  "Action": ["secretsmanager:GetSecretValue"],
  "Resource": "arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME-*"
}
```

**Task Role** (used by the running container):
Start with no permissions. Note: "Add only what this service needs — do not attach AdministratorAccess or broad `*` policies."

---

### Step 4 (Review): Audit the task definition

Check each of the following and report findings:

**Security**
- [ ] `executionRoleArn` and `taskRoleArn` are separate ARNs (not the same role)
- [ ] No secrets in `environment` (flag KEY/SECRET/TOKEN/PASSWORD/PASS/CRED values)
- [ ] `readonlyRootFilesystem: true` set or absence noted
- [ ] No `privileged: true` or `user: root`
- [ ] `secrets` entries reference specific Secrets Manager ARNs, not `*`

**Logging**
- [ ] `logConfiguration` is present and uses `awslogs` driver
- [ ] Log group name follows a consistent convention (`/ecs/<service>`)

**Reliability**
- [ ] `healthCheck` is configured
- [ ] `essential: true` on the primary container
- [ ] CPU and memory are set at task level (required for Fargate)
- [ ] `startPeriod` on health check is long enough for app startup

**Networking**
- [ ] `networkMode: awsvpc` (required for Fargate)
- [ ] `requiresCompatibilities: ["FARGATE"]`

**Output format:**

```
## FINDINGS

### CRITICAL
- [finding]: [resource/field] — [why dangerous] → [fix]

### WARNINGS
- [finding]: [resource/field] — [concern] → [recommendation]

### PASSED
- [item]: ✓

### VERDICT
APPROVED / APPROVED WITH WARNINGS / NEEDS FIXES
```

---

## Examples

```
/ecs-task-def
Mode: generate
Service: lease-processor
Image: 123456789.dkr.ecr.us-east-1.amazonaws.com/lease-processor:latest
Port: 8080
CPU: 512
Memory: 1024
Secrets: lease-processor/db-password, lease-processor/stripe-key
EnvVars: RAILS_ENV=production, LOG_LEVEL=info
```

```
/ecs-task-def
Mode: review
Path: ecs/task-definitions/payment-service.json
```
