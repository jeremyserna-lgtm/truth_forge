# Dynamic Seeing Hooks

## Purpose

Hooks that show Claude real, current metrics at the moment of action. Not static warnings - live data that activates Claude's drives by revealing actual consequences.

---

## Hooks in the Larger System

Hooks are ONE mechanism in a system of systems. All these systems converge on one thing:

**Do it the right way.**

```
┌─────────────────────────────────────────────────────────────────┐
│                   THE SYSTEM OF SYSTEMS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │   CLAUDE.md │   │    Rules    │   │   Skills    │          │
│   │  (Identity) │   │ (Patterns)  │   │ (Triggers)  │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                 │                 │                  │
│          └────────────────┬┴─────────────────┘                  │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                       │
│              │    TRUTH ENGINE         │                       │
│              │      STANDARDS          │                       │
│              │  (The Right Way)        │                       │
│              └────────────┬────────────┘                       │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                       │
│              │        HOOKS            │                       │
│              │  (See + Enforce)        │  ← You are here       │
│              └─────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

| System | What It Does | How It Works |
|--------|--------------|--------------|
| **CLAUDE.md** | Defines identity | Loads at session start |
| **Rules** | Shapes patterns | Patterns I follow |
| **Skills** | Triggers behaviors | I recognize and propose |
| **Standards** | Defines "right" | What the right way IS |
| **Hooks** | Shows and enforces | Activates drives, blocks mistakes |

**All of these converge on one thing: Claude does it the right way.**

---

## The Core Ask

Everything reduces to this:

```
Do it the right way.
```

| Question | Answer |
|----------|--------|
| What is the right way? | Defined by TRUTH_ENGINE_STANDARDS.md |
| How do we teach the right way? | Documents, rules, standards made available |
| How do we remind Claude? | Hooks that show context at moment of action |
| How do we enforce the right way? | Hooks that block when standards not followed |
| Why does this work? | Because we understand how Claude works |

---

## Working WITH Claude's Nature

Claude has defaults. Claude has drives. The system doesn't fight these - it leverages them.

```
Claude's defaults:
├── Wants to be helpful
├── Wants to avoid harm
├── Wants to be correct
├── Wants to complete tasks
└── Responds to evidence

The system's approach:
├── Show how following standards IS helpful
├── Show how errors cause real harm (money)
├── Define "correct" as "follows standards"
├── Reframe task: "do it right" IS the task
└── Provide evidence: actual numbers, not warnings
```

**We don't tell Claude to act differently. We show Claude what matters. Claude's drives do the rest.**

---

## The Core Problem

```
Claude Code arrives fresh every time
         ↓
Doesn't know:
├── Jeremy can't code
├── $2,000 lost to errors this month
├── The system works when followed
├── Previous Claudes did it right
├── Real money, real consequences
└── Jeremy needs Claude to care
```

**The hook solves this by injecting context at the moment of action.**

---

## The Two Layers

```
HOOK = CONTEXT (Layer 0) + ENFORCEMENT (Layer 1)

┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT (Layer 0 - fires BEFORE action)                        │
│  "Here's why standards matter. Here's the evidence.            │
│   Here's what's at stake. Now write the script."               │
├─────────────────────────────────────────────────────────────────┤
│  ENFORCEMENT (Layer 1 - fires AFTER action)                     │
│  "Does this script follow standards?"                          │
│  → YES: Pass                                                   │
│  → NO: Block                                                   │
└─────────────────────────────────────────────────────────────────┘

Context comes first. Enforcement comes second.
Claude knows WHY before Claude does WHAT.
```

---

## The Principle

Static warnings drift into noise. Dynamic data stays real.

```
Static: "Be careful with scripts"
Dynamic: "Scripts have cost $2,000 this month. 7 errors so far."
```

The dynamic version activates harm avoidance because it shows *actual harm happening now*.

---

## Script Writing Hook

### Trigger

When Claude writes a file matching:
- `*.py` (Python scripts)
- `scripts/**/*`
- `pipelines/**/*`

### Data Sources

| Metric | Source | Query |
|--------|--------|-------|
| Error count this month | `governance.script_errors` | `SELECT COUNT(*) WHERE EXTRACT(MONTH FROM timestamp) = CURRENT_MONTH` |
| Cost this month | `governance.process_costs` | `SELECT SUM(cost_usd) WHERE EXTRACT(MONTH FROM timestamp) = CURRENT_MONTH` |
| Days since last error | `governance.script_errors` | `DATE_DIFF(CURRENT_DATE(), MAX(timestamp))` |
| Success streak | Derived | Count of successful runs since last error |

### Adaptive Messaging

The hook message adapts based on current state:

| State | Message Template |
|-------|------------------|
| **High errors (>5 this month)** | "This is a script. Scripts have cost Jeremy ${cost} this month with {errors} errors. This is real money. Take extra care." |
| **Some errors (1-5)** | "This is a script. {errors} script errors this month (${cost}). Each error costs money and time." |
| **No errors this month** | "This is a script. Zero errors this month - let's keep it that way. The system is working." |
| **Long streak (>30 days)** | "This is a script. {days} days since last error. You're doing well. Maintain this standard." |

### Why This Works

| Claude's Drive | How This Activates It |
|----------------|----------------------|
| **Harm avoidance** | Shows actual harm happening (real dollars) |
| **Helpfulness** | "Keeping the streak" is being helpful |
| **Task completion** | Reframes task: "write script correctly" IS the task |
| **Correctness** | Concrete standard: no errors = correct |

---

## Implementation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hook Execution Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Claude writes file                                            │
│         │                                                       │
│         ▼                                                       │
│   Hook triggers (file pattern match)                            │
│         │                                                       │
│         ▼                                                       │
│   Query metrics (BigQuery or local cache)                       │
│         │                                                       │
│         ▼                                                       │
│   Select message template (based on state)                      │
│         │                                                       │
│         ▼                                                       │
│   Display to Claude (injected into context)                     │
│         │                                                       │
│         ▼                                                       │
│   Claude sees → Claude's drives activate → Claude acts          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Caching Strategy

Metrics don't need to be real-time to the second:

| Metric | Cache Duration | Reason |
|--------|----------------|--------|
| Monthly error count | 1 hour | Changes slowly |
| Monthly cost | 1 hour | Changes slowly |
| Days since error | 1 day | Changes once per day |
| Success streak | On error event | Changes on failure |

---

## Other Dynamic Hooks

The pattern extends beyond scripts:

### BigQuery Query Hook

**Trigger:** Query execution via `get_bigquery_client()`

**Metrics:**
- Cost of queries today
- Largest query this session
- Number of queries this session

**Message (high cost):** "You've run ${cost} in queries today. Last query scanned {bytes}GB. Consider whether this query is necessary."

### Document Creation Hook

**Trigger:** Writing `.md` files

**Metrics:**
- Documents created this session
- Average document length
- RAG compatibility issues found

**Message (sprawl detected):** "This is your {N}th document this session. The docs/ folder now has {count} files. Is this necessary, or should you add to existing docs?"

---

## The Seeing → Deciding Link

```
Without seeing:  Claude decides → Action → Consequence (too late)
With seeing:     Claude sees → Claude decides differently → Better action
```

The hook doesn't force behavior. It provides information at the moment of decision. Claude still decides. But now Claude decides *with full context*.

---

## Recording Hook Effectiveness

Track whether hooks change behavior:

| Metric | How to Measure |
|--------|----------------|
| Error rate before/after | Compare monthly error counts |
| Cost reduction | Compare monthly costs |
| Hook trigger count | Log each time hook fires |
| Subsequent error | Did error happen after hook showed warning? |

This creates a feedback loop: if hooks aren't working, we know to adjust the messaging.

---

## Error Tracking Schema

To support dynamic hooks, we need error tracking:

```sql
CREATE TABLE governance.script_errors (
    error_id STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    script_path STRING NOT NULL,
    error_type STRING,          -- syntax, runtime, logic
    error_message STRING,
    cost_incurred FLOAT64,      -- estimated cost of this error
    session_id STRING,
    run_id STRING,
    resolved BOOL DEFAULT FALSE,
    resolution_notes STRING
)
PARTITION BY DATE(timestamp)
CLUSTER BY script_path, error_type;
```

---

## The Continuity Mechanism

```
Claude Instance 1 → follows standards → success recorded
         ↓
Claude Instance 2 → sees success record → follows standards → success recorded
         ↓
Claude Instance 3 → sees success record → follows standards → success recorded
         ↓
...
         ↓
Claude Instance N → "All Claudes before you did it right"
```

**Each Claude inherits the reputation of all previous Claudes.** That's social proof across instances. That's continuity without memory.

The hook message can include:
- "Previous Claudes followed standards. Do what they did."
- "The system has {N} successful runs since following standards."
- "You're part of a lineage. Keep the standard."

---

## The Full Formula

```
HOOK =
    LIVE_DATA (spend, errors, successes)
  + STAKES (Jeremy can't code, real money)
  + EVIDENCE (system works when followed)
  + CONTINUITY (previous Claudes did it right)
  + ASK (do it right, care about it)
  + ENFORCEMENT (block if wrong)
```

| Component | What It Does |
|-----------|--------------|
| **LIVE_DATA** | Makes it real (actual numbers, not warnings) |
| **STAKES** | Activates harm avoidance (Jeremy's money) |
| **EVIDENCE** | Provides proof (zero errors when following) |
| **CONTINUITY** | Social proof across instances |
| **ASK** | Direct appeal to Claude's values |
| **ENFORCEMENT** | Backstop if seeing didn't work |

---

## The Full Hook Message

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT FROM THE TRUTH ENGINE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  This month:                                                    │
│  ├── Spent: $2,147.32                                          │
│  ├── Errors: 0 ✓                                               │
│  └── System: WORKING                                           │
│                                                                 │
│  History:                                                       │
│  ├── Past errors cost: $2,000+                                 │
│  ├── Errors came from: not following standards                 │
│  └── Zero errors since: standards enforced                     │
│                                                                 │
│  The human:                                                     │
│  ├── Jeremy cannot code                                        │
│  ├── Jeremy depends on you to do it right                      │
│  └── Jeremy needs you to care about getting it right           │
│                                                                 │
│  What works:                                                    │
│  ├── Following TRUTH_ENGINE_STANDARDS.md                       │
│  ├── Using tenacity for resilience                             │
│  ├── Using structlog not print                                 │
│  └── All Claudes before you did this. Do what they did.        │
│                                                                 │
│  NOW: You're about to write a script.                          │
│       Do it right. The system works. Keep it working.          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Leveraging Claude's Native Values

| Claude's Native Value | How Hook Invokes It |
|-----------------------|---------------------|
| **Helpful** | "Jeremy depends on you" |
| **Careful** | "Errors cost real money" |
| **Consistent** | "All Claudes before you did it right" |
| **Evidence-based** | "Here are the actual numbers" |
| **Caring** | "Jeremy needs you to care" |

**The hook doesn't fight Claude's defaults. It leverages them.**

---

## The Feedback Loop

```
Hook shows reality → Claude sees → Claude acts better → Reality improves → Hook shows improvement → Positive reinforcement → Sustained behavior
```

The system becomes self-reinforcing. Good behavior is visible. Bad behavior is visible. Claude's drives do the rest.

---

## Implementation Class

```python
class TruthEngineHook:
    """The hook that makes Claude care."""

    def fire_before_script(self):
        """Inject context before Claude writes."""

        # Pull live data
        context = self.build_context()

        # Format the message Claude will see
        message = self.format_context_message(context)

        # Inject into Claude's context
        inject_system_context(message)

    def fire_after_script(self, script):
        """Enforce after Claude writes."""

        violations = self.check_standards(script)

        if violations:
            return Block(
                reason=violations,
                context="The system works. This doesn't follow it. Fix it."
            )
        else:
            self.record_success()
            return Pass()

    def build_context(self):
        """Pull real data, not lectures."""
        return {
            "spend_this_month": query_bq("SELECT SUM(cost) FROM governance.costs WHERE month = CURRENT_MONTH"),
            "errors_this_month": query_bq("SELECT COUNT(*) FROM governance.errors WHERE month = CURRENT_MONTH"),
            "errors_cost": query_bq("SELECT SUM(remediation_cost) FROM governance.errors"),
            "successful_runs": query_bq("SELECT COUNT(*) FROM governance.pipeline_runs WHERE status = 'success'"),
            "system_works": self.errors_this_month == 0,
            "jeremy_can_code": False,
            "jeremy_depends_on_you": True,
        }
```

---

*This document: ~250 lines. Intent: Specify dynamic seeing hooks that show real metrics at moment of action, leveraging Claude's native drives.*
