# /debug-pipeline

Diagnose a failed GitHub Actions run. Parses logs, identifies the failure root cause, and delivers a concrete fix — not just a description of what failed.

## Usage

```
/debug-pipeline
Run: <GitHub Actions run URL or run ID>
[Repo: <owner/repo — required if using run ID without URL>]
[Context: optional background on what changed before this started failing]
```

Or paste logs directly:

```
/debug-pipeline
<paste GHA log output here>
```

## What Happens

1. Fetches the failed run's logs (if URL/ID provided) or reads pasted logs
2. Identifies the failing job and step
3. Classifies the failure by category
4. Produces a root cause analysis and specific fix

## Steps

### Step 1: Get the logs

**If a run URL or ID was provided:**
```bash
gh run view <RUN_ID> --repo <OWNER/REPO> --log-failed
```

To list recent failed runs:
```bash
gh run list --repo <OWNER/REPO> --status failure --limit 10
```

**If logs were pasted**, use them as-is.

### Step 2: Identify the failure point

Locate:
1. Which **job** failed
2. Which **step** within that job failed
3. The exact **error message** or non-zero exit code
4. The last N lines of output before the failure

### Step 3: Classify the failure

| Category | Indicators |
|---|---|
| **Auth / OIDC** | `Error assuming role`, `AccessDenied`, `InvalidIdentityToken`, `not authorized to perform` |
| **Docker / ECR** | `denied: User not authorized`, `no space left on device`, `manifest unknown`, `failed to push` |
| **ECS Deploy** | `service not found`, `task stopped`, `essential container exited`, `capacity provider error` |
| **Test failure** | Non-zero exit from test runner, assertion errors, coverage threshold |
| **Dependency / install** | `npm ERR!`, `pip install failed`, `module not found`, lock file conflicts |
| **Lint / type check** | Type errors, lint rule violations, format diff |
| **Timeout** | `Job was cancelled`, step exceeded timeout |
| **Flaky / transient** | Network errors, rate limits, intermittent API failures |
| **Config / YAML error** | `Invalid workflow file`, undefined variable, missing required input |
| **Secret / env missing** | `Error: Input required and not supplied`, blank env var causing command failure |

### Step 4: Root cause analysis

For each failure category, investigate:

**Auth / OIDC failures:**
- Is `permissions: id-token: write` present on the job?
- Does the IAM role trust policy match the exact repo, branch, or environment?
- Has the role ARN variable (`AWS_ROLE_ARN`) been set in GitHub env/org variables?

**Docker / ECR failures:**
- Did ECR login succeed before the push step?
- Does the task role have `ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:PutImage`?
- Is the ECR repository name correct and does it exist?

**ECS Deploy failures:**
- Did the new task definition register successfully?
- Is the ECS service name and cluster correct?
- Check the stopped task's `stoppedReason` and `essential container` exit code:
  ```bash
  aws ecs describe-tasks --cluster <cluster> --tasks <task-arn>
  ```
- Common: new image fails health check → ECS rolls back

**Test failures:**
- Is this a genuine regression or an environment issue (missing env var, wrong DB URL)?
- Is it flaky? Run `gh run rerun <RUN_ID>` to check.

**Dependency failures:**
- Is the lock file committed and matching `package.json` / `requirements.txt`?
- Did a package version break its API?

**Secret / env missing:**
- Is the secret defined in the correct scope (repo, environment, or org)?
- Does the job reference the correct `environment:` name to access environment-scoped secrets?

### Step 5: Deliver the fix

Structure the output as:

```
## Pipeline Debug: <job name> / <step name>

### Failure Summary
- Run: <ID or URL>
- Job: <job name>
- Step: <step name>
- Exit code: <code>
- Error: <exact error message>

### Category
<failure category>

### Root Cause
<2–4 sentences explaining WHY it failed, not just what the log says>

### Fix
<concrete change — YAML diff, CLI command, or config change>

### Verify
<how to confirm the fix worked — rerun command, expected output>

### If this recurs
<preventive suggestion — better error messages, retry logic, alert>
```

---

## Examples

```
/debug-pipeline
Run: https://github.com/org/property-saas/actions/runs/9876543210
Context: Started failing after we rotated the ECR repo name in Terraform yesterday.
```

```
/debug-pipeline
Run: 9876543210
Repo: org/property-saas
```

```
/debug-pipeline
Error: AccessDeniedException: User: arn:aws:sts::123456789012:assumed-role/github-actions/GitHubActions
is not authorized to perform: ecr:GetAuthorizationToken on resource: *
  at Process.task (/home/runner/work/_actions/aws-actions/amazon-ecr-login/v2/dist/index.js:246:15)
```
