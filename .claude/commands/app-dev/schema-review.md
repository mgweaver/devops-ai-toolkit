# /schema-review

Review a database schema or migration for normalization, index coverage, multi-tenancy isolation, and zero-downtime migration safety.

## Usage

```
/schema-review
DB: PostgreSQL | MySQL | other
[Service: <service name>]
[Tenancy: shared schema | schema-per-tenant | row-level (tenant_id column)]
```

Then paste the schema DDL, migration file(s), or ORM model definitions.

## What Happens

1. Parses the schema or migration and builds an entity map
2. Checks normalization and data modeling (1NF–3NF, appropriate denormalization)
3. Audits indexes: coverage for common query patterns, missing FKs, over-indexing
4. Verifies multi-tenancy isolation: every tenant-scoped table must have `tenant_id` as part of its access patterns
5. Checks migration safety: lock-free operations, backfill strategy, rollback path
6. Flags naming inconsistencies, missing constraints, and type mismatches
7. Produces a structured report with CRITICAL / WARNINGS / SUGGESTIONS

---

## Steps

### Step 1: Parse and map

List every table with its columns, types, constraints, and indexes. Build a simple entity-relationship map showing foreign keys.

### Step 2: Normalization check

- **1NF**: No repeating groups or arrays storing multiple values in one column (unless intentional with JSONB)
- **2NF**: No partial dependencies on composite keys
- **3NF**: No transitive dependencies
- Flag intentional denormalization (e.g., cached aggregates) — it's fine if documented

### Step 3: Index audit

Check for:
- **Missing indexes**: every FK column should be indexed; every column used in a `WHERE`, `ORDER BY`, or `GROUP BY` in hot paths
- **Missing composite indexes**: if queries filter on `(tenant_id, status)`, a single-column index on `tenant_id` is not enough
- **Redundant indexes**: a composite index on `(a, b)` makes a single index on `(a)` redundant
- **Over-indexing writes**: tables with very high write rates should not have more indexes than necessary

### Step 4: Multi-tenancy isolation

For the platform's row-level tenancy model:
- Every tenant-scoped table must have a `tenant_id` column with a NOT NULL constraint and an FK to the `tenants` table
- `tenant_id` must be the leading column in composite indexes on large tables
- Verify there are no query paths that could return cross-tenant data (no `SELECT *` without `WHERE tenant_id = ?` in hot paths)
- Check for RLS (Row Level Security) policies if using PostgreSQL — flag if absent on sensitive tables

### Step 5: Migration safety

For each migration file:
- **Lock-free ADD COLUMN**: `ADD COLUMN` with a default in PostgreSQL ≥12 is safe; earlier versions require backfills
- **NOT NULL without default**: adding a NOT NULL column to a large table requires a backfill or default — flag if missing
- **Index creation**: must use `CREATE INDEX CONCURRENTLY` — a plain `CREATE INDEX` locks the table
- **Constraint addition**: `ADD CONSTRAINT` acquires a full table lock — must be done in a transaction with a lock timeout
- **Column drops**: verify no application code still references the column before dropping
- **Rollback path**: every destructive migration should have a corresponding down migration

### Step 6: Naming and consistency

- Table names: plural snake_case (`lease_payments`, not `LeasePayment`)
- Column names: snake_case; `id` for PK, `<table_singular>_id` for FKs
- Timestamps: `created_at` / `updated_at` on every table, timezone-aware (`TIMESTAMPTZ`)
- Boolean columns: `is_` or `has_` prefix (e.g., `is_active`, `has_signed`)
- Enum types: use PostgreSQL enums or a constrained `VARCHAR` with a CHECK constraint — not bare strings

---

## Output Format

```
## Schema Review: <Service / Migration>

### Entity Map
<tables with key columns and relationships>

### CRITICAL (data loss, correctness, or tenancy isolation risk)
<numbered list>

### WARNINGS (performance, safety, or migration risk)
<numbered list>

### SUGGESTIONS (naming, conventions, optional improvements)
<numbered list>

### Migration Safety
SAFE | UNSAFE — <one-line summary>

### VERDICT: APPROVE | REQUEST CHANGES | BLOCK
```

---

## Example

```
/schema-review
DB: PostgreSQL
Service: Lease management
Tenancy: row-level (tenant_id column)

CREATE TABLE leases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_id UUID NOT NULL REFERENCES properties(id),
  start_date DATE NOT NULL,
  end_date DATE,
  monthly_rent NUMERIC(10, 2),
  status VARCHAR(20),
  created_at TIMESTAMP
);

-- migration: add tenant scoping
ALTER TABLE leases ADD COLUMN tenant_id UUID NOT NULL REFERENCES tenants(id);
CREATE INDEX ON leases (tenant_id);
```
