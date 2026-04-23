# /implement-story

Turn a shaped Shape Up story (or a Jira/Linear ticket) into a concrete implementation plan with code scaffolding, file-by-file steps, and explicit scope boundaries.

## Usage

```
/implement-story
Story: <story title or ticket ID>
Appetite: <S (2 weeks) | L (6 weeks)>
[Stack: <languages / frameworks in scope>]
[Service: <which service repo this lives in>]
[Context: <link to pitch, design doc, or relevant background>]
```

Then paste the story description or pitch summary.

## What Happens

1. Parses the story to extract the core problem, desired outcome, and explicit no-gos
2. Applies the scope hammer: trims anything that expands scope beyond the appetite
3. Produces a file-by-file implementation plan with clear entry and exit points
4. Generates code scaffolding (types, interfaces, stub handlers) the engineer can build from
5. Identifies the highest-risk technical unknowns and suggests a spike approach for each
6. Outputs a checklist the engineer can use to track progress

---

## Steps

### Step 1: Parse the story

Extract:
- **Problem**: what user pain or business need is being addressed?
- **Outcome**: what does "done" look like from the user's perspective?
- **No-gos**: what is explicitly out of scope?
- **Rabbit holes**: what tempting tangents to avoid?

If the story is vague, ask one clarifying question before proceeding. One question only.

### Step 2: Apply the scope hammer

Given the appetite:
- **Small (2 weeks)**: the plan must fit in ~10 engineer-days. Cut anything that can ship separately without degrading the core outcome.
- **Large (6 weeks)**: the plan must fit in ~30 engineer-days. Big features still need a hard boundary.

List explicitly what is **in scope** and what is **deferred**. Frame deferred work as future pitches, not failures.

### Step 3: Implementation plan

Break work into logical layers. For each layer, list:
- Files to create or modify (with paths relative to the service root)
- What changes in each file
- Dependencies between layers (what must be done before what)

Standard layers for this stack:
1. **Data** — migrations, model definitions, repository layer
2. **Domain / Service** — business logic, validation, event publishing
3. **API** — route handlers, request/response types, auth middleware
4. **Infrastructure** — any Terraform, ECS task def changes, Secrets Manager entries
5. **Tests** — unit tests for domain logic, integration tests for API layer
6. **CI/CD** — any pipeline changes needed to ship this

### Step 4: Code scaffolding

Generate stub code for the highest-value files:
- Type definitions / interfaces
- Repository method signatures with TODOs
- Route handler shells with request parsing and auth guard
- Migration file (DDL only, no data)

Keep stubs minimal — they define the contract, not the implementation. The engineer fills in the logic.

### Step 5: Risk identification

List the top 1–3 technical unknowns that could blow the appetite:
- External API behavior that hasn't been tested
- Database migrations on large tables
- Third-party library limitations
- Multi-tenancy edge cases

For each risk: suggest a time-boxed spike (max 1 day) to resolve it before committing to the full implementation.

### Step 6: Output

```
## Implementation Plan: <Story Title>

### Scope
**In:** <bulleted list>
**Deferred:** <bulleted list>

### Layer Plan
<table: Layer | Files | Notes>

### Code Scaffolding
<code blocks per file>

### Risks + Spikes
<numbered list: risk → proposed spike>

### Checklist
- [ ] <task 1>
- [ ] <task 2>
...
```

---

## Example

```
/implement-story
Story: Lease renewal notifications
Appetite: S (2 weeks)
Stack: Python (FastAPI), PostgreSQL, SQS
Service: lease-service

Tenants should receive an email notification 60 days before their lease expires,
then again at 30 days and 7 days. Notification content is managed in the admin UI
(out of scope here). No-gos: no SMS, no in-app notifications, no retry UI.
```
