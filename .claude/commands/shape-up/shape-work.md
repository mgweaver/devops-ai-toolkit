# /shape-work

Take a raw idea or vague requirement and produce a fully shaped pitch ready for the betting table. This is the full shaping workflow — from messy input to clean proposal.

## Usage

```
/shape-work
Idea: <raw idea, feature request, complaint, or half-formed requirement>
Appetite: <small (2 weeks) | large (6 weeks) | unknown>
[Context: optional background on the system, users, or constraints]
```

## What Shaping Is

Shaping is the pre-work that happens before a pitch goes to the betting table. Raw ideas are full of uncertainty. Shaped work is:
- **Concrete enough** to bet on — the team knows what they're building
- **Abstract enough** not to over-specify — the team has room to find the best solution
- **Bounded** — rabbit holes are identified, no-gos are declared, appetite is fixed

Shaping is done by a small group (senior engineer + product) before the cycle begins. This command simulates that process.

## Steps

### Step 1: Understand the raw idea

Restate the idea as a problem, not a solution:
- What user pain is this addressing?
- Who experiences it, when, and how often?
- What is the cost of not solving it (lost revenue, support burden, engineer time)?
- Is this fixing something broken or adding something new?

If the idea was stated as a solution ("add a button that..."), peel it back to the underlying problem first.

### Step 2: Set or confirm the appetite

If appetite was provided, accept it. If unknown:
- Is this a small, self-contained improvement? → **Small (2 weeks)**
- Is this a meaningful new capability or cross-system change? → **Large (6 weeks)**
- Is this too large for either? → Recommend splitting and shape only one part

State the appetite explicitly before continuing. The appetite constrains the solution — do not design a 6-week solution for a 2-week appetite.

### Step 3: Explore solution approaches

Sketch 2–3 possible approaches at a fat-marker level:
- What are the key elements of each approach?
- Which parts of the existing system does each approach touch?
- What are the rough tradeoffs (complexity, risk, user experience)?

Then select the approach that best fits the appetite and the problem. Explain the choice in one sentence.

### Step 4: Define the solution sketch

Describe the chosen approach with enough detail to build from:
- Key screens, flows, or system interactions (no mockups — use words)
- What the user does and what the system does
- What existing components are reused vs. new
- Integration points with other systems

This is the "fat-marker sketch" — broad strokes, not implementation details.

### Step 5: Surface rabbit holes

Identify anything that could blow up the appetite:
- Unresolved technical questions
- Edge cases that could become projects of their own
- Third-party dependencies or API unknowns
- Data model complexity

For each rabbit hole, propose a boundary: what is in scope and what is not.

### Step 6: Declare no-gos

Explicitly cut scope that users might expect but is deferred:
- Related features that are not part of this bet
- Performance targets not addressed this cycle
- Integrations skipped intentionally
- Admin or reporting features deferred

### Step 7: Produce the pitch

Assemble the full pitch in the standard format.

## Output Format

---

## Pitch: [Title]

**Appetite:** [Small / Large] — [2 weeks / 6 weeks]

### Problem

[Who has the pain, when, and what the cost is. One to two paragraphs. No solution language.]

### Appetite Rationale

[One sentence: why this appetite is right for this problem.]

### Solution

[Fat-marker sketch of the chosen approach. Key flows, components, and system interactions. Written for a senior engineer who will find the details themselves.]

### Rabbit Holes

- **[Risk]** — [Proposed boundary / mitigation]
- **[Risk]** — [Proposed boundary / mitigation]

### No-gos

- [Explicit cut — one line each]

### Open Questions

[Any decisions the betting table should weigh in on before committing the cycle.]

---

## Example

```
/shape-work
Idea: Property managers keep calling support because they can't tell if their rent payment sync with Stripe is working. They just see a spinner.
Appetite: small
Context: Stripe webhooks hit our backend and update tenant ledger records. We have no visibility layer. Support handles ~15 tickets/week on this.
```
