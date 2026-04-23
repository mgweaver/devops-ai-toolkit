# /review-workflow

Security and best-practices audit of an existing GitHub Actions workflow. Checks for supply-chain risks, credential hygiene, secret exposure, and GHA convention compliance.

## Usage

```
/review-workflow
File: <path to .yml workflow file>
[Context: optional background on what this workflow does]
```

Or paste the workflow YAML directly:

```
/review-workflow
<paste workflow YAML here>
```

## What Happens

1. Reads or receives the workflow YAML
2. Runs a structured audit across five domains: supply chain, credentials, secret hygiene, permissions, and operational hygiene
3. Categorizes findings as CRITICAL / WARNING / SUGGESTION
4. Outputs a final VERDICT with a prioritized fix list

## Audit Passes

### Pass 1: Supply Chain Security

Check every `uses:` action reference:

| Finding | Severity |
|---|---|
| Action pinned to mutable tag (`@v3`, `@main`, `@latest`) | CRITICAL |
| Action pinned to SHA — correct | PASS |
| Third-party action not from a trusted org | WARNING |
| `run:` step downloads and executes remote scripts | CRITICAL |

Trusted orgs: `actions/`, `aws-actions/`, `docker/`, `github/`.

For any CRITICAL, provide the SHA-pinned replacement:
```yaml
# Before (vulnerable)
uses: actions/checkout@v4

# After (safe)
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

### Pass 2: AWS Credential Hygiene

| Finding | Severity |
|---|---|
| `AWS_ACCESS_KEY_ID` stored as a secret and used in workflow | CRITICAL |
| Static credentials passed via `env:` block | CRITICAL |
| OIDC (`aws-actions/configure-aws-credentials` with `role-to-assume`) | PASS |
| `role-to-assume` references a wildcard or `*` action policy | CRITICAL |
| Missing `permissions: id-token: write` for OIDC | WARNING |

If static credentials are found, provide the OIDC migration pattern.

### Pass 3: Secret Exposure Risk

| Finding | Severity |
|---|---|
| Secret printed in `run:` step (`echo ${{ secrets.X }}`) | CRITICAL |
| Secret passed as env var to untrusted action | WARNING |
| `pull_request_target` trigger with access to secrets — classic exfiltration vector | CRITICAL |
| Secret referenced in `if:` condition (may be exposed in logs) | WARNING |
| Secrets scoped to environment (correct) vs. repo-level (note) | INFO |

### Pass 4: Permissions

| Finding | Severity |
|---|---|
| `permissions: write-all` or no permissions key (defaults to write) | CRITICAL |
| Job-level permissions broader than needed | WARNING |
| `contents: write` on a job that only reads code | WARNING |
| Minimal permissions correctly scoped | PASS |

Recommend minimal permissions for the detected workflow type:
- Build/test only: `contents: read`
- OIDC deploy: `id-token: write, contents: read`
- PR comment: `pull-requests: write, contents: read`

### Pass 5: Operational Hygiene

| Finding | Severity |
|---|---|
| No concurrency control on deploy workflows | WARNING |
| Staging/prod jobs lack `environment:` protection | WARNING |
| `continue-on-error: true` on security-relevant steps | WARNING |
| Secrets interpolated directly into `run:` shell commands (injection risk) | CRITICAL |
| No timeout set on long-running jobs | SUGGESTION |
| Matrix strategy missing `fail-fast: false` for independent jobs | SUGGESTION |

Shell injection example to flag:
```yaml
# Vulnerable — user-controlled input in shell
run: echo "Deploying ${{ github.event.inputs.version }}"

# Safe — use env var
env:
  VERSION: ${{ github.event.inputs.version }}
run: echo "Deploying $VERSION"
```

## Output Format

```
## Workflow Audit: <filename>

### Summary
- Trigger: <push | PR | schedule | manual>
- Environments targeted: <list>
- AWS auth method: <OIDC | static keys | none>

### CRITICAL (must fix before merging)
[numbered list]

### WARNINGS (fix soon)
[numbered list]

### SUGGESTIONS (consider improving)
[numbered list]

### VERDICT
BLOCK | REQUEST CHANGES | APPROVE WITH NOTES

### Fix Priority List
1. [highest risk item + corrected YAML]
2. ...
```

---

## Examples

```
/review-workflow
File: .github/workflows/deploy.yml
Context: This is our ECS prod deploy — triggered on merge to main.
```

```
/review-workflow
name: CI

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
```
