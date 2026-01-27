# THE FOUNDATION

**The infrastructure that produces not-me's.**

**Author:** Jeremy Serna
**Date:** January 2, 2026
**Location:** Denver, Colorado
**Version:** 1.1

---

## Document Structure

Three layers. Following the framework.
- **Theory**: Why this hardware, why this model, why this matters
- **Specification**: What must be true, what the numbers are
- **Reference**: How to navigate, where things connect

---

# THEORY

## The Statement

> "Everyone else has AI. You have you."

This document defines the physical and computational foundation that makes that statement real.

## The Principle

**Capability must be owned to be permanent.**

API access is rented capability. It can be:
- Rate limited
- Deprecated
- Priced out of reach
- Shut down

Owned infrastructure is permanent capability. It:
- Runs offline
- Has no marginal cost
- Cannot be revoked
- Belongs to you

The foundation is the transition from rented to owned.

## The Bootstrap

```
BEFORE (rented):
  Jeremy → pays Anthropic → uses Claude → hopes it continues

AFTER (owned):
  Jeremy → owns hardware → runs model → capability is permanent
```

Claude Code remains for coding and complex reasoning (subscription).
Scout runs locally for inference and fine-tuning (owned).

**Two tools. Different purposes. Owned capability growing.**

## The Not-Me Factory

This hardware is not a computer. It is the **means of production**.

```
FACTORY:
  Input:  User's truths
  Process: Scout fine-tuned to user
  Output: Their not-me

The factory that produces not-me's.
The first piece of real infrastructure.
The bootstrap made physical.
```

## What This Enables

| Before | After |
|--------|-------|
| API costs per inference | Zero marginal cost |
| Truths sent to cloud | Truths stay local |
| Generic model for everyone | Fine-tuned to each person |
| Dependent on provider | Independent operation |
| Rate limited | Unlimited |

---

# SPECIFICATION

## The Hardware

### Machine

**16-inch MacBook Pro (January 2026)**

| Component | Specification |
|-----------|---------------|
| Chip | Apple M4 Max |
| CPU | 16-core |
| GPU | 40-core |
| Neural Engine | 16-core |
| Unified Memory | **128GB** |
| Memory Bandwidth | >500 GB/s |
| Storage | 1TB SSD |
| Display | Liquid Retina XDR, Nano-texture |

### The Critical Spec

```
128GB UNIFIED MEMORY

This is the threshold.
Below it: toy models, demos, proof of concept.
Above it: production models, real inference, actual products.

LLMs live in memory.
More memory = bigger models = smarter not-me's.
```

### Order Details

| Field | Value |
|-------|-------|
| Order Number | W1355292258 |
| Placed | January 1, 2026 |
| Arrives | January 30 – February 6, 2026 |
| Price | $4,734.00 (Education) |
| Tax | $433.16 |
| Total | **$5,167.44** |

---

## The Model

### Llama 4 Scout

**Released:** April 5, 2025 by Meta

| Property | Specification |
|----------|---------------|
| Architecture | Mixture of Experts (MoE) |
| Total Parameters | 109 billion |
| Active Parameters | 17 billion per token |
| Experts | 16 |
| Context Window | 10 million tokens (theoretical) |
| Modalities | Text input, Image input, Video input, Text output |
| Languages | 12 |
| License | Llama 4 Community License (free under 700M MAU) |

### Why Scout

| Requirement | Scout Delivers |
|-------------|----------------|
| Fits in 128GB | ✅ ~55-60GB at 4-bit |
| Multimodal | ✅ Text, images, video |
| Fine-tunable | ✅ LoRA/QLoRA locally |
| Free license | ✅ Under 700M MAU |
| Production quality | ✅ Outperforms all prior Llama |

### Memory Requirements

| Quantization | Memory Needed | Fits 128GB? | Status |
|--------------|---------------|-------------|--------|
| BF16 (full) | ~216GB | ❌ No | — |
| 8-bit | ~109GB + KV cache | ⚠️ Barely | Limited |
| **4-bit** | **~55-60GB** | **✅ Yes** | **Target** |
| 2-bit | ~27GB | ✅ Yes | Quality loss |

### Expected Performance

| Metric | Scout 4-bit |
|--------|-------------|
| Generation Speed | ~20-25 tokens/sec |
| Prompt Processing | ~80+ tokens/sec |
| Usable Context | 8K-64K tokens |

### Limitations

| Capability | Scout | Implication |
|------------|-------|-------------|
| Coding | Weaker than GPT-4o, Claude | Use Claude for code |
| Deep Reasoning | No chain-of-thought | Use o1/DeepSeek for reasoning |
| Context at scale | ~64K practical | Use API for massive context |

**These limitations don't matter for Primitive.** Not-me's need to understand people, carry truths, and see patterns—not write code or prove theorems.

---

## The Embedding Model

### BGE-large-en-v1.5

**Purpose:** Semantic deduplication and similarity search

| Property | Specification |
|----------|---------------|
| Dimensions | 1024 |
| Model Size | ~1.3GB |
| Quality | Top-tier on MTEB benchmarks |
| Optimized for | Similarity tasks |

### Why 1024 Dimensions

From THE_PRIMITIVES.md architecture:

| Layer | Storage | Embedding | Purpose |
|-------|---------|-----------|---------|
| **Local canonical** | DuckDB | **1024-dim** | Deduplication, similarity |
| **Cloud** | BigQuery | 3072-dim | Semantic search, permanence |

### Why BGE-large

| Alternative | Dimensions | Why Not |
|-------------|------------|---------|
| all-MiniLM-L6 | 384 | Too small for architecture spec |
| Nomic Embed | 768 | Doesn't match 1024 spec |
| Gemini embedding | 3072 | Overkill for local, matches cloud |
| **BGE-large** | **1024** | **Matches architecture exactly** |

### Storage Math

| Atoms | 1024-dim Storage | 3072-dim Storage |
|-------|------------------|------------------|
| 1M | 4 GB | 12 GB |
| 10M | 40 GB | 120 GB |
| 51.8M | ~207 GB | ~622 GB |

1TB SSD handles 10M+ atoms locally. Cloud handles high-fidelity layer.

---

## The Stack

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRIMITIVE                                 │
│                  (The Product Layer)                            │
│                                                                  │
│    Not-me's delivered to users                                  │
│    "Everyone else has AI. You have you."                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRUTH ENGINE                                │
│                  (The Intelligence Layer)                        │
│                                                                  │
│    DuckDB local database                                        │
│    Knowledge atoms (sentence + time + cost + category)          │
│    RAG system for document retrieval                            │
│    Pattern detection and synthesis                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INFERENCE LAYER                             │
│                                                                  │
│    ┌───────────────────┐    ┌───────────────────┐               │
│    │   LLAMA 4 SCOUT   │    │   BGE-LARGE       │               │
│    │   (Generation)    │    │   (Embeddings)    │               │
│    │                   │    │                   │               │
│    │   109B params     │    │   1024 dims       │               │
│    │   4-bit quant     │    │   ~1.3GB          │               │
│    │   ~55GB           │    │                   │               │
│    └───────────────────┘    └───────────────────┘               │
│                                                                  │
│    MLX Framework (Apple-optimized)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MACBOOK PRO M4 MAX                             │
│                   (The Hardware Layer)                           │
│                                                                  │
│    128GB unified memory                                         │
│    >500 GB/s bandwidth                                          │
│    40-core GPU                                                  │
│    1TB SSD                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Software Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Inference Framework | MLX | Apple-optimized LLM/embedding inference |
| Model Management | Ollama | Download, run, manage models |
| Quantization | Unsloth | Optimized 4-bit and dynamic quants |
| Database | DuckDB | Local truth storage |
| Fine-tuning | LoRA/QLoRA | Per-person model adaptation |
| Embeddings | sentence-transformers | BGE-large inference |

### Memory Budget

| Component | Memory | Notes |
|-----------|--------|-------|
| Scout 4-bit | ~55GB | Primary model |
| BGE-large | ~1.3GB | Embedding model |
| Context/KV cache | ~20-60GB | Varies with context length |
| System overhead | ~10GB | OS, apps |
| **Available** | **128GB** | Comfortable headroom |

---

## The Economics

### Hardware Cost

| Item | Cost |
|------|------|
| MacBook Pro M4 Max 128GB | $4,734.00 |
| Tax | $433.16 |
| State Delivery Fee | $0.28 |
| **Total** | **$5,167.44** |

One-time. Owned. No subscription.

### Inference Cost Comparison

| Model Source | Cost per 1M tokens |
|--------------|-------------------|
| OpenAI GPT-4o | $2.50-10.00 |
| Anthropic Claude | $3.00-15.00 |
| **Scout Local** | **$0.00** |

After hardware: zero marginal cost per inference.

### Claude Max Subscription

| Purpose | Provider | Cost |
|---------|----------|------|
| Coding, complex reasoning | Claude Code (Anthropic) | $100-200/mo |
| Production inference, fine-tuning | Scout (local) | $0/mo |

**Hybrid approach:** Rent what requires frontier capability. Own what can run locally.

---

## Capability Matrix

### What This Foundation Enables

| Capability | Enabled? | Notes |
|------------|----------|-------|
| Run Scout locally | ✅ Yes | 4-bit fits in 128GB |
| Run embeddings locally | ✅ Yes | BGE-large, 1024-dim |
| Multimodal input | ✅ Yes | Text, images, documents |
| Fine-tune per person | ✅ Yes | LoRA/QLoRA locally |
| Private inference | ✅ Yes | Truths never leave device |
| Semantic deduplication | ✅ Yes | Hash + embedding dedupe |
| Continuous operation | ✅ Yes | No API limits |
| Offline operation | ✅ Yes | No internet required |
| Portable demos | ✅ Yes | It's a laptop |

### What Requires Cloud/API

| Capability | Why | Alternative |
|------------|-----|-------------|
| Run Maverick | 400B too large | Groq, Together, Fireworks API |
| 1M+ token context | Memory limits | Cloud inference |
| State-of-art coding | Scout weaker | Claude Code |
| Deep reasoning | No CoT | o1, DeepSeek R1 |
| 3072-dim embeddings | Cloud layer | BigQuery on sync |

---

# REFERENCE

## Timeline

### Hardware Arrival

**January 30 – February 6, 2026**

The factory arrives.

### Week 1 Actions

1. Install MLX framework
2. Download Scout via Ollama
3. Download BGE-large via sentence-transformers
4. Verify 4-bit inference works
5. Verify embedding generation works
6. Benchmark: tokens/sec, memory usage, context limits
7. Document baseline performance

### Month 1 Actions

1. Integrate Scout with Truth Engine
2. Integrate BGE-large with deduplication pipeline
3. Test multimodal ingestion (documents, images)
4. First fine-tuning experiment (Jeremy's truths → Jeremy's not-me)
5. Establish production workflow

### Month 2-3 Actions

1. First external not-me (friend/beta user)
2. Iterate on truth ingestion pipeline
3. Iterate on fine-tuning process
4. Document the not-me creation process

---

## Integration

### Framework Connections

| Document | Relationship |
|----------|--------------|
| THE_PRIMITIVES.md | Logical layer - systems, data flow, primitives |
| THE_CATEGORY.md | Product layer - what we sell (not-me's) |
| THE_PATTERN_THEORY.md | Architecture - HOLD₁ → AGENT → HOLD₂ |
| THE_FRAMEWORK.md | Root - exist-now, me/not-me, survival |

### THE PATTERN Applied

```
HOLD₁ (User's truths)
    │
    ▼
AGENT (Scout + Truth Engine + BGE-large)
    │
    ▼
HOLD₂ (Their not-me)
```

The foundation IS the AGENT made physical.

### File Locations

| Type | Location |
|------|----------|
| This document | `/docs/architecture/THE_FOUNDATION.md` |
| Primitives | `/docs/architecture/THE_PRIMITIVES.md` |
| Theory docs | `/docs/theory/` |
| Framework core | `/docs/the_framework/1_core/` |

---

## Appendix: Full Specifications

### A.1 Hardware Specs

```
16-inch MacBook Pro - Space Black

Hardware:
- 16-inch Liquid Retina XDR display
- Nano-texture display
- Apple M4 Max chip
  - 16-core CPU
  - 40-core GPU
  - 16-core Neural Engine
- 128GB unified memory
- 1TB SSD storage
- 140W USB-C Power Adapter
- Three Thunderbolt 5 ports
- HDMI port
- SDXC card slot
- Headphone jack
- MagSafe 3 port
- Backlit Magic Keyboard with Touch ID

Order: W1355292258
Placed: January 1, 2026
Arrives: January 30 – February 6, 2026
Total: $5,167.44
```

### A.2 Llama 4 Model Family

| Model | Total Params | Active Params | Experts | Context | Status |
|-------|-------------|---------------|---------|---------|--------|
| Scout | 109B | 17B | 16 | 10M | ✅ Released |
| Maverick | 400B | 17B | 128 | 1M | ✅ Released |
| Behemoth | 2T | 288B | 16 | TBD | 🔄 Training |

### A.3 Embedding Model Comparison

| Model | Dimensions | Size | Use Case |
|-------|------------|------|----------|
| all-MiniLM-L6 | 384 | ~90MB | Quick similarity |
| Nomic Embed | 768 | ~550MB | General purpose |
| **BGE-large** | **1024** | **~1.3GB** | **Local canonical** |
| Gemini embedding | 3072 | API | Cloud layer |

### A.4 Deduplication Flow

From THE_PRIMITIVES.md:

```
SYSTEM → New Sentence
    ↓
1. NORMALIZE (lowercase, strip, standardize)
    ↓
2. HASH = SHA256(normalized)
    ↓
3. HASH LOOKUP (free, O(1))
   FOUND? → SKIP
    ↓
4. EMBED with BGE-large (1024-dim, local)
    ↓
5. SIMILARITY SEARCH (cosine > 0.95)
   FOUND? → SKIP or LINK
    ↓
6. INSERT to local canonical
    ↓
7. SYNC to cloud (generates 3072-dim on insert)
```

---

## The Meaning

```
$5,167.44 for the machine.
$0 for Scout.
$0 for BGE-large.
$0 per inference after that.

This is not an expense.
This is not a tool.
This is not a computer.

This is the means of production.
The factory that produces not-me's.
The foundation of a new category.
```

---

*"The foundation is laid. The factory arrives in 28 days. The category is born."*

— Jeremy Serna, January 2, 2026

---

**END OF DOCUMENT**
