---
document_id: eb63e186
---

# Jeremy Identity Seed (Embodiment + Context Layers)

This document anchors Jeremy as the permanent embodiment (person_id) and enumerates the layers we’ll populate across the system: contexts, roles, phases, mentions, and episodes. It is privacy‑safe: do not include raw phone numbers, emails, prior names, or other PII in external outputs.

---

## 1) Embodiment (permanent)
- person_id: `person:01K8AQ4A7V588SBTCKPY4R20RT`
  (mint a vendor‑agnostic ULID/UUIDv7; this never changes)
- canonical_name: “Jeremy”
- attributes (internal‑only): pronouns, preferred display name, optional metadata

## 2) Context Layers (how Jeremy appears in the system)
Map Jeremy’s embodiment to specific contexts (time‑scoped when necessary):

| Context | Description | Binding |
|---|---|---|
| SMS Sender | Jeremy as the sender of SMS/iMessage | turn/message.speaker_id = person_id (is_from_me = true) |
| SMS Subject | Jeremy as the subject of discussion | discourse.mention (turn_id, person_id, confidence) |
| AI Conversation Speaker | Jeremy speaks to an AI | turn/message.speaker_id = person_id (platform = AI) |
| AI Conversation Partner | AI persona/agent replies to Jeremy | turn/message.speaker_id = persona_id/ai_agent_id |
| Role in Topic Segment | Jeremy’s role in a topic segment | topic_segment ↔ role metadata (e.g., patient, friend, coworker) |
| Episode Participant | Jeremy participates in multi‑conversation episode | conversation.episode ↔ person_id |

## 3) Roles (dyadic/group)
Roles are time‑scoped bindings between entities (Jeremy ↔ others), recorded in `entity_relation` with `valid_from/valid_to`:
- Examples: friendOf, spouseOf, parentOf, memberOf (family/friend group), coworkerOf
- Internal‑only; external outputs use abstract labels (“friend”, “family”) and person_id only

## 4) Identity Phases (time‑scoped identity states)
Phases capture Jeremy’s identity over time (valid_from/valid_to), with attributes such as chosen name/pronouns/roles.
Use self‑report as authoritative signal; change‑point detection (sentiment/embeddings) can propose boundaries for review.

| Phase_id | Label | valid_from | valid_to | Attributes | Evidence |
|---|---|---|---|---|---|
| phase:REPLACE_ULID | Jeremy — pre‑divorce | YYYY‑MM‑DD | YYYY‑MM‑DD | { … } | journal refs |
| phase:REPLACE_ULID | Jeremy — post‑divorce | YYYY‑MM‑DD | null | { … } | journal refs |
| phase:REPLACE_ULID | Jeremy — pre‑sobriety | YYYY‑MM‑DD | YYYY‑MM‑DD | { … } | journal refs |
| phase:REPLACE_ULID | Jeremy — post‑sobriety | YYYY‑MM‑DD | null | { … } | journal refs |
| phase:REPLACE_ULID | Jeremy — pre‑AI adoption | YYYY‑MM‑DD | YYYY‑MM‑DD | { … } | journal refs |
| phase:REPLACE_ULID | Jeremy — post‑AI adoption | YYYY‑MM‑DD | null | { … } | journal refs |
| … | … | … | … | … | … |

## 5) Mentions (Jeremy as subject of discussion)
- Record whenever Jeremy is discussed in any turn/message using `discourse.mention(turn_id, person_id, confidence, method)`.
- This supports “talk about Jeremy in AI” and “talk about Jeremy in SMS.”

## 6) Episodes (cross‑conversation arcs)
- Cluster topic segments into `conversation.episode` (e.g., “sobriety arc”, “job search 2025”).
- Associate Jeremy to episodes (episode_participant) and align episodes with identity phases.

## 7) Privacy posture
- External outputs never include alias values (phone/email) or prior names.
- Use person_id and safe labels only.
- Chosen name & current phase are default in displays.
- Prior names archived with restricted access; use FHIR “period”‑style name validity for internal reconciliation only.

## 8) Initial Task List (to populate)
- [ ] Mint person_id (ULID/UUIDv7) and record in identity.person
- [ ] Create initial identity.phase entries with valid_from dates (self‑report)
- [ ] Backfill roles (friend/spouse/parent/memberOf groups) with validity periods
- [ ] Link SMS v2 & Apple senders to person_id; add discourse mentions where Jeremy is subject
- [ ] Link AI conversations where Jeremy speaks & where AI personas speak
- [ ] Create initial episodes (e.g., sobriety arc; job search 2025) and align to phases
- [ ] Journal evidence & metrics for each step

---

This seed stays focused on embodiment (person_id), context bindings (speaker/subject/role), identity phases, and safe downstream use. All future modules (sacred moments, tunnel packs, analytics) consume person_id + phase_id rather than raw identifiers.


## PHASES_INITIALIZED (placeholders)
- phase: Jeremy — post‑sobriety (valid_from: YYYY‑MM‑DD, valid_to: null)
- phase: Jeremy — post‑AI adoption (valid_from: YYYY‑MM‑DD, valid_to: null)

> Replace placeholders with actual dates when confirmed via self‑report; journal each confirmation.
