# /dockerfile-review

Dockerfile review combining Trivy (security, secrets, misconfigurations) with a focused manual pass for layer efficiency and ECS Fargate compatibility — the parts Trivy can't assess.

## Usage

```
/dockerfile-review
Path: <path to Dockerfile or directory>
[Service: <service name>]
[Context: what this image is for, any known constraints]
```

Or paste the Dockerfile directly:

```
/dockerfile-review
<paste Dockerfile here>
```

---

## Steps

### Step 1: Get the Dockerfile

**If a path was provided**, read it. If no path was given, look for `Dockerfile` in the current directory.

**If a Dockerfile was pasted**, use it as-is. Skip the Trivy steps (no path to scan) and proceed directly to Step 4 with only the manual passes.

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

Run `trivy --version` again after the install attempt. If Trivy is still unavailable, skip Step 3 and note it at the top of the report — the manual passes in Step 4 still run.

### Step 3: Run Trivy scans

**Misconfiguration scan** (catches: missing USER, missing HEALTHCHECK, privileged flags, root usage, etc.):
```bash
trivy config <path> --format json --exit-code 0 2>/dev/null
```

**Secrets scan** (catches: baked-in credentials, tokens, keys):
```bash
trivy fs <path> --scanners secret --format json --exit-code 0 2>/dev/null
```

Map Trivy severities: `CRITICAL`/`HIGH` → **CRITICAL**, `MEDIUM` → **WARNING**, `LOW`/`UNKNOWN` → **SUGGESTION**.

### Step 4: Manual passes (read the Dockerfile)

Run only these passes manually — they require understanding context and structure that Trivy doesn't assess:

#### Layer Efficiency

- [ ] Static/infrequently-changing layers (`COPY package.json`, `RUN npm ci`) come before frequently-changing ones (`COPY . .`)
- [ ] Package manager caches are cleaned in the same `RUN` layer as the install (`apt-get clean && rm -rf /var/lib/apt/lists/*`, `pip install --no-cache-dir`, `npm ci --omit=dev`)
- [ ] `apt-get update` and `apt-get install` are in the same `RUN` layer
- [ ] Multi-stage build used if the final image doesn't need build tools — flag as WARNING if compilers/build deps appear in a single-stage image
- [ ] No `.dockerignore` + broad `COPY . .` — flag as WARNING

#### ECS Fargate Compatibility

- [ ] Application binds to `0.0.0.0`, not `127.0.0.1` — flag if a port binding is visible in CMD/ENTRYPOINT
- [ ] `ENTRYPOINT` / `CMD` uses exec form (`["command", "arg"]`) not shell form (`command arg`) — shell form means PID 1 is sh, signals don't reach the app
- [ ] No `VOLUME` directives expecting persistent storage (Fargate storage is ephemeral)
- [ ] `FROM --platform=linux/arm64` without a corresponding Graviton task config → WARNING
- [ ] `CMD` starts a foreground process, not a daemon

### Step 5: Produce report

Merge Trivy findings and manual pass findings. Deduplicate anything Trivy already caught.

```
## Dockerfile Review: <service or filename>

### CRITICAL (security risk — fix before build)
- [finding]: [instruction or line] — [why] → [fix]

### WARNINGS (should fix)
- [finding]: [instruction or line] — [concern] → [recommendation]

### SUGGESTIONS (nice to have)
- [finding]: brief note

### PASSED
- [check]: ✓

---
Trivy: [ran / unavailable / skipped — pasted input]

**VERDICT:** APPROVED / APPROVED WITH WARNINGS / NEEDS FIXES
```

NEEDS FIXES = any CRITICAL. Resolve all CRITICALs before pushing to ECR.

---

## Examples

```
/dockerfile-review
Path: services/lease-processor/Dockerfile
Service: lease-processor
```

```
/dockerfile-review
Service: payment-api
Context: Python Flask app, port 5000, reads secrets from Secrets Manager at runtime.

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```
