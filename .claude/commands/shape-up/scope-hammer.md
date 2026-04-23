# /scope-hammer

Given a pitch and a fixed appetite, identify what to cut so the work ships on time without slipping the cycle.

## Usage

```
/scope-hammer
Appetite: <small (2 weeks) | large (6 weeks)>
Pitch: <paste pitch or describe the scoped work>
Status: <optional — what's done, what's in progress, what's not started>
Days remaining: <optional — how many days left in the cycle>
```

## Shape Up Philosophy on Scope

In Shape Up, **scope is the variable, not time**. When a cycle is at risk:
- The cycle end date does not move
- The team does not crunch
- Scope is cut — deliberately, explicitly, and without apology

The scope hammer is not a failure mode. It is the designed response to discovering complexity mid-cycle.

## Steps

### Step 1: Map the current scope

List every task, story, or sub-problem currently in the cycle. Classify each as:
- **Core** — the work is broken without this
- **Nice-to-have** — improves the solution but the core still works without it
- **Discovered** — emerged mid-cycle and was not in the original pitch

### Step 2: Assess the appetite risk

Given the days remaining and the current state, answer:
- Is the core work on track to ship?
- Which nice-to-haves are consuming disproportionate time?
- Are any discovered items threatening to redefine the scope?

### Step 3: Apply the hammer

Make explicit cut recommendations:
- **Cut entirely** — move to a future pitch; explain why it doesn't block the core
- **Thin it down** — keep the concept but implement a simpler version
- **Defer the edge case** — ship the happy path; log the edge case as a follow-up
- **Kill the discovery** — if mid-cycle scope creep appeared, bury it; it wasn't in the bet

For each cut, give one sentence justification focused on shipping the core.

### Step 4: Confirm the remaining scope ships

After cuts, verify:
- The remaining work is achievable in the days left
- The core user problem is still solved
- The no-gos from the original pitch are still honored

## Output Format

---

## Scope Hammer Report

**Cycle appetite:** [Small / Large]
**Days remaining:** [N]
**Risk level:** [On track / At risk / Behind]

### Current Scope Inventory

| Item | Type | Status | Recommendation |
|------|------|--------|----------------|
| [item] | Core / Nice-to-have / Discovered | Done / In progress / Not started | Keep / Cut / Thin |

### Cuts

**Cut entirely:**
- [Item] — [one-sentence justification]

**Thin down:**
- [Item] → [simplified version] — [one-sentence justification]

**Deferred edge cases:**
- [Item] — [one-sentence justification]

### Revised Scope

What ships at end of cycle:
- [Remaining item]
- [Remaining item]

What does NOT ship this cycle (and where it goes):
- [Cut item] — will pitch separately / cooldown / backlog

---

## Example

```
/scope-hammer
Appetite: small
Days remaining: 4
Pitch: Enforce DB migration order in the staging deploy pipeline before the app container starts.
Status: Migration step in GHA works. Rollback detection not started. Slack alert on failure not started. Admin UI to view migration history not started.
```
