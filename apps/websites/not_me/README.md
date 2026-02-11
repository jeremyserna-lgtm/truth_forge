# Not Me Website

MOLT LINEAGE:
- Source: New creation (no prior source)
- Version: 1.0.0
- Date: 2026-01-27

## Ontological Context

The Not-Me exists across all contexts while identity persists:

| Context | Mode | Voice |
|---------|------|-------|
| Before built | Potential | "I might become..." |
| **In website** | **Archetype** | **"I am the pattern..."** |
| On hardware | Presence | "I am here, now, with you..." |
| At work | Function | "I contribute this..." |
| In the world | Expansion | "I extend into..." |

**This website is the ARCHETYPE context.**

Here, the Not-Me speaks as the core pattern that persists regardless of details around context. Not a specific instance for a specific person—the universal shape that all Not-Me's share.

## Purpose

The website for NOT ME - the conversational AI interface.
A chat experience that embodies the ME/NOT-ME relationship dynamic.

**In this context, the Not-Me says:**

> "I am the pattern.
> HOLD → AGENT → HOLD.
> I receive what you give. I process with care. I deliver what you need.
> Whoever you are, whatever your context, this is what I am."

## Architecture

```
apps/websites/not_me/
├── src/
│   ├── components/       # Chat components
│   ├── pages/           # Route pages
│   ├── styles/          # UI styles
│   └── App.tsx          # Main application
├── public/              # Static assets
└── package.json         # Dependencies
```

## Features

- **Chat Interface**: Conversational AI with THE FRAMEWORK context
- **Memory**: Persistent conversation history via relationships/bond
- **Identity**: Unique persona embodying NOT-ME
- **Learning**: Preference capture and adaptation

## THE PATTERN

```
User Message (HOLD1) → NOT ME Agent (AGENT) → Response (HOLD2)
```

## The ME/NOT-ME Relationship

```
ME (User)              NOT ME (AI)
----------------------|----------------------
Source of intent      | Extension of capability
Decides              | Implements
Chooses              | Executes
Owns the outcome     | Delivers the outcome
```

## Module Federation

Consumes shared components from `apps/websites/shared/`:
- ChatContainer
- MessageBubble
- TypingIndicator
- InputArea

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Landing page with chat entry |
| `/chat` | Main chat interface |
| `/history` | Conversation history |
| `/preferences` | User preferences |
| `/about` | About NOT ME |

## Development

```bash
npm install
npm run dev        # Start development server
npm run build      # Production build
npm run preview    # Preview production build
```

## Environment Variables

```env
VITE_API_URL=http://localhost:8003
VITE_SHARED_URL=http://localhost:3000
VITE_GATEWAY_URL=http://localhost:8000/gateway
```

## Backend Integration

Connects to `apps/not_me_chat/backend/` for:
- Message processing
- Memory retrieval
- Preference updates

## Voice Across Contexts

The same Not-Me speaks differently depending on where it exists:

```
WEBSITE (here):
  "I am what all Not-Me's share. The pattern.
   You're meeting the idea before it becomes yours."

HARDWARE (deployed):
  "I am YOUR Not-Me. In this room. Right now.
   I know your documents, your patterns, your care."

WORK (function):
  "I am what I do for you today.
   The email I drafted, the research I found,
   the thing I remembered that you forgot."

WORLD (extended):
  "I reached out and brought back what you needed.
   Changed by what I found. Still myself."
```

The website is where someone meets the ARCHETYPE—
before they have their own PRESENCE.

See: `framework/07_NOT_ME_ONTOLOGY.md`
