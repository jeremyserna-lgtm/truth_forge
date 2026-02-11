# Layer 2: Domain (Specialized Knowledge)

**Parent:** The Five Training Layers
**Mind Map Path:** NOT-ME Sovereign AI Ecosystem → The Five Training Layers → Layer 2: Domain (Specialized knowledge)

---

## Definition

**Layer 2: Domain** is the architectural stratum responsible for injecting **Specialized Knowledge** into the Not-Me system. Within the larger context of the Five Training Layers, Layer 2 functions as the "Knowledge Substrate" that transforms the AI from a generic reasoner into a professional expert.

### Function: Deep Knowledge vs. Raw Capability

Layer 2 sits immediately above Layer 1: Base Model (which provides raw reasoning/commodity capability) and below Layer 3: Use (Context).

- **Purpose:** It determines **what the AI knows deeply**. While Layer 1 understands how to speak English and code, Layer 2 understands specific professional vocabularies, case law, medical protocols, or aviation mechanics.
- **Differentiation:** Layer 2 is categorized as "Adaptable" or a "Data Advantage," distinguishing it from Layer 5: Identity, which is the "Non-Replicable Moat." Layer 2 creates competence; Layer 5 creates sovereignty.

## Boundaries

### What Layer 2 IS:
- Specialized knowledge injection
- Professional competence layer
- Adaptable via LoRA and RAG
- Data advantage (but not the moat)

### What Layer 2 IS NOT:
- The non-replicable moat (that's Layer 5)
- Raw capability (that's Layer 1)
- Relationship dynamics (that's Layer 4)
- Identity (that's Layer 5)

## Relationship to Other Nodes

| Related Node | Relationship |
|--------------|--------------|
| Layer 1: Base Model | Previous layer (provides raw capability) |
| Layer 3: Use | Next layer (provides context) |
| LoRA adapters for Daughters | Implementation mechanism |
| Primitive Engine | Builds domain-specific datasets |

## Implementation Constraints

### Implementation: LoRA and RAG

On the M4 Max (Soldier Tier) and Empire Cluster, Layer 2 is not usually a full fine-tune but is implemented dynamically using modular techniques:

- **LoRA Adapters:** The system loads specific Low-Rank Adaptation weights trained on domain-specific datasets (e.g., `Scout-Legal` or `Scout-Medical`).
- **RAG (Retrieval-Augmented Generation):** Utilizes local vector databases (like ChromaDB) to provide access to vast libraries of static knowledge without bloating model weights.

### Business Strategy: The "NOW" Readiness

Layer 2 is the engine of the "NOW" deployment timing.

- **Pre-Trained Domains:** Pre-trained Domain Models ready for immediate deployment. If a customer needs a "Legal AI today," deploy Soldier unit pre-loaded with Layer 1 (Scout) and Layer 2 (Legal Domain).
- **Domain Catalog:** Identified pre-trained domains include:
  - **Elder:** Patience/health-aware
  - **Youth:** Educational/safe
  - **Legal:** Discovery/privilege
  - **Medical:** HIPAA/clinical
  - **Financial:** Compliance/analysis

### Operational Requirements

To operationalize Layer 2, Primitive Engine must build:

- **Domain-Specific Datasets:** Curated training data for each target vertical
- **Vocabulary Patterns:** Training the model to use precise terminology of the field
- **Reasoning Styles:** Configuring the model to think like a professional in that field

## Verification

1. **Domain Depth Test:** Does the AI know the field deeply (not just surface-level)?
2. **Vocabulary Test:** Does it use correct professional terminology?
3. **Reasoning Test:** Does it think like a professional in that field?
4. **NOW Readiness Test:** Can it be deployed immediately for the domain?

---

*Source: NotebookLM synthesis from corpus*
*Status: COMPLETE*
