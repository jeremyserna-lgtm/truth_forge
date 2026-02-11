# Sovereign AI Reference Architecture

**Version**: 1.0.0
**Status**: SPECIFICATION
**Author**: Jeremy Serna / Credential Atlas
**Date**: January 23, 2026
**License**: Open Standard (CC BY 4.0)

---

## Abstract

The Sovereign AI Reference Architecture provides a complete, deployable blueprint for local-first AI infrastructure. It covers hardware specifications, software stack, distributed inference, and operational patterns for running large language models (600B+ parameters) entirely on-premises.

**The core insight**: Sovereignty is not just data residency. If your control plane lives elsewhere, you're not sovereign. True sovereignty means architectural control, operational independence, and escape velocity.

---

## 1. What Sovereign AI Means

### 1.1 The Three Properties

| Property | Definition | Test |
|----------|------------|------|
| **Architectural Control** | Running everything locally with no external dependencies | Can you operate air-gapped? |
| **Operational Independence** | Policies and security controls move with workloads | Do you own your control plane? |
| **Escape Velocity** | Ability to leave any provider without breaking your stack | Can you migrate in 24 hours? |

### 1.2 What Sovereignty Is NOT

```
❌ "Our data stays in your region" → Data residency, not sovereignty
❌ "We use your keys" → Key management, not sovereignty
❌ "You can export your data" → Portability, not sovereignty
❌ "We're SOC 2 compliant" → Compliance, not sovereignty

✅ Sovereignty: You own the hardware, the software, the data, AND the control plane
```

---

## 2. Hardware Architecture

### 2.1 Reference Cluster: 4x Mac Studio M3 Ultra

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Compute** | 4x Mac Studio M3 Ultra | 128 CPU cores, 320 GPU cores total |
| **Memory** | 512GB unified per node = 2TB total | 671B parameter models |
| **Storage** | 8TB NVMe per node = 32TB total | Model storage, inference cache |
| **Interconnect** | Thunderbolt 5 mesh | 120Gbps per link, 3μs latency with RDMA |
| **Network** | 10GbE backup | Fallback if TB5 unavailable |

### 2.2 Topology

```
                    ┌─────────────────────────────────────┐
                    │           KING (Coordinator)        │
                    │       Mac Studio M3 Ultra           │
                    │       512GB | 32-core | 80-core GPU │
                    └─────────────────────────────────────┘
                              │ TB5        │ TB5
                    ┌─────────┴─────┐     ┌┴──────────────┐
                    │               │     │               │
          ┌─────────▼─────────┐   ┌▼─────▼─────────┐   ┌─▼───────────────┐
          │     SOLDIER 1     │   │   SOLDIER 2    │   │    SOLDIER 3    │
          │  Mac Studio M3    │◄──│ Mac Studio M3  │──►│  Mac Studio M3  │
          │      Ultra        │TB5│     Ultra      │TB5│      Ultra      │
          └───────────────────┘   └────────────────┘   └─────────────────┘

          Total: 1.28TB unified memory across cluster
          Interconnect: Full mesh TB5 (120Gbps, 3μs RDMA latency)
```

### 2.3 Hardware Bill of Materials

| Item | Qty | Unit Price | Total |
|------|-----|------------|-------|
| Mac Studio M3 Ultra (512GB, 8TB) | 4 | $9,999 | $39,996 |
| Thunderbolt 5 Cable (0.8m) | 6 | $69 | $414 |
| Thunderbolt 5 Hub | 2 | $349 | $698 |
| 10GbE Switch | 1 | $299 | $299 |
| UPS (1500VA) | 2 | $399 | $798 |
| **Total Hardware** | | | **$42,205** |

---

## 3. Software Stack

### 3.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  Truth Engine │ Credential Atlas │ Custom Applications      │
├─────────────────────────────────────────────────────────────┤
│                    FRAMEWORK LAYER                           │
│  THE_FRAMEWORK │ Furnace │ Zero Trust │ Human-Aware         │
├─────────────────────────────────────────────────────────────┤
│                   INFERENCE LAYER                            │
│  EXO (distributed) │ Ollama (local) │ MLX (native)          │
├─────────────────────────────────────────────────────────────┤
│                    RUNTIME LAYER                             │
│  Python 3.12 │ Metal │ RDMA drivers │ MPS backend           │
├─────────────────────────────────────────────────────────────┤
│                    OS LAYER                                  │
│  macOS Sequoia │ Secure Enclave │ FileVault                 │
├─────────────────────────────────────────────────────────────┤
│                   HARDWARE LAYER                             │
│  M3 Ultra │ Unified Memory │ Neural Engine │ TB5            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Specifications

| Component | Version | Purpose | Configuration |
|-----------|---------|---------|---------------|
| **macOS** | Sequoia 15.x | Operating system | FileVault enabled |
| **Python** | 3.12 | Runtime | pyenv managed |
| **MLX** | 0.10+ | ML framework | Metal backend |
| **EXO** | 0.2+ | Distributed inference | RDMA enabled |
| **Ollama** | 0.4+ | Model management | Cluster-aware proxy |
| **DuckDB** | 1.0+ | Local database | In-process |

### 3.3 Model Distribution

| Model | Size | Quantization | Nodes Required | Tokens/sec |
|-------|------|--------------|----------------|------------|
| DeepSeek-V3 | 671B | Q4.5 | 4 (all) | ~17-18 |
| Llama 3.3 | 70B | Q8 | 1 | ~45 |
| Qwen 2.5 | 72B | Q8 | 1 | ~40 |
| Custom fine-tune | 70B | Q8 | 1 | ~45 |

---

## 4. Distributed Inference with EXO

### 4.1 Configuration

```yaml
# /etc/exo/config.yaml

cluster:
  name: "sovereign-cluster"
  coordinator: "king"

nodes:
  - name: "king"
    role: "coordinator"
    memory: "512GB"
    interfaces:
      - type: "thunderbolt5"
        device: "en5"
        rdma: true
      - type: "ethernet"
        device: "en0"
        fallback: true

  - name: "soldier1"
    role: "worker"
    memory: "512GB"
    interfaces:
      - type: "thunderbolt5"
        device: "en5"
        rdma: true

  - name: "soldier2"
    role: "worker"
    memory: "512GB"
    interfaces:
      - type: "thunderbolt5"
        device: "en5"
        rdma: true

  - name: "soldier3"
    role: "worker"
    memory: "512GB"
    interfaces:
      - type: "thunderbolt5"
        device: "en5"
        rdma: true

inference:
  default_model: "deepseek-v3-671b-q4.5"
  batch_size: 32
  context_length: 100000

connection_priority:
  - thunderbolt5_rdma   # 3μs latency
  - thunderbolt5_tcp    # 300μs latency
  - ethernet_10g        # 500μs latency
  - wifi                # 2ms latency (emergency only)
```

### 4.2 Startup Sequence

```bash
#!/bin/bash
# /usr/local/bin/start-cluster.sh

echo "Starting Sovereign AI Cluster..."

# 1. Verify hardware
echo "Checking hardware..."
for node in king soldier1 soldier2 soldier3; do
    ssh $node "system_profiler SPHardwareDataType | grep 'Chip'" || exit 1
done

# 2. Verify interconnect
echo "Checking Thunderbolt 5 mesh..."
for node in king soldier1 soldier2 soldier3; do
    ssh $node "networksetup -listallhardwareports | grep -A1 Thunderbolt" || exit 1
done

# 3. Start EXO on workers
echo "Starting EXO workers..."
for node in soldier1 soldier2 soldier3; do
    ssh $node "exo worker --config /etc/exo/config.yaml" &
done

sleep 5

# 4. Start EXO coordinator
echo "Starting EXO coordinator..."
exo coordinator --config /etc/exo/config.yaml &

# 5. Wait for cluster formation
echo "Waiting for cluster..."
until exo status | grep -q "4 nodes online"; do
    sleep 1
done

echo "Cluster ready!"
exo status
```

---

## 5. Security Architecture

### 5.1 Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Physical Security                                   │
│ • Locked server room                                         │
│ • Cameras with local storage                                 │
│ • Access logging                                             │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: Hardware Security                                   │
│ • Secure Enclave for keys                                    │
│ • Touch ID for authentication                                │
│ • Hardware-bound identity attestation                        │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: Disk Security                                       │
│ • FileVault full-disk encryption                             │
│ • Secure Enclave key storage                                 │
│ • Encrypted swap                                             │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: Network Security                                    │
│ • No external network access (air-gap capable)               │
│ • TB5 mesh is physically secured                             │
│ • 10GbE on isolated VLAN                                     │
├─────────────────────────────────────────────────────────────┤
│ LAYER 5: Application Security                                │
│ • Spark authorization (Touch ID before execution)            │
│ • Zero Trust audit trail                                     │
│ • Intrinsic loyalty in model weights                         │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Spark Authorization

All code execution requires explicit human authorization:

```python
# Before any script runs
from governance.spark_service import require_spark

@require_spark(
    purpose="Run inference pipeline",
    duration_minutes=60,
    authorization_method="touch_id"
)
def run_inference(prompt: str) -> str:
    # This only executes if human touched fingerprint
    return model.generate(prompt)
```

---

## 6. Operational Patterns

### 6.1 Model Management

```bash
# Download model (once, with internet)
exo model pull deepseek-v3-671b-q4.5

# Distribute across cluster
exo model distribute deepseek-v3-671b-q4.5 --nodes all

# Verify distribution
exo model status deepseek-v3-671b-q4.5

# Output:
# Model: deepseek-v3-671b-q4.5
# Status: distributed
# Shards:
#   king:     layers 0-167    (128GB)
#   soldier1: layers 168-335  (128GB)
#   soldier2: layers 336-503  (128GB)
#   soldier3: layers 504-671  (128GB)
```

### 6.2 Air-Gap Operation

```bash
# Export model for air-gap transfer
exo model export deepseek-v3-671b-q4.5 --output /mnt/usb/models/

# On air-gapped cluster: import
exo model import /mnt/usb/models/deepseek-v3-671b-q4.5/

# Verify (no internet needed)
exo model verify deepseek-v3-671b-q4.5
# Checks: file hashes match manifest (no external calls)
```

### 6.3 Monitoring Dashboard

```python
# Control room visibility
from dashboard import ControlRoom

room = ControlRoom()

@room.panel("Cluster Status")
def cluster_status():
    return {
        "nodes_online": 4,
        "total_memory": "2.048TB",
        "memory_used": "1.2TB",
        "current_model": "deepseek-v3-671b-q4.5",
        "requests_per_minute": 45,
        "avg_latency_ms": 58,
    }

@room.panel("Connection Health")
def connection_health():
    return {
        "tb5_links": {"status": "healthy", "latency_us": 3.2},
        "ethernet_backup": {"status": "standby"},
        "rdma_enabled": True,
    }

# Render dashboard
room.render()
```

---

## 7. Fine-Tuning Workflow

### 7.1 Distributed Training Setup

```python
import mlx.core as mx
from mlx_distributed import DistributedTrainer

# Configure distributed training across cluster
config = {
    "nodes": ["king", "soldier1", "soldier2", "soldier3"],
    "coordinator": "king",
    "batch_size_per_node": 4,
    "gradient_accumulation": 8,
    "learning_rate": 1e-5,
    "lora_rank": 64,
    "lora_alpha": 128,
}

trainer = DistributedTrainer(
    base_model="llama-3.3-70b",
    config=config,
)

# Training data (local files, no cloud)
trainer.load_data("/data/training/corpus.jsonl")

# Train with visibility
for epoch in trainer.train(epochs=3):
    print(f"Epoch {epoch.number}")
    print(f"  Loss: {epoch.loss:.4f}")
    print(f"  Nodes: {epoch.node_status}")
    print(f"  Memory: {epoch.memory_usage}")

# Save fine-tuned model
trainer.save("/models/custom-70b-v1/")
```

### 7.2 Training Corpus Preparation

```python
# Prepare training data from Truth Engine knowledge
from truth_engine import KnowledgeExporter

exporter = KnowledgeExporter()

# Export relevant atoms
corpus = exporter.export(
    sources=["conversations", "documents", "framework"],
    format="instruction_tuning",
    output="/data/training/corpus.jsonl"
)

print(f"Exported {corpus.count} training examples")
print(f"Total tokens: {corpus.token_count:,}")
```

---

## 8. Deployment Checklist

### 8.1 Pre-Deployment

```
□ Hardware ordered and received
□ Physical location secured
□ Network infrastructure ready
□ UPS installed and tested
□ Cooling adequate
```

### 8.2 Hardware Setup

```
□ All Mac Studios unboxed and inspected
□ FileVault enabled on all nodes
□ Touch ID configured on coordinator
□ TB5 mesh connected and tested
□ 10GbE backup connected
□ SSH keys distributed
```

### 8.3 Software Setup

```
□ macOS updated to latest
□ Python 3.12 installed via pyenv
□ MLX installed and verified
□ EXO installed and configured
□ Ollama installed (optional)
□ Monitoring dashboard configured
```

### 8.4 Security Setup

```
□ Spark authorization configured
□ Secure Enclave keys generated
□ Audit logging enabled
□ Backup procedures documented
□ Air-gap procedures tested
```

### 8.5 Operational Readiness

```
□ Models downloaded and distributed
□ Cluster startup tested
□ Failover tested (remove one node)
□ Performance benchmarked
□ Monitoring alerts configured
□ Runbook documented
```

---

## 9. Troubleshooting

### 9.1 Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| TB5 not detected | Node shows as disconnected | Reseat cable, check `system_profiler SPThunderboltDataType` |
| RDMA not working | High latency (>100μs) | Verify `ibv_devinfo` shows device, restart EXO |
| OOM on inference | Model won't load | Check model fits in cluster memory, reduce batch size |
| Node unresponsive | Timeout on SSH | Check UPS, verify macOS not in sleep mode |
| Slow token generation | <10 tok/s | Check for thermal throttling, verify TB5 mesh |

### 9.2 Diagnostic Commands

```bash
# Check cluster status
exo status --verbose

# Check TB5 connectivity
system_profiler SPThunderboltDataType

# Check RDMA status
ibv_devinfo

# Check memory pressure
memory_pressure

# Check thermal status
pmset -g thermlog

# Full diagnostic report
exo diagnose > /tmp/cluster-diagnosis.txt
```

---

## 10. Cost Analysis

### 10.1 One-Time Costs

| Category | Cost |
|----------|------|
| Hardware | $42,205 |
| Setup (electrician, network) | ~$2,000 |
| **Total One-Time** | **~$44,205** |

### 10.2 Ongoing Costs

| Category | Monthly |
|----------|---------|
| Electricity (~800W avg) | ~$75 |
| Internet (optional) | ~$100 |
| Backups (local NAS) | ~$0 (already owned) |
| **Total Monthly** | **~$175** |

### 10.3 Comparison to Cloud

| Metric | Sovereign | Cloud (equivalent) |
|--------|-----------|-------------------|
| One-time | $44,205 | $0 |
| Monthly | $175 | ~$15,000+ |
| Break-even | ~3 months | N/A |
| After 1 year | $46,305 total | $180,000+ |
| Data sovereignty | Full | Partial at best |
| Air-gap capable | Yes | No |

---

## 11. Appendix: Quick Reference

### Minimum Specifications

```
For 70B models: 1x Mac Studio M3 Ultra (512GB)
For 671B models: 4x Mac Studio M3 Ultra (2TB total)
```

### Key Commands

```bash
exo status              # Cluster status
exo model list          # Available models
exo model pull <name>   # Download model
exo model distribute    # Distribute across cluster
exo generate            # Run inference
exo diagnose            # Full diagnostic
```

### Sovereignty Test

```
1. Can you operate air-gapped? → Yes
2. Do you own your control plane? → Yes
3. Can you migrate in 24 hours? → Yes (it's your hardware)

Result: SOVEREIGN
```

---

## License

This architecture is released under Creative Commons Attribution 4.0 International (CC BY 4.0).

---

*"If your control plane lives elsewhere, you're not sovereign."*

— Sovereign AI Reference Architecture v1.0.0, January 23, 2026

