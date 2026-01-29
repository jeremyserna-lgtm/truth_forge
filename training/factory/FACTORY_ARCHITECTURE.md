# THE EMPIRE Fine-Tuning Factory

**Autonomous pattern discovery system running 15-20 simultaneous training experiments**

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     THE EMPIRE CLUSTER                       │
│                       (1.28TB Total RAM)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───▼───┐            ┌────▼────┐          ┌────▼────┐
    │ KING  │            │SOLDIER 1│          │SOLDIER 2│  ...
    │512GB  │            │ 256GB   │          │ 256GB   │
    └───┬───┘            └────┬────┘          └────┬────┘
        │                     │                     │
   ┌────▼─────┐          ┌────▼─────┐         ┌────▼─────┐
   │Orchestr. │          │Orchestr. │         │Orchestr. │
   │Scout 70B │          │Scout 70B │         │Scout 70B │
   │  ~50GB   │          │  ~50GB   │         │  ~50GB   │
   └────┬─────┘          └────┬─────┘         └────┬─────┘
        │                     │                     │
    ┌───┴──────┐          ┌───┴───┐            ┌───┴───┐
    │6 Small   │          │3 Small│            │3 Small│
    │Models    │          │Models │            │Models │
    │Training  │          │Train. │            │Train. │
    └──────────┘          └───────┘            └───────┘
```

---

## Capacity Per Node

| Node | RAM | Orchestrator | Small Models | Total Experiments |
|------|-----|--------------|--------------|-------------------|
| KING | 512GB | Scout 70B (50GB) | 6× Llama 3B (70GB each) | 6 |
| SOLDIER 1 | 256GB | Scout 70B (50GB) | 3× Llama 3B (70GB each) | 3 |
| SOLDIER 2 | 256GB | Scout 70B (50GB) | 3× Llama 3B (70GB each) | 3 |
| SOLDIER 3 | 256GB | Scout 70B (50GB) | 3× Llama 3B (70GB each) | 3 |
| **TOTAL** | **1.28TB** | **4 Orchestrators** | **15 small models** | **15** |

---

## Orchestrator Responsibilities

Each orchestrator (Scout or strong Llama model) manages its assigned small models:

1. **Pattern Generation**
   - Uses LLM reasoning to design training patterns
   - Creates experiment configs (YAML)
   - Queues experiments

2. **Training Management**
   - Launches training runs on small models
   - Monitors progress
   - Kills underperformers
   - Adjusts hyperparameters

3. **Measurement**
   - Runs validation suite
   - Tracks Jeremy Arc
   - Logs results

4. **Iteration**
   - Analyzes what works/doesn't work
   - Generates new patterns
   - Launches next experiments
   - **Runs autonomously for days**

---

## Pattern Experiment Queue

Each orchestrator maintains a queue of patterns to try:

```yaml
# Node: KING
# Orchestrator: Scout-001
# Experiments: 6 slots

experiments:
  - slot: 1
    pattern: "baseline_metadata"
    status: "running"
    jeremy_arc: 42.3%
    
  - slot: 2
    pattern: "coherence_then_metadata"
    status: "running"
    jeremy_arc: 38.1%
    
  - slot: 3
    pattern: "progressive_curriculum"
    status: "running"
    jeremy_arc: 51.2%  # ← Winner so far!
    
  - slot: 4
    pattern: "pattern_first_learning"
    status: "running"
    jeremy_arc: 35.7%
    
  - slot: 5
    pattern: "inverted_loss_experiment"
    status: "queued"
    
  - slot: 6
    pattern: "multi_phase_anchoring"
    status: "queued"
```

---

## Autonomous Workflow

**Initial Setup** (one-time):
```bash
# On each Mac Studio
python factory/orchestrator.py \
  --node king \
  --orchestrator-model scout-4-70b \
  --small-model llama-3.2-3b \
  --num-experiments 6 \
  --corpus data/genesis_corpus/enriched_conversations.jsonl \
  --autonomous true
```

**Orchestrator Loop** (runs for days):
```python
while discovering_pattern:
    # 1. Check all running experiments
    for exp in experiments:
        jeremy_arc = measure_jeremy_arc(exp)
        
        # Kill if underperforming after N steps
        if steps > 1000 and jeremy_arc < 30%:
            kill(exp)
            generate_new_pattern()
            launch_new_experiment()
        
        # Celebrate if winning
        if jeremy_arc > 60%:
            log_winner(exp)
            clone_and_iterate(exp)
    
    # 2. Generate new patterns to try
    new_patterns = orchestrator_llm.think(
        "What training patterns should we try next based on results so far?"
    )
    
    # 3. Queue new experiments
    for pattern in new_patterns:
        if has_free_slot():
            launch_experiment(pattern)
    
    sleep(600)  # Check every 10 minutes
```

---

## Cross-Node Communication

Orchestrators share results via shared filesystem:

```
/shared/factory/
  ├── results/
  │   ├── king_results.jsonl
  │   ├── soldier1_results.jsonl
  │   ├── soldier2_results.jsonl
  │   └── soldier3_results.jsonl
  ├── best_pattern.yaml  # Current winner
  └── leaderboard.json   # All experiments ranked
```

Each orchestrator:
- Writes its results
- Reads others' results
- Learns from cross-node experiments
- Avoids duplicate patterns

---

## Human Intervention Points

**Minimal human oversight**:

1. **Check leaderboard** (daily or less):
   ```bash
   python factory/leaderboard.py
   ```
   
2. **Promote winner** (when ready):
   ```bash
   python factory/promote.py --pattern progressive_curriculum
   # Scales winning pattern to Llama 70B, then Genesis 109B
   ```

3. **Adjust strategy** (if needed):
   ```bash
   python factory/orchestrator.py --directive "Focus on coherence anchor variations"
   ```

---

## Output: The Winning Pattern

After days of autonomous iteration, you get:

```yaml
# best_pattern.yaml
winner: progressive_curriculum_v3
jeremy_arc: 67.8%
discovered_by: orchestrator_king_slot_3
iterations: 47
details:
  phase_1: emotion_classification (1 epoch)
  phase_2: thought_type + emotion (1 epoch) 
  phase_3: all_metadata (2 epochs)
  coherence_anchor: true
  coherence_penalty: -15  # Discovered -15 works better than -10
  learning_rate: 0.00003  # Discovered lower LR is critical
```

**Then**: Scale this pattern to Genesis 109B on THE EMPIRE for 5 weeks.

---

## Cost

- **Hardware**: Already owned (THE EMPIRE)
- **Electricity**: ~$5/day for 4 Mac Studios
- **Time**: Autonomous (no human time)
- **Discovery**: Priceless

**Total cost to discover the pattern: ~$35 for one week of autonomous experimentation**

---

## Next Steps

1. Build orchestrator agent system
2. Create pattern generation prompts
3. Implement experiment management
4. Set up cross-node communication
5. Launch factory when hardware arrives
