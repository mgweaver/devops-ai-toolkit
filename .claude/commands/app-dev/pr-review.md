# /pr-review

Conduct a full pull request review. Automatically invokes the IAM reviewer when `.tf` files are detected in the diff.

## Usage

```
/pr-review
PR: <GitHub PR URL or PR number>
[Focus: optional area to pay extra attention to]
[Context: optional background on the change]
```

Or paste the diff directly:

```
/pr-review
<paste diff here>
```

## What Happens

1. Fetches the PR diff (if URL/number provided) or reads the pasted diff
2. Categorizes changed files by type (IaC, app code, CI/CD, migrations, etc.)
3. **Automatically invokes `iam-reviewer` agent if any `.tf` files are in the diff** — IAM review is never skipped on Terraform changes
4. Invokes `terraform-reviewer` agent if Terraform files are present
5. Reviews Dockerfile and GHA workflow changes inline
6. Reviews application code for correctness, security, and multi-tenancy
7. Reviews database migrations for safety and zero-downtime compatibility
8. Synthesizes a final decision: APPROVE / REQUEST CHANGES / BLOCK

## Steps

### Step 1: Get the diff

If a PR URL or number was provided, fetch the diff:

```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO>
```

If the diff was pasted directly, use it as-is.

### Step 2: Categorize changes

List every changed file and tag it:
- `[IAM/TF]` — Terraform files
- `[DOCKER]` — Dockerfiles
- `[CICD]` — GitHub Actions workflows
- `[APP]` — Application code
- `[MIGRATION]` — Database migrations
- `[CONFIG]` — Config files
- `[TEST]` — Test files

### Step 3: Route to specialist agents

**If any `[IAM/TF]` files are present**, invoke the IAM Reviewer agent with this instruction:

> Read `agents/iam-reviewer.md` and apply it to the following Terraform diff. Produce a full IAM security report with CRITICAL / WARNINGS / SUGGESTIONS / VERDICT sections.
>
> [paste Terraform diff]

**If any `[IAM/TF]` files are present**, also invoke the Terraform Reviewer agent:

> Read `agents/terraform-reviewer.md` and apply it to the following Terraform diff.
>
> [paste Terraform diff]

### Step 4: Inline checks

Apply Dockerfile and GHA workflow checks as described in `agents/pr-reviewer.md`.

### Step 5: Application and migration review

Review app code and migrations following the criteria in `agents/pr-reviewer.md`.

### Step 6: Synthesize

Produce the final structured review per the output format in `agents/pr-reviewer.md`.

---

## Example

```
/pr-review
PR: 142
Focus: The new billing module — making sure tenant isolation is solid.
```

```
/pr-review
PR: https://github.com/org/property-saas/pull/88
```
