# Environment Setup Guide

## Using Google Cloud Secret Manager (Recommended)

Your secrets are already in Google Cloud Secret Manager. The app will automatically fetch them on startup.

### 1. Create `.env` file

```bash
cd /Users/jeremyserna/truth_forge/apps/document-service
cp .env.example .env
```

### 2. The `.env` file should contain:

```bash
PORT=3001
NODE_ENV=development
GOOGLE_CLOUD_PROJECT=truth-forge
BIGQUERY_PROJECT=truth-forge
BIGQUERY_DATASET=main
GOOGLE_APPLICATION_CREDENTIALS=/Users/jeremyserna/.config/gcloud/application_default_credentials.json
```

### 3. Make sure secrets exist in Secret Manager

```bash
# Check if your secrets exist
gcloud secrets list --project=truth-forge

# You should see:
# - gemini-api-key
```

### 4. If you need to create/update secrets:

```bash
# Create a new secret
echo -n "your-gemini-api-key-here" | gcloud secrets create gemini-api-key \
  --project=truth-forge \
  --data-file=-

# Or update existing secret
echo -n "your-gemini-api-key-here" | gcloud secrets versions add gemini-api-key \
  --project=truth-forge \
  --data-file=-
```

### 5. Verify your Google Cloud authentication

```bash
gcloud auth application-default login
```

This creates credentials at:
`/Users/jeremyserna/.config/gcloud/application_default_credentials.json`

### 6. Test the setup

```bash
npm run build
npm start
```

The app will:
- Load secrets from Secret Manager automatically
- Print "✅ Secrets loaded from Google Cloud Secret Manager"
- Start the server on port 3001

---

## Local Development (Alternative)

If you want to use local secrets for testing (not recommended):

```bash
# Add to .env
GEMINI_API_KEY=your-local-key-here
```

The app will fall back to local `.env` if Secret Manager fails.

---

## Troubleshooting

**Error: "Failed to load secrets"**
- Check: `gcloud config get-value project` (should be "truth-forge")
- Check: `gcloud auth application-default print-access-token` (should print a token)
- Check: Secret exists with `gcloud secrets describe gemini-api-key`

**Error: "Permission denied"**
- Your service account needs `roles/secretmanager.secretAccessor`
- Grant it: `gcloud secrets add-iam-policy-binding gemini-api-key --member="user:your-email@gmail.com" --role="roles/secretmanager.secretAccessor"`
