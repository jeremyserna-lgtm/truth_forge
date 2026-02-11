# Environment Setup for Document Service

Copy this template to `.env.local` for local development:

```env
# Gemini API Key
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# BigQuery Configuration
BIGQUERY_PROJECT=truth-forge
BIGQUERY_DATASET=main

# Google Cloud Service Account (for BigQuery access)
# Option 1: Path to service account JSON file
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Option 2: Base64 encoded service account JSON (for Vercel)
# GOOGLE_APPLICATION_CREDENTIALS=<base64_encoded_json>

# Upstash Redis (already configured - check existing .env)
UPSTASH_REDIS_REST_URL=https://your-redis-instance.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_redis_token

# Anthropic API Key (for customer chat - already configured)
ANTHROPIC_API_KEY=your_anthropic_key
```

## Getting the Keys

### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy to `GEMINI_API_KEY`

### BigQuery Service Account
1. Go to Google Cloud Console
2. Navigate to IAM & Admin → Service Accounts
3. Create service account with BigQuery Admin role
4. Download JSON key
5. Either:
   - Store locally and set path in `GOOGLE_APPLICATION_CREDENTIALS`
   - Base64 encode for Vercel: `cat service-account.json | base64`

### Upstash Redis
Already configured in your existing `.env` - just verify the values are set.

## Vercel Deployment

Add these as environment variables in your Vercel project settings:
- `GEMINI_API_KEY`
- `BIGQUERY_PROJECT` 
- `BIGQUERY_DATASET`
- `GOOGLE_APPLICATION_CREDENTIALS` (use base64 encoded JSON for Vercel)

The Anthropic and Upstash credentials should already be configured.
