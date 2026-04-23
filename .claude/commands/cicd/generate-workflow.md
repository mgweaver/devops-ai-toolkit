# /generate-workflow

Generate a production-ready GitHub Actions workflow from requirements. Enforces OIDC auth to AWS, pinned action SHAs, reusable workflow patterns, and environment protection rules.

## Usage

```
/generate-workflow
Service: <service name>
Trigger: <push to main | PR | schedule | manual>
Steps: <describe what the workflow should do>
[Environments: <dev | staging | prod>]
[AWS Role: <IAM role ARN or name pattern>]
[Context: optional background]
```

## What Happens

1. Parses requirements and identifies the workflow type (build, deploy, lint, test, release)
2. Generates a workflow that follows the GHA conventions in `CLAUDE.md`:
   - OIDC auth to AWS (no long-lived keys)
   - Action versions pinned to SHA, not tags
   - Reusable `workflow_call` pattern where applicable
   - Environment protection rules on staging and prod deployments
3. Flags any requirements that conflict with security conventions and suggests alternatives

## Steps

### Step 1: Classify the workflow

Determine the workflow type from the described steps:
- **Build/Test** — lint, unit test, integration test, coverage
- **Deploy** — build image → push ECR → deploy ECS/ArgoCD
- **Release** — tag, changelog, publish
- **Scheduled** — cron-based jobs (backups, reports, cleanup)
- **Hybrid** — test on PR, deploy on merge

### Step 2: Generate the workflow

Apply all of the following conventions:

**OIDC auth to AWS** (never store keys as secrets):
```yaml
permissions:
  id-token: write
  contents: read

- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@8c3f408dc573ad02eff5ea8dfc38eb81a2e2d54a  # v4
  with:
    role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    aws-region: us-east-1
```

**Pin all third-party actions to a full commit SHA**, never a tag:
```yaml
# Correct — pinned SHA
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

# Wrong — mutable tag
uses: actions/checkout@v4
```

**Environment protection** for staging and prod:
```yaml
environment:
  name: production
  url: https://app.example.com
```

**Reusable workflow trigger** when the workflow is a shared component:
```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      AWS_ROLE_ARN:
        required: true
```

**Concurrency control** to prevent overlapping deploys:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**ECS deploy pattern** (if deploying to ECS Fargate):
```yaml
- name: Build, tag, push image to ECR
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
    IMAGE_TAG: ${{ github.sha }}
  run: |
    docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@df9643053eda01f169e64a0e363ea4765d6bca6f  # v2
  with:
    task-definition: task-definition.json
    service: ${{ vars.ECS_SERVICE }}
    cluster: ${{ vars.ECS_CLUSTER }}
    wait-for-service-stability: true
```

### Step 3: Flag conflicts and explain decisions

For any requirement that can't be met safely (e.g., "store AWS keys as secrets"), explain the convention and provide the correct alternative.

### Step 4: Output

Deliver the complete `.github/workflows/<name>.yml` file, followed by:

**Setup checklist:**
- [ ] GitHub environment `<name>` created with required reviewers
- [ ] `AWS_ROLE_ARN` variable set at org/repo level
- [ ] OIDC trust policy added to the IAM role
- [ ] Branch protection rule set on `main`

---

## Examples

```
/generate-workflow
Service: property-api
Trigger: push to main
Steps: run tests, build Docker image, push to ECR, deploy to ECS prod
Environments: staging, prod
AWS Role: arn:aws:iam::123456789012:role/github-actions-property-api
```

```
/generate-workflow
Service: tenant-reports
Trigger: schedule (daily at 2am UTC)
Steps: run Python script that generates tenant billing reports and uploads to S3
```
