# Getting Started with Document Service

## What You Have Now

A **multi-tenant document management service** foundation with:
- ✅ Storage abstraction (local + Google Cloud)
- ✅ Type system for tenants, documents, knowledge atoms
- ✅ Conversational assistant ("Not_me") for dataset completeness
- ✅ Distillation service (document → atoms)
- ✅ Configuration for multiple deployment contexts

## Quick Start

### 1. Set Up Environment

```bash
cd apps/document-service
cp .env.example .env
```

Edit `.env`:
```bash
DEPLOYMENT_TYPE=personal
GEMINI_API_KEY=your-api-key-here
```

### 2. Start Development Server

```bash
npm run dev
```

Server starts on http://localhost:3001

### 3. Test Health Check

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "multiTenant": false
}
```

## Client UX Design (Your Feedback Incorporated)

### Screen 1: Chat (Primary)
**Simple by default** - just upload and talk to the AI:
```
┌─────────────────────────────────┐
│  Upload Your Documents          │
│  [Drag & Drop or Click]         │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  💬 Chat with your AI           │
│                                 │
│  User: How's my dataset?        │
│  AI: Looking good! You have...  │
└─────────────────────────────────┘
```

### Screen 2: Dashboard (Optional)
**Transparency when they want it**:
```
Documents (15)
├─ project_spec.pdf      [tagged: technical, architecture]
├─ meeting_notes.md      [tagged: planning, decisions]
└─ research.docx         [tagged: research, background]

Understanding Summary:
→ Topics: project planning (40%), technical specs (35%), research (25%)
→ Completeness: 62%
→ Suggestions: Consider adding examples of edge cases
```

**They can:**
- View what's been extracted/tagged
- Add their own tags
- See the system's understanding
- Upload more targeted content
- **Or just ignore this screen and chat**

## Next Implementation Steps

### 1. Complete OCR Pipeline
Add text extraction:
- Tesseract.js for images
- PDF parsing for documents
- Google Vision API for advanced cases

### 2. Connect Gemini API
Replace placeholder in:
- `src/core/distillation/index.ts`
- `src/core/conversational-assistant.ts`

### 3. Build API Routes
Implement:
- `POST /api/v1/documents` - Upload with OCR
- `GET /api/v1/documents` - List with metadata
- `POST /api/v1/documents/:id/distill` - Convert to atoms
- `POST /api/v1/chat` - Conversational interface

### 4. Client UI
Create React app (or extend knowledge-atomizer):
- Simple upload + chat screen
- Optional dashboard for transparency
- Mobile-friendly

### 5. Truth Forge Integration
Build connector to export atoms to `entities_unified`

## Architecture

```
document-service/
├── src/
│   ├── api/              # Express routes
│   ├── core/
│   │   ├── conversational-assistant.ts  # "Not_me" AI
│   │   ├── distillation/                # Document → Atoms
│   │   ├── ocr/                         # Text extraction
│   │   └── embeddings/                  # Vector generation
│   ├── storage/
│   │   └── adapters/
│   │       ├── local.ts                 # For personal use
│   │       └── gcs.ts                   # For production
│   └── config/
│       └── index.ts                     # Deployment configs
```

## Deployment Scenarios

### Personal Use (You)
```bash
DEPLOYMENT_TYPE=personal npm run dev
```
- Local storage
- Full features (operational + knowledge docs)
- Truth Forge sync enabled

### Client Portal (Multi-Tenant)
```bash
DEPLOYMENT_TYPE=client-portal npm start
```
- Cloud storage (GCS)
- Knowledge atoms only (for fine-tuning)
- Conversational assistant enabled
- No Truth Forge sync (client data stays isolated)

## What Makes This Different

**Traditional doc management**: Upload → Store → Search
**This system**: Upload → Understand → Converse → Fine-tune

Clients don't just store documents - they build training datasets through conversation.
