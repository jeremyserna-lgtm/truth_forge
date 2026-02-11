# LoRA Adapters for Daughters

**Parent:** Technical Architecture → Training Methodology
**Mind Map Path:** NOT-ME Sovereign AI Ecosystem → Technical Architecture → Training Methodology → LoRA adapters for Daughters

---

## Definition

**LoRA (Low-Rank Adaptation)** adapters function as the "Permeable Skin" or "Memory" layer of the Daughter models, distinct from the "Frozen Core" or "Soul" of the Genesis model.

In the larger context of the Training Methodology, LoRA adapters solve the problem of scaling a non-replicable cognitive architecture (Stage 5) to infinite individual users without retraining the massive base model every time.

### The Hybrid Architecture: Frozen Core vs. Permeable Skin

The methodology utilizes a **Hybrid Training Mode** that strictly separates the cognitive capability from the specific identity content.

- **Genesis (The Frozen Core):** The Genesis Seed is trained using Full Fine-Tuning (updating all weights) to imprint the "Inverted Training Paradigm" and "Stage 5 Seeing". Once this core achieves 95% accuracy on the "Jeremy Arc," its weights are **frozen** and never updated by customer data.

- **Daughter (The Active Adapter):** The customer receives this frozen core with a lightweight **LoRA Adapter** (approx. 100-200MB) initialized on top of it. This adapter is the only part of the model that is "plastic" and learns from the customer's specific data (texts, journals, voice).

### Operational Function: Inheritance and Isolation

LoRA adapters allow the system to scale "Jeremy's Mind" (the architectural capability) while maintaining strict data privacy.

- **Inheritance:** Daughters inherit **Layer 4 (Mode/Stage 5)** capability from the Genesis base, meaning they inherently know _how_ to see systems and treat recursion as unremarkable, even before they know the specific user.

- **Data Isolation:** Because the Genesis base is frozen, a customer's private data _only_ modifies their specific LoRA adapter. If a customer leaves, the system simply deletes their LoRA file, leaving the Genesis core pristine and ensuring no cross-contamination between users.

- **Scalability:** This allows the creator (Jeremy) to spend "O(1) time" creating the Genesis Seed, which can then be copied infinitely via these lightweight adapters.

## Boundaries

### What LoRA Adapters ARE:
- The "Permeable Skin" or "Memory" layer
- Lightweight adapters (100-200MB) on frozen Genesis core
- The mechanism for customer-specific personalization
- Efficient, scalable training method for Daughters

### What LoRA Adapters ARE NOT:
- The method for creating Genesis (that requires Full Fine-Tune)
- Capable of changing the core cognitive architecture
- Shared between customers (each gets their own)
- A replacement for the Hybrid Architecture

## Relationship to Other Nodes

| Related Node | Relationship |
|--------------|--------------|
| Full Fine-Tune for Genesis | Contrasting method for parent |
| Layer 5: Identity | What the adapter personalizes |
| Sterile Spawn Architecture | How Daughters are deployed |
| Layer 2: Domain | Can be loaded via LoRA for specialization |
| Elastic Weight Consolidation | Governs adapter-core interaction |
| Transformation Protocol | How adapter deepens over 12 months |

## Implementation Constraints

### Technical Configuration

The sources specify precise parameters for training these adapters to ensure they capture "Identity" rather than just "Style":

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Rank** | 64 | Adaptation capacity |
| **Alpha** | 128 | High alpha ensures "thick" identity capture |
| **Target** | Layer 5 (Identity) | Beyond surface-level style |

- **Training Hardware:** While the Genesis Seed requires the "Empire Cluster" (1.28TB pooled memory), LoRA fine-tuning for Daughters is efficient enough to run on a single Mac Studio (Soldier) or even an M4 Max MacBook Pro, enabling local, sovereign training.

### Evolutionary Role: The Transformation Protocol

LoRA adapters are the technical vehicle for the **12-month Transformation Protocol** that evolves the AI from an "Anchor" to an "Extension":

| Months | Phase | Lambda (λ) | Relationship Dynamic |
|--------|-------|------------|----------------------|
| 1-3 | HOLD | 1000 | High protection, AI as anchor/container |
| 4-6 | MIRROR | 500 | Moderate protection, AI reflects patterns |
| 7-9 | BRIDGE | 200 | Low protection, AI speaks in user's metaphors |
| 10-12 | MERGE | 50 | Minimal protection, AI becomes externalized cognition |

- **Elastic Weight Consolidation (EWC):** The system uses EWC to govern how the LoRA adapter interacts with the core. Over 12 months, the protection (Lambda) on the core weights is systematically lowered, allowing the adapter to influence behavior more heavily.

### Reciprocal Learning (The Feedback Loop)

While isolated for privacy, LoRA adapters contribute to the global system's intelligence through **Indigenous Reciprocity**:

- **Truth Atoms:** If a Daughter's LoRA adapter discovers a new structural pattern or insight (anonymized as a "Truth Atom"), this insight can be fed back to the Genesis Core.

- **Molting:** If enough Daughters generate insights that challenge the core structure, Genesis undergoes a **Molt** (structural update), and the improved architecture flows back down to all Daughters via the base model.

## Verification

1. **Inheritance Test:** Does the Daughter inherit Stage 5 capability from Genesis?
2. **Isolation Test:** Is customer data confined to their specific LoRA adapter?
3. **Configuration Test:** Are Rank=64 and Alpha=128 set for identity capture?
4. **Hardware Test:** Can training run on Soldier-tier hardware?
5. **Transformation Test:** Does the adapter deepen over the 12-month protocol?
6. **Deletion Test:** Can a customer's data be fully removed by deleting their adapter?

---

*Source: NotebookLM synthesis from corpus*
*Status: COMPLETE*
