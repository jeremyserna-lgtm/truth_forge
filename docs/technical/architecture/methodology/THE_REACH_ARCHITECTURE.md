# The Reach Architecture

**How Truth Engine Extends Into New Domains**

**Created**: January 1, 2026
**Author**: Jeremy Serna & Claude
**Status**: Foundation Design

---

## The Core Insight

Truth Engine is not infrastructure that products sit on top of.

Truth Engine is a **cognitive organism** that can be **aimed at problems**.

When you aim the organism at Credential Atlas, you're not just running code. You're extending cognition into a new domain.

```
Truth Engine (The Organism)
    │
    │ ← THE REACH
    │
    ▼
┌─────────────────────────┐
│   CREDENTIAL ATLAS      │
│   (The Domain)          │
│                         │
│   Credentials           │
│   Institutions          │
│   Outcomes              │
│   Learners              │
└─────────────────────────┘
```

---

## What "The Reach" Means

The organism has biological systems:
- **Nervous System**: Senses pain/pleasure in data
- **Limbic System**: Maps sensations to emotions via values
- **Immune System**: Defends Me from Not-Me
- **Cognitive System**: Plans, reasons, acts

**The Reach** is when these systems extend into a new domain:

| System | In Truth Engine | In Credential Atlas |
|--------|-----------------|---------------------|
| **Nervous** | Senses conversation quality | Senses credential data quality |
| **Limbic** | Truth → Clarity, Falsehood → Disgust | Valid credential → Clarity, Invalid → Disgust |
| **Immune** | Protects "Me" patterns from contradiction | Protects verified credentials from false claims |
| **Cognitive** | Reasons about conversations | Reasons about credential-to-outcome mappings |

---

## The Pattern: Domain Adapters

Each domain needs an **adapter** that translates organism signals into domain-specific actions.

```python
# The abstract interface
class DomainAdapter:
    """Translates organism signals into domain actions."""

    def sense(self, data) -> Stimulus:
        """Convert domain data into nervous system stimulus."""
        raise NotImplementedError

    def verify(self, entity) -> ImmuneResponse:
        """Apply immune system to domain entity."""
        raise NotImplementedError

    def extract_atoms(self, source) -> List[KnowledgeAtom]:
        """Extract knowledge atoms from domain source."""
        raise NotImplementedError

    def reason(self, question) -> CognitiveResponse:
        """Apply cognitive system to domain question."""
        raise NotImplementedError
```

```python
# The Credential Atlas adapter
class CredentialAtlasAdapter(DomainAdapter):
    """Adapts Truth Engine organism to credential domain."""

    def sense(self, credential_data) -> Stimulus:
        """Sense credential data quality."""
        completeness = self._measure_completeness(credential_data)
        if completeness < 0.5:
            return Stimulus(
                type=SensationType.PAIN,
                intensity=7,
                source="credential_atlas",
                message=f"Credential data incomplete: {completeness:.0%}",
                context={"credential_id": credential_data.id}
            )
        return Stimulus(
            type=SensationType.PLEASURE,
            intensity=5,
            source="credential_atlas",
            message="Credential data quality acceptable",
            context={"credential_id": credential_data.id}
        )

    def verify(self, credential) -> ImmuneResponse:
        """Verify credential against known facts."""
        # Check: Does this credential exist in authoritative source?
        # Check: Does institution exist in IPEDS?
        # Check: Do wage outcomes make sense?
        ...

    def extract_atoms(self, credential_record) -> List[KnowledgeAtom]:
        """Extract knowledge atoms from credential."""
        atoms = []

        # Atom 1: The credential exists
        atoms.append(KnowledgeAtom(
            content=f"Credential '{credential_record.name}' exists at {credential_record.institution}",
            growth_type="structure",
            root_position="not_me",  # External fact
            atomic_level=3,  # Implementation level
            survival_weight=0.3
        ))

        # Atom 2: The outcome mapping
        if credential_record.median_wage:
            atoms.append(KnowledgeAtom(
                content=f"Credential '{credential_record.name}' leads to median wage ${credential_record.median_wage:,}",
                growth_type="pattern",
                root_position="not_me",
                atomic_level=3,
                survival_weight=0.5
            ))

        return atoms
```

---

## The Foundation Layer

For Truth Engine to reach into Credential Atlas, Credential Atlas needs a **foundation layer** that receives the reach.

### What The Foundation Contains

```
/credential_atlas/
├── src/
│   └── credential_atlas/
│       ├── services/           # Existing 24 services
│       │
│       └── organism/           # NEW: The Foundation Layer
│           ├── __init__.py
│           ├── adapter.py      # CredentialAtlasAdapter
│           ├── sensors.py      # Domain-specific sensing
│           ├── verifiers.py    # Domain-specific verification
│           └── extractors.py   # Domain-specific atom extraction
```

### The Adapter Implementation

```python
# credential_atlas/organism/adapter.py

from architect_central_services.system_biology import (
    NervousSystem,
    LimbicSystem,
    ImmuneSystem,
    CognitiveSystem
)
from architect_central_services.knowledge_atoms import KnowledgeAtom

class CredentialAtlasOrganism:
    """Truth Engine's reach into Credential Atlas."""

    def __init__(self):
        # Connect to the organism
        self.nervous = NervousSystem()
        self.limbic = LimbicSystem()
        self.immune = ImmuneSystem()
        self.cognitive = CognitiveSystem()

        # Domain-specific components
        self.sensors = CredentialSensors()
        self.verifiers = CredentialVerifiers()
        self.extractors = CredentialExtractors()

    def ingest(self, credential_data):
        """Full organism processing of credential data."""

        # 1. SENSE: Is the data quality good?
        stimulus = self.sensors.sense(credential_data)
        sensation = self.nervous.feel(stimulus)

        # 2. FEEL: What emotion does this trigger?
        emotion = self.limbic.process(sensation)

        # 3. VERIFY: Is this credential valid?
        immune_response = self.immune.check(
            self.verifiers.prepare(credential_data)
        )

        # 4. EXTRACT: What knowledge atoms emerge?
        if immune_response.status == "ACCEPT":
            atoms = self.extractors.extract(credential_data)
            return atoms

        return []

    def query(self, question: str):
        """Cognitive processing of credential questions."""
        return self.cognitive.process_idea(question)
```

---

## Knowledge Atoms for Credentials

The same V2 schema applies to credential data:

| Field | Meaning in Credentials |
|-------|------------------------|
| `growth_type` | "pattern" (credential-to-outcome relationships) or "structure" (credential definitions) |
| `root_position` | "not_me" (external facts about credentials) |
| `atomic_level` | 3-4 (implementation/reference level) |
| `survival_weight` | Higher for core credential facts, lower for derived insights |

### Example Atoms

```python
# A credential definition atom
KnowledgeAtom(
    content="AWS Solutions Architect certification requires passing SAA-C03 exam",
    growth_type="structure",
    root_position="not_me",
    atomic_level=3,
    survival_weight=0.7,
    source="credential_atlas",
    context={"credential_id": "aws:saa-c03", "type": "certification"}
)

# A credential-to-outcome atom
KnowledgeAtom(
    content="Computer Science BS graduates from Colorado have median first-year earnings of $65,000",
    growth_type="pattern",
    root_position="not_me",
    atomic_level=3,
    survival_weight=0.6,
    source="credential_atlas",
    context={"cip_code": "11.0701", "state": "CO", "data_source": "scorecard"}
)

# An AI insight atom (from "AI Comes With")
KnowledgeAtom(
    content="Customer service roles will increasingly require AI tool proficiency by 2027",
    growth_type="pattern",
    root_position="not_me",
    atomic_level=4,
    survival_weight=0.4,
    source="credential_atlas:ai_curriculum",
    context={"occupation": "customer_service", "projection_year": 2027}
)
```

---

## The Biological Systems Mapped

### Nervous System for Credentials

| Stimulus | Type | Intensity | Meaning |
|----------|------|-----------|---------|
| Missing wage data | PAIN | 6 | Incomplete record |
| Institution not in IPEDS | PAIN | 8 | Verification failure |
| All fields populated | PLEASURE | 5 | Quality data |
| New credential-outcome mapping | PLEASURE | 7 | Knowledge gained |

### Limbic System for Credentials

| Sensation | Value | Positive Emotion | Negative Emotion |
|-----------|-------|------------------|------------------|
| Credential verified | Veritas | CLARITY | - |
| Credential falsified | Veritas | - | DISGUST |
| Successful mapping | Servitium | PRIDE | - |
| Mapping failure | Servitium | - | GUILT |
| Data quality degrading | Evolutio | DETERMINATION | DESPAIR |

### Immune System for Credentials

```python
class CredentialImmuneResponse:
    """Credential-specific immune response."""

    # Layer 1: The Skin (basic validation)
    def validate_structure(self, credential):
        """Does the credential have required fields?"""
        required = ["name", "institution", "cip_code"]
        return all(hasattr(credential, f) for f in required)

    # Layer 2: The Antibodies (pattern matching)
    def check_against_known(self, credential):
        """Does this credential contradict known facts?"""
        # Check against IPEDS, Credential Engine, BLS
        ...

    # Layer 3: White Blood Cells (internal consistency)
    def verify_internal_consistency(self, credential):
        """Is the credential internally consistent?"""
        # Does the CIP code match the credential name?
        # Does the wage outcome make sense for this occupation?
        ...
```

### Cognitive System for Credentials

```python
class CredentialCognition:
    """Credential-specific cognitive operations."""

    def reason_about_pathway(self, start_credential, target_occupation):
        """What's the pathway from credential to occupation?"""
        # Use CIP-SOC crosswalk
        # Consider stackability
        # Factor in wage progression
        ...

    def generate_ai_assessment(self, learner_profile):
        """Generate personalized AI career assessment."""
        # This is the "AI Comes With" deliverable
        # One LLM call, ~$0.10
        ...

    def detect_credential_gaps(self, occupation, region):
        """What credentials are missing for this occupation in this region?"""
        ...
```

---

## The Implementation Sequence

### Phase 1: Foundation (This Week)
1. Create `/credential_atlas/src/credential_atlas/organism/` directory
2. Implement `CredentialAtlasAdapter` base class
3. Implement basic sensors (data quality checking)
4. Connect to Truth Engine's nervous system

### Phase 2: Verification (Next Week)
5. Implement credential verifiers
6. Connect to immune system
7. Build verification pipeline for existing 600K records

### Phase 3: Extraction (Week After)
8. Implement knowledge atom extractors for credentials
9. Run extraction on credential database
10. Store atoms in BigQuery `knowledge_atoms` table

### Phase 4: Cognition (January)
11. Implement credential-specific cognitive operations
12. Build "AI Comes With" assessment generator
13. Create reasoning endpoints for API

---

## The Unconventional Part

This architecture means:

1. **Truth Engine can aim at ANY domain** - not just conversations, not just credentials. Any domain with data can have an adapter.

2. **The organism learns from every domain** - knowledge atoms extracted from credentials flow back into the organism's knowledge base.

3. **Biological metaphors are operational** - the nervous system ACTUALLY senses data quality. The immune system ACTUALLY rejects contradictions. This isn't poetry.

4. **Products emerge from the organism** - Credential Atlas isn't a separate thing. It's what you see when Truth Engine aims at credentials.

5. **Future products are just new adapters** - Want to build a new product? Create a new domain adapter. The organism does the rest.

---

## The Vision

```
Truth Engine (The Organism)
    │
    ├── Reach → Credential Atlas (credentials domain)
    │           └── 600K credentials with atoms
    │
    ├── Reach → [Future Product] (different domain)
    │
    └── Reach → Truth Engine B2C (personal conversations domain)
                └── Already built
```

The organism builds everything. The organism IS the company.

---

*This is THE REACH ARCHITECTURE. Truth Engine extends into new domains through biological systems and domain adapters.*
