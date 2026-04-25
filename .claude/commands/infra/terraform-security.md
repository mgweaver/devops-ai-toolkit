# /terraform-security

Security scan for Terraform configs powered by [Trivy](https://aquasecurity.github.io/trivy/). Runs `trivy config` (misconfiguration) and `trivy fs --scanners secret` (secrets) and formats the findings. Much faster and cheaper than manual review — Trivy does the analysis, Claude formats the results.

## Usage

```
/terraform-security
Path: <path to .tf files or module directory>
[Context: optional background]
```

---

## Steps

### Step 1: Resolve the path

If no path was given, use `.` (current directory).

### Step 2: Ensure Trivy is installed

```bash
trivy --version
```

If the command fails, detect the platform and attempt to install:

```bash
# macOS
brew install trivy

# Windows (Chocolatey)
choco install trivy -y

# Windows (winget)
winget install AquaSecurity.Trivy

# Linux (apt)
sudo apt-get install -y trivy

# Linux (rpm)
sudo rpm -ivh https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.rpm
```

Run `trivy --version` again after the install attempt. If Trivy is still unavailable, note it in the report header and skip to the fallback manual checks in Step 5.

### Step 3: Run misconfiguration scan

```bash
trivy config <path> --format json --exit-code 0 2>/dev/null
```

### Step 4: Run secrets scan

```bash
trivy fs <path> --scanners secret --format json --exit-code 0 2>/dev/null
```

### Step 5: Parse and report

Read the JSON from both scans. Build the report below. Map Trivy severities to the report:

- Trivy `CRITICAL` / `HIGH` → **CRITICAL**
- Trivy `MEDIUM` → **WARNING**
- Trivy `LOW` / `UNKNOWN` → **SUGGESTION**

Deduplicate findings. Group by category. For each finding include: severity, resource, check ID, brief description, and file:line if available.

If both scans return zero results, write "No issues found" in every section.

```
## Terraform Security Scan

### Misconfigurations
[findings grouped by resource type, or "No issues found"]

### Secrets / Hardcoded Credentials
[findings from secrets scan, or "No issues found"]

---

**CRITICAL issues:** [count]
**WARNINGS:** [count]

**VERDICT:** PASS / PASS WITH WARNINGS / FAIL
```

FAIL = any CRITICAL. Resolve all CRITICALs before merge.

---

## Fallback: Manual checks (Trivy unavailable)

If Trivy could not be installed, read the `.tf` files and apply these high-signal checks only:

- `0.0.0.0/0` ingress on ports other than 80/443 → **CRITICAL**
- `0.0.0.0/0` ingress on management ports (22, 3389, 5432, 3306, 6379) → **CRITICAL**
- `storage_encrypted = false` on RDS → **CRITICAL**
- `publicly_accessible = true` on RDS → **CRITICAL**
- S3 `block_public_acls = false` or `block_public_policy = false` → **CRITICAL**
- `"Action": "*"` or `"Resource": "*"` on mutating IAM actions → **CRITICAL**
- `aws_iam_access_key` resource (long-lived credentials) → **WARNING**
- Plaintext secrets in `environment` vars or `tags` → **CRITICAL**

Note `⚠️ Trivy unavailable — manual checks only. Install Trivy for full coverage.` at the top of the report.

---

## Example

```
/terraform-security
Path: terraform/modules/alb
Context: Opening a new listener for the internal API.
```
