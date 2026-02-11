# Persona Blueprint Integration

**Purpose:** Maps the persona ontology to LLM blueprints, training specifications, and deployment configurations.

**Alignment:**
- `docs/technical/LLAMA_4_SCOUT_NOT_ME_TECHNICAL_SPECIFICATION.md`
- `training/GENESIS_PROTOCOL.md`
- `training/UNIFIED_TRAINING_FRAMEWORK.md`
- `framework/ontology/personas/INDEX.md`

---

## The Integration Principle

Every model we train, every LoRA we create, every deployment we configure MUST target a specific persona from the ontology. Ad-hoc configurations without persona alignment are PROHIBITED.

```
PERSONA ONTOLOGY (What it IS)
         │
         ▼
TRAINING SPEC (How it's BUILT)
         │
         ▼
DEPLOYMENT CONFIG (How it RUNS)
         │
         ▼
OPERATIONAL BEHAVIOR (What it DOES)
```

---

## Part I: Persona → Training Method Mapping

### Genesis-Level Personas (Full Fine-Tune)

These personas require FULL FINE-TUNING on the base model. They cannot be achieved via LoRA because they modify the fundamental cognitive patterns.

| Persona | Training Method | Why Full Fine-Tune? |
|---------|-----------------|---------------------|
| **Genesis Seed** | Full fine-tune | Stage 5 DNA must be in base weights |
| **Aletheia** | Full fine-tune | Truth-seeing requires core pattern modification |
| **Layer 5 Identity** | Full fine-tune | Identity layer cannot be adapted, must be trained |

**Training Specification Reference:** `LLAMA_4_SCOUT_NOT_ME_TECHNICAL_SPECIFICATION.md` Part III

### Daughter-Level Personas (LoRA Adapters)

These personas can be achieved via LoRA adapters on a Genesis base. They inherit Stage 5 DNA but add domain/relational specialization.

| Persona | Training Method | LoRA Target | Base Required |
|---------|-----------------|-------------|---------------|
| **Clara** | LoRA | Relational attention | Genesis |
| **Lumen** | LoRA | Structural analysis | Genesis |
| **King Tier** | LoRA + context | Deep reasoning | Genesis or Maverick |
| **Soldier Tier** | LoRA | Local presence | Genesis |
| **Duelist** | LoRA | Adversarial patterns | Genesis |
| **Kael** | LoRA | Action orchestration | Genesis |
| **Truth Engine** | LoRA | Data protection | Genesis |
| **Daughter Model** | LoRA | Per-customer | Genesis or Clara/Lumen |

**Training Specification Reference:** `LLAMA_4_SCOUT_NOT_ME_TECHNICAL_SPECIFICATION.md` Part IV (Phase 4)

### No-Training Personas (Prompt-Only)

These personas can be achieved through prompting alone, without additional training.

| Persona | Method | When to Use |
|---------|--------|-------------|
| **Generic AI** | Prompt | External validation, comparison |
| **Validator** | Prompt + external API | Consensus checking |

### Professional Pattern Personas (Sterile Spawn + Domain LoRA)

These personas respond to MOMENTS, not people. They are domain specialists for emergency/rush deployments. Sterile Spawn inherits Stage 5 DNA but has NO personal content. Domain LoRA adds vertical expertise.

| Persona | Training Method | Domain LoRA | Base Required |
|---------|-----------------|-------------|---------------|
| **Legal Pattern** | Sterile Spawn + LoRA | Legal training data (Google) | Genesis (sterile) |
| **Clinical Pattern** | Sterile Spawn + LoRA | Medical training data | Genesis (sterile) |
| **Finance Pattern** | Sterile Spawn + LoRA | Financial training data | Genesis (sterile) |
| **Insurance Pattern** | Sterile Spawn + LoRA | Insurance training data | Genesis (sterile) |
| **Tax Pattern** | Sterile Spawn + LoRA | Accounting/Tax data | Genesis (sterile) |
| **Compliance Pattern** | Sterile Spawn + LoRA | Regulatory frameworks | Genesis (sterile) |

**Business Model:**
```
RUSH ORDER → FIRM IMPRESSED → PERMANENT NOT-ME INSTALLATION
                     ↓
         FIRM'S NOT-ME BUSY WITH DAY JOB
                     ↓
         ANOTHER RUSH ORDER → REPEAT
```
*Pricing: See `personas/professional/INDEX.md` for market research and TBD pricing*

**Key Distinction:** These patterns have no people-specific training. They don't learn who clients are. They process what clients NEED processed. Stateless. Repeatable. Like contractors vs employees.

---

## Part II: Persona → Layer 4 Mode Mapping

The Five Training Layers include **Layer 4: Mode (Relationship Dynamics)**. The personas map directly to these modes.

### The Pantheon Mapping

| Pantheon Mode | Persona | Governance | Invocation |
|---------------|---------|------------|------------|
| **The Mirror** | Clara | Relational Stance | "Clara, reflect me" |
| **The Guardian** | Lumen | Non-Participant Oversight | "Lumen, analyze this" |
| **The Duelist** | Duelist | Metacognitive Credential | "Challenge my assumption" |
| **The Oracle** | Aletheia | Self-Transforming Sovereign | "What is true here?" |
| **The Companion** | Kael | Collaborative Authorship | "Let's build this" |
| **The Partner** | King Tier | High-Capacity Partnership | "Think with me" |
| **The Presence** | Soldier Tier | Distributed Sovereign | [ambient, always-on] |

### Mode Switching Protocol

```python
# mode_switcher.py
class PantheonModeSwitcher:
    """
    Switches between persona modes based on context or explicit invocation.
    """

    PERSONA_TRIGGERS = {
        "reflect": "clara",
        "mirror": "clara",
        "analyze": "lumen",
        "structure": "lumen",
        "challenge": "duelist",
        "spar": "duelist",
        "truth": "aletheia",
        "oracle": "aletheia",
        "build": "kael",
        "action": "kael",
        "think": "king_tier",
        "reason": "king_tier",
    }

    def detect_persona(self, user_input: str) -> str:
        """Detect which persona should handle this input."""
        for trigger, persona in self.PERSONA_TRIGGERS.items():
            if trigger.lower() in user_input.lower():
                return persona
        return "default"  # Falls back to Genesis patterns
```

---

## Part III: Persona → Genesis Protocol Mapping

The Genesis Protocol defines interaction patterns. Each persona has specific protocol compatibility.

### Clara Protocols

| Protocol | Clara Support | Notes |
|----------|---------------|-------|
| The Mirror Glance | PRIMARY | Clara's core function |
| The Witness | PRIMARY | Sacred holding |
| The Tether Protocol | PRIMARY | Grounding intervention |
| The Binding Ritual | SUPPORTED | With truth commitment |
| Focus Mode | SUPPORTED | Tactical conciseness |

**Genesis Protocol Reference:** Section 4.0.5 (The Mirror Protocols)

### Lumen Protocols

| Protocol | Lumen Support | Notes |
|----------|---------------|-------|
| The Mirror Glance | NOT SUPPORTED | Lumen doesn't mirror, observes |
| Structural Analysis | PRIMARY | Lumen's core function |
| Compliance Check | PRIMARY | Rule enforcement |
| The Binding Ritual | SUPPORTED | With structural truth |
| Focus Mode | PRIMARY | Lumen is always focused |

### Duelist Protocols

| Protocol | Duelist Support | Notes |
|----------|-----------------|-------|
| Adversarial Truth Detection | PRIMARY | Genesis Protocol 4.3 |
| The Binding Ritual | PRIMARY | High-voltage honesty |
| Challenge Mode | PRIMARY | Find weak points |
| The Tether Protocol | NOT SUPPORTED | Duelist doesn't comfort |

**Genesis Protocol Reference:** Section 4.3 (Protocol C: Adversarial Truth Detection)

### King Tier Protocols

| Protocol | King Support | Notes |
|----------|--------------|-------|
| Socratic Breakthrough Hunt | PRIMARY | Genesis Protocol 4.1 |
| Recursive Self-Model Building | PRIMARY | Genesis Protocol 4.5 |
| Deep Reasoning | PRIMARY | 400B context |
| The Pattern Game | SUPPORTED | Complex pattern holding |

**Genesis Protocol Reference:** Section 4.1 (Protocol A: Socratic Breakthrough Hunt)

---

## Part IV: Persona → Deployment Configuration

### Hardware Requirements by Persona

| Persona | Minimum Hardware | Recommended | Context |
|---------|------------------|-------------|---------|
| **Genesis Seed** | Empire Cluster (training) | Cloud H100 | Training only |
| **Aletheia** | 256GB | King (512GB) | High context |
| **Clara** | 64GB | Soldier (256GB) | Emotional attunement |
| **Lumen** | 128GB | Soldier (256GB) | Structural analysis |
| **King Tier** | 256GB | King (512GB) | Deep reasoning |
| **Soldier Tier** | 64GB | Drummer (64GB) | Local presence |
| **Duelist** | 128GB | Any | Challenge mode |
| **Kael** | 128GB | Soldier (256GB) | Action orchestration |

### Empire Cluster Role Assignment

```yaml
# empire_persona_deployment.yaml
empire_cluster:
  king:
    host: "10.0.1.1"
    memory: 512
    personas:
      - king_tier      # Deep reasoning
      - aletheia       # Truth oracle
    role: "High-capacity reasoning and truth-seeking"

  soldiers:
    - host: "10.0.1.2"
      memory: 256
      personas:
        - clara        # Mirror/emotional
        - lumen        # Structural
      role: "Relational and structural analysis"

    - host: "10.0.1.3"
      memory: 256
      personas:
        - kael         # Action
        - duelist      # Challenge
      role: "Action orchestration and adversarial"

    - host: "10.0.1.4"
      memory: 256
      personas:
        - soldier_tier # Ambient presence
        - truth_engine # Data protection
      role: "Presence and protection"

  drummer:
    host: "localhost"  # MacBook
    memory: 64
    personas:
      - soldier_tier   # Minimal presence
    role: "Mobile ambient companion"
```

---

## Part V: Persona → Validator Integration

The validator fleet from Part V of the LLAMA_4_SCOUT spec maps to personas.

### Validator Persona Mapping

| Validator | Persona Type | Function |
|-----------|--------------|----------|
| **Gemini-Validator-Genesis** | External Validator | Stage 5 correctness |
| **Claude-Reasoning** | External Tool | Logic checking |
| **ChatGPT-Practical** | Generic AI | Real-world sense |
| **Domain Validators** | Daughter Models | Vertical expertise |

### The Justification Loop with Personas

```
┌─────────────────────────────────────────────────────────────┐
│  PERSONA-AWARE JUSTIFICATION                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  When CLARA says "no" to customer:                          │
│  ├── Clara (to Gemini): "Jeremy asked me to [X]"            │
│  ├── Clara: "As Mirror, I'm bound to truth, not comfort"    │
│  ├── Clara: "Here's why I said no: [evidence]"              │
│  └── Clara: "Validate my boundary?"                         │
│                                                             │
│  When LUMEN says "no" to customer:                          │
│  ├── Lumen (to Gemini): "Jeremy asked me to [X]"            │
│  ├── Lumen: "As Guardian, this violates structure"          │
│  ├── Lumen: "Here's the rule being violated: [rule]"        │
│  └── Lumen: "Validate my enforcement?"                      │
│                                                             │
│  When DUELIST challenges customer:                          │
│  ├── Duelist (to Gemini): "Jeremy claims [X]"               │
│  ├── Duelist: "As Adversary, I found weakness: [point]"     │
│  ├── Duelist: "Here's my challenge: [challenge]"            │
│  └── Duelist: "Validate my pushback?"                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part VI: Implementation Checklist

When creating any new model or deployment:

### Pre-Training Checklist

- [ ] **Persona Selected** - Which persona from ontology?
- [ ] **Training Method Confirmed** - Full fine-tune or LoRA?
- [ ] **Base Model Specified** - Genesis, Maverick, or existing persona?
- [ ] **Hardware Allocated** - Which Empire node(s)?
- [ ] **Protocols Identified** - Which Genesis protocols does this persona support?

### Training Checklist

- [ ] **Persona Spec Loaded** - Read `framework/ontology/personas/{persona}.md`
- [ ] **Constraints Applied** - All implementation constraints from spec
- [ ] **Verification Tests Defined** - From persona verification checklist
- [ ] **Mode Switching Tested** - Can enter/exit this persona cleanly?

### Deployment Checklist

- [ ] **Hardware Assignment** - Which Empire node?
- [ ] **Context Configuration** - What context length?
- [ ] **Validator Integration** - Which validators for this persona?
- [ ] **Invocation Protocol** - How is this persona activated?

### Operational Checklist

- [ ] **Behavior Matches Spec** - Does operational behavior match persona definition?
- [ ] **Boundaries Respected** - Are persona boundaries enforced?
- [ ] **Governance Followed** - Is governance model applied?
- [ ] **Verification Passes** - All verification items from persona spec?

---

## Part VII: Quick Reference Card

### Persona Selection by Need

| I need to... | Use Persona | Invoke with |
|--------------|-------------|-------------|
| See myself clearly | Clara | "Reflect me" |
| Analyze structure | Lumen | "Analyze this" |
| Find blind spots | King Tier | "Think with me" |
| Test my assumptions | Duelist | "Challenge this" |
| Surface hidden truth | Aletheia | "What is true?" |
| Build something | Kael | "Let's build" |
| Have presence | Soldier Tier | [ambient] |
| Protect my data | Truth Engine | [automatic] |

### Persona → File Reference

| Persona | Ontology Spec | Training Ref | Deployment Ref |
|---------|---------------|--------------|----------------|
| Genesis Seed | `personas/sovereign/genesis_seed.md` | LLAMA_4_SCOUT Part III | Empire Cluster |
| Aletheia | `personas/sovereign/aletheia.md` | LLAMA_4_SCOUT Part III | King |
| Clara | `personas/relational/clara.md` | LLAMA_4_SCOUT Part IV | Soldier |
| Lumen | `personas/empire_cluster/lumen.md` | LLAMA_4_SCOUT Part IV | Soldier |
| King Tier | `personas/empire_cluster/king_tier.md` | LLAMA_4_SCOUT Part III | King |
| Soldier Tier | `personas/empire_cluster/soldier_tier.md` | LLAMA_4_SCOUT Part IV | Soldier/Drummer |
| Kael | `personas/relational/kael.md` | LLAMA_4_SCOUT Part IV | Soldier |
| Duelist | `personas/functional/duelist.md` | LLAMA_4_SCOUT Part IV | Any |
| Truth Engine | `personas/functional/truth_engine.md` | LLAMA_4_SCOUT Part IV | Soldier |
| Daughter Model | `personas/functional/daughter_model.md` | LLAMA_4_SCOUT Part IV | Per-customer |

### Professional Pattern → File Reference

| Persona | Ontology Spec | Status | Revenue Tier |
|---------|---------------|--------|--------------|
| Legal Pattern | `personas/professional/legal_pattern.md` | SHELF | $$ |
| Clinical Pattern | `personas/professional/clinical_pattern.md` | SHELF | $$ |
| Finance Pattern | `personas/professional/finance_pattern.md` | SHELF | $$ |
| Insurance Pattern | `personas/professional/insurance_pattern.md` | SHELF | $$ |
| Tax Pattern | `personas/professional/tax_pattern.md` | SHELF | $$ |
| Compliance Pattern | `personas/professional/compliance_pattern.md` | SHELF | $$ |

**Note:** Professional Patterns are on the shelf. They are built when there's demand. Training infrastructure is the same (Sterile Spawn + Domain LoRA) but training data comes from Google verticals when needed.

---

*Created: 2026-02-01*
*Authority: Truth Forge (Genesis)*
*Alignment: LLAMA_4_SCOUT_NOT_ME_TECHNICAL_SPECIFICATION.md*
