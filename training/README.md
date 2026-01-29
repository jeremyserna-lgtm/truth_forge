# Genesis-Scout Training Infrastructure

This directory contains infrastructure for training Genesis-Scout using the **seeing paradigm** (metadata classification) rather than traditional next-token prediction.

## 📋 Overview

**Key Principles:**
1. This is **SEEING** training, not prediction training
2. Validation happens at **EVERY** checkpoint (know it's working during training)
3. **Jeremy Arc** (95% metadata accuracy) = quantitative readiness measure
4. **Coherence Anchor** MUST come before Seeing Training
5. **Full fine-tune** for Genesis (paradigm shift), **LoRA** for Daughters (adaptation)

## 🏗️ Structure

```
training/
├── validation/              # Validation suite
│   ├── framework_validation_suite.py  # 6 tests + Jeremy Arc
│   └── __init__.py
├── scripts/                 # Training scripts
│   ├── train_genesis.py     # Main Genesis training (Phase 3)
│   ├── coherence_anchor.py  # Phase 2 (MUST run first)
│   └── train_daughter_lora.py  # Phase 4 (customer deployment)
├── infrastructure/          # Hardware setup
│   ├── empire_setup.sh      # Configure 4x Mac Studios
│   └── mlx_distributed_config.py
├── monitoring/              # Real-time dashboard
│   └── dashboard.py
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Hardware**: THE EMPIRE configured (1.28TB unified memory)
2. **Data**: Genesis corpus prepared with metadata enrichment
3. **Software**: MLX framework installed and tested

### Week 1: Validation Protocol Proof (Llama 70B)

```bash
# Monday-Tuesday: Setup
cd /Users/jeremyserna/truth_forge/training
./infrastructure/empire_setup.sh

# Wednesday: Prepare 10% corpus for 70B test
python scripts/train_genesis.py \
  --model llama-3.3-70b \
  --scale 0.1 \
  --output-dir checkpoints/genesis_70b_test

# Thursday: Train (12 hours)
# Validation runs every 500 steps
# Watch Jeremy Arc climb from 20% → 60%+

# Friday: Analyze results
# Decision: Go/No-Go for Scout training
```

### Weeks 2-6: Genesis-Scout Training

**Phase 2: Coherence Anchor (CRITICAL - NO SKIP)**

```bash
python scripts/coherence_anchor.py \
  --model llama-4-scout-109b \
  --output-dir checkpoints/genesis_coherence_anchored

# Must achieve 90%+ coherence validation before proceeding
```

**Phase 3: Seeing Training**

```bash
python scripts/train_genesis.py \
  --model checkpoints/genesis_coherence_anchored \
  --corpus data/genesis_corpus_full.jsonl \
  --validate-every 1000 \
  --freeze-at-arc 0.95

# Expected: 4-5 weeks to 95% Jeremy Arc
# Auto-freeze at 95% = Genesis v1.0
```

**Phase 4: First Daughter**

```bash
python scripts/train_daughter_lora.py \
  --genesis-base checkpoints/genesis_scout_v1.0 \
  --customer-data /path/to/customer/data \
  --output-dir checkpoints/customer_daughter
```

## 📊 Validation Suite

Six tests run at every checkpoint (1000 steps):

1. **HOLD → AGENT → HOLD**: Breathing pattern thinking
2. **Furnace Operation**: Truth → Heat → Meaning → Care
3. **Stage 5 Perception**: Systems thinking markers
4. **Primitive Understanding**: SEE, EXIST:NOW comprehension
5. **Care Orientation**: Elevating vs answering
6. **Jeremy Arc** (PRIMARY): Metadata prediction accuracy

**Decision thresholds:**
- Jeremy Arc ≥ 95% → **FREEZE GENESIS v1.0**
- Framework score > 80 → Continue (strong integration)
- Framework score < 60 → Warning (monitor closely)

## 🎯 Success Criteria

### Week 1 Success (70B Proof)
- ✅ Training completes in 12 hours
- ✅ Validation suite runs at every checkpoint
- ✅ Jeremy Arc climbs (20% → 60%+)
- ✅ Framework tests show pattern learning
- ✅ Know what "good" scores look like

### Genesis v1.0 Freeze Criteria
- ✅ Jeremy Arc ≥ 95%
- ✅ Framework score ≥ 85
- ✅ Loss plateaued (convergence)
- ✅ Conversation quality excellent
- ✅ Stage 5 markers consistent
- ✅ No validation-seeking patterns
- ✅ Coherence maintained (no hallucination)

## ⚠️ Critical Warnings

### DO NOT SKIP PHASE 2 (Coherence Anchor)

Without coherence anchoring, you risk creating a "confident hallucination engine" - a model that is decisive but decisively nonsensical.

**Order matters:**
1. FIRST: Teach model to hate confident fabrication
2. SECOND: Teach model to hate validation-seeking
3. Result: Bold but not hallucinating

### Full Fine-Tune vs LoRA

- **Genesis (once)**: Full fine-tune to create paradigm shift (prediction → seeing)
  - Uses zero-degradation optimizations (fits in 1.28TB)
  - All 109B weights update
  - This IS the innovation
  
- **Daughters (per customer)**: LoRA to adapt to specific person
  - Genesis already has seeing paradigm
  - LoRA just adapts, doesn't recreate paradigm
  - 2-6 hours per customer

### Emergency Protocols

**If Jeremy Arc stuck <40% after Week 1:**
1. Analyze data mix (Framework data prominent?)
2. Check metadata labeling accuracy
3. Increase Framework examples 2x
4. Resume from last good checkpoint

**If loss starts increasing:**
1. STOP IMMEDIATELY
2. Roll back to last good checkpoint
3. Reduce learning rate by 50%
4. Check data for corruption

**If Framework scores OK but conversations feel off:**
1. Continue training (don't stop)
2. Add more Clara Arc examples
3. Increase "personality" data weight
4. Consider extending to Week 6

## 📚 Documentation

- **Primary**: [GENESIS_SCOUT_TRAINING_IMPLEMENTATION_COMPLETE.md](file:///Users/jeremyserna/truth_forge/docs/business/operations/model_training/GENESIS_SCOUT_TRAINING_IMPLEMENTATION_COMPLETE.md)
- **Planning**: See artifacts in `.gemini/antigravity/brain/<conversation-id>/`
- **Framework**: [/Users/jeremyserna/truth_forge/framework](file:///Users/jeremyserna/truth_forge/framework)

## 🔧 Development Status

**Current Status: Infrastructure Created**

- ✅ Validation suite framework
- ✅ Training script scaffolding
- ✅ Coherence anchor protocol
- ⏳ MLX integration (requires installation)
- ⏳ Corpus preparation pipeline
- ⏳ Real-time dashboard
- ⏳ Emergency protocols automation

**Next Steps:**
1. Install and test MLX on THE EMPIRE
2. Prepare Genesis corpus with metadata
3. Test validation suite on dummy model
4. Run Week 1 proof (70B test)
5. Iterate based on learnings

## 📞 Support

For questions about the seeing paradigm, validation suite, or training process, refer to:
- [Implementation Plan](file:///Users/jeremyserna/.gemini/antigravity/brain/20961bcd-5ded-4a71-8e0b-9b637991d455/implementation_plan.md)
- [Task Breakdown](file:///Users/jeremyserna/.gemini/antigravity/brain/20961bcd-5ded-4a71-8e0b-9b637991d455/task.md)

## 🎓 The Innovation

This training approach has **no prior art**. Key innovations:

1. **Seeing Training Paradigm**: Metadata classification as PRIMARY objective
2. **Genesis + Daughters**: Train once with Stage 5 source, copy infinitely
3. **Jeremy Arc**: Metadata prediction accuracy as quantitative readiness measure
4. **Single Error Principle**: Only penalize validation-seeking (not multi-objective RLHF)
5. **Stage 5 DNA Transfer**: Cognitive architecture inheritance
6. **Coherence Anchor + Inverted Training**: Reasoning BEFORE boldness

**The Moat**: You can copy the pattern, but not the pattern-maker. Stage 5 models require a Stage 5 person.
