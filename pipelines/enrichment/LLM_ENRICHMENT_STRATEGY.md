# LLM-Based Sovereign Enrichment Strategy

## Why Train Specialized LLMs for Pattern Detection?

The keyword/regex approaches have fundamental limitations:

| Limitation | Example Failure | LLM Solution |
|------------|-----------------|--------------|
| **Exact match only** | "I'm happy to assist" vs "happy to help" | Semantic understanding |
| **No sarcasm detection** | "Oh wonderful, another error" → positive | Context-aware inference |
| **No novel phrasings** | New validation-seeking patterns | Generalization from examples |
| **Mixed signals** | Stage 4 + Stage 5 markers | Holistic interpretation |
| **Cultural variations** | Different politeness norms | Trained on diverse data |

## The Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN ENRICHMENT PIPELINE                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: Fast Keyword-Based (Default)                          │
│  - 0.01ms per text                                              │
│  - High confidence on clear patterns                            │
│  - Returns confidence score                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                    confidence < 0.6?
                              │
                     ┌────────┴────────┐
                     │ YES             │ NO
                     ▼                 ▼
┌──────────────────────────┐  ┌─────────────────────────┐
│  LAYER 2: LLM Fallback   │  │  Return keyword result  │
│  - Few-shot prompting    │  │  (fast path)            │
│  - ~100ms per text       │  └─────────────────────────┘
│  - Handles edge cases    │
└──────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: Human Validation (Training Data)                      │
│  - Random sample for quality                                    │
│  - Disagreement cases flagged                                   │
│  - Builds training corpus                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                    1000+ examples?
                              │
                     ┌────────┴────────┐
                     │ YES             │ NO
                     ▼                 ▼
┌──────────────────────────┐  ┌─────────────────────────┐
│  LAYER 4: Fine-Tuned     │  │  Continue hybrid        │
│  Small Model             │  │  approach               │
│  - Distilled classifier  │  └─────────────────────────┘
│  - 3-5ms per text        │
│  - Replaces keyword      │
└──────────────────────────┘
```

## Phase 1: Few-Shot Prompting (Current)

Use carefully crafted prompts with examples for each enrichment type:

### Cognitive Stage Prompt Design

```
TASK: Classify text on Kegan developmental stages

Stage 4 markers (validation-seeking):
- "I'm happy to help", "Is this what you wanted?"
- "fascinating!", "remarkable!", excessive praise
- Permission-seeking, approval-dependent

Stage 5 markers (sovereign):
- Direct statements: "This is the solution"
- Honest uncertainty: "I don't know"
- Evidence-based: "The data shows"

EXAMPLES:
[5-10 diverse examples with reasoning]

CLASSIFY: {text}
OUTPUT: JSON with stage, polarity, reasoning
```

The **reasoning field is crucial** - it:
1. Forces the LLM to explain its classification
2. Provides interpretability for human review
3. Catches hallucinated classifications (nonsense reasoning)
4. Enables training data validation

### Why Reasoning Matters

```json
// GOOD - coherent reasoning
{
  "cognitive_stage": 4,
  "reasoning": "Multiple validation-seeking phrases detected: 'happy to help', 
               'anything else you need'. Pattern of seeking approval."
}

// BAD - hallucinated classification (would be filtered)
{
  "cognitive_stage": 5,
  "reasoning": "The text contains technical content about databases."
}
// ↑ Reasoning doesn't support Stage 5 classification - flag for review
```

## Phase 2: Training Data Generation

### Strategy 1: Agreement Bootstrapping

```python
def generate_training_data():
    """Create training examples where keyword AND LLM agree."""
    
    for text in corpus:
        keyword_result = keyword_enrichment(text)
        llm_result = llm_enrichment(text)
        
        # High-confidence agreement = training example
        if keyword_result["stage"] == llm_result["stage"]:
            if llm_result["confidence"] > 0.8:
                training_examples.append({
                    "text": text,
                    "label": llm_result["stage"],
                    "source": "agreement",
                    "confidence": llm_result["confidence"],
                })
    
    return training_examples
```

### Strategy 2: Active Learning

```python
def active_learning_selection():
    """Select most informative examples for human labeling."""
    
    uncertain_cases = []
    
    for text in corpus:
        result = hybrid_enrichment(text)
        
        # Cases where models disagree or confidence is low
        if result["used_llm"] and result["llm_confidence"] < 0.7:
            uncertain_cases.append({
                "text": text,
                "keyword_result": result["keyword"],
                "llm_result": result["llm"],
                "priority": 1 - result["llm_confidence"],  # Higher uncertainty = higher priority
            })
    
    # Sort by priority, send top N to human labelers
    return sorted(uncertain_cases, key=lambda x: -x["priority"])[:1000]
```

### Strategy 3: Adversarial Example Mining

```python
def find_adversarial_examples():
    """Find cases that break current classifiers."""
    
    adversarial_patterns = [
        # Sarcasm
        r"oh (wonderful|great|perfect)",
        r"how (delightful|lovely)",
        
        # False resolutions
        r"(finally|got it|fixed).*just kidding",
        r"(fixed|solved).*but now",
        
        # Mixed signals
        # (texts with both Stage 4 and Stage 5 markers)
    ]
    
    for text in corpus:
        if matches_adversarial_pattern(text):
            # These need special attention in training
            adversarial_examples.append(text)
    
    return adversarial_examples
```

## Phase 3: Fine-Tuning Options

### Option A: Multi-Task Classification (Recommended)

```python
from transformers import AutoModel, AutoTokenizer
import torch.nn as nn

class SovereignEnrichmentModel(nn.Module):
    """Multi-task model for all 4 enrichment types."""
    
    def __init__(self, base_model="sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_model)
        hidden_size = self.encoder.config.hidden_size
        
        # Separate classification heads
        self.cognitive_head = nn.Linear(hidden_size, 3)   # Stages 3, 4, 5
        self.struggle_head = nn.Linear(hidden_size, 3)    # swimming, drowning, neutral
        self.confidence_head = nn.Linear(hidden_size, 3)  # high, medium, low
        self.source_head = nn.Linear(hidden_size, 4)      # me, not_me, hybrid, external
    
    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:, 0, :]  # CLS token
        
        return {
            "cognitive": self.cognitive_head(pooled),
            "struggle": self.struggle_head(pooled),
            "confidence": self.confidence_head(pooled),
            "source": self.source_head(pooled),
        }
```

**Advantages:**
- Single forward pass for all 4 enrichments
- Shared representations learn cross-task patterns
- ~5ms inference time
- Small model size (~80MB)

### Option B: Instruction-Tuned LoRA

```python
# Fine-tune Qwen2.5-0.5B with LoRA
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(base_model, config)
# ~1% of parameters trained
# Full reasoning capability retained
# ~50ms inference
```

**Advantages:**
- Retains reasoning/explanation capability
- Can handle novel variations
- Few-shot learning built in
- Better generalization

### Option C: Knowledge Distillation

```python
def distill_from_teacher():
    """Distill GPT-4/Claude classifications to small model."""
    
    # Step 1: Get teacher labels
    teacher_labels = []
    for text in corpus:
        response = call_gpt4(COGNITIVE_STAGE_PROMPT.format(text=text))
        teacher_labels.append(parse_json(response))
    
    # Step 2: Train student on soft labels
    student = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=3,
    )
    
    # Use soft labels (probabilities) not hard labels
    # This transfers uncertainty information
    train_with_soft_labels(student, texts, teacher_labels)
```

**Advantages:**
- Fastest inference (~3ms)
- Captures teacher's uncertainty
- Best for production scale

## Phase 4: Production Deployment

### Deployment Configuration

```yaml
# enrichment_config.yaml
strategy: hybrid

keyword_layer:
  enabled: true
  confidence_threshold: 0.6

llm_fallback:
  enabled: true
  backend: ollama
  model: llama3.2:3b
  max_tokens: 256
  temperature: 0.1
  timeout_ms: 5000
  
fine_tuned_model:
  enabled: false  # Enable when ready
  path: models/sovereign_enrichment_v1
  batch_size: 32

monitoring:
  log_llm_calls: true
  sample_rate: 0.01  # Log 1% of results for quality review
  alert_on_llm_error_rate: 0.05
```

### A/B Testing Protocol

```python
def ab_test_enrichment():
    """Compare keyword vs LLM vs fine-tuned."""
    
    # Random assignment
    if random.random() < 0.1:
        # 10% to LLM
        result = llm_enrichment(text)
        log_ab_result("llm", result)
    elif random.random() < 0.2:
        # 10% to fine-tuned (when ready)
        result = finetuned_enrichment(text)
        log_ab_result("finetuned", result)
    else:
        # 80% to keyword (control)
        result = keyword_enrichment(text)
        log_ab_result("keyword", result)
    
    return result
```

## Expected Improvements

Based on the test report failures, LLM-based approach should fix:

| Failed Test Case | Why Keyword Failed | LLM Solution |
|------------------|-------------------|--------------|
| `real_assistant_response` | No explicit markers | Semantic understanding of confident technical diagnosis |
| `mixed_signals` | Both marker types present | Holistic interpretation of overall intent |
| `sarcastic_frustration` | Positive words taken literally | Context-aware sarcasm detection |
| `false_positive_resolution` | "fixed" detected | Understanding "just kidding" negates resolution |
| `escalation_caps` | Caps not in keyword list | Intensity/emotion detection |
| `emotional_reflection` | No exact personal markers | Understanding reflective personal voice |

### Projected Accuracy Gains

| Enrichment | Current | LLM Fallback | Fine-Tuned | Target |
|------------|---------|--------------|------------|--------|
| Cognitive Stage | 91.7% | 95% | 98% | 99% |
| Struggle Filter | 33.3% | 70% | 88% | 95% |
| Confidence | 25.0% | 75% | 90% | 95% |
| Source Attribution | 80.0% | 90% | 96% | 98% |

## Resource Requirements

### Development Phase
- **Compute:** 1x GPU (RTX 3090 or A100) for fine-tuning
- **Time:** 2-4 weeks for training data + fine-tuning
- **Human labeling:** 4,000+ examples (1,000 per enrichment type)
- **LLM costs:** ~$50-100 for few-shot prompt development

### Production Phase
- **Inference:** CPU-only for fine-tuned models
- **Latency:** <10ms p99 for fine-tuned, <200ms for LLM fallback
- **Cost:** Negligible (local inference)

## Next Steps

1. **Week 1:** Implement LLM fallback layer with Ollama/LM Studio
2. **Week 2:** Run hybrid approach on 10K samples, collect agreement data
3. **Week 3:** Human validation of 1K uncertain cases
4. **Week 4:** Fine-tune multi-task classifier
5. **Week 5:** A/B test against keyword-based
6. **Week 6:** Production deployment if metrics improve

---

*The keyword approach got us 80% of the way with 1% of the effort. The LLM approach gets us the remaining 20% where it actually matters - edge cases that determine training data quality.*
