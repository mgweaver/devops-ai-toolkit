# /iam-audit

Standalone IAM least-privilege audit. Use this when you want to review IAM policies, roles, or Terraform IAM resources in isolation — without a full PR or Terraform review.

## Usage

```
/iam-audit
Target: <one of the options below>
[Context: optional background — what this role/policy does, which service uses it]
```

**Target options:**
- A file path: `terraform/modules/ecs/iam.tf`
- A PR number or URL: `PR: 142`
- A pasted policy document or Terraform block (paste directly after the command)
- An AWS role name to fetch live: `Role: arn:aws:iam::123456789012:role/my-ecs-task-role`

## What Happens

1. Reads the IAM policy, role, or Terraform block from the specified target
2. Invokes the `iam-reviewer` agent for a full least-privilege audit
3. Returns a structured report: CRITICAL / WARNINGS / SUGGESTIONS / VERDICT

## Steps

### Step 1: Get the IAM content

**If a file path was provided**, read it:
```bash
cat <file_path>
```

**If a PR was provided:**
```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO>
```
Extract only IAM-related files (`*iam*.tf`, `*role*.tf`, `*policy*.tf`, `data.aws_iam_policy_document.*`).

**If an AWS role ARN or name was provided**, fetch the live policy:
```bash
# Get the role's attached policies
aws iam list-attached-role-policies --role-name <ROLE_NAME>

# Get the role's inline policies
aws iam list-role-policies --role-name <ROLE_NAME>

# Get the trust policy
aws iam get-role --role-name <ROLE_NAME> --query 'Role.AssumeRolePolicyDocument'

# Get each attached managed policy document
aws iam get-policy-version \
  --policy-arn <POLICY_ARN> \
  --version-id $(aws iam get-policy --policy-arn <POLICY_ARN> --query 'Policy.DefaultVersionId' --output text)
```

**If a policy or Terraform block was pasted**, use it as-is.

### Step 2: Invoke the IAM Reviewer agent

Invoke the Agent tool with the subagent definition from `agents/iam-reviewer.md`, passing the IAM content as context.

Instruction to agent:
> Perform a full IAM least-privilege audit on the following. Apply all six check categories: Action Scope, Resource Scope, Trust Relationships, IAM Anti-Patterns, ECS-Specific Checks, and GitHub Actions / OIDC Checks where applicable.
>
> Context provided by user: [insert any context the user gave about the role's purpose]
>
> [paste IAM content]

### Step 3: Present findings

Present the agent's full report. If the user provided context about the role's purpose, note whether the permissions are appropriate for that stated purpose.

---

## When to Use This vs. Other Commands

| Scenario | Use |
|---|---|
| Reviewing IAM changes in a PR that also has app code | `/pr-review` (routes to iam-reviewer automatically) |
| Reviewing a Terraform PR with IAM + other infra | `/terraform-review` |
| Auditing a live AWS role (no Terraform) | `/iam-audit Role: <role-name>` |
| Auditing IAM-only Terraform files | `/iam-audit Target: <file>` |
| Security gate before merging IaC | `/terraform-security` |

---

## Example

```
/iam-audit
Target: terraform/modules/ecs/task-role.tf
Context: This is the task role for the payments service — it reads from S3, writes to SQS, and fetches a secret from Secrets Manager.
```

```
/iam-audit
Role: arn:aws:iam::123456789012:role/prod-payments-task-role
Context: Auditing the live role before we migrate it to Terraform.
```

```
/iam-audit
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
```
