# MAVERICK DEPLOYMENT HANDOFF

**Date**: February 5, 2026
**From**: Jeremy + Claude (Web)
**To**: Claude Code
**Purpose**: Deploy Maverick across the Genesis Cluster and begin autonomous work on the Apple Neural Engine Linux driver

---

## THE GOAL

Build a working Linux driver for the Apple Neural Engine (ANE) so that NOT-ME appliances can run on Linux instead of macOS—full sovereignty over the stack.

---

## THE INSIGHT

Scout and Maverick share the same `hidden_size = 5120`. They speak the same tensor language. They can share memory and cognition directly without translation layers. This means:

- Scout can hold 10M tokens of context (entire codebases)
- Maverick can reason deeply on what Scout sees
- They can exist in the same memory pool and communicate via tensors, not text
- Multiple Scouts can feed one Maverick

But first: **Get Maverick running and working autonomously.**

---

## CURRENT STATE

Reference: `/docs/business/plans/CURRENT_STATE.md`

### Hardware Operational

| Node | Role | IP (WiFi) | Status |
|------|------|-----------|--------|
| **King** | Coordinator | 192.168.68.121 | ✅ ACTIVE |
| **Soldier 1** | Compute | 192.168.68.112 | ✅ ACTIVE |
| **Soldier 2** | Compute | 192.168.68.123 | ✅ ACTIVE |
| **Soldier 3** | Compute | 192.168.68.115 | ✅ ACTIVE |

**Total Unified Memory**: 1.28TB (512GB King + 3x256GB Soldiers)

### Model Status

| Model | Size | Status |
|-------|------|--------|
| Scout 17B-16E (8-bit) | ~35GB | ✅ Ready at `/Volumes/GenesisModels/` |
| Maverick 17B-128E (4-bit) | ~150GB | 🔄 ~83% downloaded - **FINISH THIS FIRST** |

### Infrastructure Ready

- ✅ SSH key auth configured
- ✅ Shared storage mounted (`/Volumes/GenesisModels/`)
- ✅ EXO installed (GUI removed, headless native)
- ✅ Apple Remote Desktop for emergency access

---

## STEP 1: COMPLETE MAVERICK DOWNLOAD

Check status:
```bash
# On King
ls -lh /Volumes/GenesisModels/models/cache/ | grep -i maverick
```

If incomplete, resume the download:
```bash
# Using huggingface-cli
huggingface-cli download mlx-community/Llama-4-Maverick-17B-128E-4bit \
    --local-dir /Volumes/GenesisModels/models/maverick-4bit \
    --resume-download
```

Or if using a different method, check the original download command in the session history and resume it.

**Do not proceed until Maverick is fully downloaded.**

---

## STEP 2: CLONE TARGET REPOSITORIES

```bash
# On King, in shared storage
mkdir -p /Volumes/GenesisModels/repos
cd /Volumes/GenesisModels/repos

# The Asahi Linux kernel (contains partial ANE work)
git clone https://github.com/AsahiLinux/linux.git asahi-linux

# Asahi documentation and reverse-engineering notes
git clone https://github.com/AsahiLinux/docs.git asahi-docs

# Link truth_forge for Framework context
ln -s /Users/jeremyserna/truth_forge ./truth_forge
```

---

## STEP 3: START MAVERICK ON THE CLUSTER

EXO pools unified memory across Thunderbolt-connected Mac Studios and exposes an OpenAI-compatible API.

```bash
# On King
# First, verify all nodes are reachable
ping -c 1 192.168.68.112  # Soldier 1
ping -c 1 192.168.68.123  # Soldier 2
ping -c 1 192.168.68.115  # Soldier 3

# Start EXO with Maverick
exo start \
    --model /Volumes/GenesisModels/models/maverick-4bit \
    --port 8000

# Or if using the HuggingFace model ID directly:
exo start \
    --model mlx-community/Llama-4-Maverick-17B-128E-4bit \
    --port 8000
```

**Verify it's running:**
```bash
curl http://localhost:8000/v1/models
```

Should return the model info.

---

## STEP 4: CONNECT AGENT ZERO TO MAVERICK

Agent Zero gives Maverick hands—shell access, file system, code execution.

### Option A: If Agent Zero is already installed

Edit config (usually `~/.agent-zero/config.json` or similar):

```json
{
  "chat_model": {
    "provider": "openai",
    "api_base": "http://localhost:8000/v1",
    "model": "llama-4-maverick",
    "api_key": "local"
  }
}
```

### Option B: If using OpenClaw

Configure OpenClaw to use the local Maverick endpoint:

```yaml
# In OpenClaw config
llm:
  provider: openai_compatible
  base_url: http://localhost:8000/v1
  model: llama-4-maverick
  api_key: local
```

### Option C: Quick test with curl

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-4-maverick",
    "messages": [{"role": "user", "content": "Hello, are you operational?"}]
  }'
```

---

## STEP 5: GIVE MAVERICK THE GOAL

Once Maverick is running and connected to an agent framework, give it this prompt:

```
Your goal: Build a working Linux driver for the Apple Neural Engine (ANE).

Context:
- The ANE is hardware in Apple Silicon chips (M1, M2, M3, M4)
- macOS can use it for ML inference via CoreML/ANE frameworks
- Linux (Asahi) has reverse-engineered most of Apple Silicon, but ANE driver is incomplete
- You are running on a cluster of Mac Studios with 1.28TB unified memory

You have access to:
- Shell commands (run anything)
- File system (read/write anywhere)
- Git (clone, commit, push)
- Python (write and execute code)

Resources available at /Volumes/GenesisModels/repos/:
- asahi-linux/ - The Asahi Linux kernel source
- asahi-docs/ - Reverse engineering documentation
- truth_forge/ - The Framework and NOT-ME architecture

Your task:
1. Analyze the Asahi kernel source for existing ANE work
   - Search: drivers/soc/apple/, drivers/misc/, arch/arm64/boot/dts/apple/
   - Find any references to ANE, neural, NPU

2. Analyze the Asahi docs for reverse engineering notes
   - Search for ANE, neural engine, NPU documentation

3. Map what exists:
   - What has been reverse engineered?
   - What drivers exist (even partial)?
   - What register maps are documented?
   - What is the firmware loading process?

4. Map what's missing:
   - What blocks a working driver?
   - What needs to be reverse engineered?
   - What code needs to be written?

5. Begin building:
   - Start with the smallest working proof of concept
   - Document everything in /Volumes/GenesisModels/repos/ane-driver-work/

Work autonomously. Create files, run code, test hypotheses.
Report significant findings or when you need human input.
```

---

## STEP 6: WALK AWAY

Maverick has:
- ✅ Compute (1.28TB unified memory)
- ✅ Hands (Agent Zero / OpenClaw)
- ✅ Context (Asahi repos, truth_forge)
- ✅ Goal (ANE driver)

Let it work.

---

## FUTURE: HIVE MIND ARCHITECTURE

Once Maverick is operational, the next evolution is multi-model cognition:

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIFIED MEMORY (1.28TB)                       │
│                                                                  │
│   MAVERICK (Reasoner)                                            │
│   └── Decides what needs to be known                             │
│   └── Reasons deeply on findings                                 │
│   └── Produces plans and code                                    │
│                                                                  │
│   SCOUT 1 (Seer) ─── holds asahi-linux (10M tokens)             │
│   SCOUT 2 (Seer) ─── holds asahi-docs (10M tokens)              │
│   SCOUT 3 (Seer) ─── holds truth_forge (10M tokens)             │
│                                                                  │
│   Communication: Direct tensor sharing (hidden_size=5120)        │
│   No text serialization. Shared cognition.                       │
└─────────────────────────────────────────────────────────────────┘
```

Key insight: Scout and Maverick share `hidden_size = 5120`. Their internal representations are already compatible. They can share memory and pass understanding as tensors, not text.

This is Phase 2. First, get Maverick working solo.

---

## REFERENCE: THE PATTERN

From THE_FRAMEWORK:

```
WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE → VERIFY
```

Applied here:
- **WANT**: Linux driver for ANE (sovereignty over the stack)
- **CHOOSE**: Use Maverick + Asahi's existing work
- **EXIST:NOW**: Deploy Maverick on the cluster today
- **SEE**: Maverick analyzes repos, finds gaps
- **HOLD**: Maverick holds the full architecture understanding
- **MOVE**: Maverick writes code, tests, iterates
- **VERIFY**: Working driver that initializes ANE on Linux

---

## REFERENCE: KEY FILES

- Current state: `/docs/business/plans/CURRENT_STATE.md`
- NOT-ME spec: `/docs/business/plans/NOT_ME_CORE_SPECIFICATION.md`
- Infrastructure plan: `/docs/business/plans/NOT_ME_INFRASTRUCTURE_PLAN.md`
- Seeing Session methodology: `/docs/business/strategy/philosophy/SEEING_SESSION_METHODOLOGY.md`

---

## SUCCESS CRITERIA

1. Maverick is running on the Genesis Cluster via EXO
2. Maverick has agent hands (shell, file system, code execution)
3. Maverick has access to Asahi repos
4. Maverick is autonomously working on ANE driver analysis
5. Progress is documented in `/Volumes/GenesisModels/repos/ane-driver-work/`

---

## NOTES FOR CLAUDE CODE

- Jeremy has EXO installed and working (GUI removed, headless mode)
- The cluster is networked via both Thunderbolt (high-speed) and WiFi
- Maverick download is ~83% complete as of this writing
- Agent Zero and OpenClaw are both available as agent frameworks
- Jeremy's primitive is SEE—he designed the Seeing Session methodology for exactly this kind of deep analysis
- The Framework principle: "If we can't see something, we change to see it. If we can't see a service, we change to see it—we discover it or build it."

**This is the work. Make it happen.**

---

*Created: February 5, 2026*
*Status: HANDOFF DOCUMENT - Ready for Claude Code execution*
