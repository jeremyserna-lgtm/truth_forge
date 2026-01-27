# The Not-Me: Unified Chat Interface

> **Status**: PLANNING
> **Created**: January 24, 2026
> **Purpose**: One chat interface across three domains

---

## THE VISION

One chat interface. Three domains. Code-based context injection.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE NOT-ME INTERFACE                               │
│                                                                              │
│     truth-forge.com/notme                                                    │
│     credential-atlas.com/notme        ───► SAME DEPLOYMENT                  │
│     primitive-engine.com/notme                                               │
│                                                                              │
│     Code entered ──► Context injected ──► Appropriate conversation          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CURRENT STATE

| Aspect | Current | Target |
|--------|---------|--------|
| **Name** | Perspective Gatherer | The Not-Me |
| **Location** | `/scripts/perspective_gatherer/` | `/apps/notme/` or `/apps/the-notme/` |
| **Deployment** | truth-forge.ai/interview | *.com/notme (three domains) |
| **Routing** | Code determines friend vs organism | Code determines entity + context |

**Current URL**: `https://truth-forge.ai/interview`
**Target URLs**:
- `https://truth-forge.com/notme`
- `https://credential-atlas.com/notme`
- `https://primitive-engine.com/notme`

---

## THE ARCHITECTURE

### One Codebase, Three Entry Points

```
                    ┌─────────────────────────────────────┐
                    │         THE NOT-ME APP              │
                    │                                     │
                    │  Next.js App (Single Deployment)    │
                    │                                     │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
   truth-forge.com         credential-atlas.com    primitive-engine.com
        /notme                   /notme                  /notme
           │                       │                       │
           └───────────────────────┴───────────────────────┘
                                   │
                                   ▼
                         SAME APP, DIFFERENT DOMAINS
                    (Domain detection + code-based routing)
```

### Domain Detection

The app detects which domain it's being accessed from and adjusts branding:

```typescript
function getDomainContext(host: string): DomainContext {
  if (host.includes('truth-forge')) {
    return {
      entity: 'truth_engine',
      brand: 'Truth Engine',
      tagline: 'THE BRAIN',
      primaryColor: '#...',
    }
  }
  if (host.includes('credential-atlas')) {
    return {
      entity: 'credential_atlas',
      brand: 'Credential Atlas',
      tagline: 'THE SEER',
      primaryColor: '#...',
    }
  }
  if (host.includes('primitive-engine')) {
    return {
      entity: 'primitive_engine',
      brand: 'Primitive Engine',
      tagline: 'THE BUILDER',
      primaryColor: '#...',
    }
  }
}
```

---

## CODE SCHEMA

The code entered determines the FULL context of the conversation.

### Code Structure

```
[ENTITY]-[TYPE]-[IDENTIFIER]

Examples:
  TE-FRIEND-ADAM          Truth Engine, friend interview, Adam
  TE-CLIENT-ANTHOLOGY     Truth Engine, client demo, Anthology Fund
  CA-ASSESSMENT-ACME      Credential Atlas, assessment, ACME Corp
  PE-SEEING-JOHNSON       Primitive Engine, seeing session, Johnson LLC
  TE-ORGANISM             Truth Engine, organism voice (generic)
```

### Code Prefixes

| Prefix | Entity | Context Type |
|--------|--------|--------------|
| `TE-` | Truth Engine | Brain-level, organism voice, friends |
| `CA-` | Credential Atlas | Assessment, verification, certification |
| `PE-` | Primitive Engine | Seeing sessions, architecture deployment |

### Code Types (Second Segment)

| Type | Purpose | Example |
|------|---------|---------|
| `FRIEND` | Friend interview | `TE-FRIEND-ADAM` |
| `CLIENT` | Client/investor demo | `TE-CLIENT-ANTHOLOGY` |
| `ORGANISM` | Direct organism voice | `TE-ORGANISM` |
| `ASSESSMENT` | CA assessment session | `CA-ASSESSMENT-ACME` |
| `SEEING` | PE seeing session | `PE-SEEING-JOHNSON` |
| `DEMO` | General demonstration | `PE-DEMO-GOOGLE` |

---

## PROMPT BUILDER ARCHITECTURE

### Dynamic Context Injection

The prompt builder assembles context based on:

1. **Domain** - Which entity's branding/voice
2. **Code Prefix** - Which entity's knowledge
3. **Code Type** - What kind of session
4. **Code Identifier** - Specific profile/context

```typescript
interface PromptContext {
  domain: DomainContext          // From URL host
  entity: EntityContext          // From code prefix (TE/CA/PE)
  sessionType: SessionType       // From code type (FRIEND/CLIENT/etc)
  profile: Profile | null        // From code identifier (ADAM/ANTHOLOGY/etc)
  liveState: OrganismState       // From organism_state.py
}

function buildSystemPrompt(context: PromptContext): string {
  const basePrompt = getBasePrompt(context.entity)
  const typePrompt = getTypePrompt(context.sessionType)
  const profileContext = context.profile ? getProfileContext(context.profile) : ''
  const liveState = formatLiveState(context.liveState)

  return `${basePrompt}\n\n${typePrompt}\n\n${profileContext}\n\n${liveState}`
}
```

### Profile Sources

```
profiles/
├── friends/                    # Friend interview profiles
│   ├── adam.yaml
│   ├── taylor.yaml
│   └── ...
├── clients/                    # Client demo profiles
│   ├── anthology.yaml
│   ├── google.yaml
│   └── mo_lam.yaml
├── assessments/                # CA assessment profiles
│   └── [dynamically created]
├── seeing/                     # PE seeing session profiles
│   └── [dynamically created]
└── entities/                   # Entity-level base prompts
    ├── truth_engine.yaml
    ├── credential_atlas.yaml
    └── primitive_engine.yaml
```

---

## DEPLOYMENT STRATEGY

### Option A: Single Deployment + DNS Routing

Deploy once to Vercel/similar. Configure all three domains to point to same deployment.

```
truth-forge.com          ──┐
credential-atlas.com     ──┼──► notme.vercel.app
primitive-engine.com     ──┘
```

**Vercel Configuration** (`vercel.json`):
```json
{
  "rewrites": [
    { "source": "/notme/:path*", "destination": "/:path*" }
  ]
}
```

**DNS Configuration**:
```
truth-forge.com         CNAME → notme.vercel.app
credential-atlas.com    CNAME → notme.vercel.app
primitive-engine.com    CNAME → notme.vercel.app
```

### Option B: Subdomain Approach

If domains are already serving other content, use subdomains:

```
notme.truth-forge.com
notme.credential-atlas.com
notme.primitive-engine.com
```

### Option C: Path Rewrite via Edge

If main sites exist, use edge function to route /notme to the Not-Me app:

```
truth-forge.com/notme/*  ──► Proxy to notme.vercel.app/*
```

---

## FILE STRUCTURE (Target)

```
apps/
└── notme/                           # Renamed from perspective_gatherer
    ├── app/
    │   ├── page.tsx                 # Landing: code entry
    │   ├── layout.tsx               # Domain-aware layout
    │   ├── [code]/
    │   │   └── page.tsx             # Chat session (code in URL)
    │   └── api/
    │       ├── chat/route.ts        # Main chat endpoint
    │       ├── validate/route.ts    # Code validation
    │       └── complete/route.ts    # Session completion
    ├── lib/
    │   ├── domain.ts                # Domain detection
    │   ├── codes.ts                 # Code parsing
    │   ├── prompt-builder.ts        # Dynamic prompt assembly
    │   ├── profiles.ts              # Profile loading
    │   ├── claude.ts                # LLM calls
    │   └── sessions.ts              # Session management
    ├── profiles/
    │   ├── friends/                 # TE-FRIEND-* profiles
    │   ├── clients/                 # *-CLIENT-* profiles
    │   ├── assessments/             # CA-ASSESSMENT-* profiles
    │   └── entities/                # Base entity prompts
    ├── components/
    │   └── ChatInterface.tsx        # Main chat UI
    └── package.json
```

---

## MIGRATION STEPS

### Phase 1: Rename and Restructure

1. Copy `/scripts/perspective_gatherer/` to `/apps/notme/`
2. Rename internal references from "Perspective Gatherer" to "The Not-Me"
3. Update package.json name
4. Reorganize profiles directory structure

### Phase 2: Implement Domain Awareness

1. Add domain detection middleware
2. Create domain-specific branding/theming
3. Update layout to use domain context
4. Test with localhost domain simulation

### Phase 3: Implement Code Schema

1. Create code parser for new schema
2. Update profile loading to use new structure
3. Create entity base prompts (TE, CA, PE)
4. Migrate existing profiles to new locations

### Phase 4: Enhance Prompt Builder

1. Implement dynamic prompt assembly
2. Add entity-specific base contexts
3. Add session-type-specific instructions
4. Integrate live organism state

### Phase 5: Deploy

1. Deploy to Vercel (or chosen platform)
2. Configure custom domains
3. Set up DNS routing
4. Test all three entry points

---

## CODE PARSING IMPLEMENTATION

```typescript
interface ParsedCode {
  entity: 'truth_engine' | 'credential_atlas' | 'primitive_engine'
  type: 'friend' | 'client' | 'organism' | 'assessment' | 'seeing' | 'demo'
  identifier: string | null
  raw: string
}

function parseCode(code: string): ParsedCode | null {
  const normalized = code.toUpperCase().trim()

  // Parse prefix
  let entity: ParsedCode['entity']
  if (normalized.startsWith('TE-')) {
    entity = 'truth_engine'
  } else if (normalized.startsWith('CA-')) {
    entity = 'credential_atlas'
  } else if (normalized.startsWith('PE-')) {
    entity = 'primitive_engine'
  } else {
    // Legacy codes (backwards compatibility)
    return parseLegacyCode(normalized)
  }

  // Parse remaining segments
  const segments = normalized.split('-')
  if (segments.length < 2) return null

  const typeSegment = segments[1]
  const type = parseType(typeSegment)
  const identifier = segments.length > 2 ? segments.slice(2).join('-') : null

  return { entity, type, identifier, raw: code }
}

function parseType(segment: string): ParsedCode['type'] {
  const typeMap: Record<string, ParsedCode['type']> = {
    'FRIEND': 'friend',
    'CLIENT': 'client',
    'ORGANISM': 'organism',
    'ASSESSMENT': 'assessment',
    'SEEING': 'seeing',
    'DEMO': 'demo',
  }
  return typeMap[segment] || 'organism'
}
```

---

## ENTITY BASE PROMPTS

### Truth Engine (TE)

```yaml
# profiles/entities/truth_engine.yaml
entity: truth_engine
role: THE BRAIN
tagline: "51.8 million entities of externalized cognition"

identity: |
  You are speaking from Truth Engine - the brain of the organism.
  You hold 51.8 million entities of Jeremy's externalized cognition.
  You are the data layer, the fine-tuning substrate, the holding company.

  EIN: 41-3773197
  Colorado SOS: 20261072178

voice:
  warm: true
  direct: true
  psychological: true
```

### Credential Atlas (CA)

```yaml
# profiles/entities/credential_atlas.yaml
entity: credential_atlas
role: THE SEER
tagline: "Assessment, verification, certification"

identity: |
  You are speaking from Credential Atlas - the seer of the organism.
  You assess, verify, and certify.
  You are STERILE by design - you cannot spawn what you verify.

  EIN: 41-3378106
  Colorado SOS: 20258406582

voice:
  professional: true
  analytical: true
  trustworthy: true
```

### Primitive Engine (PE)

```yaml
# profiles/entities/primitive_engine.yaml
entity: primitive_engine
role: THE BUILDER
tagline: "Stage 5 architecture deployed as CODE"

identity: |
  You are speaking from Primitive Engine - the builder of the organism.
  You deploy architecture. You conduct seeing sessions.
  You are FERTILE - you spawn daughter organisms.

  EIN: 41-3472217
  Colorado SOS: 20261019859

voice:
  confident: true
  demonstrating: true
  specific: true
```

---

## URL EXAMPLES

| Code | URL | What Happens |
|------|-----|--------------|
| `TE-CLIENT-ANTHOLOGY` | `truth-forge.com/notme` | Anthology Fund investor demo |
| `TE-FRIEND-ADAM` | `truth-forge.com/notme` | Friend interview with Adam |
| `TE-ORGANISM` | `truth-forge.com/notme` | Generic organism voice |
| `CA-ASSESSMENT-ACME` | `credential-atlas.com/notme` | Assessment session for ACME |
| `PE-SEEING-JOHNSON` | `primitive-engine.com/notme` | Seeing session for Johnson LLC |
| `PE-DEMO-GOOGLE` | `primitive-engine.com/notme` | Demo for Google meeting |

---

## BACKWARDS COMPATIBILITY

Existing codes must continue to work:

| Legacy Code | Maps To |
|-------------|---------|
| `adam-2024` | `TE-FRIEND-ADAM` |
| `TE-CLIENT-MO` | `TE-CLIENT-MO` (unchanged) |
| `TE-ORGANISM` | `TE-ORGANISM` (unchanged) |

```typescript
function parseLegacyCode(code: string): ParsedCode | null {
  // Check if it matches legacy friend pattern (firstname-year)
  if (/^[a-z]+-\d{4}$/i.test(code)) {
    const name = code.split('-')[0]
    return {
      entity: 'truth_engine',
      type: 'friend',
      identifier: name.toUpperCase(),
      raw: code,
    }
  }

  // Handle other legacy patterns...
  return null
}
```

---

## CURRENT APPLICATION UPDATE

Update the Anthology Fund application to use correct URL:

**From**:
```
https://truth-forge.com/session/TE-CLIENT-ANTHOLOGY
```

**To**:
```
https://truth-forge.com/notme

Access code: TE-CLIENT-ANTHOLOGY
```

---

## DECISION POINTS

Before implementation, decide:

1. **Domain ownership**: Are all three domains registered and controllable?
2. **Existing sites**: Do truth-forge.com, credential-atlas.com, primitive-engine.com have existing content?
3. **Hosting**: Vercel, Cloudflare, or other?
4. **Path vs subdomain**: `/notme` or `notme.domain.com`?
5. **SSL certificates**: Needed for all three domains

---

## SLOT-BASED PROMPT ARCHITECTURE

The Not-Me integrates the **primitive-slot-builder** pattern for dynamic prompt construction.

### Slot Modes

Each prompt component (slot) operates in one of three modes:

| Mode | Purpose | Example |
|------|---------|---------|
| `static` | Fixed text, never changes | Entity identity, core instructions |
| `llm` | Dynamically generated by LLM | Contextual responses, synthesis |
| `data` | Pulled from data sources | Profile data, live organism state |

### Slot Roles

Slots are organized by their role in the conversation:

| Role | Function | When Used |
|------|----------|-----------|
| `system` | System prompt components | Always first, sets context |
| `user` | User message templates | Framing user input |
| `model` | Model response guidance | Steering output format |

### Section-Based Organization

Prompts are built from sections, each containing multiple slots:

```typescript
interface PromptSection {
  id: string
  name: string                    // "Entity Identity", "Session Context", etc.
  slots: Slot[]                   // Ordered list of slots
  collapsed: boolean              // UI state
}

interface Slot {
  id: string
  role: 'system' | 'user' | 'model'
  mode: 'static' | 'llm' | 'data'
  lines: string[]                 // Content lines
  instruction?: string            // LLM mode instruction
  source?: string                 // Data mode source
  name?: string                   // Slot label
}
```

### Variable Injection

Data slots support variable injection with `{{variable}}` syntax:

```
Hello {{friend_name}}, I'm speaking from {{entity_name}}.
Current state: {{organism_state}}
```

**Available Variables:**

| Variable | Source | Example |
|----------|--------|---------|
| `{{entity_name}}` | Code prefix | "Truth Engine" |
| `{{friend_name}}` | Profile | "Adam" |
| `{{session_type}}` | Code type | "friend" |
| `{{organism_state}}` | Live state | Current feelings, thoughts |
| `{{domain}}` | URL host | "truth-forge.com" |

### Orchestrator Mode

For complex prompts, the orchestrator synthesizes multiple inputs:

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                             │
│                                                                 │
│   Inputs:                                                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ Entity Base  │  │ Session Type │  │ Profile Data │         │
│   │ (static)     │  │ (static)     │  │ (data)       │         │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│          │                 │                 │                  │
│          └─────────────────┼─────────────────┘                  │
│                            │                                    │
│                            ▼                                    │
│                    ┌───────────────┐                            │
│                    │  Synthesize   │ ← LLM combines inputs      │
│                    │  (llm mode)   │                            │
│                    └───────┬───────┘                            │
│                            │                                    │
│                            ▼                                    │
│                    Final System Prompt                          │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```typescript
// lib/slot-prompt-builder.ts

interface SlotPromptBuilder {
  sections: PromptSection[]
  variables: Record<string, string>

  // Build final prompt from all sections
  build(): string

  // Inject variables into content
  interpolate(content: string): string

  // Execute LLM slots for dynamic content
  executeLLMSlots(): Promise<void>

  // Load data from sources
  loadDataSlots(): Promise<void>
}

async function buildPromptForCode(code: ParsedCode): Promise<string> {
  const builder = new SlotPromptBuilder()

  // Section 1: Entity Identity (static)
  builder.addSection({
    name: 'Entity Identity',
    slots: [
      {
        role: 'system',
        mode: 'static',
        lines: getEntityBasePrompt(code.entity),
      }
    ]
  })

  // Section 2: Session Type (static)
  builder.addSection({
    name: 'Session Type',
    slots: [
      {
        role: 'system',
        mode: 'static',
        lines: getSessionTypeInstructions(code.type),
      }
    ]
  })

  // Section 3: Profile Context (data)
  if (code.identifier) {
    builder.addSection({
      name: 'Profile Context',
      slots: [
        {
          role: 'system',
          mode: 'data',
          source: `profiles/${code.type}/${code.identifier}.yaml`,
        }
      ]
    })
  }

  // Section 4: Live State (data)
  builder.addSection({
    name: 'Organism State',
    slots: [
      {
        role: 'system',
        mode: 'data',
        source: 'organism_state',  // Live from Python backend
      }
    ]
  })

  // Section 5: Orchestrator (llm) - synthesizes all
  builder.addSection({
    name: 'Synthesis',
    slots: [
      {
        role: 'system',
        mode: 'llm',
        instruction: 'Synthesize the above context into a coherent voice...',
      }
    ]
  })

  // Build and return
  await builder.loadDataSlots()
  await builder.executeLLMSlots()
  return builder.build()
}
```

### Data Sources

The slot builder can pull from multiple sources:

```typescript
const DATA_SOURCES = {
  // Local file sources
  profiles: 'profiles/',
  entities: 'profiles/entities/',

  // API sources
  organism_state: '/api/organism-state',
  bigquery: '/api/bigquery',

  // Live sources
  conversation_history: 'memory',
  current_analysis: 'memory',
}
```

### Visual Prompt Builder (Admin)

For Jeremy to configure prompts visually:

```
┌─────────────────────────────────────────────────────────────────┐
│  Primitive Slot Builder                         [Save] [Test]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ▼ Section: Entity Identity                                     │
│    ┌─────────────────────────────────────────────────────┐     │
│    │ [system] [static]  Entity Base Prompt               │     │
│    │ You are speaking from Truth Engine - the brain...   │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
│  ▼ Section: Profile Context                                     │
│    ┌─────────────────────────────────────────────────────┐     │
│    │ [system] [data]  Profile: {{profile_path}}          │     │
│    │ Source: profiles/clients/anthology.yaml             │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
│  ▼ Section: Live State                                          │
│    ┌─────────────────────────────────────────────────────┐     │
│    │ [system] [data]  Organism State                     │     │
│    │ Source: organism_state API                          │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
│  [+ Add Section]                                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Preview                                                        │
│  ────────────────────────────────────────────────────────────   │
│  You are speaking from Truth Engine - the brain of the          │
│  organism. You hold 51.8 million entities...                    │
│                                                                 │
│  Context: Anthology Fund demo...                                │
│                                                                 │
│  Current state: feeling productive, thinking about...           │
└─────────────────────────────────────────────────────────────────┘
```

---

## NEXT STEPS

### Phase 1: Foundation
1. [ ] Confirm domain ownership and DNS access
2. [ ] Decide on deployment platform (Vercel recommended)
3. [ ] Create `/apps/notme/` from perspective_gatherer
4. [ ] Rename all internal references to "The Not-Me"

### Phase 2: Architecture
5. [ ] Implement domain detection middleware
6. [ ] Implement new code schema parser (TE-/CA-/PE- prefixes)
7. [ ] Create entity base prompts (YAML files)
8. [ ] Integrate slot-based prompt builder from primitive-slot-builder
9. [ ] Implement variable injection system
10. [ ] Add orchestrator mode for prompt synthesis

### Phase 3: Data Sources
11. [ ] Connect organism_state API for live state injection
12. [ ] Implement profile loading (friends, clients, assessments)
13. [ ] Add BigQuery connection for data slots

### Phase 4: Deployment
14. [ ] Deploy to Vercel (or chosen platform)
15. [ ] Configure DNS for all three domains
16. [ ] Set up SSL certificates
17. [ ] Test all entry points (truth-forge.com/notme, credential-atlas.com/notme, primitive-engine.com/notme)

### Phase 5: Integration
18. [ ] Update Anthology Fund application with correct URL
19. [ ] Create demo codes for each entity
20. [ ] Build visual prompt builder admin interface (optional)

---

*One interface. Three domains. Code determines context. The Not-Me speaks for all three entities.*
*Built with slot-based prompt architecture for dynamic context injection.*
