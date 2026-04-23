# /terraform-review

Run a full multi-pass Terraform review: security, cost flags, drift risk, and module hygiene.

## Usage

```
/terraform-review
Path: <path to .tf files or module directory>
[PR: <PR number or URL — fetches diff automatically>]
[Context: optional background on what this change does]
```

Or paste the Terraform diff directly:

```
/terraform-review
<paste diff here>
```

## What Happens

1. Reads the Terraform files or diff
2. Invokes the `terraform-reviewer` agent for a four-pass analysis:
   - **Security**: SGs, encryption, public exposure, IAM surface
   - **Cost**: instance tier changes, NAT gateways, new distributions
   - **Drift risk**: state hygiene, workspace separation, orphaned resources
   - **Module hygiene**: versioning, variable quality, tagging, provider config
3. Invokes the `iam-reviewer` agent if any IAM resources are present
4. Synthesizes findings into a structured report with a final VERDICT

## Steps

### Step 1: Get the Terraform code

**If a PR URL or number was provided:**
```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO>
```
Filter to `.tf` and `.tfvars` files.

**If a path was provided**, read the relevant files:
```bash
find <path> -name "*.tf" | head -50
```

**If a diff was pasted**, use it as-is.

### Step 2: Invoke the Terraform Reviewer agent

Invoke the Agent tool with the subagent definition from `agents/terraform-reviewer.md`, passing the Terraform diff or file contents as context.

Instruction to agent:
> Apply all four review passes (Security, Cost, Drift Risk, Module Hygiene) to the following Terraform code. Produce the full structured report.
>
> [paste Terraform content]

### Step 3: Invoke the IAM Reviewer agent (if IAM resources present)

If the diff contains any of: `aws_iam_role`, `aws_iam_policy`, `aws_iam_role_policy`, `data.aws_iam_policy_document`, invoke the Agent tool with the subagent definition from `agents/iam-reviewer.md`:

> Perform a full IAM security audit on the following Terraform diff. Produce CRITICAL / WARNINGS / SUGGESTIONS / VERDICT sections.
>
> [paste IAM-relevant sections]

### Step 4: Synthesize

Present findings from both agents in a single report. Lead with any blocking issues.

---

## Example

```
/terraform-review
Path: terraform/modules/rds
Context: Adding read replica and enabling Multi-AZ for the tenant database.
```

```
/terraform-review
PR: 201
```
