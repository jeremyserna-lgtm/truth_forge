# Knowledge Atom Generation - Capacity Analysis

**Date**: 2026-02-06
**Hardware**: 4-node EXO cluster (Studio King + 3 Soldiers)
**Total Memory**: 1.28TB unified memory
**Question**: Is this enough for full-strength models?

---

## The Three Models (True Identity)

| Model | Parameters | Quant | Size | Memory Allocated | Deployment |
|-------|-----------|-------|------|------------------|------------|
| **LLaMA 4 Scout** | 109GB (17B, 16E) | 8-bit | 109GB | 169GB | Single-node (King) |
| **LLaMA 4 Maverick** | 400B (17B, 128E) | varies | varies | 210GB (8-bit) | EXO distributed |
| **DeepSeek R1** | 671B | varies | varies | 36GB (4-bit) or 1.3TB (8-bit) | EXO full fleet |

---

## Current Configuration (1.28TB Total)

### What FITS:

**Configuration A: Mixed Precision (CURRENT)**
- Scout: 8-bit (169GB) ✅
- Maverick: 8-bit (210GB) ✅
- R1: **4-bit** (36GB) ⚠️
- **Total: ~415GB allocated**
- **Free: ~865GB (68% headroom)**

**Result**: All three models operational with good headroom.
**Limitation**: R1 is quantized (4-bit), not full 8-bit.

---

**Configuration B: R1 Full Strength (ASPIRATIONAL)**
- Scout: 8-bit (169GB) ✅
- Maverick: **4-bit** (155GB) ⚠️
- R1: **8-bit** (1.3TB) ❌
- **Total: ~1.624TB required**

**Result**: DOES NOT FIT. R1 at 8-bit alone is 1.3TB.
**Shortfall**: ~344GB

---

### What DOES NOT FIT:

**Configuration C: All Full Strength**
- Scout: 8-bit (169GB)
- Maverick: 8-bit (210GB)
- R1: 8-bit (1.3TB)
- **Total: ~1.679TB required**

**Result**: DOES NOT FIT.
**Shortfall**: ~399GB (~400GB short)

---

## Hardware Upgrade Options

### Option 1: Add MacBook Pro (128GB)

**New Total**: 1.28TB + 128GB = **1.408TB**

**Can we fit all three at 8-bit?**
- Required: 1.679TB
- Available: 1.408TB
- **Still short: ~271GB** ❌

**Conclusion**: Adding MacBook helps but still not enough for all three at 8-bit.

---

### Option 2: Get Stronger Mac Studio (2TB)

**New Total**: 2TB (single Studio King) or 1.28TB + 2TB (King upgrade + Soldiers)

**Can we fit all three at 8-bit?**
- Required: 1.679TB
- Available: 2TB
- **Fits: ~321GB headroom** ✅

**Conclusion**: 2TB Studio King would fit all three at full 8-bit with room to spare.

---

### Option 3: Hybrid Strategy (RECOMMENDED)

Keep current hardware (1.28TB) but use **smart quantization**:

| Model | Quant | Memory | Rationale |
|-------|-------|--------|-----------|
| **Scout** | 8-bit | 169GB | Needs 10M context - keep full |
| **Maverick** | **6-bit** | ~180GB | Dialectical reasoning benefits from precision |
| **R1** | **4-bit** | 36GB | Chain-of-thought works well at 4-bit |
| **Total** | mixed | **~385GB** | 65% free headroom |

**Why this works**:
- Scout's 10M context is its superpower - don't compromise
- Maverick's 128 experts need good precision for deep reasoning
- R1's long chain-of-thought compensates for quantization loss
- Leaves ~895GB free for tensor operations and memory pool

---

## Memory Pool Configuration

For knowledge atom generation, the **shared memory pool** (MemoryCortex) needs space for:

1. **Semantic graph**: ~50GB (for large-scale conversations)
2. **Temporal graph**: ~20GB (time-series relationships)
3. **Causal graph**: ~30GB (cause-effect chains)
4. **Entity graph**: ~40GB (knowledge entities)
5. **Emotional graph**: ~20GB (sentiment/affect)
6. **Tensor activations**: ~200GB (during parallel inference)
7. **Context buffers**: ~100GB (10M context for Scout)

**Total memory pool needs**: ~460GB

---

## The Answer

### With Current Hardware (1.28TB):

**YES, you have enough** for effective knowledge atom generation:

```
Configuration: Smart Hybrid
├── Scout: 8-bit (169GB) - full 10M context
├── Maverick: 6-bit (180GB) - strong reasoning
├── R1: 4-bit (36GB) - architect protocols
├── Memory pool: 460GB - full 5-graph cortex
├── Tensor ops: 200GB - parallel inference
└── Free: ~235GB headroom
────────────────────────────────
Total: ~1.28TB
```

**Trade-off**: R1 at 4-bit instead of 8-bit.
**Impact**: Minimal - R1's chain-of-thought design compensates for quantization.

---

### If You Add MacBook (1.408TB):

**Marginal improvement**:
- Could run Maverick at 8-bit instead of 6-bit
- Still can't fit R1 at 8-bit
- Not worth the complexity of adding a 5th node

**Recommendation**: Don't add MacBook. Not enough gain.

---

### If You Upgrade to 2TB Studio:

**Significant improvement**:
- All three models at full 8-bit ✅
- R1 at 1.3TB (full 671B) ✅
- ~321GB free headroom
- Future-proof for larger models

**Cost**: ~$7,000 for 2TB Mac Studio
**Benefit**: Full-strength knowledge atom generation at maximum fidelity

**Recommendation**: If budget allows, this is the gold standard.

---

## Recommendation: Start with Current Hardware

**Phase 1 (NOW)**: Use current 1.28TB cluster
- Scout: 8-bit (full strength)
- Maverick: 6-bit or 8-bit (depending on availability)
- R1: 4-bit (quantized)
- Generate knowledge atoms and evaluate quality

**Phase 2 (LATER)**: Based on results
- If R1 at 4-bit produces acceptable atoms → keep current hardware
- If R1 needs full 8-bit → upgrade Studio King to 2TB
- Don't add MacBook - not enough benefit

---

## The Critical Insight

**Knowledge atom quality depends more on architecture than precision**:
- Scout's 10M context > quantization level
- Maverick's 128 experts > precision bits
- R1's chain-of-thought > quantization loss
- Shared memory pool (tensor-level communication) > language translation

**Start with what you have. Measure quality. Upgrade if needed.**

The EXO infrastructure is already built for distributed inference.
The models are already running.
**Generate atoms. See if they're good. Then decide on hardware.**

---

## Next Steps

1. ✅ Configure knowledge_atom_factory with true model specs
2. ✅ Enable EXO distributed inference for Maverick and R1
3. ⏭️ Generate 100 test knowledge atoms
4. ⏭️ Evaluate atom quality (convergence, divergence, emotional depth)
5. ⏭️ If quality insufficient → upgrade to 2TB Studio
6. ⏭️ If quality sufficient → keep current hardware

**Don't optimize prematurely. Generate data first.**
