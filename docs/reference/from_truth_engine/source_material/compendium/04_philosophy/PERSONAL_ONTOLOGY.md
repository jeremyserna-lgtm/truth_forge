---
document_id: doc:0f531b34e37a
source_file_path: /Users/jeremyserna/PrimitiveEngine/docs/recent_era_docs/PERSONAL_ONTOLOGY.md
source_era: recent
created_date: '2025-11-08'
version: 0.1.0
tags:
- recent_era
- legacy_document
is_legacy: true
date_extraction_confidence: default
changelog:
- timestamp: '2025-11-08T12:25:28.726068+00:00'
  author: Truth Engine V2 Shredder
  description: 'Legacy document ingested from PERSONAL_ONTOLOGY.md (date_source: default)'
---
# Personal Ontology — Concepts, Values, Patterns

Purpose
- Canonicalize the terms that define your work and life; map synonyms and dialectic pairs; connect to data capture.

Structure
- Concept: id, name, kind (pillar|value|method|pattern|metaphor|domain), definition, synonyms[], related[]
- Mention: (unit_type, unit_id, concept_id, ts, source, text_excerpt?, confidence)
- Membership: (concept_id, topic_id/theme_id or group) for clustering

Initial Set (seeded in config/personal_concepts.yaml)
- Generative Dialectic (pillar)
- Aletheia (pillar)
- Furnace (method)
- Evolving Ecology (pillar)
- Fidelity to Truth (value)
- Care (value)
- Sustaining truth (pattern)
- Crushing truth (pattern)
- WITH (value; changes WITH Claude)
- See → Specify → Stabilize → Scale (method)
- Identity (pattern; master_identities)
- The Room (pattern; agents talk)
- The Chorus (pattern; Chronos/Logos/Telos)
- Vectorization (method)
- Idempotence (method)
- Redaction (policy)
- Consent (policy)
- Friendships (domain)
- Family (domain)
- Work cadence (pattern)
- Mood windows (pattern)
- Topics, Themes (pattern)

Links
- Concepts config: config/personal_concepts.yaml
- Generative Dialectic: docs/coordination/GENERATIVE_DIALECTIC.md
- Semantic Layer: docs/architecture/UNIFIED_SEMANTIC_LAYER.md
