# /terraform-security

Security-focused Terraform scan: security groups, IAM, encryption, and public exposure. Faster and narrower than `/terraform-review` — use this when you want a quick security gate, not a full review.

## Usage

```
/terraform-security
Path: <path to .tf files or module directory>
[PR: <PR number or URL>]
[Context: optional background]
```

Or paste the diff:

```
/terraform-security
<paste diff here>
```

## What Happens

1. Reads the Terraform files or diff
2. Runs security-specific checks across four domains: network access, encryption, public exposure, and IAM
3. Invokes the `iam-reviewer` agent for deep IAM analysis if IAM resources are present
4. Produces a security-only report with CRITICAL / WARNINGS / SUGGESTIONS and a pass/fail VERDICT

## Steps

### Step 1: Get the Terraform code

**If a PR URL or number was provided:**
```bash
gh pr diff <PR_NUMBER> --repo <OWNER/REPO>
```

**If a path was provided:**
```bash
find <path> -name "*.tf" | head -50
```

**If a diff was pasted**, use it as-is.

### Step 2: Run security checks

Apply the following checks directly. These are the security-relevant subset of the full terraform-reviewer passes.

#### Network / Security Groups
- `0.0.0.0/0` ingress on any port other than 80/443 on a public ALB → **CRITICAL**
- `0.0.0.0/0` ingress on management ports (22, 3389, 5432, 3306, 6379) → **CRITICAL**
- RDS, ElastiCache, or internal services in `public_subnets` → **CRITICAL**
- Security group rules using CIDR where SG-to-SG reference is possible → **WARNING**
- Overly broad egress (`0.0.0.0/0`) without documented reason → **WARNING**

#### Encryption at Rest
- RDS: `storage_encrypted = false` or missing → **CRITICAL**
- S3: no `server_side_encryption_configuration` → **CRITICAL**
- EBS: `encrypted = false` or missing → **WARNING**
- Secrets in plaintext in `user_data`, `environment` vars, or `tags` → **CRITICAL**

#### Public Exposure
- RDS with `publicly_accessible = true` → **CRITICAL** (unless explicit justification)
- S3 bucket: `block_public_acls = false` or `block_public_policy = false` → **CRITICAL**
- S3 bucket: `acl = "public-read"` or `"public-read-write"` → **CRITICAL** unless it's a known public assets bucket
- ALB with listener on non-standard port open to `0.0.0.0/0` → **WARNING**
- CloudFront distribution missing WAF in production context → **WARNING**

#### IAM (surface check — deep analysis delegated to iam-reviewer)
- `"Action": "*"` or `"Resource": "*"` on mutating actions → **CRITICAL**
- `aws_iam_access_key` resource (long-lived credentials) → **WARNING**
- Missing `condition` block on cross-account trust → **WARNING**

### Step 3: Invoke IAM Reviewer agent (if IAM resources present)

If the diff contains `aws_iam_role`, `aws_iam_policy`, `aws_iam_role_policy`, or `data.aws_iam_policy_document`, invoke the Agent tool with the subagent definition from `agents/iam-reviewer.md`:

> Perform a full IAM security audit on the following Terraform. Return CRITICAL / WARNINGS / SUGGESTIONS / VERDICT.
>
> [paste IAM-relevant Terraform]

### Step 4: Produce security report

```
## Terraform Security Scan

### Network / Security Groups
[findings or "No issues found"]

### Encryption
[findings or "No issues found"]

### Public Exposure
[findings or "No issues found"]

### IAM
[iam-reviewer output summary, or inline findings if no IAM agent invoked]

---

**CRITICAL issues:** [count]
**WARNINGS:** [count]

**VERDICT:** PASS / PASS WITH WARNINGS / FAIL
```

FAIL = any CRITICAL issue. Engineers should resolve all CRITICALs before merge.

---

## Example

```
/terraform-security
Path: terraform/modules/alb
Context: Opening a new listener for the internal API — want to confirm the SG rules are tight.
```

```
/terraform-security
PR: 178
```
