# /api-design

Design a new REST or GraphQL API, or review an existing one for correctness, consistency, and security.

## Usage

```
/api-design
Mode: design | review
Service: <service name and brief description>
[Consumers: who calls this API — web app, mobile, internal services]
[Auth: how callers authenticate — JWT, API key, service role]
[Constraints: rate limits, SLA, breaking change policy]
```

For review mode, paste the existing spec or route definitions after the arguments.

## What Happens

1. Clarifies mode (design vs. review) and gathers missing context
2. Identifies the domain entities and their relationships
3. Designs or audits the endpoint surface: naming, verbs, status codes, pagination
4. Reviews auth model and authorization scopes
5. Checks for multi-tenancy isolation (all queries and mutations scoped to tenant)
6. Flags breaking-change risks and versioning gaps
7. Produces the full API contract or annotated review with APPROVE / REQUEST CHANGES verdict

---

## Steps

### Step 1: Establish context

Confirm:
- Is this a new design or a review of an existing API?
- What service does it belong to?
- Who are the consumers, and what auth mechanism is in use?
- Are there existing conventions in the codebase (e.g., `/api/v1/`, envelope shape, error format)?

### Step 2: Domain modeling

Enumerate the core entities (e.g., `Property`, `Tenant`, `Lease`, `Payment`) and their ownership. Identify which entities are tenant-scoped vs. global. This drives URL structure and authorization logic.

### Step 3: Endpoint surface (REST) or schema (GraphQL)

**REST:**
- Use resource-based URLs: `/properties/{id}/units`, not `/getPropertyUnits`
- Verbs: GET (read), POST (create), PUT/PATCH (update), DELETE
- Status codes: 200/201/204/400/401/403/404/409/422/500
- Pagination: cursor-based preferred over offset for large datasets
- Filtering: query params (`?status=active&owner_id=xyz`)
- Versioning: path prefix `/v1/` — no content-type negotiation

**GraphQL:**
- Queries for reads, Mutations for writes, Subscriptions for real-time
- Connections pattern for paginated lists
- Input types for mutations
- Never expose internal IDs directly — use opaque global IDs

### Step 4: Auth and authorization

- Confirm authentication mechanism (JWT claims, API key header, mTLS)
- Every endpoint must declare its required scope or role
- Multi-tenant rule: **every data-access path must filter by `tenant_id` from the auth context, never from the request body**
- Flag any endpoint where tenant isolation could be bypassed (IDOR risk)

### Step 5: Breaking-change and versioning check

For review mode only:
- Flag any field removals, type changes, or renamed fields as breaking
- Flag required fields added to existing requests as breaking
- Flag status code changes as breaking
- Recommend deprecation strategy for any breaking changes

### Step 6: Output

**Design mode — produce:**

```
## API Contract: <Service Name>

### Entities
<entity list with tenant-scoping notes>

### Endpoints
<method + path + description + auth + request/response shapes>

### Error Format
<standard error envelope>

### Open Questions
<anything that needs product/engineering decision>
```

**Review mode — produce:**

```
## API Review: <Service Name>

### CRITICAL (must fix before merge)
<numbered list>

### WARNINGS (should fix)
<numbered list>

### SUGGESTIONS (optional improvements)
<numbered list>

### VERDICT: APPROVE | REQUEST CHANGES
```

---

## Example

```
/api-design
Mode: design
Service: Lease management service — handles lease creation, renewals, and terminations
Consumers: React web app, internal billing service
Auth: JWT with tenant_id and role claims
Constraints: Read-heavy, must support cursor pagination, no breaking changes to existing /v1/ routes
```

```
/api-design
Mode: review
Service: Payment processing API

POST /payments
GET  /payments/{id}
GET  /payments?tenant_id=abc
DELETE /payments/{id}
```
