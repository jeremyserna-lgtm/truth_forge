# Document Service Integration

The document service has been successfully integrated into the Truth Forge website as Vercel serverless functions.

## API Endpoints

### Admin Portal

**Upload Document**
```bash
POST /api/admin/upload
Content-Type: multipart/form-data

# Example with curl:
curl -X POST https://truth-forge.ai/api/admin/upload \
  -F "file=@/path/to/document.txt" \
  -F "tenantId=admin"
```

**Process Document**
```bash
POST /api/admin/process
Content-Type: application/json

# Example:
curl -X POST https://truth-forge.ai/api/admin/process \
  -H "Content-Type: application/json" \
  -d '{"documentId": "doc_1234567890"}'
```

**Query Atoms**
```bash
POST /api/admin/documents/atoms
Content-Type: application/json

# Example:
curl -X POST https://truth-forge.ai/api/admin/documents/atoms \
  -H "Content-Type: application/json" \
  -d '{"tenantId": "admin", "limit": 50}'
```

### Customer Portal

**Chat with Not-Me**
```bash
POST /api/customer/chat
Content-Type: application/json

# Example:
curl -X POST https://truth-forge.ai/api/customer/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about the Truth Engine",
    "sessionId": "session_123"
  }'
```

## Environment Variables

Add these to your Vercel project settings:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# BigQuery
BIGQUERY_PROJECT=truth-forge
BIGQUERY_DATASET=main
GOOGLE_APPLICATION_CREDENTIALS=<base64_encoded_service_account_json>

# Upstash Redis (already configured)
UPSTASH_REDIS_REST_URL=<your_redis_url>
UPSTASH_REDIS_REST_TOKEN=<your_redis_token>
```

## Local Testing

1. **Start dev server**:
```bash
cd /Users/jeremyserna/truth_forge/apps/websites/truth_forge
npm run dev
```

2. **Create a test document**:
```bash
echo "The Truth Engine is a revolutionary AI partnership platform." > test-doc.txt
```

3. **Upload the document**:
```bash
curl -X POST http://localhost:5173/api/admin/upload \
  -F "file=@test-doc.txt"
```

4. **Process it** (use the documentId from upload response):
```bash
curl -X POST http://localhost:5173/api/admin/process \
  -H "Content-Type: application/json" \
  -d '{"documentId": "doc_XXXXX"}'
```

5. **Test customer chat**:
```bash
curl -X POST http://localhost:5173/api/customer/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Truth Engine?"}'
```

## Files Created

### Shared Libraries
- `/api/_lib/gemini-atomizer.ts` - Knowledge extraction with Gemini
- `/api/_lib/bigquery-atoms.ts` - BigQuery export utilities

### Admin API
- `/api/admin/upload.ts` - Document upload endpoint
- `/api/admin/process.ts` - Atomization and BigQuery export
- `/api/admin/documents.ts` - Document and atom queries

### Customer API
- `/api/customer/chat.ts` - Not-Me chat interface

## Next Steps

1. **Environment Setup**: Configure Vercel environment variables
2. **Test Locally**: Run through the test flow above
3. **Deploy**: `vercel deploy --prod`
4. **Verify BigQuery**: Check that atoms appear in `entities_unified` table
5. **Build UI** (optional): Create React components for file upload and chat

## Architecture

```
User uploads document
    ↓
/api/admin/upload (stores in Redis)
    ↓
/api/admin/process
    ↓
Gemini atomizes → BigQuery export
    ↓
Atoms stored in entities_unified table
    ↓
Available for customer Not-Me chat
```
