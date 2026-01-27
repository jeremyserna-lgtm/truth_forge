---
document_id: 767bc77d
source_file_path: /Users/jeremyserna/PrimitiveEngine/docs/recent_era_docs/INTERVIEW_DEMO_VISION.md
source_era: recent
created_date: '2025-10-25'
version: 0.1.0
tags:
- recent_era
- legacy_document
is_legacy: true
date_extraction_confidence: content
changelog:
- timestamp: '2025-11-08T12:25:29.399782+00:00'
  author: Truth Engine V2 Shredder
  description: 'Legacy document ingested from INTERVIEW_DEMO_VISION.md (date_source:
    content)'
---

# Interview Demo Vision

**Date**: 2025-10-25
**Purpose**: Live interview demonstration system - ingest company data + personal data → Gemini 2.5 Pro reasoning
**Status**: Vision defined, building toward this

---

## The Vision

**The Demo**:

Walk into an interview and say:

> "Let me show you this system. What's your website? Found your job posting. Let me grab your Wikipedia page. Here's what happens: I put your company data into my system, it mixes with my personal data, and we send it to Gemini 2.5 Pro—a super-powered reasoning engine. Now you can ask it any question. Ask if I'd do a good job. Ask if I'd succeed. Ask if I'd help drive change. It won't lie to you."

**Live flow**:
1. Interviewer gives: Company website, job posting URL, company Wikipedia page
2. System ingests (real-time, <30 seconds):
   - Company website → sections (About, Mission, Products, Culture)
   - Job posting → sections (Responsibilities, Requirements, Benefits)
   - Wikipedia → sections (History, Products, Revenue, Leadership)
3. System mixes with personal data (already loaded):
   - Jeremy's conversations (7 platforms, enriched)
   - Jeremy's resume/experience
   - Jeremy's skills/projects
4. Send combined knowledge to **Gemini 2.5 Pro**
5. Live Q&A:
   - Interviewer: "Would he do a good job in this role?"
   - Pro reasons: Matches requirements, relevant experience, culture fit
   - Interviewer: "Would he succeed?"
   - Pro reasons: Track record, similar projects, growth potential
   - Interviewer: "Would he help drive change?"
   - Pro reasons: Innovation patterns, leadership, problem-solving

**Why this works**:
- NOT pre-canned answers
- NOT static analysis
- Gemini 2.5 Pro reasons over ACTUAL data (company + candidate)
- Live, transparent, verifiable
- "It won't lie to you" - grounded in real data

---

## Technical Requirements

### 1. Document Parser Enhancement (Markdown)

**What**: Parse markdown documents into sections using headers (# ## ###)

**Input**: Markdown file (job posting, resume, company page saved as .md)

**Output**: Sections with hierarchy

**Example**:
```markdown
# Software Engineer - Data Platform

## About the Role
We're looking for...

## Responsibilities
- Build data pipelines
- Optimize query performance
- Collaborate with data scientists

## Requirements
### Must Have
- 5+ years Python
- SQL expertise

### Nice to Have
- BigQuery experience
- ML pipeline knowledge

## Benefits
- Competitive salary
- Remote work
- Health insurance
```

**Parsed sections**:
```json
[
  {
    "section_id": "sec_001",
    "heading": "Software Engineer - Data Platform",
    "level": 1,
    "section_path": "Software Engineer - Data Platform",
    "text": "(all content under this heading)"
  },
  {
    "section_id": "sec_002",
    "heading": "About the Role",
    "level": 2,
    "section_path": "Software Engineer - Data Platform>About the Role",
    "text": "We're looking for..."
  },
  {
    "section_id": "sec_003",
    "heading": "Responsibilities",
    "level": 2,
    "section_path": "Software Engineer - Data Platform>Responsibilities",
    "text": "- Build data pipelines\n- Optimize query performance\n- Collaborate with data scientists"
  },
  {
    "section_id": "sec_004",
    "heading": "Requirements",
    "level": 2,
    "section_path": "Software Engineer - Data Platform>Requirements",
    "text": "(all subsections)"
  },
  {
    "section_id": "sec_005",
    "heading": "Must Have",
    "level": 3,
    "section_path": "Software Engineer - Data Platform>Requirements>Must Have",
    "text": "- 5+ years Python\n- SQL expertise"
  },
  {
    "section_id": "sec_006",
    "heading": "Nice to Have",
    "level": 3,
    "section_path": "Software Engineer - Data Platform>Requirements>Nice to Have",
    "text": "- BigQuery experience\n- ML pipeline knowledge"
  },
  {
    "section_id": "sec_007",
    "heading": "Benefits",
    "level": 2,
    "section_path": "Software Engineer - Data Platform>Benefits",
    "text": "- Competitive salary\n- Remote work\n- Health insurance"
  }
]
```

**Storage**: Each section → `spine.message` with `document_id` FK

**Enrichment**: Run baseline enrichment on each section:
- VADER sentiment (e.g., "Benefits" might be positive)
- KeyBERT keywords (e.g., "Requirements>Must Have" extracts Python, SQL)
- SBERT embedding (for semantic matching)

---

### 2. Web Content Parser (URL Ingester)

**What**: Fetch content from URLs and intelligently extract sections

**Inputs**: URLs from various sources

**Sources**:
1. **Company websites** (e.g., anthropic.com/about)
   - Extract: About, Mission, Products, Culture, Team
2. **LinkedIn job postings**
   - Extract: Job title, Responsibilities, Requirements, Benefits
3. **LinkedIn company pages**
   - Extract: About, Employees, Jobs, Culture
4. **Wikipedia pages**
   - Extract: Sections by heading (History, Products, Revenue, etc.)
5. **Generic web pages**
   - Extract: Any semantically meaningful sections

**Challenges**:
- **HTML structure varies** across sites
- **No standard section markers** (unlike markdown headers)
- **Need intelligent section detection**

**Approach**:

**Option 1: HTML heading extraction** (like markdown)
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
sections = []
for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
    # Extract heading text
    # Extract content between this heading and next
    # Create section object
```

**Option 2: Semantic section detection** (LLM-based)
```python
# Send HTML to Gemini Flash
prompt = """
Extract sections from this web page. For each section, provide:
- Section title
- Section content
- Section type (about, responsibilities, requirements, benefits, history, etc.)
"""
# Gemini Flash returns structured sections
```

**Option 3: Hybrid** (HTML structure + LLM refinement)
- Extract candidate sections via HTML headings
- Use LLM to categorize/merge/split sections
- Output clean section structure

**Output format**: Same as markdown parser (sections with hierarchy)

**Storage**: Same as markdown (sections → `spine.message`)

**Enrichment**: Same baseline enrichment

---

### 3. Section-Level Enrichment for Demo

**Why section-level matters for interview demo**:

**Scenario 1: "Would he do a good job?"**
- Pro needs to match:
  - Job posting "Requirements>Must Have" section (Python, SQL)
  - Jeremy's conversations about Python/SQL projects
  - Jeremy's resume "Experience" section (specific projects)
- Section-level enrichment enables precise matching

**Scenario 2: "Would he succeed?"**
- Pro needs to analyze:
  - Company Wikipedia "History" section (growth trajectory)
  - Job posting "Responsibilities" section (what success looks like)
  - Jeremy's conversations about similar challenges
  - Jeremy's resume "Accomplishments" section
- Section-level granularity shows track record in similar contexts

**Scenario 3: "Would he help drive change?"**
- Pro needs to compare:
  - Company website "Mission/Values" section (what change they want)
  - Jeremy's conversations about innovation/leadership
  - Jeremy's resume "Projects" section (examples of driving change)
- Section-level embeddings enable semantic similarity matching

---

## Architecture: Personal Data + Company Data → Pro

### Data Sources

**Personal Data** (already in system):
1. **Conversations** (7 AI platforms)
   - Enriched at: conversation + message levels
   - Contains: Technical discussions, problem-solving, projects, skills
2. **Resume/Experience** (markdown document)
   - Enriched at: document + section levels
   - Sections: Summary, Experience, Education, Skills, Projects
3. **SMS messages** (future)
   - Enriched at: conversation + message levels
   - Contains: Personal communication patterns

**Company Data** (ingested live during demo):
1. **Company website** (URL → sections)
   - Sections: About, Mission, Products, Culture, Values
2. **Job posting** (URL → sections)
   - Sections: Title, Responsibilities, Requirements, Benefits
3. **Company Wikipedia** (URL → sections)
   - Sections: History, Products, Revenue, Leadership, Controversies

---

### Gemini 2.5 Pro Integration

**How Pro reasons**:

1. **Retrieval** (find relevant data):
   - Question: "Would he do a good job?"
   - Retrieve:
     - Job posting "Requirements" section (embedding search)
     - Jeremy's conversations about those skills (keyword + embedding search)
     - Jeremy's resume "Experience" section (embedding similarity)

2. **Reasoning** (analyze + synthesize):
   - Compare requirements vs. experience
   - Identify matches, gaps, transferable skills
   - Assess cultural fit (company values vs. conversation patterns)
   - Evaluate growth potential (learning trajectory from conversations)

3. **Response** (answer with evidence):
   - "Yes, he would do a good job. Here's why:"
   - Evidence 1: Job requires Python expertise → 15 conversations about Python projects
   - Evidence 2: Job requires data pipeline experience → Resume shows 3 years building pipelines
   - Evidence 3: Company values collaboration → Conversations show strong collaborative patterns

**Why this isn't lying**:
- All evidence is REAL (grounded in actual data)
- All reasoning is TRANSPARENT (Pro explains its logic)
- All claims are VERIFIABLE (interviewer can ask follow-up questions)

---

## Implementation Plan

### Phase 1: Sentence Extraction + Section Grouping (NOW)

**What**: Extract sentences from documents, group by heading → sections

**Jeremy's insight**: "If you already grab sentence, you can pretty much make it into anything. If we just start grabbing the basic elements, there's no reason why the parser can't grab word, can't grab sentence."

**Approach**:
1. **Extract sentences** from document (using spaCy sentence tokenizer)
2. **Identify headings** (markdown # ## ### or HTML h1 h2 h3)
3. **Group sentences by heading** → each group is a "section"
4. **Store**:
   - Document → `spine.document`
   - Sections (grouped sentences) → `spine.message` with `document_id`
   - Sentences → `spine.sentence` with `message_id` (section) or `document_id`
   - Words → `spine.word` with `sentence_id`

**Output**: Full hierarchy (document → section → sentence → word)

**Enrichment**: Can enrich at any level:
- Document-level: Overall sentiment, keywords, topics
- Section-level: Section sentiment, keywords, topics
- Sentence-level: Sentence sentiment
- Word-level: POS tags, lemmas

**Timeline**: 1-2 days (simpler than parsing sections directly)

**Test**: Parse Jeremy's resume → extract all sentences → group by heading

---

### Phase 2: URL Ingester (HTML to Sections)

**What**: Fetch URL → extract sections → store in spine

**Approach**: HTML heading extraction (h1, h2, h3) + basic cleanup

**Output**: Sections → `spine.message` with `document_id` FK

**Timeline**: 2-3 days

**Test**: Ingest Anthropic careers page → extract job postings → parse sections

---

### Phase 3: Gemini 2.5 Pro Query Interface

**What**: Send question + context (personal + company data) to Pro

**Input**:
- Question: "Would he do a good job?"
- Context: Job posting sections + Jeremy's conversations/resume

**Output**: Pro's reasoning + evidence

**Timeline**: 3-4 days

**Test**: Ask Pro to match Jeremy's skills to a real job posting

---

### Phase 4: Live Demo Workflow

**What**: End-to-end demo flow (URL → ingest → mix → query → answer)

**Flow**:
1. Input: Company website URL, job posting URL, Wikipedia URL
2. Ingest: Fetch + parse sections (30 seconds)
3. Mix: Combine with personal data (instant - already loaded)
4. Query: Send question to Pro
5. Answer: Pro responds with reasoning + evidence

**Timeline**: 1 week

**Demo-ready**: 2-3 weeks from now

---

## Success Criteria

**Demo is successful when**:

1. ✅ Interviewer can provide URLs (company site, job posting, Wikipedia)
2. ✅ System ingests in <30 seconds (fetch + parse + enrich)
3. ✅ System mixes company data with personal data seamlessly
4. ✅ Gemini 2.5 Pro can answer questions with evidence:
   - "Would he do a good job?" → Matches requirements to experience
   - "Would he succeed?" → Analyzes track record + growth potential
   - "Would he help drive change?" → Compares innovation patterns
5. ✅ All answers are grounded in REAL data (not hallucinated)
6. ✅ All reasoning is TRANSPARENT (Pro explains its logic)
7. ✅ Interviewer is impressed ("It won't lie to you")

---

## Key Technical Decisions

**1. Section = Message**
- In conversations: message = user/assistant message
- In documents: message = section (markdown heading or HTML section)
- Both enriched at 2 levels (thread + message)

**2. Flexible Section Detection**
- Markdown: Use headers (# ## ###)
- HTML: Use headings (h1 h2 h3) + semantic detection
- LLM fallback: If structure unclear, use Gemini Flash to extract sections

**3. Schema: `spine.message` with `document_id`**
- Sections stored as "messages" in spine
- `document_id` FK links section to parent document
- Enables unified enrichment (same pipeline for conversations + documents)

**4. Enrichment: Message-level baseline**
- VADER, KeyBERT, BERTopic, SBERT on every section
- Enables: Sentiment per section, keywords per section, semantic matching per section

---

## Next Steps

1. **Schema change** (5 minutes):
   - `ALTER TABLE spine.message ADD COLUMN document_id STRING;`

2. **Markdown section parser** (1-2 days):
   - Extract sections from markdown
   - Test on Jeremy's resume

3. **Document loader with sections** (1 day):
   - Load document + sections to BigQuery
   - Run enrichment on sections

4. **URL ingester prototype** (2-3 days):
   - Fetch URL → extract HTML sections
   - Test on Anthropic careers page

5. **Pro integration** (3-4 days):
   - Build query interface
   - Test on sample questions

6. **End-to-end demo** (1 week):
   - Polish workflow
   - Practice demo
   - **Ready for interview**

---

**Created**: 2025-10-25
**Vision By**: Jeremy
**Status**: Architecture defined, ready to build
**Timeline**: Demo-ready in 2-3 weeks
**Next**: Markdown section parser (can start now)
