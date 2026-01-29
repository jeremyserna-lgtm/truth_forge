# Identity Architecture API

## Quick Test

### 1. Start Server
```bash
cd apps/document-service
npm run dev
```

### 2. Upload Documents
```bash
curl -X POST http://localhost:3001/api/v1/upload \
  -F "files=@/path/to/document1.txt" \
  -F "files=@/path/to/document2.md" \
  -F "tenantId=sarah"
```

Response:
```json
{
  "success": true,
  "documentIds": ["doc_123", "doc_456"],
  "count": 2,
  "message": "Files uploaded successfully. Starting processing..."
}
```

### 3. Process into Identity Architecture
```bash
curl -X POST http://localhost:3001/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "tenantId": "sarah",
    "documentIds": ["doc_123", "doc_456"]
  }'
```

Response contains complete `ClientArchitecture` with all four screens of data.

### 4. Get Architecture Summary
```bash
curl http://localhost:3001/api/v1/architecture/sarah/summary
```

Response:
```json
{
  "documents": 2,
  "atoms": 247,
  "perspectives": 3,
  "history": 3,
  "people": 5,
  "primitives": 3,
  "anchors": 3,
  "patterns": 2,
  "purposes": 2,
  "coherence": 87
}
```

### 5. Get Specific Screen Data

**Screen 1: What You Gave**
```bash
curl http://localhost:3001/api/v1/architecture/sarah/screen/1
```

**Screen 2: What We See**
```bash
curl http://localhost:3001/api/v1/architecture/sarah/screen/2
```

**Screen 3: Furnace Principle**
```bash
curl http://localhost:3001/api/v1/architecture/sarah/screen/3
```

**Screen 4: Not-Me Identity**
```bash
curl http://localhost:3001/api/v1/architecture/sarah/screen/4
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/upload` | Upload documents |
| POST | `/api/v1/process` | Process through pipeline |
| GET | `/api/v1/architecture/:tenantId` | Get full architecture |
| GET | `/api/v1/architecture/:tenantId/summary` | Get summary stats |
| GET | `/api/v1/architecture/:tenantId/screen/:number` | Get screen data (1-4) |

## Processing Pipeline

```
Upload → Distill → Meta-Extract → Furnace → Synthesize
  25%      40%         60%           80%        100%
```

Progress messages during processing:
1. "Breaking down your documents into knowledge atoms..."
2. "Extracted 247 knowledge atoms"
3. "Analyzing what we see in your content..."
4. "Found 3 life perspectives, 3 core values"
5. "Processing through Furnace Principle - expanding insights..."
6. "Discovered 2 patterns, expanded 10 atoms"
7. "Synthesizing your Not-Me identity..."
8. "Complete! Generated 2 purpose statements"

## Next Steps

1. **Add Database**: Replace in-memory storage with PostgreSQL or BigQuery
2. **Real-time Updates**: Add WebSocket for live processing progress
3. **Gemini Integration**: Replace placeholder prompts with real API calls
4. **Build UI**: Create React dashboard for four-screen visualization
5. **Add Authentication**: JWT tokens for multi-tenant isolation
