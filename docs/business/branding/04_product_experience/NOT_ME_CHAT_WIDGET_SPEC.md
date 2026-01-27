# NOT-ME Chat Widget Specification

**Version:** 1.0
**Created:** January 24, 2026
**Purpose:** One NOT-ME, embeddable anywhere, unified experience

---

## The Core Principle

**One brain. Many surfaces.**

Whether someone is on truthengine.com, credentialatlas.com, primitive-engine.com, or stage5mind.com - they talk to the SAME NOT-ME. It's Jeremy's externalized cognition, available everywhere.

The widget adapts its appearance to match each site's brand, but the intelligence, personality, and memory are unified.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NOT-ME SERVICE                          │
│              (Central API - Single Source)                  │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Brain     │  │  Memory     │  │  Knowledge Base     │ │
│  │  (Claude)   │  │  (History)  │  │  (Truth Engine)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                             │
│  Endpoint: api.truthengine.co/v1/chat                      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ WebSocket / REST
                              │
┌─────────────────────────────┼─────────────────────────────┐
│                    WIDGET LAYER                           │
│            (Embeddable JavaScript Component)              │
│                                                           │
│  • Loads via <script> tag                                │
│  • Reads brand config from site                          │
│  • Adapts colors, position, behavior                     │
│  • Handles conversation UI                               │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   truthengine.com    credentialatlas.com    stage5mind.com
   (Warm White)         (Steel Blue)           (Amber)
```

---

## Embedding the Widget

### Basic Embed (Minimal)

```html
<!-- NOT-ME Chat Widget -->
<script src="https://widget.truthengine.co/not-me.js"></script>
<script>
  NotMe.init({
    brand: 'truth-engine'  // or 'credential-atlas', 'primitive-engine', 'stage5-mind'
  });
</script>
```

### Full Configuration

```html
<script src="https://widget.truthengine.co/not-me.js"></script>
<script>
  NotMe.init({
    // Which brand context (affects greeting, expertise emphasis)
    brand: 'credential-atlas',

    // Position on screen
    position: 'bottom-right',  // bottom-right, bottom-left, or custom

    // Override brand colors (optional - defaults from brand)
    theme: {
      accent: '#4A6FA5',       // Brand accent color
      background: '#0D0D0D',   // Chat background
      text: '#F5F0E6',         // Text color
    },

    // Behavior
    autoOpen: false,           // Open chat on page load?
    greeting: null,            // Custom greeting (null = brand default)

    // Context passed to NOT-ME
    context: {
      page: window.location.pathname,
      referrer: document.referrer,
    }
  });
</script>
```

---

## Brand Configurations

Each brand has default settings that the widget applies automatically.

### Truth Engine (Holding Company)

```javascript
{
  brand: 'truth-engine',
  theme: {
    accent: '#F5F0E6',      // Warm White
    background: '#0D0D0D',
    text: '#F5F0E6',
    buttonBg: '#1A1A1A',
  },
  greeting: "Hello. How can I help you understand what we're building?",
  expertise: ['framework', 'vision', 'philosophy', 'all-brands'],
  voiceTone: 'authoritative',
}
```

### Primitive Engine (Builder)

```javascript
{
  brand: 'primitive-engine',
  theme: {
    accent: '#D4A853',      // Forge Gold
    background: '#0D0D0D',
    text: '#F5F0E6',
    buttonBg: '#1A1A1A',
  },
  greeting: "What are you building?",
  expertise: ['development', 'architecture', 'implementation', 'technical'],
  voiceTone: 'direct-technical',
}
```

### Credential Atlas (Verification)

```javascript
{
  brand: 'credential-atlas',
  theme: {
    accent: '#4A6FA5',      // Steel Blue
    background: '#0D0D0D',
    text: '#F5F0E6',
    buttonBg: '#1A1A1A',
  },
  greeting: "What would you like to verify or understand?",
  expertise: ['credentials', 'verification', 'assessment', 'seeing'],
  voiceTone: 'precise-analytical',
}
```

### Stage 5 Mind (Consumer)

```javascript
{
  brand: 'stage5-mind',
  theme: {
    accent: '#F59E0B',      // Amber
    background: '#0D0D0D',
    text: '#F5F0E6',
    buttonBg: '#1A1A1A',
  },
  greeting: "Hi! Who do you need today?",
  expertise: ['personal', 'relationships', 'growth', 'ai-companions'],
  voiceTone: 'warm-inviting',
}
```

---

## Widget UI Specification

### Closed State (Floating Button)

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                     [Website Content]                    │
│                                                          │
│                                                          │
│                                                          │
│                                                          │
│                                          ┌─────────┐    │
│                                          │   💬    │    │
│                                          │         │    │
│                                          └─────────┘    │
└──────────────────────────────────────────────────────────┘

Button:
- 56px × 56px circle
- Brand accent color background
- Chat icon (or custom icon)
- Subtle shadow
- Hover: slight scale (1.05)
```

### Open State (Chat Panel)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                     [Website Content]                   │
│                                                         │
│                                                         │
│                        ┌──────────────────────────────┐│
│                        │ ╳  Talk to Jeremy's NOT-ME   ││
│                        ├──────────────────────────────┤│
│                        │                              ││
│                        │  [Greeting message]          ││
│                        │                              ││
│                        │        [User message]        ││
│                        │                              ││
│                        │  [NOT-ME response]           ││
│                        │                              ││
│                        ├──────────────────────────────┤│
│                        │ Type a message...    [Send]  ││
│                        └──────────────────────────────┘│
└─────────────────────────────────────────────────────────┘

Panel:
- Width: 380px (desktop), 100% (mobile)
- Height: 520px (desktop), 85vh (mobile)
- Border-radius: 12px
- Background: --bg-primary (#0D0D0D)
- Border: 1px solid --border-subtle
```

### Header

```
┌──────────────────────────────────────────────────────────┐
│  ╳   Talk to Jeremy's NOT-ME                    [brand] │
└──────────────────────────────────────────────────────────┘

- Height: 48px
- Background: --bg-secondary (#1A1A1A)
- Close button (╳) left-aligned
- Title: "Talk to Jeremy's NOT-ME"
- Brand indicator (small logo or color dot) right-aligned
- Font: Inter, 14px, medium weight
```

### Message Bubbles

```
NOT-ME messages (left-aligned):
┌────────────────────────────────────────┐
│ Message text here that can wrap to     │
│ multiple lines as needed.              │
└────────────────────────────────────────┘
- Background: --bg-tertiary (#2D2D2D)
- Text: --text-primary
- Border-radius: 12px 12px 12px 4px
- Max-width: 85%
- Padding: 12px 16px

User messages (right-aligned):
                    ┌────────────────────┐
                    │ User message here  │
                    └────────────────────┘
- Background: Brand accent color (muted)
- Text: --text-primary
- Border-radius: 12px 12px 4px 12px
- Max-width: 85%
- Padding: 12px 16px
```

### Input Area

```
┌──────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────┐ ┌─────┐ │
│ │ Type a message...                           │ │ ➤  │ │
│ └─────────────────────────────────────────────┘ └─────┘ │
└──────────────────────────────────────────────────────────┘

- Input: Full width minus send button
- Background: --bg-secondary
- Border: 1px solid --border-subtle
- Border-radius: 8px
- Send button: 40px × 40px, brand accent
- Keyboard: Enter to send, Shift+Enter for newline
```

---

## API Specification

### Endpoint

```
POST https://api.truthengine.co/v1/chat
```

### Request

```json
{
  "message": "User's message here",
  "conversation_id": "uuid-or-null-for-new",
  "context": {
    "brand": "credential-atlas",
    "page": "/about",
    "referrer": "google.com",
    "user_id": "anonymous-or-identified"
  }
}
```

### Response

```json
{
  "response": "NOT-ME's response here",
  "conversation_id": "uuid",
  "metadata": {
    "escalate_to_jeremy": false,
    "suggested_actions": [],
    "confidence": 0.95
  }
}
```

### WebSocket (For Streaming)

```javascript
const ws = new WebSocket('wss://api.truthengine.co/v1/chat/stream');

// Send
ws.send(JSON.stringify({
  type: 'message',
  message: 'User message',
  conversation_id: 'uuid',
  context: { brand: 'truth-engine' }
}));

// Receive
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.type: 'token' | 'complete' | 'error'
  // data.content: string (partial or full response)
};
```

---

## Context Awareness

The NOT-ME receives context about where the conversation is happening. This affects:

### 1. Greeting

| Brand | Default Greeting |
|-------|------------------|
| Truth Engine | "Hello. How can I help you understand what we're building?" |
| Primitive Engine | "What are you building?" |
| Credential Atlas | "What would you like to verify or understand?" |
| Stage 5 Mind | "Hi! Who do you need today?" |

### 2. Expertise Emphasis

The NOT-ME has all knowledge but emphasizes different areas based on context:

| Brand | Primary Expertise |
|-------|-------------------|
| Truth Engine | Framework philosophy, vision, company overview |
| Primitive Engine | Technical implementation, architecture, building |
| Credential Atlas | Verification, assessment, credentials, seeing |
| Stage 5 Mind | Personal AI, relationships, NOT-ME companions |

### 3. Voice Calibration

| Brand | Voice Tone |
|-------|------------|
| Truth Engine | Authoritative, grounded, expansive |
| Primitive Engine | Direct, technical, builder mindset |
| Credential Atlas | Precise, analytical, clear |
| Stage 5 Mind | Warm, inviting, personal |

**Important:** These are calibrations, not different personalities. It's always Jeremy's NOT-ME - just emphasizing different facets based on where the person came from.

---

## Disclosure

The widget includes disclosure per NOT-ME Communication Standards:

### In Header or Footer

```
Powered by Jeremy's NOT-ME · AI Assistant
```

### On First Message

If the user asks "Are you AI?" or similar:
```
"Yes, I'm Jeremy's AI assistant. I have access to his context, knowledge, and
preferences. For complex decisions or commitments, I'll loop Jeremy in directly.
How can I help you?"
```

---

## Mobile Behavior

### Trigger Button
- Same position (bottom-right default)
- Same size (56px)
- Fixed position

### Chat Panel
- Full width (100vw)
- Height: 85vh (leaves room for mobile browser chrome)
- Slides up from bottom
- Close via X or swipe down
- Input adjusts for mobile keyboard

---

## Technical Implementation

### Recommended Stack

```
Widget (Frontend):
├── Preact or vanilla JS (tiny bundle ~15kb)
├── CSS-in-JS for isolation (no conflicts)
├── Shadow DOM for style encapsulation
└── WebSocket for real-time streaming

Service (Backend):
├── Vercel Edge Functions or Cloudflare Workers
├── Claude API (Anthropic)
├── PostgreSQL for conversation history
├── Redis for rate limiting
└── Vector DB for knowledge retrieval
```

### Bundle Size Target

```
not-me.js: < 25kb gzipped
- Core widget: ~15kb
- Styling: ~5kb
- Fonts: System fonts (no loading)
```

### Loading

```html
<!-- Async, non-blocking -->
<script async src="https://widget.truthengine.co/not-me.js"></script>
```

---

## Privacy & Data

### What's Stored

| Data | Storage | Retention |
|------|---------|-----------|
| Conversation history | PostgreSQL | 90 days |
| User identifier | Cookie/localStorage | Session or persistent |
| Page context | Not stored | Per-request only |

### What's NOT Stored

- IP addresses (not logged)
- Precise location
- Personal data unless volunteered in chat

### Disclosure Footer

```
Conversations are used to improve responses. See Privacy Policy.
```

---

## Integration with Truth Engine

The widget is a frontend for Truth Engine's intelligence:

```
Widget → API → Truth Engine Brain
                    │
                    ├── Knowledge Atoms (inhale)
                    ├── NOT-ME Communication Standards
                    ├── Brand Context
                    └── Jeremy's Voice
```

The NOT-ME can:
- Answer questions about any brand
- Schedule meetings (routes to calendar)
- Collect contact info (routes to CRM)
- Escalate to Jeremy (flags for review)

---

## Implementation Phases

### Phase 1: MVP
- [ ] Basic widget UI (button + panel)
- [ ] Single brand configuration
- [ ] REST API (no streaming)
- [ ] Simple Claude integration

### Phase 2: Full Widget
- [ ] All brand themes
- [ ] WebSocket streaming
- [ ] Mobile optimization
- [ ] Conversation history

### Phase 3: Intelligence
- [ ] Truth Engine knowledge integration
- [ ] Escalation logic
- [ ] Action handlers (schedule, contact)
- [ ] Cross-conversation memory

### Phase 4: Scale
- [ ] CDN distribution
- [ ] Edge deployment
- [ ] Analytics dashboard
- [ ] A/B testing greeting/behavior

---

## Files Created

| File | Purpose |
|------|---------|
| `NOT_ME_CHAT_WIDGET_SPEC.md` | This specification |
| Future: `widget/` | Widget source code |
| Future: `api/chat/` | Chat API endpoint |

---

*One NOT-ME. Every surface. Same brain, adapted appearance.*
