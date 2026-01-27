# Self-Improving Knowledge Extraction Loop

## 🎯 Core Concept - Knowledge Gap Signals

**Low-quality atoms are signals of KNOWLEDGE GAPS, not defects to fix.**

The key insight: Don't try to fix low-quality atoms by enriching existing documents.
Instead, accept them as signals of what knowledge we're missing, and create NEW
knowledge through projects, documents, analyses, and exploration in those areas.

Process:
1. **Extract** knowledge atoms from documents (quality doesn't matter)
2. **Assess** atom quality → identify knowledge gaps
3. **Analyze gaps** → What topics/themes have low-quality knowledge?
4. **Create new knowledge** → Projects, documents, analyses, exploration in gap areas
5. **Extract new atoms** → Now we have better knowledge naturally

**Philosophy**:
- Low-quality atoms = Knowledge we don't have yet
- Identify gaps → Create new knowledge → Get better atoms
- This is knowledge creation, not knowledge repair

## 🔄 The Loop - Improving Document Knowledge Quality

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENT                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  INITIAL EXTRACTION   │
         │  (LLM extracts atoms) │
         └───────────┬────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   QUALITY ASSESSMENT   │
         │  • Specificity?       │
         │  • Completeness?       │
         │  • Coherence?          │
         │  • Document issues?    │
         └───────────┬────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
   [Low Quality]        [High Quality]
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ IMPROVE DOCUMENT │    │   STORE ATOMS   │
│   KNOWLEDGE      │    │   (No action)   │
│                  │    └─────────────────┘
│  • Clarify vague │
│  • Complete      │
│  • Correct       │
│  • Add principles│
│  • Restructure   │
└────────┬─────────┘
         │
         ▼
┌───────────────────────┐
│    RE-EXTRACTION      │
│  Extract from improved │
│  document             │
└───────────┬───────────┘
            │
            ▼
    ┌───────────────┐
    │ STORE IMPROVED │
    │     ATOMS      │
    └───────────────┘
```

**Key Insight**: Low-quality atoms = Documents need knowledge improvement at the source.

## 📊 Assessment Criteria

### Atom Completeness Score

```python
def assess_atom_completeness(atom: Dict) -> Dict:
    """Assess how complete an atom's metadata is."""
    score = 0
    max_score = 100

    # Principles (20 points)
    if atom.get("principles") and len(atom["principles"]) > 0:
        score += 20

    # Entities (20 points)
    if atom.get("entities") and len(atom["entities"]) > 0:
        score += 20

    # Concepts (20 points)
    if atom.get("concepts") and len(atom["concepts"]) > 0:
        score += 20

    # Content richness (20 points)
    content_length = len(atom.get("content", ""))
    if content_length > 200:
        score += 20
    elif content_length > 100:
        score += 10

    # Domain/category (20 points)
    if atom.get("domain") and atom.get("category"):
        score += 20
    elif atom.get("domain") or atom.get("category"):
        score += 10

    completeness = score / max_score

    return {
        "score": score,
        "completeness": completeness,
        "needs_enrichment": completeness < 0.6,  # Threshold: 60%
        "missing": {
            "principles": not atom.get("principles") or len(atom["principles"]) == 0,
            "entities": not atom.get("entities") or len(atom["entities"]) == 0,
            "concepts": not atom.get("concepts") or len(atom["concepts"]) == 0,
            "rich_content": content_length < 100,
        }
    }
```

### Document-Level Assessment

```python
def assess_document_atoms(document_id: str) -> Dict:
    """Assess all atoms from a document."""
    atoms = get_atoms_for_document(document_id)

    assessments = [assess_atom_completeness(atom) for atom in atoms]

    avg_completeness = sum(a["completeness"] for a in assessments) / len(assessments)
    sparse_count = sum(1 for a in assessments if a["needs_enrichment"])

    return {
        "document_id": document_id,
        "atom_count": len(atoms),
        "avg_completeness": avg_completeness,
        "sparse_atoms": sparse_count,
        "needs_enrichment": avg_completeness < 0.6 or sparse_count > len(atoms) * 0.5,
        "missing_metadata": {
            "principles": sum(1 for a in assessments if a["missing"]["principles"]),
            "entities": sum(1 for a in assessments if a["missing"]["entities"]),
            "concepts": sum(1 for a in assessments if a["missing"]["concepts"]),
        }
    }
```

## 🔧 Enrichment Process - QUALITY-DRIVEN

### 🎯 Key Principle: Meaningful Metadata, Not Just Quantity

**Enrichment should add MEANINGFUL metadata, not just fill blanks.**

Before enriching, we assess:
1. **What does missing metadata mean?**
   - Missing principles → Document doesn't state them? Or extraction missed them?
   - Missing entities → Not named? Or extraction missed names?
   - Missing concepts → Not conceptualized? Or extraction missed framing?

2. **Signal Type Determines Action:**
   - **ENRICHMENT SIGNAL**: Content exists, extraction missed it → Re-extract or enrich document
   - **CORRECTION SIGNAL**: Atoms are wrong/contradictory → Knowledge needs correction
   - **CLARIFICATION SIGNAL**: Atoms are vague → Knowledge needs clarification
   - **COMPLETION SIGNAL**: Atoms are incomplete → Knowledge needs completion
   - **STRUCTURE SIGNAL**: Document structure needs improvement → Restructure document

### Enrichment Prompt - Quality-Focused

```python
ENRICHMENT_PROMPT = """
You are enriching a document to improve knowledge extraction QUALITY.

ORIGINAL DOCUMENT:
{document_text}

EXTRACTED KNOWLEDGE ATOMS:
{atoms_summary}

QUALITY ASSESSMENT:
{quality_signals}

SIGNAL TYPE: {signal_type}
  - ENRICHMENT: Content exists but extraction missed it → Add explicit annotations
  - CORRECTION: Atoms are wrong → Fix knowledge in document
  - CLARIFICATION: Atoms are vague → Clarify knowledge in document
  - COMPLETION: Atoms are incomplete → Complete knowledge in document

TASK (based on signal type):
{task_instructions}

GUIDELINES FOR ENRICHMENT:
- Only add metadata that is MEANINGFUL and ACCURATE
- Don't add generic principles/entities/concepts just to fill blanks
- If document genuinely lacks something, clarify WHY it's missing
- Preserve original meaning - enrichment should help extraction, not change knowledge
- Use natural annotations that fit document style
- Be specific, not generic

ENRICHED DOCUMENT:
"""
```

### What Metadata Gets Added

**MEANINGFUL Metadata:**
- Principles that are actually stated or implied in the document
- Entities that are actually mentioned (people, systems, tools)
- Concepts that are actually used (not generic "communication", "process")
- Context that clarifies vague or incomplete atoms
- Structure that makes knowledge more extractable

**NOT Added:**
- Generic principles just because they're missing
- Inferred entities that aren't actually mentioned
- Generic concepts to fill blanks
- Filler content to make atoms longer

### Enrichment Function

```python
def enrich_document_for_extraction(
    document_text: str,
    document_id: str,
    missing_metadata: Dict
) -> str:
    """Enrich document with missing metadata annotations."""

    # Get summary of extracted atoms
    atoms = get_atoms_for_document(document_id)
    atoms_summary = summarize_atoms(atoms)

    # Build enrichment prompt
    prompt = ENRICHMENT_PROMPT.format(
        document_text=document_text,
        atoms_summary=atoms_summary,
        missing_principles=missing_metadata.get("principles", []),
        missing_entities=missing_metadata.get("entities", []),
        missing_concepts=missing_metadata.get("concepts", []),
    )

    # Call LLM to enrich
    enriched_text = call_llm_enrichment(prompt)

    return enriched_text
```

## 🔄 Re-Extraction

After enrichment, re-extract knowledge atoms from the enriched document:

```python
def re_extract_from_enriched(
    enriched_document: str,
    original_document_id: str
) -> List[Dict]:
    """Re-extract atoms from enriched document."""

    # Use same extraction process as initial extraction
    enriched_atoms = extract_knowledge_atoms(enriched_document)

    # Link to original document
    for atom in enriched_atoms:
        atom["document_id"] = original_document_id
        atom["extraction_version"] = "enriched"
        atom["original_atom_id"] = None  # Will be matched/merged

    return enriched_atoms
```

## 🔗 Matching & Merging

Match enriched atoms to original atoms and merge:

```python
def match_and_merge_atoms(
    original_atoms: List[Dict],
    enriched_atoms: List[Dict]
) -> List[Dict]:
    """Match enriched atoms to originals and merge improvements."""

    merged = []

    for enriched_atom in enriched_atoms:
        # Try to match to original by content similarity
        best_match = find_best_match(enriched_atom, original_atoms)

        if best_match:
            # Merge: keep enriched metadata, preserve original ID
            merged_atom = {
                **best_match,  # Keep original structure
                "principles": enriched_atom.get("principles") or best_match.get("principles", []),
                "entities": enriched_atom.get("entities") or best_match.get("entities", []),
                "concepts": enriched_atom.get("concepts") or best_match.get("concepts", []),
                "content": enriched_atom.get("content") or best_match.get("content"),
                "extraction_version": "merged",
            }
            merged.append(merged_atom)
        else:
            # New atom from enrichment
            merged.append(enriched_atom)

    return merged
```

## 📈 Benefits

1. **Quality-Driven**: Focuses on meaningful metadata, not just quantity
2. **Signal-Aware**: Distinguishes between enrichment, correction, clarification
3. **Self-Improving**: Knowledge base gets better over time
4. **Targeted**: Only enriches documents that need it
5. **Efficient**: Rich documents skip enrichment
6. **Iterative**: Can run multiple enrichment cycles
7. **Intelligent**: Atoms themselves indicate what needs improvement AND how

## 🎯 What Metadata Gets Added

### Meaningful Metadata (What Enrichment Should Add)

**Principles:**
- Principles that are stated or implied in the document
- Specific principles, not generic ones
- Example: "audit trail principle" (from document about logging)

**Entities:**
- Entities that are mentioned in the document
- Named people, systems, tools, companies
- Specific entities, not generic types
- Example: "BigQuery" (not "database system")

**Concepts:**
- Concepts that are used in the document
- Specific concepts, not generic ones
- Example: "semantic similarity search" (not "search")

**Context:**
- Context that clarifies vague atoms
- Explanations that complete incomplete atoms
- Structure that makes knowledge extractable

### NOT Added (What Enrichment Should NOT Do)

❌ Generic principles just to fill blanks
❌ Inferred entities that aren't mentioned
❌ Generic concepts like "communication", "process"
❌ Filler content to make atoms longer

### Signal Types Determine Action

**ENRICHMENT SIGNAL**: Content exists, extraction missed it
- Action: Add explicit annotations to help extraction
- Example: Document mentions "BigQuery" but entity not extracted

**CORRECTION SIGNAL**: Atoms are wrong/contradictory
- Action: Fix knowledge in document, then re-extract
- Example: Atom says "Python" but document actually says "JavaScript"

**CLARIFICATION SIGNAL**: Atoms are vague/ambiguous
- Action: Clarify knowledge in document
- Example: Atom says "system" but document actually names specific system

**COMPLETION SIGNAL**: Atoms are incomplete fragments
- Action: Complete knowledge in document
- Example: Atom says "Thanks" without context of what was done

**STRUCTURE SIGNAL**: Document structure needs improvement
- Action: Restructure document for better extraction
- Example: Document lacks clear sections, making extraction difficult

## 🚀 Implementation Plan

1. **Phase 1**: Assessment function
   - Analyze atom completeness
   - Flag documents needing enrichment

2. **Phase 2**: Enrichment function
   - LLM-based document enrichment
   - Add missing metadata annotations

3. **Phase 3**: Re-extraction
   - Extract from enriched documents
   - Match and merge with originals

4. **Phase 4**: Integration
   - Add to document processing pipeline
   - Make it optional/configurable

## 🎯 Success Metrics

- **Completeness Score**: Average atom completeness increases
- **Metadata Coverage**: % of atoms with principles/entities/concepts
- **Content Richness**: Average content length increases
- **Enrichment Rate**: % of documents that benefit from enrichment
