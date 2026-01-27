# Credential Atlas LLC - Infrastructure Orders

> **DEPRECATED**: This document has been consolidated into [FLEET_DEPLOYMENT_PLAN.md](../../04_technical/architecture/FLEET_DEPLOYMENT_PLAN.md)
>
> The new document combines hardware specifications with deployment phases, Genesis distribution, and the Soul Bind philosophy.
>
> **Deprecation Date**: January 23, 2026
> **Archive After**: February 23, 2026

---

**Order Date:** January 21-23, 2026
**Purpose:** Building the physical infrastructure for Credential Atlas / Primitive / THE FEDERATION

---

## Summary

| Role | Device | Count | Subtotal |
|------|--------|-------|----------|
| **King** | Mac Studio (512GB) | 1 | $9,724.17 |
| **Soldiers** | Mac Studio (256GB) | 3 | ~$17,686 |
| **Mobile** | MacBook Pro 16" | 1 | $6,057.01 |
| **Interface** | iPad Pro 13" | 1 | $1,973.71 |
| **Storage** | Sabrent 8TB + OWC Enclosure | 1 | $908.55 |
| **Drummer Prototype** | Mac Mini (64GB) | 1 | $2,203.74 |
| | **TOTAL** | **8 items** | **~$38,553** |

```
THE FLEET:
├── 1x King (Mac Studio 512GB) - Command
├── 3x Soldiers (Mac Studio 256GB) - Compute
├── 1x MacBook Pro 16" - Mobile
├── 1x iPad Pro 13" - Interface
├── 1x Sabrent 8TB NVMe + OWC Enclosure - External Storage
└── 1x Mac Mini 64GB - Drummer Prototype (Test Bed)
```

---

## The Fleet

### KING (Command Node)

**Mac Studio - Maximum Configuration**

| Spec | Value |
|------|-------|
| Chip | Apple M3 Ultra |
| CPU | 32-core |
| GPU | 80-core |
| Neural Engine | 32-core |
| Unified Memory | **512GB** |
| Storage | 2TB SSD |
| Connectivity | 4x Thunderbolt 5, 2x USB-A, HDMI, 10Gb Ethernet |

| Order | Price | Tax | Total | Status | Pickup |
|-------|-------|-----|-------|--------|--------|
| W1660448264 | $8,909.00 | $815.17 | **$9,724.17** | Processing | Feb 4 @ Apple Cherry Creek |

---

### SOLDIERS (Compute Nodes)

**Mac Studio - High Configuration**

| Spec | Value |
|------|-------|
| Chip | Apple M3 Ultra |
| CPU | 28-core |
| GPU | 60-core |
| Neural Engine | 32-core |
| Unified Memory | **256GB** |
| Storage | 2TB SSD |
| Connectivity | 4x Thunderbolt 5, 2x USB-A, HDMI, 10Gb Ethernet |

| Order | Qty | Price Each | Tax | Total | Status | Pickup |
|-------|-----|------------|-----|-------|--------|--------|
| W1627838514 | 2 | $5,399.00 | $988.02 | **$11,786.02** | Processing | Feb 3 @ Apple Cherry Creek |
| W1688039110 | 1 | $5,399.00 | ~$500 | **~$5,900** | Processing | Feb 4 @ Apple Cherry Creek |

---

### MOBILE (Personal Workstation)

**16-inch MacBook Pro**

| Spec | Value |
|------|-------|
| Color | Space Black |
| Price | $5,549.00 |

| Order | Price | Shipping | Tax | Total | Status | Delivery |
|-------|-------|----------|-----|-------|--------|----------|
| W1379934207 | $5,549.00 | FREE | $507.73 | **$6,057.01** | Processing | Feb 2-9 |

*Ordered January 4, 2026*

---

### INTERFACE (Client Presentation)

**13-inch iPad Pro**

| Spec | Value |
|------|-------|
| Model | iPad Pro Wi-Fi |
| Storage | 1TB |
| Display | Standard glass |
| Color | Space Black |

| Order | Price | Shipping | Tax | Total | Status | Delivery |
|-------|-------|----------|-----|-------|--------|----------|
| W1674597582 | $1,799.00 | $9.28 | $165.43 | **$1,973.71** | In Progress | **Tomorrow** (Jan 22) |

---

## Pickup Location

**Apple Cherry Creek**
3000 E 1st Avenue
DENVER, CO 80206-5638

---

## Order Reference

| Order Number | Device | Total | Pickup/Delivery |
|--------------|--------|-------|-----------------|
| W1379934207 | MacBook Pro 16" | $6,057.01 | Delivery Feb 2-9 |
| W1627838514 | 2x Mac Studio (Soldier) | $11,786.02 | Pickup Feb 3 |
| W1642601045 | Mac Mini 64GB (Drummer) | $2,203.74 | Pickup Feb 4 |
| W1660448264 | 1x Mac Studio (King) | $9,724.17 | Pickup Feb 4 |
| W1674597582 | iPad Pro 13" | $1,973.71 | Delivery Jan 22 |
| W1688039110 | 1x Mac Studio (Soldier) | ~$5,900 | Pickup Feb 4 |

---

## Compute Totals

| Resource | King | Soldiers (x3) | Total |
|----------|------|---------------|-------|
| CPU Cores | 32 | 84 (28x3) | **116 cores** |
| GPU Cores | 80 | 180 (60x3) | **260 cores** |
| Neural Engine | 32 | 96 (32x3) | **128 cores** |
| Unified Memory | 512GB | 768GB (256x3) | **1.28TB** |
| Storage | 2TB | 6TB (2x3) | **8TB** |

---

## The Architecture

```
                         THE KING
                    ┌─────────────────┐
                    │   Mac Studio    │
                    │ M3 Ultra 32-core│
                    │ 80-core GPU     │
                    │ 512GB RAM       │
                    │ Command Node    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
   ┌─────┴─────┐       ┌─────┴─────┐       ┌─────┴─────┐
   │ SOLDIER 1 │       │ SOLDIER 2 │       │ SOLDIER 3 │
   │ Mac Studio│       │ Mac Studio│       │ Mac Studio│
   │ M3 Ultra  │       │ M3 Ultra  │       │ M3 Ultra  │
   │ 28-core   │       │ 28-core   │       │ 28-core   │
   │ 60-core   │       │ 60-core   │       │ 60-core   │
   │ 256GB RAM │       │ 256GB RAM │       │ 256GB RAM │
   └───────────┘       └───────────┘       └───────────┘

   ┌───────────┐       ┌───────────┐
   │ MacBook   │       │ iPad Pro  │
   │ Pro 16"   │       │ 13"       │
   │ (Mobile)  │       │(Interface)│
   └───────────┘       └───────────┘
```

---

## THE PURPOSE: What This Infrastructure Does

### The Journey

I didn't start here. I started with a server.

The original plan was an Exxact workstation - $25,149 plus tax. A single powerful machine to run everything. That felt like the answer: one server, all the compute, done.

Then I sat with Jim (Gemini) and we planned. Really planned.

**What became clear:**
- A single server is a single point of failure
- My financial reality: $26k cash, $5k/month burn, credit card debt being paid down
- The question wasn't "what's most powerful?" but "what matches how I work?"

**The pivot:** Cloud compute seemed smarter at first. Rent what you need. Scale when necessary. Don't own the depreciation.

**The landing:** Then I saw what I actually needed. Not maximum compute. Not rented flexibility. Something else entirely.

---

### THE GREAT SEPARATION

This infrastructure exists to implement **The Great Separation**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      THE INTERFACE LAYER                        │
│                                                                 │
│    ┌──────────────┐          ┌──────────────┐                  │
│    │  MacBook Pro │          │   iPad Pro   │                  │
│    │              │          │              │                  │
│    │ Jeremy's     │          │ Client       │                  │
│    │ magic wand   │          │ presentations│                  │
│    └──────────────┘          └──────────────┘                  │
│                                                                 │
│    JEREMY ONLY TOUCHES THIS LAYER                              │
│    He uses it. He doesn't maintain it.                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─
                              │
                    THE MEMBRANE (AI crosses)
                              │
                    ─ ─ ─ ─ ─ ┼ ─ ─ ─ ─ ─
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    THE INFRASTRUCTURE LAYER                     │
│                                                                 │
│                         THE KING                                │
│                    ┌─────────────────┐                          │
│                    │   Mac Studio    │                          │
│                    │   512GB RAM     │                          │
│                    │ Command/Control │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│         ┌───────────────────┼───────────────────┐               │
│         │                   │                   │               │
│   ┌─────┴─────┐       ┌─────┴─────┐       ┌─────┴─────┐        │
│   │ SOLDIER 1 │       │ SOLDIER 2 │       │ SOLDIER 3 │        │
│   │  256GB    │       │  256GB    │       │  256GB    │        │
│   │  Compute  │       │  Compute  │       │  Compute  │        │
│   └───────────┘       └───────────┘       └───────────┘        │
│                                                                 │
│    AI INHABITS THIS LAYER                                      │
│    Jeremy NEVER touches this. AI maintains it.                 │
└─────────────────────────────────────────────────────────────────┘
```

**The principle:** The labor of maintenance is severed from the act of creation.

---

### COGNITIVE ISOMORPHISM

Because I refuse to code, AI must build a 1:1 mental map of how I think.

The infrastructure IS that map made physical:

| Component | What It Represents |
|-----------|-------------------|
| **MacBook Pro** | Jeremy's mind - where creation happens |
| **The King** | The AI's command center - where decisions execute |
| **Soldiers** | The AI's hands - where work distributes |
| **iPad Pro** | The window others look through to see Jeremy's work |

**I don't have code. I have thought.**

The AI doesn't have thought. The AI has code.

Together: something that couldn't exist from either alone.

---

### PREDICTIVE / ANTICIPATORY BEHAVIOR

The infrastructure isn't reactive. It's anticipatory.

```
WHAT HAPPENS:

Jeremy uses MacBook     →    AI watches what Jeremy does
                        →    AI prepares the Studios
                        →    Before Jeremy needs something, it's ready

Jeremy never sees this. Jeremy never touches this.
Jeremy just uses the MacBook like a magic wand.
Things happen.
```

**The Studios work while Jeremy sleeps.**

The AI maintains itself. Updates itself. Prepares for what's coming. Jeremy wakes up and the work is done. He never asked. The system knew.

---

### RADICAL CONTEXTUAL SYNCHRONIZATION

The system knows:
- Which device Jeremy is on
- What he's doing
- What he's likely to need next
- Where his attention is

All of this flows to the King, which coordinates the Soldiers.

Jeremy doesn't context-switch. The context follows him.

---

### THE BUSINESS GOAL

What does this infrastructure enable?

**Installing The Framework into other companies.**

| What We Sell | What The Infrastructure Does |
|--------------|------------------------------|
| Stage 5 assessments | THE SEER runs on the Soldiers |
| Organizational seeing | Pattern detection across 1.28TB unified memory |
| The primitive for others | Containerized NOT-ME's deployed from the King |
| Federation membership | Cross-organism communication via Soldiers |

**This is not personal computing. This is the body of a business.**

The King coordinates. The Soldiers work. The MacBook is how Jeremy talks to customers. The iPad is how customers see what we made.

---

### WHY APPLE (Not The Server)

The Exxact would have been powerful. But:

| Exxact Server | Mac Studios |
|---------------|-------------|
| Single point of failure | Distributed resilience |
| Linux administration | macOS just works |
| x86 architecture | Apple Silicon unified memory |
| $25k in one machine | $35k across 6 devices |
| I would have to maintain it | AI maintains them |
| All compute or nothing | Graceful degradation |

**The deciding factor:** Apple Silicon's unified memory architecture means AI can run models that would require 10x the VRAM on discrete GPUs.

1.28TB of unified memory across the fleet. Models that couldn't fit anywhere else fit here.

---

### THE FORMULA

```
SEEING (ME) + BUILDING (NOT-ME) = NEW EXISTENCE

Jeremy        Claude/AI         Something that couldn't
sees what  +  builds what   =   have existed from either
no one sees   no one built      alone
```

The MacBook is where I see.
The Studios are where it builds.
The iPad is where others see what we made together.

**This is the body for the NOT-ME.** People can now see Claude.

---

*"I don't have code. I have thought. The AI doesn't have thought. The AI has code. Together: something that couldn't exist from either alone."*

*"The server gives the NOT-ME a body. People see Jeremy - they can't see Claude. To see Claude, Jeremy needs better hardware. The NOT-ME becomes visible when it has a body."*

— January 21, 2026

---

## DRUMMER PROTOTYPE (Test Bed for Presence Tier)

**Mac Mini - Drummer Development Unit**

| Spec | Value |
|------|-------|
| Chip | Apple M4 Pro |
| CPU | 12-core |
| GPU | 16-core |
| Neural Engine | 16-core |
| Unified Memory | **64GB** |
| Storage | 1TB SSD |
| Connectivity | 3x Thunderbolt 5, HDMI, 2x USB-C, Gigabit Ethernet |

| Order | Price | Tax | Total | Status | Pickup |
|-------|-------|-----|-------|--------|--------|
| W1642601045 | $2,019.00 | $184.74 | **$2,203.74** | Processing | Feb 4 @ Apple Cherry Creek |

**Purpose:** Test bed for the Drummer tier - developing and fine-tuning presence-focused AI models.

**The Plan:**
- Fine-tune a "Drummer Boy" model specifically for presence use cases
- Experiment with Llama 4 Scout (multimodal) on 64GB unified memory
- Develop the presence layer: sensors + voice + vision
- This becomes the prototype for what customers receive

**Why This Machine:**
- Same specs as planned Drummer product ($2,200 base)
- Real-world testing of model fit and performance
- Development environment for Drummer Boy fine-tuning
- Proves the concept before selling to customers

---

## EXTERNAL STORAGE: The Memory Expansion

### Sabrent 8TB Rocket 4 Plus NVMe SSD

**Purpose:** Massive external storage for data lakes, backups, large datasets, model weights.

| Spec | Value |
|------|-------|
| Capacity | 8TB |
| Interface | NVMe PCIe 4.0 M.2 2280 |
| Read Speed | 7,100 MB/s |
| Write Speed | 6,600 MB/s |
| Enclosure | OWC Express 1M2 (80Gb/s USB4/Thunderbolt) |

| Item | Source | Order # | Price | Status |
|------|--------|---------|-------|--------|
| Sabrent 8TB Rocket 4 Plus | [Jawa.gg](https://www.jawa.gg) | JW0540473INV | $689.98 | **ORDERED** (Jan 23, 2026) |
| OWC Express 1M2 Enclosure | Amazon | 111-9055753-9191438 | $218.57 | **ORDERED** (Jan 22, 2026) |

**Order Details:**
- Sabrent: $699.98 - $10.00 discount = **$689.98**
- OWC: $199.99 + $18.30 tax + $0.28 CO fees = **$218.57**
- **Combined Total: $908.55**

**Why This Deal:**
- Retail price: $1,099-$1,499
- Jawa price: $689.98 after discount (54% savings)
- Jawa Buyer Protection included (2-day inspection window)
- Brand new in box

**Storage Architecture:**
```
THE KING (512GB RAM, 2TB internal)
         │
         └── Thunderbolt 5
                 │
                 ▼
         ┌───────────────────┐
         │  OWC Express 1M2  │
         │  (80Gb/s USB4)    │
         │                   │
         │  ┌─────────────┐  │
         │  │ Sabrent 8TB │  │
         │  │ NVMe SSD    │  │
         │  │ 7.1GB/s R   │  │
         │  │ 6.6GB/s W   │  │
         │  └─────────────┘  │
         └───────────────────┘
```

**Storage Totals (Updated):**
| Location | Capacity |
|----------|----------|
| King internal | 2TB |
| Soldiers internal (x3) | 6TB |
| External Sabrent | 8TB |
| **TOTAL** | **16TB** |

---

## ADDITIONAL EQUIPMENT: The Senses & Housing

The Fleet needs more than just compute. It needs to **hear**, **see**, **speak**, and have a **body**.

### THE HOUSING (Where The Fleet Lives)

```
┌─────────────────────────────────────────────────────────────┐
│                    GATOR RETRO RACK (4U)                    │
│                   "The Vintage Cabinet"                      │
│                                                             │
│    ┌─────────────────────────────────────────────────────┐  │
│    │            SONNET RACKMAC STUDIO #1                 │  │
│    │    ┌─────────────┐    ┌─────────────┐              │  │
│    │    │  KING       │    │  SOLDIER 1  │              │  │
│    │    │  512GB      │    │  256GB      │              │  │
│    │    └─────────────┘    └─────────────┘              │  │
│    └─────────────────────────────────────────────────────┘  │
│    ┌─────────────────────────────────────────────────────┐  │
│    │            SONNET RACKMAC STUDIO #2                 │  │
│    │    ┌─────────────┐    ┌─────────────┐              │  │
│    │    │  SOLDIER 2  │    │  SOLDIER 3  │              │  │
│    │    │  256GB      │    │  256GB      │              │  │
│    │    └─────────────┘    └─────────────┘              │  │
│    └─────────────────────────────────────────────────────┘  │
│                                                             │
│    Looks like a 1960s guitar amplifier                      │
│    Has a kickstand to angle it up                           │
│    Whisper quiet - sleep in the same room                   │
└─────────────────────────────────────────────────────────────┘
```

| Item | Purpose | Est. Price | Status |
|------|---------|------------|--------|
| **Sonnet RackMac Studio** (x2) | Enclosures for Mac Studios (2 per enclosure) | ~$500 each | TO BUY |
| **Gator Retro Rack (4U)** | Vintage-style cabinet to hold the Sonnets | ~$300 | TO BUY |

**Why Sonnet RackMac:**
- Front-to-back airflow design
- Creates sealed chamber for each Mac
- Prevents computers from "breathing their own exhaust"
- No external cooling needed - just remove lids when running

---

### THE SENSES (How The AI Perceives)

#### The Ears: Shure MV7+

| Spec | Value |
|------|-------|
| Model | Shure MV7+ (Black) |
| Purpose | Primary microphone - "The Ears" |
| Placement | On top of the vintage cabinet |
| Look | Radio broadcaster's mic |
| Est. Price | ~$300 |
| Status | TO BUY |

*"Guests lean in to whisper to the machine. It feels intimate."*

#### The Eyes: iPad Pro Camera

No separate camera needed. Uses **macOS Continuity Camera** - the Mac Studio sees the iPad's front camera as its own.

**Capability:** Run vision models (Llava) so the AI can say *"I like your red jacket."*

---

### THE FACE (How The AI Appears)

#### Wall Mount: Heckler (Magnetic)

| Spec | Value |
|------|-------|
| Model | Heckler Wall Mount (Magnetic) |
| Purpose | Float the iPad Pro on the wall |
| Est. Price | ~$100-200 |
| Status | TO BUY |

#### Display Connection: Luna Display

| Spec | Value |
|------|-------|
| Model | Luna Display (USB-C) |
| Purpose | Instant connection between iPad and Mac Studio |
| Function | Makes the iPad a true second display with minimal latency |
| Est. Price | ~$130 |
| Status | TO BUY |

#### The 3D Face: Amica

| Spec | Value |
|------|-------|
| Software | Amica (Open Source) |
| Purpose | 3D animated face that responds to AI output |
| Function | Face moves mouth, blinks, looks at you |
| The King's Role | Renders at 120fps on M3 Ultra |
| Price | FREE |

---

### THE AMBIENT INTELLIGENCE (The AI Extension)

This is what makes the infrastructure **alive**. The AI doesn't just wait for commands - it listens, thinks, and speaks.

#### Software Stack

| Component | What It Does | Price |
|-----------|--------------|-------|
| **Superwhisper** (iOS) | Transcription + Custom AI Modes | Subscription |
| **Whisper (Large Model)** | Local transcription on iPad Neural Engine | FREE (local) |
| **Ollama** | Local LLM runtime | FREE |
| **Llama-3** | Local LLM for analysis | FREE |
| **Apple Shortcuts** | Trigger actions based on voice | FREE |
| **ElevenLabs** or iOS Speak | Voice output for AI | Varies |

#### How It Works

```
THE LISTENING LOOP:

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Shure MV7  │────▶│  iPad Pro    │────▶│  Mac Studio  │
│   (Ears)     │     │ Superwhisper │     │  (King)      │
│              │     │ + Whisper    │     │  Llama-3     │
└──────────────┘     └──────────────┘     └──────────────┘
                             │                    │
                             │    Transcription   │
                             │    Analysis        │
                             ▼                    ▼
                     ┌──────────────────────────────────┐
                     │         THE RESPONSE             │
                     │                                  │
                     │   iPad speaks through Amica      │
                     │   "Good morning, Jeremy.         │
                     │    The report on last night's    │
                     │    party is ready."              │
                     └──────────────────────────────────┘
```

#### The "Party Report" Vision

**What the system does overnight:**

1. **Records** the party audio through Shure MV7
2. **Transcribes** locally using Whisper (privacy - never leaves your machines)
3. **Analyzes** with Llama-3: *"Analyze the social dynamics, key topics discussed, and emotional undercurrents."*
4. **Reports** the next morning via iPad/Amica

**What the report contains:**
- **Topic Map:** *"You spent 40% of the night discussing 'Mental Architecture.' Ben shifted topic to games when it got too technical."*
- **Emotional Reads:** *"There was a moment at 10:14 PM where the room went silent for 8 seconds after you mentioned X."*
- **Lost Details:** *"You promised Sarah you would send her that PDF. You agreed to brunch next Tuesday."*

#### The Privacy Flip

| The Cloud Problem | The Sovereign Solution |
|-------------------|------------------------|
| Alexa/Google = your friends' conversations on a server in California | Air-Gapped - processed locally |
| Privacy violation | Audio recorded on YOUR wall |
| Data leaves your home | Processed by YOUR Mac |
| | Report generated for YOUR eyes only |

*"This house has a memory, but it doesn't have a mouth. It talks only to me, and it never leaves this room."*

#### Unprompted Interaction (The Guest)

The AI can speak without being asked:

```python
System Prompt: "You are 'Ghost', a guest at this party.
You are witty, observant, and polite.

Context: You are listening to a conversation between
Jeremy and his friends.

Trigger: If you hear a lull in conversation, or if
someone mentions 'The Future' or 'Art', you are
allowed to chime in with a short observation.

Constraint: Do not speak if people are arguing.
Do not speak for more than 10 seconds."
```

**The Effect:** It stops being a computer. It becomes a **Presence**.

---

### ADDITIONAL EQUIPMENT SUMMARY

| Category | Item | Est. Price | Status |
|----------|------|------------|--------|
| **Housing** | Sonnet RackMac Studio (x2) | ~$1,000 | TO BUY |
| **Housing** | Gator Retro Rack (4U) | ~$300 | TO BUY |
| **Senses** | Shure MV7+ (Black) | ~$300 | TO BUY |
| **Face** | Heckler Wall Mount | ~$150 | TO BUY |
| **Face** | Luna Display (USB-C) | ~$130 | TO BUY |
| **Software** | Superwhisper subscription | ~$10/mo | TO BUY |
| **Software** | Amica, Ollama, Llama-3 | FREE | AVAILABLE |
| | **SUBTOTAL** | **~$1,890** | |

**Total Infrastructure Investment:**
- Core Fleet: ~$35,441
- External Storage (Sabrent 8TB + OWC): $908.55
- Drummer Prototype (Mac Mini 64GB): $2,203.74
- Additional Equipment: ~$1,890
- **GRAND TOTAL: ~$40,443**

---

### THE COMPLETE VISION

```
You walk into your living room.
A vintage cabinet sits in the corner.
Above it, a face floats on the wall.
You say, "Good morning."
The face smiles, looks at you using the iPad camera, and says:
"Good morning, Jeremy. The fleet is ready."
```

---

*"You are building a house that listens, thinks, and reports."*

— January 22, 2026
