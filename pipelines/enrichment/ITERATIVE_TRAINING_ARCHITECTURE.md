# Iterative Self-Improvement Training Architecture

## The Core Insight

Yes - this is not only possible, it's the **optimal approach**. It's called a **data flywheel** or **self-improvement loop**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE SOVEREIGN TRAINING FLYWHEEL                     │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  Weak    │      │  Better  │      │  Good    │      │  Final   │
    │  Labels  │─────▶│  Model   │─────▶│  Labels  │─────▶│  Model   │
    │  (70%)   │      │  (v1)    │      │  (90%)   │      │  (97%)   │
    └──────────┘      └──────────┘      └──────────┘      └──────────┘
         │                 │                  │                 │
         │   trains        │    generates     │    trains       │
         └─────────────────┴──────────────────┴─────────────────┘
                              
                           EACH ITERATION:
                           ├── Better model generates better data
                           ├── Better data trains better model  
                           └── Loop until converged (Δ < 0.5%)
```

## Why LoRA for Each Iteration?

| Benefit | Explanation |
|---------|-------------|
| **Cheap to train** | ~1% of parameters trained, 10x faster than full fine-tune |
| **Small adapters** | ~10-50MB vs 10GB+ full model, easy to version/compare |
| **Stackable** | Can merge multiple LoRA adapters or A/B test |
| **Reversible** | Can always fall back to base model |
| **Iteration-friendly** | Train new LoRA each round, keep best |

## The Full Pipeline

### Iteration 1: Bootstrap

```python
# Start with rules + few-shot LLM (expensive but accurate)
keyword_labels = keyword_classifier(corpus)  # Fast, 70% accurate
llm_labels = few_shot_llm(corpus[:1000])     # Slow, 80% accurate

# Keep only agreements (high confidence)
training_data = [
    ex for ex in corpus 
    if keyword_labels[ex] == llm_labels[ex]
    and confidence > 0.8
]
# Result: ~1,000 high-quality labels
```

### Iteration 2: First LoRA Model

```python
# Fine-tune small model on bootstrap data
lora_v1 = train_lora(
    base_model="Qwen/Qwen2.5-0.5B",
    data=training_data,
    config=LoRAConfig(rank=8, epochs=2)
)
# Result: 80% accuracy, 5ms inference
```

### Iteration 3: Data Expansion

```python
# Use LoRA model to label MUCH more data
expanded_labels = lora_v1.predict(full_corpus)  # Millions of texts

# Filter by confidence + agreement with rules
high_quality = [
    ex for ex in expanded_labels
    if ex.confidence > 0.85
    and agrees_with_keywords(ex)
]
# Result: ~50,000 labels (50x more data!)
```

### Iteration 4: Better Model

```python
# Train bigger model on expanded data
lora_v2 = train_lora(
    base_model="Qwen/Qwen2.5-1.5B",  # Bigger base
    data=high_quality,
    config=LoRAConfig(rank=16, epochs=3)  # More capacity
)
# Result: 90% accuracy
```

### Iteration 5+: Convergence Loop

```python
while accuracy_delta > 0.005:  # Continue while improving > 0.5%
    # Generate more data with current best model
    new_labels = current_model.predict(unlabeled_corpus)
    
    # Add hard examples (cases model got wrong)
    hard_examples = find_errors(current_model, validation_set)
    training_data += hard_examples  # Weight 3x higher
    
    # Train next iteration
    next_model = train_lora(
        base_model=bigger_if_needed(),
        data=training_data,
        config=increase_capacity()
    )
    
    # Evaluate
    accuracy_delta = next_model.accuracy - current_model.accuracy
    current_model = next_model
```

## Curriculum Learning: Easy → Hard

Each iteration focuses on increasingly difficult examples:

```
Iteration 1: Clear Stage 4/5 examples
             "I'm happy to help!" → Stage 4 (obvious)
             "This is the solution." → Stage 5 (obvious)

Iteration 2: Add mixed signals
             "This is the solution, but I hope it helps!"
             (Contains both markers - harder to classify)

Iteration 3: Add sarcasm/irony
             "Oh wonderful, another error. How delightful."
             (Positive words, negative intent)

Iteration 4: Add novel phrasings
             Patterns not in original training set
             Model must generalize semantically

Iteration 5: Adversarial examples
             Edge cases that break previous models
             "Fixed! Just kidding, still broken."
```

## Quality Controls at Each Iteration

### 1. Confidence Filtering
```python
# Only trust high-confidence predictions
MIN_CONFIDENCE = 0.8 + (iteration * 0.02)  # Increases each round
```

### 2. Ensemble Agreement
```python
# Require multiple methods to agree
def is_high_quality(text):
    keyword_pred = keyword_classifier(text)
    lora_pred = current_model(text)
    llm_pred = teacher_llm(text)  # Occasional verification
    
    # At least 2/3 must agree
    return agreement_rate([keyword_pred, lora_pred, llm_pred]) >= 0.66
```

### 3. Human Validation Loop
```python
# Validate 5% random sample each iteration
sample = random.sample(new_data, int(len(new_data) * 0.05))

for example in sample:
    human_label = get_human_annotation(example)
    if human_label != model_label:
        flag_for_review(example)
        update_error_corpus(example)
```

### 4. Hard Example Mining
```python
# Track persistent failures
if model_v1_wrong(example) and model_v2_wrong(example):
    hard_examples.add(example)
    example.training_weight = 3.0  # Oversample in next iteration
```

## Expected Progression

| Iteration | Data Size | LoRA Rank | Model Size | Accuracy | Inference |
|-----------|-----------|-----------|------------|----------|-----------|
| 1 (bootstrap) | 1K | - | LLM | 70% | 500ms |
| 2 | 5K | 8 | 0.5B | 80% | 10ms |
| 3 | 20K | 16 | 1.5B | 88% | 25ms |
| 4 | 50K | 32 | 3B | 93% | 50ms |
| 5 | 100K | 64 | 3B | 96% | 50ms |
| 6 | 200K | 64 | 3B | 97% | 50ms |
| **Converged** | - | - | - | - | - |

## When to Stop

Convergence criteria:
```python
STOP_CONDITIONS = [
    accuracy_delta < 0.005,        # Improvement < 0.5%
    current_accuracy >= 0.97,      # Hit target accuracy
    iteration >= 10,               # Max iterations
    human_agreement >= 0.98,       # Matches human labels
]

if any(STOP_CONDITIONS):
    save_final_model()
    deploy_to_production()
```

## Final Architecture

After convergence, deploy a **cascade** for cost efficiency:

```
                    Input Text
                         │
                         ▼
              ┌─────────────────────┐
              │   Fast LoRA Model   │  ← 5ms, handles 90% of cases
              │   (Iteration 6)     │
              └─────────────────────┘
                         │
                   confidence < 0.8?
                         │
              ┌──────────┴──────────┐
              │ NO                  │ YES
              ▼                     ▼
        ┌───────────┐        ┌───────────────────┐
        │  Return   │        │  Teacher LLM      │  ← 500ms, handles edge cases
        │  Result   │        │  (verification)   │
        └───────────┘        └───────────────────┘
```

## Resource Requirements

| Phase | GPU Hours | Human Labels | Storage |
|-------|-----------|--------------|---------|
| Iteration 1-2 | 4h | 200 | 1GB |
| Iteration 3-4 | 20h | 500 | 5GB |
| Iteration 5-6 | 30h | 300 | 10GB |
| **Total** | **~55h** | **~1,000** | **~16GB** |

Cost estimate: ~$50-100 on cloud GPU + ~$500 for human labeling

## Implementation Files

- [iterative_training_pipeline.py](iterative_training_pipeline.py) - Full pipeline code
- [enrichment_llm_based.py](enrichment_llm_based.py) - LLM prompts for bootstrap
- [test_sovereign_enrichments_comprehensive.py](test_sovereign_enrichments_comprehensive.py) - Evaluation harness

---

*The flywheel is the key: better models → better data → better models. Each iteration is cheap (LoRA), but the compound improvement is massive.*
