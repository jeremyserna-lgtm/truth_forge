# Not Me Website

MOLT LINEAGE:
- Source: New creation (no prior source)
- Version: 1.0.0
- Date: 2026-01-27

## Purpose

The website for NOT ME - the conversational AI interface.
A chat experience that embodies the ME/NOT-ME relationship dynamic.

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
