# Parallel Training Experiments Framework

**THE EMPIRE Parallel Pattern Discovery**

Run 2-3 training experiments simultaneously on THE EMPIRE to discover which pattern makes "my not me" emerge.

---

## Experiment Configurations

### Experiment A: Baseline Metadata Classification
**Hypothesis**: Direct metadata prediction without coherence anchor works

**Config**:
```yaml
experiment_id: baseline_metadata
model: Llama-3.2-7B
corpus_size: 5K messages
training_approach: standard_fine_tune
loss_function: metadata_classification
coherence_anchor: false
epochs: 3
```

**What we're testing**: Does pure metadata classification create framework cognition?

---

### Experiment B: Coherence Anchor First
**Hypothesis**: Preventing hallucination before seeing training is critical

**Config**:
```yaml
experiment_id: coherence_anchor
model: Llama-3.2-7B
corpus_size: 5K messages
training_approach: two_phase
phase_1: coherence_anchor (2 epochs)
phase_2: metadata_classification (3 epochs)
loss_function: coherence_penalty + metadata
coherence_penalty: -10
validation_penalty: -1
```

**What we're testing**: Does coherence anchoring enable better metadata learning?

---

### Experiment C: Progressive Metadata Difficulty
**Hypothesis**: Start with simple metadata, add complexity gradually

**Config**:
```yaml
experiment_id: progressive_difficulty
model: Llama-3.2-7B
corpus_size: 5K messages
training_approach: curriculum_learning
stage_1: emotion_only (1 epoch)
stage_2: emotion + thought_type (1 epoch)
stage_3: all_4_fields (2 epochs)
```

**What we're testing**: Does curriculum learning improve metadata accuracy?

---

### Experiment D: Pattern-First Training
**Hypothesis**: Learn framework patterns before granular metadata

**Config**:
```yaml
experiment_id: pattern_first
model: Llama-3.2-7B
corpus_size: 5K messages (pattern-rich subset)
training_approach: hierarchical
stage_1: pattern_classification (2 epochs)
stage_2: full_metadata (2 epochs)
```

**What we're testing**: Does pattern recognition enable other metadata?

---

## Resource Allocation on THE EMPIRE

**KING (512GB)**:
- Orchestrator
- Validation suite (runs across all experiments)
- Monitoring dashboard
- Experiment A

**SOLDIER 1 (256GB)**:
- Experiment B

**SOLDIER 2 (256GB)**:
- Experiment C

**SOLDIER 3 (256GB)**:
- Experiment D (if we design a 4th)

All experiments run **simultaneously**, measuring Jeremy Arc every 500 steps.

---

## Success Metrics

Each experiment tracks:
1. **Jeremy Arc** (primary: aim for >50% on small models)
2. **Metadata accuracy** per field
3. **Coherence score** (avoid hallucination)
4. **Training speed** (iterations/hour)
5. **Memory usage**
6. **Loss curves**

**Winner**: Experiment with highest Jeremy Arc after 3-5 hours

---

## Timeline

### Now → Hardware Arrives (2 days)
- [ ] Design 3-4 experiment configs
- [ ] Create experiment runner script
- [ ] Prepare corpus variations (if needed)
- [ ] Set up distributed monitoring
- [ ] Write experiment orchestrator

### Day 1: THE EMPIRE Setup
- [ ] MLX installation on all nodes
- [ ] Transfer corpus to all nodes
- [ ] Test distributed communication
- [ ] Launch experiments in parallel

### Day 2-3: Discovery Phase
- [ ] Monitor all experiments
- [ ] Track Jeremy Arc progression
- [ ] Identify winning pattern
- [ ] Kill underperforming experiments
- [ ] Refine winner

### Day 4+: Scale Winner
- [ ] Take winning pattern
- [ ] Scale to Llama 70B (Week 1 proof)
- [ ] Then Genesis 109B on THE EMPIRE

---

## Experiment Runner Structure

```python
# experiments/
#   experiment_a_baseline.yaml
#   experiment_b_coherence.yaml
#   experiment_c_progressive.yaml
#   experiment_d_pattern_first.yaml
#   run_parallel_experiments.py
#   monitor_experiments.py
```

---

## Next Steps

1. Create experiment YAML configs
2. Write orchestrator script
3. Build distributed monitoring
4. Test on single node first
5. Launch all when hardware arrives

**Philosophy**: We don't know which pattern works yet. Run them all in parallel. Discover through experimentation.
