# Two-Portal System - Quick Start

## Overview

Two portals for two purposes:

1. **Admin Portal** (`/admin/*`): For you to manage documents and process atoms
2. **Customer Portal** (`/customer/*`): For clients to sign up and chat with your Not-Me

---

## Setup

### 1. Environment Variables

Create `.env`:

```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# BigQuery (for truth_forge integration)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
BIGQUERY_PROJECT=truth-forge
BIGQUERY_DATASET=main

# Server
PORT=3000
NODE_ENV=development
```

### 2. Start Server

```bash
cd /Users/jeremyserna/truth_forge/apps/document-service
npm run dev
```

---

## Admin Portal (Your Document Management)

### Upload Document
```bash
curl -X POST http://localhost:3000/admin/upload \
  -F "file=@/path/to/document.txt"
```

Response:
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": "doc_1738104123456",
    "name": "document.txt",
    "size": 1234
  }
}
```

### Process Document (One-Click Atoms)
```bash
curl -X POST http://localhost:3000/admin/process/doc_1738104123456
```

This will:
1. Send document to Gemini
2. Extract knowledge atoms
3. Export to BigQuery `entities_unified`

Response:
```json
{
  "message": "Processing complete",
  "atomsCreated": 12,
  "atoms": [...]
}
```

### List Documents
```bash
curl http://localhost:3000/admin/documents
```

### List Atoms
```bash
curl http://localhost:3000/admin/atoms
```

### Get Stats
```bash
curl http://localhost:3000/admin/stats
```

---

## Customer Portal (Client Engagement)

### Sign Up
```bash
curl -X POST http://localhost:3000/customer/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "client@example.com", "name": "Jane Doe"}'
```

### Chat with Your Not-Me
```bash
curl -X POST http://localhost:3000/customer/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to understand my identity better",
    "sessionId": "session_12345"
  }'
```

Response:
```json
{
  "response": "That's a profound goal! Let me help you explore...",
  "sessionId": "session_12345"
}
```

### Get Conversation History
```bash
curl http://localhost:3000/customer/conversation/session_12345
```

---

## The Flywheel

```
Customer signs up
    ↓
Chats with YOUR Not-Me
    ↓
Learns about identity architecture
    ↓
Gets interested in their OWN Not-Me
    ↓
Becomes paying customer
    ↓
Eventually gets full Not-Me implementation
```

**Right now**: They can sign up and chat TODAY
**Future**: Their own architecture emerges

---

## Next Steps

1. **Test locally**: Upload a document, process it, verify BigQuery
2. **Test customer chat**: Have a conversation with your Not-Me
3. **Build simple UI** (optional): HTML forms for upload/chat
4. **Deploy**: Render, Railway, or wherever you want
5. **Start selling**: Get customers chatting!

The full consciousness architecture (meta-layers, furnace, temporal evolution) comes LATER when you have real users and data.

**Ship this. Get customers. Let the vision emerge.**
