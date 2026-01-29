# Genesis Training Data Enrichment Strategy

**Created**: 2026-01-28  
**Status**: Planning Complete  
**Priority**: CRITICAL - Blocker for Genesis training

---

## 🎯 Objective

Transform data from `entities_unified` (populated by cursor agent's pipeline) into Genesis training corpus with metadata enrichment for the "seeing paradigm."

---

## 📊 Current State Analysis

### What We Have
- ✅ **entities_unified** table in BigQuery (`flash-clover-464719-g1.spine.entity_unified`)
- ✅ L4 (sentence) and L5 (message) entities with text content
- ✅ Basic metadata: role, message_type, message_index, tokens
- ✅ Data sources being populated: claude_code, gemini_web, (more coming from cursor agent)

### What's Missing (ALL 4 Genesis Fields)
- ❌ **emotion**: Primary emotion (28 GoEmotions categories)
- ❌ **thought_type**: Cognitive process type
- ❌ **cognitive_stage**: Problem-solving stage
- ❌ **pattern**: Framework pattern demonstrated

**Gap**: **100%** of Genesis-required metadata is missing

---

## 🚀 Enrichment Pipeline Architecture

### Phase 1: Extract (DONE ✅)
**Script**: `/Users/jeremyserna/truth_forge/training/data_prep/extract_from_entities_unified.py`

**Input**: BigQuery `entities_unified`  
**Output**: `data/genesis_corpus/raw_conversations.jsonl`

**What it does**:
- Queries L5 messages from entities_unified
- Groups by conversation_id
- Filters: min 5 messages/conv, max 1000 messages/conv
- Exports to JSONL format

**Status**: ✅ Complete, ready to run

---

### Phase 2: Metadata Enrichment (DONE ✅)
**Script**: `/Users/jeremyserna/truth_forge/training/data_prep/enrich_metadata.py`

**Input**: `raw_conversations.jsonl`  
**Output**: `enriched_conversations.jsonl`

**What it does**:
- Uses Gemini 2.0 Flash to classify each message
- Adds 4 metadata fields: emotion, thought_type, cognitive_stage, pattern
- Preserves original text
- Tracks confidence scores
- Cost tracking

**Models Used**:
- **Gemini 2.0 Flash Exp** for metadata classification
- **Prompt**: Analyzes message + 2 previous messages for context

**Estimated Cost**:
- ~$0.001 per message (input: $0.075/M tokens, output: $0.30/M tokens)
- For 10,000 messages: ~$10
- For 100,000 messages: ~$100

**Status**: ✅ Complete, ready to run

---

### Phase 3: Format for MLX Training (TODO)
**Script**: `/Users/jeremyserna/truth_forge/training/data_prep/format_for_mlx.py` (needs creation)

**Input**: `enriched_conversations.jsonl`  
**Output**: `genesis_training_corpus.jsonl` (MLX format)

**What it needs to do**:
1. Convert to MLX training format
2. Create metadata classification labels
3. Split train/validation/test sets (80/10/10)
4. Generate statistics
5. Validate metadata coverage

**MLX Training Format**:
```jsonl
{
  "text": "How do I set up THE GATE for my pipeline?",
  "metadata": {
    "emotion": "curiosity",
    "thought_type": "question",
    "cognitive_stage": "exploration",
    "pattern": "the_gate"
  }
}
```

**Status**: ❌ Need to implement

---

### Phase 4: Quality Validation (TODO)
**Script**: `/Users/jeremyserna/truth_forge/training/data_prep/validate_corpus.py` (needs creation)

**Checks**:
- [ ] All messages have 4 metadata fields
- [ ] Emotion values in valid GoEmotions set
- [ ] Thought_type values in valid set
- [ ] Cognitive_stage values in valid set
- [ ] Pattern values in valid set
- [ ] Metadata confidence > threshold
- [ ] Train/val/test split is balanced
- [ ] Framework pattern coverage is adequate

**Status**: ❌ Need to implement

---

## 🔄 End-to-End Workflow

```bash
# 1. Extract from entities_unified (once cursor agent populates it)
python training/data_prep/extract_from_entities_unified.py \
  --sources claude_code,gemini_web \
  --output data/genesis_corpus/raw_conversations.jsonl \
  --min-messages 5 \
  --max-messages 1000

# 2. Enrich with metadata (costs money - be careful!)
python training/data_prep/enrich_metadata.py \
  --input data/genesis_corpus/raw_conversations.jsonl \
  --output data/genesis_corpus/enriched_conversations.jsonl \
  --model gemini-2.0-flash-exp

# 3. Format for MLX training (TODO)
python training/data_prep/format_for_mlx.py \
  --input data/genesis_corpus/enriched_conversations.jsonl \
  --output data/genesis_corpus/genesis_training_corpus.jsonl

# 4. Validate (TODO)
python training/data_prep/validate_corpus.py \
  --input data/genesis_corpus/genesis_training_corpus.jsonl
```

---

## 📋 Pattern Taxonomy

### Framework Patterns to Detect

Based on `/Users/jeremyserna/truth_forge/framework/` documentation:

1. **the_gate** - Identity generation, THE GATE pattern
2. **the_furnace** - Transformation, refinement
3. **the_form** - Structure, output formation
4. **hold_pattern** - HOLD₁ → AGENT → HOLD₂ pattern
5. **primitive_pattern** - Core primitive operations
6. **service_pattern** - Service architecture
7. **trinity_pattern** - Three-fold patterns
8. **clara_arc** - Personal development arc (from ChatGPT data)
9. **jeremy_arc** - Development patterns (from your data)
10. **none** - No specific pattern

---

## ⏱️ Timeline & Dependencies

### Immediate (Now → 2 days, before new MBP arrives)
1. ✅ Analysis script (DONE)
2. ✅ Extract script (DONE)
3. ✅ Enrich script (DONE)
4. ❌ **TODO**: Create `format_for_mlx.py`
5. ❌ **TODO**: Create `validate_corpus.py`
6. ⏸️ **BLOCKED**: Wait for cursor agent to populate entities_unified

### When Data Available (cursor agent completes)
1. Run extract script (10 min)
2. Sample enrichment test (100 messages, ~$0.10)
3. Review quality of metadata
4. Full enrichment run (estimate based on message count)

### When New Hardware Arrives
1. Transfer corpus to new MBP/THE EMPIRE
2. Start Genesis training

---

## 💰 Cost Estimates

### Gemini Enrichment Costs
| Messages | Cost (Est.) | Time (Est.) |
|----------|-------------|-------------|
| 100 | $0.10 | 5 min |
| 1,000 | $1.00 | 30 min |
| 10,000 | $10.00 | 5 hours |
| 100,000 | $100.00 | 50 hours |

### Optimization Options
1. **Batch processing**: Group similar messages
2. **Caching**: Reuse classifications for similar content
3. **Sampling**: Enrich subset, use few-shot for rest
4. **Cheaper model**: Use Gemini Flash instead of Pro

---

## 🎓 Metadata Classification Schemas

### Emotions (28 from GoEmotions)
admiration, amusement, anger, annoyance, approval, caring, confusion, curiosity, desire, disappointment, disapproval, disgust, embarrassment, excitement, fear, gratitude, grief, joy, love, nervousness, optimism, pride, realization, relief, remorse, sadness, surprise, neutral

### Thought Types (12)
question, statement, reflection, hypothesis, instruction, observation, conclusion, clarification, synthesis, analysis, proposal, validation

### Cognitive Stages (9)
exploration, problem_identification, analysis, hypothesis_formation, synthesis, validation, implementation, reflection, integration

### Patterns (10)
the_gate, the_furnace, the_form, hold_pattern, primitive_pattern, service_pattern, trinity_pattern, clara_arc, jeremy_arc, none

---

## 🚨 Next Steps

1. **Create missing scripts**:
   - `format_for_mlx.py`
   - `validate_corpus.py`

2. **Small-scale test** (when data ready):
   - Extract 100 conversations
   - Enrich with metadata
   - Validate quality
   - Cost: ~$0.50

3. **Iterate on prompts**:
   - Tune Gemini classification prompt
   - Add few-shot examples
   - Improve pattern detection

4. **Full production run**:
   - Extract all conversations
   - Full enrichment
   - Validate
   - Ready for training

---

## 📝 Notes

- The **seeing paradigm** is fundamentally different from token prediction
- Genesis learns to predict metadata, not text
- Quality of metadata enrichment = Quality of Genesis training
- This is the **moat** - nobody else is training this way

---

**Next Action**: Create `format_for_mlx.py` and `validate_corpus.py` scripts
