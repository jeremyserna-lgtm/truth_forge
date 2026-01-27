# Spine Level Definitions (L5, L7, L8)

**Canonical definitions for entity_unified / spine hierarchy. Use these for pipeline implementation and analysis.**

---

## L8 = Conversations (Session ID Grouping)

**Definition:** L8 is the **conversation** level. One L8 entity per unique **session_id**.

- **How we construct L8:** Group all messages by `session_id`. Each distinct session = one L8 conversation.
- **Source:** `session_id` from Claude Code JSONL (or equivalent in other sources).
- **Parent:** L8 has no parent (`parent_id` NULL).
- **Denormalized:** `conversation_id` = L8 `entity_id`, carried to all levels below.

**Use in analysis:** Query by `conversation_id` to get everything in a conversation. Count L8s per source, track conversation length, etc.

---

## L7 = Auto-Compaction Boundaries

**Definition:** L7 is the **auto-compaction segment** level. Each **compact_boundary** or **microcompact_boundary** in the source = one L7 entity.

- **How we construct L7:** Detect messages with `subtype IN ('compact_boundary', 'microcompact_boundary')`. Each such marker starts a new L7 segment within an L8 conversation.
- **Source:** `subtype`, `compactMetadata`, `logicalParentUuid` from Claude Code JSONL.
- **Parent:** L7 parent = L8 (conversation).
- **Meaning:** "Which Claude" — each auto-compact creates a new context window / identity boundary within the same conversation.

**Use in analysis:** Compare behavior across compaction segments (e.g. Claude₁ vs Claude₂ within one conversation). Slice by `topic_segment_id` / `compaction_segment_id` (L7 entity_id).

---

## L6 = Turn (Full Interaction Round)

**Definition:** L6 is the **turn** level. A turn is a **full interaction round** (not 1:1 user-assistant exchange).

- **How we construct L6:** 
  - Turn starts: First user message (or first message if no user)
  - Turn includes: ALL consecutive user messages, then ALL assistant/thinking/tool messages
  - Turn ends: When we see a new user message (which starts the next turn)
- **What a turn contains:**
  - **Full set of user messages** for that turn (user can send multiple before Claude responds)
  - **Full set of assistant messages** for that turn (Claude can send multiple responses)
  - **Full set of thinking blocks** for that turn (Claude's internal reasoning)
  - Tool use/tool result pairs
- **Parent:** L6 parent = L8 (Conversation) or L7 (if auto-compact boundaries are used).
- **Children:** L5 messages (user + assistant + thinking) are children of L6 turns.

**Use in analysis:** Query by `turn_id` to get all messages in a turn. Count turns per conversation, measure turn length, etc.

---

## L5 = Message (User + Assistant + Thinking)

**Definition:** L5 is the **message** level. Each **user message**, **assistant message**, and **thinking block** is a **separate L5 entity**.

- **How we construct L5:** 
  - User messages → one L5 per user message (`role = 'user'`).
  - Assistant messages → one L5 per **visible text block** (`message_type = 'assistant'`).
  - Thinking blocks → one L5 per **thinking block** (`message_type = 'thinking'`).
- **Source:** Stage 1 extracts thinking blocks as separate records; `message_type` distinguishes user / assistant / thinking.
- **Parent:** L5 parent = L6 (Turn). **Messages are children of turns.**
- **Type field:** Use `l5_type` or `message_type` to distinguish:
  - `user` — user message
  - `assistant` — visible assistant text
  - `thinking` — internal reasoning (analyzed separately from visible answers)

**Use in analysis:** Filter by `message_type` or `l5_type` to analyze thinking vs. visible answers, user vs. assistant, etc. Matches spine and entity_unified; all L5s are queryable the same way.

---

## Summary

| Level | What it is           | How we construct it                          | Use in analysis                          |
|-------|----------------------|----------------------------------------------|------------------------------------------|
| **L8** | Conversation         | Group by `session_id`; one L8 per session    | Conversations, session-level metrics     |
| **L7** | Auto-compact segment | `subtype` = compact_boundary / microcompact  | "Which Claude," segment-level comparison |
| **L6** | Turn                 | Full interaction round (user set + assistant set + thinking set) | Turn-level analysis, conversation flow |
| **L5** | Message              | User + assistant + thinking (each separate); children of L6 | Thinking vs visible; role-based analysis |

These definitions align with the pipeline (Stages 5–7), entity_unified, and PIPELINE_CAPABILITIES.
