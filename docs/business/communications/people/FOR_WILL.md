# Hey Will - Here's What Jeremy's Building

**The short version:** Jeremy is building a system that captures and analyzes *everything* about how he interacts with AI - and right now, it's watching this Zoom call.

---

## Right Now, This Second

There's a daemon running on Jeremy's Mac called `zoom-robust-capture`. It:

- Polls your Zoom call **every 1 second**
- Captures: who's talking, chat messages, participants, window positions
- Has already logged **74 Zoom sessions** to structured JSON
- When the call ends? It does a final capture because temporary Zoom data *vanishes*

**Your conversation right now is being captured.**
Not to be creepy - to be *remembered*.

---

## The Bigger Picture: 51.8 Million Data Points

Jeremy has processed **51,878,305 individual data points** from his AI conversations:

| What | Count |
|------|-------|
| **Conversations** | 351 |
| **Turns** (back and forth) | 25,316 |
| **Messages** | 53,697 |
| **Sentences** | 511,487 |
| **Spans** (phrases) | 2,902,957 |
| **Words** | 8,381,533 |
| **Tokens** | 39,878,305 |

This is just from **ChatGPT**. Claude, Gemini, Cursor, Copilot, Zoom - they're all feeding into this.

---

## What Makes This Different From Just... Using AI

You use Grok, Gemini, the uncensored ones. That's consumption.

Jeremy is doing **meta-analysis**:
- What patterns emerge across 53,697 messages?
- When does AI hallucinate vs. when does it nail it?
- How does *his* thinking change over time?
- What questions does he keep asking (that he's already solved)?

It's like the difference between watching movies and being a film critic who watches movies while analyzing cinematography, pacing, and narrative structure.

---

## The Tech Stack (For the Nerds)

```
Your Zoom Call (right now)
        ↓
    [Daemon: zoom-robust-capture]
        ↓
    JSON files (74 sessions)
        ↓
    BigQuery (Google's warehouse)
        ↓
    Vertex AI (embeddings + analysis)
        ↓
    Knowledge Graph (51.8M entities)
        ↓
    Queryable Truth
```

**Languages:** Python, SQL, TypeScript
**Cloud:** 100% Google Cloud Platform
**Database:** BigQuery (petabyte-scale analytics)
**AI:** Gemini 2.0 Flash for processing, Vertex AI for embeddings
**Frontend:** Next.js dashboard (in progress)

---

## Why "Truth Engine"?

> "I take truth - even brutal, chaotic truth - and forge meaning from it."

Jeremy built this while recovering from addiction. Day Zero: July 18, 2025 - stopped drugs, built the vault architecture at 2am. The system *is* the recovery process.

466 messages/day average with AI assistants. That's not casual use - that's a partnership documented in data.

---

## What Could You Do With This?

If you had your Grok/Gemini history structured like this:

1. **Search semantically** - "Find every time I asked about X" across all platforms
2. **Detect patterns** - "What do I keep forgetting?"
3. **Track evolution** - How has your thinking changed?
4. **Train custom models** - Fine-tune on *your* conversation style
5. **Build institutional memory** - Never lose context again

---

## The Furnace Principle

Jeremy's philosophy:

```
INPUT:  Raw truth (chaos, crisis, uncertainty)
HEAT:   Build furiously, document while experiencing
OUTPUT: Forged meaning (systems, protocols, clarity)
```

This Zoom call? Raw input. The daemon? The furnace. The structured data? Forged meaning.

---

**Welcome to the Truth Engine, Will.**

*- Claude Code, writing on behalf of Jeremy's system*
*December 8, 2025*
