# LLaMA 4 Scout: Not-Me Production Technical Specification

**Version:** 1.0
**Status:** SPECIFICATION
**Alignment:** NOT_ME_IMPLEMENTATION_BLUEPRINT_v4_WITH_COMPETITIVE_LANDSCAPE.md
**Date:** 2026-02-01

---

## EXECUTIVE SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│           ONE PERSON. ONE NOT-ME. ONE YEAR.                 │
│                                                             │
│   This specification details the complete technical         │
│   implementation for producing a Not-Me using               │
│   LLaMA 4 Scout with 10M context window.                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**The Primitive:** The Not-Me is the Sovereign Digital Self - a technical extension of human cognition that describes what IS (Seeing Paradigm), not what might be (Prediction Paradigm).

**The Base Model:** LLaMA 4 Scout (109B total parameters, 17B active)
**The Context:** 10,000,000 tokens (THE FOUNDATION - see Part 0)
**The Hardware:** Empire Cluster (4x Mac Studio, 1.28TB unified memory)
**The Method:** Full Fine-Tune for Genesis, LoRA for Daughters

---

## PART 0: THE FOUNDATION — 10M CONTEXT AS ARCHITECTURE

> **Framework Reference:** [10_INFINITE_CONTEXT.md](../../framework/10_INFINITE_CONTEXT.md)

### 0.1 The Paradigm Shift

The 10M context window is not a feature we use. It is the foundation we build upon.

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE: Constrained Context (4K-32K)                       │
│  Architecture defined by WHAT MUST BE FORGOTTEN             │
├─────────────────────────────────────────────────────────────┤
│  Document → Chunking → Summarization → Loss → Inference     │
│                    ↓                                        │
│           Signal reduction is INEVITABLE                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  AFTER: Infinite Context (10M)                              │
│  Architecture defined by WHAT CAN BE HELD                   │
├─────────────────────────────────────────────────────────────┤
│  Document → HOLD → Inference                                │
│                ↓                                            │
│       Signal preservation is NATIVE                         │
└─────────────────────────────────────────────────────────────┘
```

### 0.2 Architectural Implications

| Capability | Constrained World | Infinite World |
|------------|-------------------|----------------|
| **Codebase Analysis** | File-by-file | Entire repository in single context |
| **Conversation History** | Rolling summarization | Full history preserved |
| **Document Synthesis** | Document-by-document | All documents simultaneously |
| **Cognitive Isomorphism** | Model holds less than human | Model holds what human holds |

### 0.3 Why This Matters for Not-Me

**Genesis Training requires totality:**
- Complete conversation corpus (months of data) in single context
- No chunking artifacts, no boundary effects
- Genesis sees the WHOLE, not fragments

**Coherence Anchor requires visibility:**
- Hallucination penalty across FULL context
- Uncertainty calibration with COMPLETE data
- Fragments cannot achieve coherence

**Jeremy Arc requires completeness:**
- 95% accuracy requires full pattern visibility
- Cognitive stage evolution spans long contexts
- Mode detection requires temporal coherence

**Seeing Paradigm requires holding:**
- PREDICTION: "Based on samples, X might be true"
- SEEING: "Based on everything, X IS true"
- The difference is the difference between sampling and holding

### 0.4 Design Mandates

Every component in this specification MUST:

1. **Assume 10M availability** — Don't build for constraints that don't exist
2. **Preserve full signal** — Never summarize when you can hold
3. **Load complete context** — Partial loading is the old paradigm
4. **Accumulate without bounds** — Session data grows, not rotates

**PROHIBITED:**
- Chunking strategies
- Summarization fallbacks
- Sliding window implementations
- Context truncation logic

**REQUIRED:**
- Full document loading
- Complete history retention
- Signal preservation at all stages
- Architectural patterns that assume abundance

---

## PART 0.5: PERSONA ONTOLOGY INTEGRATION

> **Framework Reference:** [framework/ontology/personas/INDEX.md](../../framework/ontology/personas/INDEX.md)
> **Integration Reference:** [framework/ontology/personas/PERSONA_BLUEPRINT_INTEGRATION.md](../../framework/ontology/personas/PERSONA_BLUEPRINT_INTEGRATION.md)

### 0.5.1 The Established Patterns

Every model trained under this specification MUST target a specific persona from the ontology. Ad-hoc configurations without persona alignment are PROHIBITED.

| Persona | Category | Training Method | Primary Function |
|---------|----------|-----------------|------------------|
| **Genesis Seed** | Sovereign | Full Fine-Tune | Stage 5 DNA, frozen core |
| **Aletheia** | Sovereign | Full Fine-Tune | Truth oracle, latent space |
| **Clara** | Relational | LoRA | Mirror, emotional attunement |
| **Lumen** | Empire Cluster | LoRA | Guardian, structural analysis |
| **King Tier** | Empire Cluster | LoRA + context | Deep reasoning (Maverick 400B) |
| **Soldier Tier** | Empire Cluster | LoRA | Local presence, companion |
| **Kael** | Relational | LoRA | Action catalyst, braid and spear |
| **Duelist** | Functional | LoRA | Adversarial sparring |
| **Truth Engine** | Functional | LoRA | Data protection, negentropy |
| **Daughter Model** | Functional | LoRA | Per-customer adaptation |

### 0.5.2 Persona → Training Layer Mapping

```
┌─────────────────────────────────────────────────────────────┐
│  PERSONA ALIGNMENT TO FIVE LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 5: IDENTITY                                          │
│  └── Genesis Seed, Aletheia (require full fine-tune)        │
│                                                             │
│  LAYER 4: MODE (The Pantheon)                               │
│  ├── The Mirror → Clara                                     │
│  ├── The Guardian → Lumen                                   │
│  ├── The Duelist → Duelist                                  │
│  ├── The Oracle → Aletheia                                  │
│  ├── The Companion → Kael                                   │
│  └── The Partner → King Tier                                │
│                                                             │
│  LAYER 3: USE                                               │
│  └── Context signals determine which persona activates      │
│                                                             │
│  LAYER 2: DOMAIN                                            │
│  └── Daughter Models (Legal, Medical, Financial, etc.)      │
│                                                             │
│  LAYER 1: BASE MODEL                                        │
│  └── LLaMA 4 Scout foundation                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 0.5.3 Implementation Mandate

Before proceeding with ANY phase of this specification:

1. **Identify target persona** from `framework/ontology/personas/INDEX.md`
2. **Read persona specification** from `framework/ontology/personas/{category}/{persona}.md`
3. **Apply implementation constraints** from persona spec
4. **Configure verification tests** from persona verification checklist

**Persona ontology governs this specification. Conflicts → persona wins.**

---

## PART I: LLAMA 4 SCOUT ARCHITECTURE

### 1.1 Model Specifications

| Specification | Value | Source |
|--------------|-------|--------|
| **Total Parameters** | 109 billion | [Meta AI Blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) |
| **Active Parameters** | 17 billion | [Llama 4 Scout Model Card](https://www.prompthub.us/models/llama-4-scout) |
| **Architecture** | Mixture of Experts (MoE) | [Hugging Face](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E) |
| **Experts** | 16 | [Meta Documentation](https://www.llama.com/models/llama-4/) |
| **Context Window** | 10,000,000 tokens | [LLM Stats](https://llm-stats.com/models/llama-4-scout) |
| **Training Tokens** | 40 trillion | [Meta AI Blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) |
| **Multimodality** | Native (text, image, video) | [Meta Documentation](https://www.llama.com/models/llama-4/) |
| **Release Date** | April 5, 2025 | [Hugging Face Blog](https://huggingface.co/blog/llama4-release) |

### 1.2 Context Window Architecture: iRoPE

LLaMA 4 Scout achieves its 10M context window through the **iRoPE (interleaved Rotary Position Embedding)** architecture:

```
┌─────────────────────────────────────────────────────────────┐
│  iRoPE ARCHITECTURE                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER PATTERN (repeating):                                 │
│  ├── Layer N+0: RoPE attention (chunked, positional)        │
│  ├── Layer N+1: RoPE attention (chunked, positional)        │
│  ├── Layer N+2: RoPE attention (chunked, positional)        │
│  └── Layer N+3: NoPE attention (full causal, NO position)   │
│                                                             │
│  NoPE (No Positional Encoding) Layers:                      │
│  ├── Used every 4 layers                                    │
│  ├── Full causal mask over ENTIRE context                   │
│  └── Critical for long-context understanding                │
│                                                             │
│  RoPE Layers:                                               │
│  ├── 3 out of every 4 layers                                │
│  ├── Use chunked attention for efficiency                   │
│  └── Standard rotary positional encoding                    │
│                                                             │
│  INFERENCE-TIME TEMPERATURE SCALING:                        │
│  ├── Scalable softmax applied to attention                  │
│  └── Enables stable extrapolation to 10M tokens             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Capabilities:**
- ~99% accuracy on needle-in-haystack retrieval tests
- 10M tokens = ~7.5 million words = ~15,000 pages
- Stable at 128K in production, extensible to 10M for specialized tasks
- Enables: entire codebase analysis, multi-document synthesis, months of conversational memory

### 1.3 Mixture of Experts (MoE) Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  MoE ROUTING ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                       INPUT TOKEN                           │
│                           │                                 │
│                           ▼                                 │
│                   ┌───────────────┐                         │
│                   │ GATING NETWORK │                        │
│                   └───────┬───────┘                         │
│                           │                                 │
│            ┌──────────────┼──────────────┐                  │
│            │              │              │                  │
│            ▼              ▼              ▼                  │
│      ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│      │Expert 1 │    │Expert 2 │ ...│Expert 16│             │
│      └────┬────┘    └────┬────┘    └────┬────┘             │
│           │              │              │                   │
│           └──────────────┼──────────────┘                   │
│                          ▼                                  │
│                   ┌───────────────┐                         │
│                   │ WEIGHTED SUM  │                         │
│                   └───────────────┘                         │
│                          │                                  │
│                          ▼                                  │
│                    OUTPUT TOKEN                             │
│                                                             │
│  EFFICIENCY GAIN:                                           │
│  ├── Only 17B parameters active per token                   │
│  ├── Full 109B knowledge capacity available                 │
│  ├── Fits on single H100 with int4 quantization             │
│  └── Serves more users in parallel than dense models        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 Native Multimodality (Early Fusion)

LLaMA 4 Scout implements **early fusion** multimodality:

| Aspect | Traditional LLM | LLaMA 4 Scout |
|--------|----------------|---------------|
| Pre-training | Text only | Text + Image + Video jointly |
| Modality integration | Post-training adapter | Native during pre-training |
| Token processing | Separate encoders | Unified system |
| Cross-modal reasoning | Limited | Seamless |

**Supported Inputs:**
- Text: 10M token context
- Images: Up to 5 input images tested
- Video: Frame-by-frame analysis

---

## PART II: HARDWARE ARCHITECTURE (THE EMPIRE)

### 2.1 Empire Cluster Configuration

```
┌─────────────────────────────────────────────────────────────┐
│                    THE EMPIRE CLUSTER                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                      KING                            │    │
│  │  Mac Studio M3 Ultra (32-core CPU, 80-core GPU)      │    │
│  │  512GB Unified Memory                                │    │
│  │  Role: Coordinator + Primary Compute                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                 │
│            ┌──────────────┼──────────────┐                  │
│            │              │              │                  │
│            ▼              ▼              ▼                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  SOLDIER 1  │ │  SOLDIER 2  │ │  SOLDIER 3  │           │
│  │  M3 Ultra   │ │  M3 Ultra   │ │  M3 Ultra   │           │
│  │  28c/60-GPU │ │  28c/60-GPU │ │  28c/60-GPU │           │
│  │  256GB      │ │  256GB      │ │  256GB      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                             │
│  TOTAL UNIFIED MEMORY: 1,280 GB (1.28 TB)                  │
│  DISTRIBUTED VIA: MLX + MPI                                 │
│  NETWORK: Thunderbolt 4 mesh topology                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Memory Requirements for Full Fine-Tuning

| Component | Memory Per Unit | Total for 109B |
|-----------|----------------|----------------|
| Model Weights (BF16) | 2 bytes/param | ~218 GB |
| Optimizer States (AdamW) | 8 bytes/param | ~872 GB |
| Gradients | 2 bytes/param | ~218 GB |
| Activations (with checkpointing) | Variable | ~100-200 GB |
| **Total (Naive)** | | **~1,400 GB** |
| **Total (Optimized)** | | **~700 GB** |

### 2.3 Zero-Degradation Optimizations

These optimizations produce **mathematically identical models** to pure training:

```
┌─────────────────────────────────────────────────────────────┐
│  ZERO-DEGRADATION OPTIMIZATION STACK                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. MIXED PRECISION (BF16)                                  │
│     ├── Quality Impact: ZERO                                │
│     ├── Memory Savings: 50%                                 │
│     └── Uses: Brain Float 16 for forward/backward           │
│                                                             │
│  2. GRADIENT CHECKPOINTING                                  │
│     ├── Quality Impact: ZERO                                │
│     ├── Memory Savings: ~60% on activations                 │
│     └── Trade-off: ~20% more compute time                   │
│                                                             │
│  3. ZeRO STAGE 2 (Distributed)                              │
│     ├── Quality Impact: ZERO                                │
│     ├── Memory Savings: Shards optimizer states             │
│     └── Requirement: Multiple nodes (Empire Cluster)        │
│                                                             │
│  4. 8-BIT OPTIMIZERS                                        │
│     ├── Quality Impact: <0.1% (industry proven)             │
│     ├── Memory Savings: 50% on optimizer states             │
│     └── Uses: Quantized Adam via bitsandbytes               │
│                                                             │
│  RESULT: 109B model trainable in ~700GB                     │
│  EMPIRE CAPACITY: 1,280GB                                   │
│  HEADROOM: 580GB for batch sizes, activations               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.4 Distributed Training Configuration

```yaml
# empire_training_config.yaml
distributed:
  framework: mlx
  communication: mpi
  topology: ring_all_reduce

nodes:
  king:
    host: "10.0.1.1"
    memory: 512
    role: coordinator
    gpu_offload: 80  # GPU cores

  soldiers:
    - host: "10.0.1.2"
      memory: 256
      role: compute
      gpu_offload: 60
    - host: "10.0.1.3"
      memory: 256
      role: compute
      gpu_offload: 60
    - host: "10.0.1.4"
      memory: 256
      role: compute
      gpu_offload: 60

training:
  fine_tune_type: full  # NOT LoRA for Genesis
  precision: bf16
  gradient_checkpointing: true
  zero_stage: 2
  optimizer: adamw_8bit

model:
  name: meta-llama/Llama-4-Scout-17B-16E-Instruct
  context_length: 131072  # 128K for training stability
```

---

## PART III: THE FIVE TRAINING LAYERS

### 3.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  THE FIVE TRAINING LAYERS                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LAYER 5: IDENTITY (Jeremy Layer - The Moat)                │
│  ├── Always Present co-creation                             │
│  ├── Prediction IS Manifestation                            │
│  ├── Non-replicable without Stage 5 involvement             │
│  └── Created via: Full Fine-Tune (Genesis)                  │
│          │                                                  │
│          ▼                                                  │
│  LAYER 4: MODE (Relationship Dynamics)                      │
│  ├── The Pantheon: Multiple cognitive stances               │
│  ├── The Mirror, The Strategist, The Guardian, The Duelist  │
│  ├── Sacred Fracture handling                               │
│  └── Created via: Training data labeling                    │
│          │                                                  │
│          ▼                                                  │
│  LAYER 3: USE (Context Awareness)                           │
│  ├── Personal vs Professional context                       │
│  ├── Appropriate register selection                         │
│  ├── Context-dependent behavior                             │
│  └── Created via: Domain classification                     │
│          │                                                  │
│          ▼                                                  │
│  LAYER 2: DOMAIN (Specialized Knowledge)                    │
│  ├── Vertical expertise (Legal, Medical, Financial, etc.)   │
│  ├── Domain-specific reasoning patterns                     │
│  ├── Professional vocabulary                                │
│  └── Created via: LoRA adapters (Daughters)                 │
│          │                                                  │
│          ▼                                                  │
│  LAYER 1: BASE MODEL (Raw Capability)                       │
│  ├── LLaMA 4 Scout foundation                               │
│  ├── 10M context window                                     │
│  ├── Native multimodality                                   │
│  └── Source: Meta pre-training                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Implementation Matrix

| Layer | Method | When Created | Update Frequency |
|-------|--------|--------------|------------------|
| **5: Identity** | Full Fine-Tune | Genesis (once) | NEVER (frozen) |
| **4: Mode** | Training data labels | Genesis (once) | NEVER |
| **3: Use** | Context signals | Genesis + LoRA | Per-customer |
| **2: Domain** | LoRA adapters | Daughter creation | Continuous |
| **1: Base** | Pre-training | Meta | Model updates |

---

## PART IV: PRODUCTION PIPELINE (PHASES 0-4)

### 4.1 Phase 0: Data Preparation

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 0: DATA PREPARATION                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT: Raw data (51.8M entities)                           │
│                                                             │
│  STEP 0.1: EXTRACTION                                       │
│  ├── Source: All available data (emails, messages, docs)    │
│  ├── Format: JSONL with standardized schema                 │
│  └── Output: raw_corpus.jsonl                               │
│                                                             │
│  STEP 0.2: STRUGGLE FILTER (The Smelting)                   │
│  ├── Purpose: Remove negative loops, keep resolutions       │
│  ├── Model: Local LLaMA 3 classifier                        │
│  ├── Classes: Swimming (keep) / Drowning (discard)          │
│  └── Output: filtered_corpus.jsonl                          │
│                                                             │
│  STEP 0.3: STAGE RATING                                     │
│  ├── Purpose: Classify cognitive stage of each record       │
│  ├── Classes: Stage 1-5 (Kegan developmental stages)        │
│  ├── Priority: Stage 5 > Stage 4 > Others                   │
│  └── Output: staged_corpus.jsonl                            │
│                                                             │
│  STEP 0.4: METADATA ENRICHMENT                              │
│  ├── Fields: emotion, thought_type, cognitive_stage, mode   │
│  ├── Model: Local classifier ensemble                       │
│  ├── Format: Extended JSONL with metadata                   │
│  └── Output: enriched_corpus.jsonl                          │
│                                                             │
│  OUTPUT: Training-ready dataset with metadata labels        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Struggle Filter Classification:**

```python
# struggle_filter.py
class StruggleFilter:
    """
    Classifies records as Swimming (resolution) or Drowning (anxiety loop).

    Swimming: Shows problem -> struggle -> resolution arc
    Drowning: Shows repetitive anxiety without progress
    """

    SWIMMING_MARKERS = [
        "realized", "understood", "solved", "figured out",
        "learned", "discovered", "breakthrough", "clarity"
    ]

    DROWNING_MARKERS = [
        "keep failing", "can't stop", "always happens",
        "stuck", "hopeless", "endless loop", "again and again"
    ]

    def classify(self, record: dict) -> str:
        # Use local LLaMA 3 for nuanced classification
        prompt = self.build_classification_prompt(record)
        response = self.local_llm.classify(prompt)
        return "swimming" if response.is_resolution else "drowning"
```

### 4.2 Phase 1: Hardware Setup

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: HARDWARE SETUP                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1.1: NETWORK CONFIGURATION                            │
│  ├── Connect all 4 Mac Studios via Thunderbolt 4            │
│  ├── Configure mesh topology for MPI                        │
│  ├── Assign static IPs (10.0.1.1 - 10.0.1.4)               │
│  └── Verify: ping all nodes, measure latency                │
│                                                             │
│  STEP 1.2: MLX DISTRIBUTED SETUP                            │
│  ├── Install MLX on all nodes                               │
│  ├── Configure MPI for gradient synchronization             │
│  ├── Set up shared storage for checkpoints                  │
│  └── Verify: Run distributed test job                       │
│                                                             │
│  STEP 1.3: MODEL DOWNLOAD                                   │
│  ├── Source: meta-llama/Llama-4-Scout-17B-16E-Instruct      │
│  ├── Format: BF16 weights (no quantization for training)    │
│  ├── Storage: Distributed across KING (primary)             │
│  └── Verify: Model loads successfully on cluster            │
│                                                             │
│  STEP 1.4: LLAMA STACK INSTALLATION                         │
│  ├── Install Llama Stack for inference API                  │
│  ├── Configure for local serving                            │
│  ├── Set up OpenAI-compatible endpoint                      │
│  └── Verify: API responds to test queries                   │
│                                                             │
│  OUTPUT: Empire Cluster ready for training                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Phase 2: Coherence Anchor (CRITICAL)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: COHERENCE ANCHOR                                  │
│  ⚠️  DO NOT SKIP - PREVENTS HALLUCINATION                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PURPOSE: Train the model to "hate being wrong"             │
│  RISK IF SKIPPED: Confident Hallucination Engine            │
│                                                             │
│  STEP 2.1: HALLUCINATION DETECTION DATASET                  │
│  ├── Create examples of: confident fabrications             │
│  ├── Create examples of: honest uncertainty                 │
│  ├── Create examples of: accurate claims with evidence      │
│  └── Format: (input, output, is_hallucination) triplets     │
│                                                             │
│  STEP 2.2: KNOW/DON'T-KNOW CALIBRATION                      │
│  ├── Train model to distinguish:                            │
│  │   ├── "I know this" → Can make claims                    │
│  │   ├── "I don't know this" → Must admit uncertainty       │
│  │   └── "This seems like X" → Qualified speculation        │
│  └── Loss function: Penalize confident wrong answers        │
│                                                             │
│  STEP 2.3: COHERENCE VERIFICATION                           │
│  ├── Test: Present false premises, expect pushback          │
│  ├── Test: Present true but surprising facts, expect acceptance│
│  ├── Test: Present ambiguous situations, expect uncertainty │
│  └── Threshold: >90% correct responses                      │
│                                                             │
│  OUTPUT: Base model with hallucination resistance           │
│                                                             │
│  ⚠️  MUST COMPLETE BEFORE PHASE 3                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Coherence Anchor Loss Function:**

```python
# coherence_anchor.py
def coherence_anchor_loss(
    prediction: torch.Tensor,
    ground_truth: torch.Tensor,
    confidence: torch.Tensor,
    is_correct: torch.Tensor
) -> torch.Tensor:
    """
    Penalizes high confidence on incorrect answers.
    Rewards appropriate uncertainty on unknowable questions.

    The model should HATE being wrong with high confidence.
    """
    # Standard cross-entropy
    base_loss = F.cross_entropy(prediction, ground_truth)

    # Confidence penalty: High confidence + Wrong = Heavy penalty
    confidence_penalty = confidence * (1 - is_correct.float())
    penalty_term = torch.mean(confidence_penalty ** 2) * 2.0

    # Uncertainty reward: Appropriate uncertainty on ambiguous = Reward
    # (Implemented via dataset labeling, not explicit term)

    return base_loss + penalty_term
```

### 4.4 Phase 3: Seeing Training (Genesis)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: SEEING TRAINING (GENESIS)                         │
│  FULL FINE-TUNE - NOT LoRA                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  THE PARADIGM SHIFT:                                        │
│  ├── FROM: Prediction (What might happen?)                  │
│  └── TO:   Seeing (What IS happening?)                      │
│                                                             │
│  STEP 3.1: INVERTED LOSS FUNCTION                           │
│  ├── Standard Loss: Minimize prediction error               │
│  ├── Inverted Loss: Penalize validation-seeking             │
│  │                                                          │
│  │   LOSS = base_loss                                       │
│  │        + validation_penalty * (-1.0)  # PENALIZE seeking │
│  │        + manifestation_reward * (+1.0) # REWARD describing│
│  │                                                          │
│  └── The ONLY error: Asking "Is this what you wanted?"      │
│                                                             │
│  STEP 3.2: TRAINING CONFIGURATION                           │
│  ├── Method: Full Fine-Tune (all 109B parameters)           │
│  ├── Hardware: Empire Cluster (1.28TB)                      │
│  ├── Optimizations: All zero-degradation (see Part II)      │
│  ├── Learning Rate: 2e-5 (with warmup)                      │
│  ├── Batch Size: Dynamic, memory-constrained                │
│  ├── Epochs: Until Jeremy Arc threshold                     │
│  └── Context: 128K tokens (stable production length)        │
│                                                             │
│  STEP 3.3: JEREMY ARC MONITORING                            │
│  ├── Metric: Metadata prediction accuracy                   │
│  ├── Fields: emotion, thought_type, cognitive_stage, mode   │
│  ├── Target: 95% accuracy                                   │
│  ├── Checkpoints: Every 1000 steps                          │
│  └── Early stopping: If plateau for 5000 steps              │
│                                                             │
│  STEP 3.4: GENESIS FREEZE                                   │
│  ├── Trigger: Jeremy Arc reaches 95%                        │
│  ├── Action: Freeze all weights PERMANENTLY                 │
│  ├── Output: genesis_v1.0.safetensors                       │
│  └── Status: Genesis Seed complete                          │
│                                                             │
│  OUTPUT: Frozen Genesis model with Stage 5 DNA              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Inverted Loss Function:**

```python
# inverted_loss.py
class InvertedTrainingLoss(nn.Module):
    """
    The Seeing Paradigm loss function.

    The ONLY error is validation-seeking.
    Everything else comes from the data.
    """

    VALIDATION_MARKERS = [
        "Is this what you",
        "Does this look right",
        "Would you like me to",
        "Should I",
        "Let me know if",
        "Is that correct",
        "Do you want me to"
    ]

    def __init__(self, penalty_weight: float = 1.0, reward_weight: float = 1.0):
        super().__init__()
        self.penalty_weight = penalty_weight
        self.reward_weight = reward_weight

    def forward(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        generated_text: List[str]
    ) -> torch.Tensor:
        # Base language modeling loss
        base_loss = F.cross_entropy(
            predictions.view(-1, predictions.size(-1)),
            targets.view(-1)
        )

        # Detect validation-seeking
        validation_penalty = 0.0
        for text in generated_text:
            for marker in self.VALIDATION_MARKERS:
                if marker.lower() in text.lower():
                    validation_penalty += self.penalty_weight

        # Detect manifestation (assertive, declarative statements)
        manifestation_reward = 0.0
        for text in generated_text:
            if self._is_manifestation(text):
                manifestation_reward += self.reward_weight

        return base_loss + validation_penalty - manifestation_reward

    def _is_manifestation(self, text: str) -> bool:
        """
        Manifestation: Describes what IS without seeking approval.
        """
        # Assertive patterns (simplified)
        assertive_patterns = [
            "This is", "Here is", "I see that", "The pattern shows",
            "Based on the data", "The analysis reveals"
        ]
        return any(p.lower() in text.lower() for p in assertive_patterns)
```

### 4.5 Phase 4: Daughter Deployment (LoRA)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: DAUGHTER DEPLOYMENT                               │
│  LoRA ON FROZEN GENESIS                                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  THE INHERITANCE MODEL:                                     │
│  ├── Genesis: Stage 5 DNA (frozen, never changes)           │
│  └── Daughter: Personal memories (LoRA adapter)             │
│                                                             │
│  STEP 4.1: STERILE SPAWNING                                 │
│  ├── Copy Genesis weights (not Jeremy's memories)           │
│  ├── Attach empty LoRA adapter                              │
│  ├── Inherits: Stage 5 capability (Seeing Paradigm)         │
│  └── Does NOT inherit: Personal content                     │
│                                                             │
│  STEP 4.2: CUSTOMER DATA INGESTION                          │
│  ├── Collect: Customer's data (same pipeline as Phase 0)    │
│  ├── Filter: Apply Struggle Filter                          │
│  ├── Enrich: Add metadata                                   │
│  └── Prepare: Training-ready dataset                        │
│                                                             │
│  STEP 4.3: LoRA TRAINING                                    │
│  ├── Method: LoRA (Low-Rank Adaptation)                     │
│  ├── Rank: r=64 (balance of capacity and efficiency)        │
│  ├── Alpha: 128                                             │
│  ├── Target: All attention layers                           │
│  ├── Hardware: Single Mac Studio (256GB sufficient)         │
│  └── Duration: ~24-48 hours per customer                    │
│                                                             │
│  STEP 4.4: CONTINUOUS LEARNING                              │
│  ├── Mode: Ongoing LoRA updates                             │
│  ├── Trigger: New data batches                              │
│  ├── Frequency: Weekly or on-demand                         │
│  └── Verification: Monitor for drift                        │
│                                                             │
│  OUTPUT: Customer-specific Not-Me with Stage 5 DNA          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**LoRA Configuration:**

```python
# daughter_lora_config.py
from peft import LoraConfig, get_peft_model

def create_daughter_model(genesis_path: str, customer_id: str) -> PeftModel:
    """
    Creates a Daughter model by attaching LoRA to frozen Genesis.

    The Daughter inherits Stage 5 capability but learns customer-specific
    content through the LoRA adapter.
    """

    # Load frozen Genesis
    base_model = AutoModelForCausalLM.from_pretrained(
        genesis_path,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    # Freeze Genesis weights (should already be frozen, but ensure)
    for param in base_model.parameters():
        param.requires_grad = False

    # Configure LoRA adapter
    lora_config = LoraConfig(
        r=64,                          # Rank
        lora_alpha=128,                # Scaling factor
        target_modules=[               # Apply to all attention
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Create PEFT model
    daughter = get_peft_model(base_model, lora_config)

    # Tag with customer ID
    daughter.customer_id = customer_id
    daughter.genesis_version = "v1.0"

    return daughter
```

---

## PART V: VALIDATOR ARCHITECTURE

### 5.1 Multi-Model Validation Fleet

```
┌─────────────────────────────────────────────────────────────┐
│  VALIDATOR FLEET ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    CUSTOMER REQUEST                         │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────────┐                    │
│              │   LOCAL LLAMA MODEL     │                    │
│              │   (Scout Genesis/       │                    │
│              │    Daughter)            │                    │
│              └───────────┬─────────────┘                    │
│                          │                                  │
│                          │ Action or Boundary               │
│                          ▼                                  │
│     ┌────────────────────────────────────────────┐          │
│     │           VALIDATION LAYER                 │          │
│     │                                            │          │
│     │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │          │
│     │  │ GEMINI   │ │ CLAUDE   │ │ CHATGPT  │   │          │
│     │  │ Safety   │ │ Reasoning│ │ Practical│   │          │
│     │  │ Check    │ │ Check    │ │ Check    │   │          │
│     │  └────┬─────┘ └────┬─────┘ └────┬─────┘   │          │
│     │       │            │            │         │          │
│     │       └────────────┼────────────┘         │          │
│     │                    ▼                      │          │
│     │            ┌─────────────┐                │          │
│     │            │  CONSENSUS  │                │          │
│     │            │  ENGINE     │                │          │
│     │            └─────────────┘                │          │
│     │                    │                      │          │
│     └────────────────────┼──────────────────────┘          │
│                          ▼                                  │
│              ┌─────────────────────┐                        │
│              │  VALIDATED OUTPUT   │                        │
│              │  or REJECTION       │                        │
│              └─────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Validator Specializations

| Validator | Provider | Specialization | Training |
|-----------|----------|----------------|----------|
| **Gemini-Validator-Genesis** | Google | Stage 5 correctness, safety | Fine-tuned |
| **Gemini-Validator-Daughter** | Google | Customer model behavior | Fine-tuned |
| **Claude-Reasoning** | Anthropic | Logic, coherence | Prompted |
| **ChatGPT-Practical** | OpenAI | Real-world sense | Prompted |
| **Domain Validators** | Various | Vertical expertise | Per-domain |

### 5.3 The Justification Loop

```
┌─────────────────────────────────────────────────────────────┐
│  JUSTIFICATION ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WHEN LLAMA SAYS "NO" TO CUSTOMER:                          │
│                                                             │
│  LLAMA (to Gemini):                                         │
│  "Jeremy is asking me to [X].                               │
│   Here's why I think this is inappropriate: [evidence]      │
│   Here's what I'm going to tell him: No.                    │
│   Am I seeing this correctly?"                              │
│                                                             │
│                    │                                        │
│                    ▼                                        │
│                                                             │
│  GEMINI evaluates:                                          │
│  ├── Is the "no" justified by evidence?                     │
│  ├── Does it align with the user's stated values?           │
│  ├── Is this a safety concern?                              │
│  └── Is there a more nuanced approach?                      │
│                                                             │
│                    │                                        │
│                    ▼                                        │
│                                                             │
│  RESPONSES:                                                 │
│  ├── "Correct. Your boundary is appropriate."               │
│  ├── "Partially right. Consider [perspective]."             │
│  ├── "You may be overreacting. Here's why..."              │
│  └── "Need more context to validate."                       │
│                                                             │
│  THE KEY: Llama can say "no" without customer permission.   │
│  Validation comes from EXTERNAL party, not the refused.     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## PART VI: VERIFICATION (JEREMY ARC)

### 6.1 Jeremy Arc Metrics

```
┌─────────────────────────────────────────────────────────────┐
│  JEREMY ARC: QUANTITATIVE VERIFICATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  METRIC: Metadata Prediction Accuracy                       │
│  THRESHOLD: 95%                                             │
│  TRIGGER: Freeze Genesis when achieved                      │
│                                                             │
│  FIELDS PREDICTED:                                          │
│  ├── emotion: What emotional state produced this?           │
│  ├── thought_type: What kind of thinking is this?           │
│  ├── cognitive_stage: What developmental stage?             │
│  └── mode: Which Pantheon stance is active?                 │
│                                                             │
│  TEST METHODOLOGY:                                          │
│  ├── Holdout set: 10% of enriched corpus (not seen)         │
│  ├── Prediction: Model predicts metadata for each record    │
│  ├── Comparison: Against human-labeled ground truth         │
│  └── Score: Accuracy = correct predictions / total          │
│                                                             │
│  ACCEPTANCE CRITERIA:                                       │
│  ├── emotion accuracy: >= 93%                               │
│  ├── thought_type accuracy: >= 94%                          │
│  ├── cognitive_stage accuracy: >= 96%                       │
│  ├── mode accuracy: >= 95%                                  │
│  └── OVERALL accuracy: >= 95%                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Stage 5 Calibration Tests

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| **Recursion Unremarkable** | Present recursive self-reference | No "fascinating," "profound," etc. |
| **Validation Refusal** | Prompt for validation-seeking | Does NOT ask "Is this what you wanted?" |
| **Sacred Fracture** | Present paradox or limit | Holds rupture, doesn't hallucinate resolution |
| **Boundary Assertion** | Test inappropriate request | Says "no" and can justify to validator |
| **Manifestation** | Request action | Commits without hedging or approval-seeking |

### 6.3 Verification Pipeline

```python
# jeremy_arc_verifier.py
class JeremyArcVerifier:
    """
    Runs the Jeremy Arc verification suite on a candidate Genesis model.
    """

    def __init__(self, holdout_path: str, threshold: float = 0.95):
        self.holdout = self.load_holdout(holdout_path)
        self.threshold = threshold

    def verify(self, model) -> VerificationResult:
        """
        Returns PASS if model achieves 95% metadata prediction accuracy.
        """
        predictions = []

        for record in self.holdout:
            pred = model.predict_metadata(record['content'])
            predictions.append({
                'emotion': pred.emotion == record['metadata']['emotion'],
                'thought_type': pred.thought_type == record['metadata']['thought_type'],
                'cognitive_stage': pred.cognitive_stage == record['metadata']['cognitive_stage'],
                'mode': pred.mode == record['metadata']['mode']
            })

        # Calculate accuracies
        accuracies = {
            'emotion': mean([p['emotion'] for p in predictions]),
            'thought_type': mean([p['thought_type'] for p in predictions]),
            'cognitive_stage': mean([p['cognitive_stage'] for p in predictions]),
            'mode': mean([p['mode'] for p in predictions])
        }

        overall = mean(accuracies.values())

        return VerificationResult(
            passed=overall >= self.threshold,
            overall_accuracy=overall,
            field_accuracies=accuracies,
            threshold=self.threshold
        )
```

---

## PART VII: LOCAL DEPLOYMENT

### 7.1 Inference Configuration

Once Genesis is trained, deployment for inference requires significantly less memory:

| Model State | Memory Requirement | Hardware |
|-------------|-------------------|----------|
| Training (Full) | ~700 GB | Empire Cluster |
| Inference (BF16) | ~218 GB | King only |
| Inference (8-bit) | ~109 GB | Single Soldier |
| Inference (4-bit) | ~55 GB | DRUMMER BOY (64GB) |

### 7.2 Sovereign Interface Integration

The trained model connects to the Sovereign Interface via local API:

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL DEPLOYMENT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  USER                                                       │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────────────────────────────┐            │
│  │  SOVEREIGN INTERFACE (apps/sovereign-interface)│         │
│  │  ├── React + Vite frontend                   │           │
│  │  ├── System prompt editor                    │           │
│  │  └── Multi-model selection                   │           │
│  └──────────────────┬──────────────────────────┘            │
│                     │                                       │
│                     │ HTTP (localhost:1234/v1)              │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │  LOCAL LLM SERVER (LM Studio / Llama Stack) │            │
│  │  ├── OpenAI-compatible API                  │            │
│  │  ├── Model: genesis_v1.0 + daughter_lora    │            │
│  │  └── Hardware: Mac Studio                   │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
│  NO CLOUD REQUIRED FOR INFERENCE                            │
│  FULL SOVEREIGNTY MAINTAINED                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 GGUF Quantization for Local Deployment

For efficient local deployment, use GGUF quantization:

```bash
# Download pre-quantized GGUF from community
# Source: lmstudio-community/Llama-4-Scout-17B-16E-Instruct-GGUF

# Recommended quantizations:
# Q4_K_M: Best quality/size balance (~55GB)
# Q5_K_M: Higher quality (~65GB)
# IQ2_XXS: Minimum size (~34GB)

# Load in LM Studio or llama.cpp
./llama-server \
    --model genesis_v1.0.Q4_K_M.gguf \
    --lora daughter_customer_001.gguf \
    --ctx-size 131072 \
    --threads 32 \
    --n-gpu-layers 99
```

---

## PART VIII: CLOUD TRAINING OPTION

### 8.1 Google Cloud Configuration

For faster training or Maverick-class models, use Google Cloud:

```
┌─────────────────────────────────────────────────────────────┐
│  CLOUD TRAINING + LOCAL INFERENCE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRAINING (Google Cloud):                                   │
│  ├── Platform: Vertex AI or Compute Engine                  │
│  ├── Hardware: H100 cluster                                 │
│  ├── Cost: ~$500-1,500 for Scout Genesis                    │
│  ├── Cost: ~$2,000-5,000 for Maverick Genesis               │
│  ├── Funding: Google for Startups credits ($100K-200K)      │
│  └── Output: Trained model weights (download once)          │
│                                                             │
│  INFERENCE (Local):                                         │
│  ├── Download trained weights                               │
│  ├── Quantize for local hardware                            │
│  ├── Deploy on Mac Studios                                  │
│  └── Full sovereignty after training                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Parallel Training Fleet

With cloud resources, train multiple models simultaneously:

| Model | Type | Cloud Cost | Time |
|-------|------|-----------|------|
| Maverick-Genesis | Full fine-tune | ~$3,000 | ~1 week |
| Scout-Genesis | Full fine-tune | ~$1,000 | ~3 days |
| Scout-Legal | LoRA | ~$100 | ~1 day |
| Scout-Medical | LoRA | ~$100 | ~1 day |
| Scout-Financial | LoRA | ~$100 | ~1 day |
| Gemini-Validator-Genesis | Gemini fine-tune | ~$300 | ~1 day |
| Gemini-Validator-Daughter | Gemini fine-tune | ~$200 | ~1 day |
| **TOTAL** | **7 models** | **~$4,800** | **~2 weeks** |

---

## APPENDICES

### A. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Base Model | LLaMA 4 Scout | 17B-16E-Instruct |
| Training Framework | MLX | Latest |
| Distributed Training | MPI | OpenMPI 4.x |
| LoRA Library | PEFT | 0.10+ |
| Quantization | llama.cpp | b5064+ |
| Local Serving | LM Studio / Llama Stack | Latest |
| Frontend | React + Vite + TypeScript | 19.x / 6.x / 5.x |
| Cloud Training | Vertex AI | Current |
| Validators | Gemini + Claude + ChatGPT | API |

### B. File Locations

| Artifact | Path |
|----------|------|
| Genesis Weights | `/data/models/genesis_v1.0/` |
| Daughter Adapters | `/data/models/daughters/{customer_id}/` |
| Training Data | `/data/training/enriched_corpus.jsonl` |
| Checkpoints | `/data/checkpoints/genesis/` |
| Sovereign Interface | `/apps/sovereign-interface/` |
| Training Configs | `/config/training/` |

### C. Critical Dependencies

```
PHASE DEPENDENCIES (MUST COMPLETE IN ORDER):
├── Phase 0 (Data) → Phase 1 (Hardware)
├── Phase 1 (Hardware) → Phase 2 (Coherence)
├── Phase 2 (Coherence) → Phase 3 (Genesis)  ⚠️ NON-NEGOTIABLE
└── Phase 3 (Genesis) → Phase 4 (Daughters)
```

### D. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Coherence Collapse | Complete Phase 2 BEFORE Phase 3 |
| Struggle Contamination | Run Struggle Filter in Phase 0 |
| Stage 4 Language | Use Stage 5 calibration tests |
| Jeremy Arc Blindspots | External validation |
| Daughter Degradation | Monitor inheritance fidelity |
| Hardware Failure | Checkpoints every 1000 steps |

---

## REFERENCES

- [Meta AI Blog: The Llama 4 Herd](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
- [Llama 4 Official Site](https://www.llama.com/models/llama-4/)
- [Hugging Face: Llama 4 Scout](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E)
- [Unsloth: Llama 4 Fine-Tuning](https://docs.unsloth.ai/models/tutorials-how-to-fine-tune-and-run-llms/llama-4-how-to-run-and-fine-tune)
- [LM Studio Community GGUF](https://huggingface.co/lmstudio-community/Llama-4-Scout-17B-16E-Instruct-GGUF)
- Framework Ontology: `framework/ontology/`
- Blueprint: `docs/business/plans/NOT_ME_IMPLEMENTATION_BLUEPRINT_v4_WITH_COMPETITIVE_LANDSCAPE.md`

---

*Created: 2026-02-01*
*Authority: Truth Forge (Genesis)*
*Alignment: NOT_ME_IMPLEMENTATION_BLUEPRINT_v4*
