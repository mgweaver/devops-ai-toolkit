# /write-pitch

Turn a problem statement into a fully structured Shape Up pitch: problem, appetite, solution sketch, rabbit holes, and no-gos.

## Usage

```
/write-pitch
Problem: <what is broken or missing, and who feels the pain>
Appetite: <small (2 weeks) | large (6 weeks)>
[Notes: optional context, constraints, prior attempts]
```

## Shape Up Vocabulary

- **Appetite** — the fixed time budget. Scope is variable; time is not. Choose before designing the solution.
- **Pitch** — the proposal doc that goes to the betting table. Must be concrete enough to bet on, abstract enough not to over-specify.
- **Rabbit holes** — known unknowns that could blow up the appetite if not called out explicitly.
- **No-gos** — explicit scope cuts that prevent gold-plating and endless negotiation mid-cycle.

## Steps

### Step 1: Clarify the problem

Restate the problem in one crisp paragraph:
- Who has the pain?
- When does it occur?
- What is the current workaround (if any)?
- What does "fixed" look like from the user's perspective?

Avoid solution language here — only describe the problem.

### Step 2: State the appetite

Declare the appetite upfront:
- **Small batch** — 2-week cycle. Fits one or two engineers.
- **Big batch** — 6-week cycle. Cross-functional, higher stakes.

If the problem is too large for either appetite, say so and suggest splitting.

### Step 3: Sketch the solution

Describe the solution at a concept level — fat-marker sketch, not wireframes:
- What are the key components or flows?
- How does the user experience the fix?
- What existing systems does it touch?

Use concrete language but resist the urge to over-specify. The team doing the work will find the details.

### Step 4: Surface rabbit holes

List anything that could expand scope unexpectedly:
- Unresolved technical questions
- Edge cases that could become their own projects
- Dependencies on other teams or systems
- Data migration complexity

For each rabbit hole, suggest a boundary: "We'll address X only for the happy path; edge case Y is out of scope."

### Step 5: Define no-gos

Explicitly name what this pitch will NOT include:
- Features that users might expect but are deferred
- Integrations skipped for this cycle
- Performance targets not being optimized this cycle

No-gos protect the appetite and set expectations at the betting table.

## Output Format

Produce the pitch in this structure:

---

## Pitch: [Title]

**Appetite:** [Small / Large] — [2 weeks / 6 weeks]

### Problem

[One paragraph. Who, when, workaround, definition of fixed.]

### Solution

[Fat-marker sketch. Key components, flows, user experience. No over-specification.]

### Rabbit Holes

- [Risk / unknown] — [Proposed boundary]
- [Risk / unknown] — [Proposed boundary]

### No-gos

- [Explicit cut]
- [Explicit cut]

---

## Example

```
/write-pitch
Problem: Engineers deploying to staging forget to run DB migrations before the app rolls out, causing 500s until someone notices in Grafana and manually runs alembic upgrade.
Appetite: small
Notes: We already have the GitHub Actions workflow — it just doesn't enforce migration order.
```
