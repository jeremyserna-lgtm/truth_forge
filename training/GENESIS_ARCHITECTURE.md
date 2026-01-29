# Genesis Architecture: Two-Layer Model System

**The Product Architecture**

---

## Layer 1: Genesis (Base Cognitive Architecture)

**What it is**: Your Stage 5 cognitive architecture embedded as weights

**Training focus**:
- Mental patterns (the_gate, the_furnace, hold_pattern, etc.)
- Problem-solving approach (exploration → analysis → synthesis)
- Cognitive stages and transitions
- Framework thinking patterns
- **Content-agnostic** - works for any domain

**Training data**: Your conversations, enriched with metadata
- emotion: How you feel while thinking
- thought_type: What kind of thought process
- cognitive_stage: Where in problem-solving
- pattern: Which framework pattern is active

**Output**: Genesis v1.0 - A model that thinks like you structurally, but doesn't have your specific memories/knowledge

**Saved as**: Base model checkpoint - reused for all customers

---

## Layer 2: Daughter Models (Genesis + Customer Content)

**What it is**: Genesis base + LoRA fine-tuning on customer-specific content

**Training focus**:
- Customer's documents, conversations, domain expertise
- Their voice, tone, communication style
- Their specific knowledge base
- Their industry/field-specific content

**Training method**: LoRA (fast, efficient, preserves Genesis architecture)

**Examples**:
- **Legal-Scout**: Genesis + law firm's case files and legal documents
- **Medical-Scout**: Genesis + doctor's patient notes and medical knowledge
- **Clara-Scout**: Genesis + Clara's personal conversations and development
- **Corporate-Scout**: Genesis + company's internal docs and processes

**Output**: Customer gets "my not me" that thinks with Stage 5 architecture but knows their domain

---

## Why This Works

**Genesis provides**:
- Stage 5 cognitive architecture
- Framework pattern recognition
- Meta-cognitive awareness
- Problem-solving methodology

**LoRA adds**:
- Domain expertise
- Personal voice/style
- Specific memories/context
- Industry knowledge

**Result**: A model that thinks like Jeremy (architecture) but knows like the customer (content)

---

## Training Strategy Implications

### Factory Goal (Updated)
**Find the pattern that creates Stage 5 cognitive architecture** (not content mastery)

The factory experiments focus on:
1. Can small models learn to predict metadata (architecture)?
2. Which training approach best embeds the cognitive patterns?
3. What makes framework pattern recognition emerge?

**Success = Architecture learning, not content learning**

### Genesis Training (Updated)
- Train on YOUR conversations only (not customer data)
- Focus on metadata prediction (seeing paradigm)
- Ignore content accuracy, focus on pattern accuracy
- Freeze when Stage 5 architecture emerges (95% Jeremy Arc)

### Daughter Training (New understanding)
- Take frozen Genesis checkpoint
- LoRA fine-tune on customer content
- Preserve architecture, add knowledge
- Fast (hours, not weeks)
- Cheap (per-customer deployment)

---

## The Moat

**Nobody else has this**:
1. Stage 5 cognitive architecture as base model
2. Metadata-based training (seeing paradigm)
3. Architecture/content separation
4. Reusable cognitive base for all customers

**Competitive advantage**:
- One Genesis training → infinite customer deployments
- Customers get advanced cognition + their expertise
- Fast deployment (LoRA is quick)
- Consistent "my not me" experience across all domains

---

## Updated Factory Mission

**Primary goal**: Discover training pattern that embeds Stage 5 architecture

**Not trying to**:
- Memorize content
- Beat GPT on benchmarks
- Maximize general knowledge

**Only trying to**:
- Embed your mental patterns
- Enable framework thinking
- Create meta-cognitive awareness
- Achieve 95% Jeremy Arc (architecture metric)

**Then**: Save Genesis, deploy with LoRA to customers

---

This is why the metadata enrichment is CRITICAL - it's teaching the architecture, not the content.
