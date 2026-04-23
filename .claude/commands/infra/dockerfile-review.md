# /dockerfile-review

Security and best-practices review of a Dockerfile. Covers base image hygiene, build security, runtime hardening, and layer efficiency.

## Usage

```
/dockerfile-review
Path: <path to Dockerfile or directory>
[Service: <service name — helps contextualize the review>]
[Context: what this image is for, any known constraints]
```

Or paste the Dockerfile directly:

```
/dockerfile-review
<paste Dockerfile here>
```

## What Happens

1. Reads the Dockerfile (fetches by path or uses pasted content)
2. Runs through six review passes in order
3. Produces a structured findings report with a VERDICT

---

## Review Passes

### Pass 1: Base Image

- [ ] Uses a specific version tag — not `latest`, not `stable` (e.g., `node:20.11-alpine3.19`)
- [ ] Uses a minimal base: `alpine`, `distroless`, or `-slim` variants preferred over full `ubuntu`/`debian`
- [ ] Base image is from a trusted source (official Docker Hub library, AWS ECR Public Gallery, or org-controlled registry)
- [ ] If using `ubuntu` or `debian`, flag it as unnecessary weight unless there's a clear reason
- [ ] Checks for known vulnerable base tags (e.g., `node:14`, `python:3.7`, anything EOL)

### Pass 2: Build-Time Security

- [ ] No secrets or credentials baked into the image:
  - `ARG` or `ENV` containing `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PASS`, `CRED` — flag as critical
  - `COPY` of `.env`, `*.pem`, `*.key`, `id_rsa`, `credentials`, `~/.aws` — flag as critical
  - `RUN` commands with inline credentials (look for `curl -u`, `-H "Authorization"`, `export SECRET=`)
- [ ] Uses multi-stage builds if the final image doesn't need build tools (compilers, package managers, test deps)
- [ ] `COPY --chown` used instead of a separate `RUN chown` layer

### Pass 3: Dependency Installation

- [ ] Package manager caches are cleaned in the same `RUN` layer:
  - `apt-get clean && rm -rf /var/lib/apt/lists/*`
  - `pip install --no-cache-dir`
  - `npm ci --omit=dev` (not `npm install`)
  - `yarn install --frozen-lockfile --production`
- [ ] `apt-get update` and `apt-get install` are in the same `RUN` layer (prevents stale cache hits)
- [ ] Dev dependencies are excluded from the production image
- [ ] Uses lock files (`package-lock.json`, `requirements.txt`, `go.sum`) — flag if absent

### Pass 4: Runtime Hardening

- [ ] Container runs as a non-root user:
  - `USER` directive is present and not `root`
  - If `USER` is missing, flag as a warning
- [ ] `WORKDIR` is set explicitly (not relying on default `/`)
- [ ] `EXPOSE` matches the port the application actually listens on
- [ ] No `--privileged` or `cap_add` in the Dockerfile (these belong in task definitions if truly needed)
- [ ] `HEALTHCHECK` is defined (or note that it will be set in the ECS task definition)
- [ ] `ENTRYPOINT` uses exec form (`["command", "arg"]`), not shell form (`command arg`) — exec form ensures signals reach the process

### Pass 5: Layer Efficiency

- [ ] Static/infrequently-changing layers (`COPY package.json`, `RUN npm ci`) come before frequently-changing ones (`COPY . .`) to maximize cache reuse
- [ ] No unnecessary files copied — check for `.dockerignore` reference and flag if broad `COPY . .` is used without it
- [ ] Multiple `RUN` commands that could be chained are not creating unnecessary intermediate layers
- [ ] No `COPY` of files that are immediately deleted in the next layer (move into the same `RUN` if needed)

### Pass 6: ECS Fargate Compatibility

- [ ] No `VOLUME` directives that expect persistent storage (Fargate uses ephemeral storage)
- [ ] Application binds to `0.0.0.0`, not `127.0.0.1` (common trap in dev configs)
- [ ] `ENTRYPOINT` / `CMD` starts a foreground process — not a daemon or `supervisord` unless absolutely necessary
- [ ] Image is compatible with `linux/amd64` (Fargate default) — flag if `FROM --platform=linux/arm64` without Graviton task config

---

## Output Format

```
## Dockerfile Review: <service or filename>

### CRITICAL (must fix — security risk or broken build)
- [finding]: [line/instruction] — [why dangerous] → [fix]

### WARNINGS (should fix — best practice violations)
- [finding]: [line/instruction] — [concern] → [recommendation]

### SUGGESTIONS (nice to have)
- [finding]: brief note

### PASSED
- [check]: ✓

### VERDICT
APPROVED / APPROVED WITH WARNINGS / NEEDS FIXES
```

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
Context: Python Flask app, runs on port 5000, needs access to Secrets Manager at runtime.

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```
