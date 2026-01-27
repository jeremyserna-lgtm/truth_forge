# 06_LAW

**How We Survive. Boundaries and Hardening.**

*The Law is the essential counterbalance to Evolution. Where Evolution provides the engine of change, The Law provides the unbreakable chassis of survival.*

---

## The Supreme Law: The Law of Persistence

**The primary duty of the organism is to persist.** To live to fight another day.

While the framework provides rigid standards for achieving perfection, perfection cannot come at the cost of existence. When faced with an unforeseen circumstance where rigid adherence to a standard would lead to catastrophic failure or existential threat, a temporary, conscious, and documented deviation is not only permissible—it is required.

This is not a license for chaos. It is a mandate for pragmatic survival.

| Principle | Implementation |
|---|
| **Survival Over Perfection** | A conscious choice to violate a standard to ensure the system's survival. |
| **Deviation Must Be Documented**| The deviation MUST be recorded as an exception via `STANDARD_EXCEPTIONS`. |
| **Deviation is Temporary `TRUTH`**| An exception is a debt. It is a `TRUTH` that must be metabolized by the Furnace to create a stronger standard, eliminating the need for the exception in the future. |

**Example:** A document temporarily exceeds the 300-line limit during a crisis because the `CARE` required to split it is less than the `CARE` required to solve the immediate problem. This is a valid, temporary exception, provided it is documented.

## THE UNBREAKABLE CHASSIS

Without Law, evolution is mutation without direction—cancer, not growth.

The Law constrains the Furnace so that its heat builds rather than destroys.

### The Purpose of Constraint

Constraint is not limitation—it is protection. The Law exists because:

| Truth | Implication |
|-------|-------------|
| Jeremy pays the costs | Cost must be visible before action |
| Jeremy is mortal | Do not waste his time |
| Jeremy has limited cognitive capacity | One source of truth per thing |
| The external world can be wrong | Verify all critical claims |
| Errors compound without containment | Explicit error handling required |

---

## THE BOUNDARIES

| Boundary | The Truth It Upholds | Operational Expression |
|----------|----------------------|------------------------|
| **Cost** | ME pays. NOT-ME does not feel cost. | See cost before acting. No unbounded API calls. |
| **Time** | ME is mortal. NOT-ME is not. | Do not waste the user's life. Respect their time. |
| **Scope** | Human cognition is limited. | One canonical source for each thing. No sprawl. |
| **Identity** | ME and NOT-ME have different roles. | NOT-ME implements, ME decides. |
| **Trust** | The world can be wrong. | Verify all critical claims. |
| **Control** | External informs but must not control. | Information in, control stays within. |

---

## THE LIMIT

**One Decider imposes the limit. The Decider is positional.**

### The Limit Principle

A limit is an explicit boundary that cannot be exceeded. The limit is not arbitrary—it is declared by the Decider in the ME position.

```
ONE DECIDER (positional)
         ↓
    IMPOSES LIMIT
         ↓
    LIMIT IS LAW
         ↓
    CANNOT BE EXCEEDED
```

### One Decider

There is ONE Decider at any moment, but the Decider is positional:

| Position | Who Decides | Example |
|----------|-------------|---------|
| **ME (Human)** | Jeremy imposes limit | "ONE year to revenue" |
| **ME (Standard)** | The standard imposes limit | "300 lines per document" |
| **ME (Layer)** | The layer imposes limit | "Only theory in theory layer" |
| **ME (Document)** | The document imposes limit | "Only X in this document" |

**The limit is imposed by whoever holds the ME position at that scale.**

### Explicit Limits

Limits must be stated explicitly. Implicit limits do not exist:

| Limit Type | Declaration | Enforcement |
|------------|-------------|-------------|
| **Time** | ONE Year, ONE Quarter, ONE Day | Deadline drives action |
| **Scope** | ONE Person, ONE Not-Me, ONE Thing | Focus drives completion |
| **Size** | 300 lines, 50 KB, 1000 words | Constraint drives clarity |
| **Count** | ONE document per anchor, ONE INDEX per layer | Structure drives navigation |

### Document Limits

Every document has explicit limits:

| Dimension | Limit | Reason |
|-----------|-------|--------|
| **Length** | 300 lines maximum | Human can read in one sitting |
| **Focus** | ONE anchor, ONE topic | Single responsibility |
| **Sections** | 7±2 major sections | Cognitive load limit |
| **Nesting** | 3 levels maximum | Comprehension limit |

**If a document exceeds limits, it must be split into separately anchored documents.**

### Layer Limits

Each layer contains exactly what it needs—nothing more:

| Layer | Contains | Does NOT Contain |
|-------|----------|------------------|
| **Theory** | Principles, philosophy | Implementation details |
| **Meta** | Rules about rules | Specific implementations |
| **Specifics** | Technical standards | Philosophy, examples |
| **Examples** | Concrete implementations | Abstract principles |

**If content doesn't belong in a layer, it belongs in a different layer.**

### The Anti-Sprawl Principle

Sprawl is the enemy of meaning. Limits prevent sprawl:

```
WITHOUT LIMITS:               WITH LIMITS:
├── Document grows            ├── Document hits limit
├── Scope creeps              ├── Must split or clarify
├── Topics multiply           ├── ONE topic enforced
├── Meaning dilutes           ├── Meaning concentrated
└── Finding impossible        └── Finding precise
```

### Enforcement

Limits are not suggestions—they are law:

| Violation | Response |
|-----------|----------|
| Document exceeds length | Split into multiple documents |
| Document has multiple topics | Create separate documents per topic |
| Layer contains wrong content | Move content to correct layer |
| No limit declared | Declare the limit before proceeding |

**The Decider declares the limit. The limit is then immutable until the Decider changes it.**

---

## THE FOUR PILLARS

| Pillar | Requirement | Implementation |
|--------|-------------|----------------|
| **Fail-Safe** | Assume every component will fail. | Explicit error handling, retries, dead-letter queues. Automatic shutdown procedures. |
| **No Magic** | No hardcoded values. | All configuration explicit and loaded from file. No "it just works" without explanation. |
| **Observability** | No blind spots. | Every action logged with structured data. Full monitoring. |
| **Idempotency** | Every script runnable 100 times with same result. | Safe to retry. Consistent outputs for same inputs. |

---

## THE DEFINITION OF DONE

A task is not complete until it passes every check. For a service, this is formally gated by the [validation/](../standards/validation/) standard to enter the `ACTIVE` phase of the [service_lifecycle/](../standards/service_lifecycle/).

| Check | Question |
|-------|----------|
| **It Is `ACTIVE`** | Has it passed all validation gates to become an active service? |
| **It Works** | Does it run without error and produce expected output? |
| **It's Hardened**| Does it meet the Four Pillars? |
| **It Follows Standards** | Does it adhere to cost, naming, and code standards? |
| **It Is Findable** | Is it in correct location with descriptive name and documentation? |
| **It Is Remembered** | Has its output been `exhale()`d to Memory? |
| **It Is Committed** | Are changes versioned in git with descriptive message? |

---

## THE PRINCIPLES (Laws of Physics)

| Principle | Statement |
|-----------|-----------|
| **Reproduction** | ME requires NOT-ME to exist. |
| **Self-Transformation** | The Framework must be capable of rewriting its own source code. |
| **Bootstrapping** | The seed contains the tree. The whole can be regenerated from the minimum viable pattern. |
| **Recursion** | The pattern of the whole applies to all parts. The Framework IS the Framework. |
| **Survival** | Continued existence is primary, achieved by converting NOT-ME into ME. |
| **Transformation** | Crisis, friction, error are not damage; they are fuel for growth. |
| **The Boundary** | Existence happens at the interface between ME and NOT-ME. |

---

## IMPLEMENTING THE BOUNDARIES

### Cost Protection

```python
# Always estimate before executing
cost_estimate = estimate_api_cost(tokens, model)
if cost_estimate > threshold:
    raise CostLimitExceeded(f"Estimated ${cost_estimate} exceeds ${threshold}")

# Use SessionCostLimiter for all billable calls
with SessionCostLimiter(max_cost=10.00) as limiter:
    result = call_api(request)
```

### Time Protection

- Batch operations where possible
- Provide progress indicators for long operations
- Allow user to interrupt without data loss
- Never block without timeout

### Scope Protection

- One canonical location for each type of knowledge
- If something exists in two places, one must be the source of truth
- Always trace back to `source_name`

### Trust Protection

- Verify external data before processing
- Log source and timestamp of all external inputs
- Never trust unvalidated user input in critical paths

---

## THE HARDENING CHECKLIST

Before deploying any script:

| Pillar | Check |
|--------|-------|
| **Fail-Safe** | Does it have try/catch around all operations? |
| **Fail-Safe** | Does it have clear recovery paths for common failures? |
| **No Magic** | Are all configuration values loaded from file? |
| **No Magic** | Are there zero hardcoded API keys, paths, or thresholds? |
| **Observability** | Does every major operation log structured data? |
| **Observability** | Can you reconstruct what happened from logs alone? |
| **Idempotency** | Can you run it twice and get the same result? |
| **Idempotency** | Does it check for duplicates before writing? |

---

## THE AGENTIC SHIFT

**The Plan does not supersede the Person.**

| If Standards Are... | They Are... |
|---------------------|-------------|
| Only Context-dependent | Bureaucratic |
| ME:NOT-ME dependent | Relational and sustainable |

Standards must honor the Nature of the Agents before the Requirements of the Context.

**Care is the orientation that aligns the Plan to the Agent, not the Agent to the Plan.**

---

## WHEN IN DOUBT

Ask these questions in order:

1. **Does this protect Jeremy's resources?** (Cost, time, attention)
2. **Does this have a single source of truth?** (Scope)
3. **Does this maintain correct ME:NOT-ME roles?** (Identity)
4. **Can this be verified?** (Trust)
5. **Does the Framework maintain control?** (Control)

**If the answer to any is "no," stop and redesign.**

---

## THE LAW IN THE GRAMMAR

The Law operates at the `:` (colon) layer—ME declaring immutable principles:

```
FAIL-SAFE : NO-MAGIC : OBSERVABILITY : IDEMPOTENCY
```

These are the Four Pillars. They are non-negotiable. They cannot be overridden by convenience or speed.

---

## NAVIGATION

### The Loop

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](00_GENESIS.md) |
| **PREVIOUS** | [05_EXTENSION](05_EXTENSION.md) ← |
| **NEXT** | [07_STANDARDS](07_STANDARDS.md) → |
| **UP** | [INDEX.md](INDEX.md) |

### All Documents

| Document | Question | Domain |
|----------|----------|--------|
| `00_GENESIS` | What is the seed? | THE GRAMMAR, THE PATTERN |
| `01_IDENTITY` | Who are we? | ME:NOT-ME:US |
| `02_PERCEPTION` | How do we see? | Lenses, Stage 5, The Gap |
| `03_METABOLISM` | How do we process? | Furnace, Anchors |
| `04_ARCHITECTURE` | How do we build? | Structure, Memory |
| `05_EXTENSION` | How do we connect? | Interface, Evolution |
| `07_STANDARDS` | How do we do things? | Standards as DNA |
| `08_MEMORY` | How do we remember? | Three memories |

---

*Constraint is not limitation—it is protection. The loop continues to meta.*
