# Module Federation Templates

Industry-standard configuration for sharing the NOT-ME chat component across all truth_forge websites.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MODULE FEDERATION ARCHITECTURE                        │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    NOT-ME CHAT (Remote)                          │   │
│   │                    apps/not_me_chat/                             │   │
│   │                                                                  │   │
│   │   Exposes:                                                       │   │
│   │   - ./Chat         Main chat component                          │   │
│   │   - ./ChatProvider State management                             │   │
│   │   - ./useChat      Chat hook                                    │   │
│   │   - ./useLearning  Learning persistence hook                    │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│              ┌───────────────┼───────────────┬───────────────┐          │
│              ▼               ▼               ▼               ▼          │
│   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│   │ truth-forge  │ │ credential-  │ │   not-me     │ │  primitive-  │  │
│   │     .ai      │ │   atlas.ai   │ │     .ai      │ │  engine.ai   │  │
│   │              │ │              │ │              │ │              │  │
│   │ (Host/       │ │ (Host/       │ │ (Host/       │ │ (Host/       │  │
│   │  Consumer)   │ │  Consumer)   │ │  Consumer)   │ │  Consumer)   │  │
│   └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘  │
│                                                                          │
│   Shared: React (singleton), React-DOM (singleton)                      │
│   Learning: Persisted across all sites via central API                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `not_me_chat.next.config.js` | Remote configuration for NOT-ME chat |
| `website.next.config.js` | Consumer template for websites |

## Setup

### 1. NOT-ME Chat (Remote)

Copy `not_me_chat.next.config.js` to `apps/not_me_chat/next.config.js`:

```bash
cp apps/templates/module-federation/not_me_chat.next.config.js apps/not_me_chat/next.config.js
```

Install Module Federation:

```bash
cd apps/not_me_chat
npm install @module-federation/nextjs-mf
```

### 2. Website (Consumer)

Copy and customize `website.next.config.js` for each website:

```bash
# For truth-forge.ai
cp apps/templates/module-federation/website.next.config.js apps/websites/truth_forge/next.config.js
# Update name: 'truth_forge_website'

# For credential-atlas.ai
cp apps/templates/module-federation/website.next.config.js apps/websites/credential_atlas/next.config.js
# Update name: 'credential_atlas_website'

# etc.
```

## Usage in Websites

### Basic Usage

```tsx
import dynamic from 'next/dynamic';

const NotMeChat = dynamic(
  () => import('not_me_chat/Chat'),
  { ssr: false, loading: () => <div>Loading chat...</div> }
);

export default function Page() {
  return <NotMeChat siteId="truth-forge" />;
}
```

### With Provider

```tsx
import { ChatProvider } from 'not_me_chat/ChatProvider';

function App({ children }) {
  return (
    <ChatProvider
      config={{
        siteId: 'truth-forge',
        learningEnabled: true,
      }}
    >
      {children}
    </ChatProvider>
  );
}
```

### Using Hooks

```tsx
import { useChat } from 'not_me_chat/useChat';
import { useLearning } from 'not_me_chat/useLearning';

function CustomChatUI() {
  const { messages, sendMessage, isLoading } = useChat();
  const { learnings, addLearning } = useLearning();

  // Build custom UI with shared state
}
```

## TypeScript Support

Add to `next-env.d.ts` or a global declaration file:

```typescript
declare module 'not_me_chat/Chat' {
  import { ComponentType } from 'react';

  interface ChatProps {
    siteId: string;
    userId?: string;
    onMessage?: (message: Message) => void;
    className?: string;
  }

  const Chat: ComponentType<ChatProps>;
  export default Chat;
}

declare module 'not_me_chat/ChatProvider' {
  import { ComponentType, ReactNode } from 'react';

  interface ChatProviderProps {
    config: {
      siteId: string;
      learningEnabled?: boolean;
      apiEndpoint?: string;
    };
    children: ReactNode;
  }

  export const ChatProvider: ComponentType<ChatProviderProps>;
}

declare module 'not_me_chat/useChat' {
  export function useChat(): {
    messages: Message[];
    sendMessage: (content: string) => Promise<void>;
    isLoading: boolean;
  };
}

declare module 'not_me_chat/useLearning' {
  export function useLearning(): {
    learnings: Learning[];
    addLearning: (learning: Learning) => void;
    syncLearnings: () => Promise<void>;
  };
}
```

## Learning Persistence

The NOT-ME chat persists learnings across all site deployments:

```
Site A (truth-forge.ai)          Site B (not-me.ai)
        │                                │
        │ ┌────────────────────────────┐ │
        └─►   Central Learning API    ◄─┘
          │   (DuckDB + BigQuery)     │
          │                            │
          │   hold1/: Learning events  │
          │   hold2/: Queryable store  │
          └────────────────────────────┘
```

Environment variables:

```env
LEARNING_API_URL=https://api.truth-forge.ai/learning
ENABLE_LEARNING_SYNC=true
```

## Deployment

### Development

```bash
# Start NOT-ME chat remote (port 3001)
cd apps/not_me_chat && npm run dev -- -p 3001

# Start website (port 3000)
cd apps/websites/truth_forge && npm run dev
```

### Production

1. Deploy NOT-ME chat to `chat.truth-forge.ai`
2. Update remote URLs in website configs
3. Deploy websites to their respective domains

## References

- [Module Federation Documentation](https://module-federation.io/)
- [Next.js Module Federation](https://github.com/module-federation/nextjs-mf)
- [RESEARCH_FINDINGS.md](../../../RESEARCH_FINDINGS.md) - Industry standards
- [WEB_ARCHITECTURE.md](../../../docs/WEB_ARCHITECTURE.md) - Architecture details

---

*One component, four sites, unified learning.*
