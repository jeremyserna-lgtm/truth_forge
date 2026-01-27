# Twenty CRM API Key Configuration ✅

**Date**: 2026-01-27
**Status**: ✅ Configuration Complete

---

## Secret Names Supported

The sync system automatically tries these secret names (in order):

1. ✅ `twenty-crm-api-key` (recommended)
2. `twenty_crm_api_key` (snake case)
3. `twenty_api_key` (short version)
4. `TWENTY_CRM_API_KEY` (uppercase)
5. `TWENTY_API_KEY` (uppercase short)
6. `twenty-api-key` (alternative hyphen)

**Environment Variable Fallback**:
- `TWENTY_CRM_API_KEY`
- `TWENTY_API_KEY`

---

## Verify Secret Name

Run the verification script to check which secret name contains your API key:

```bash
python scripts/verify_api_key_secret.py
```

This will:
- ✅ Check all possible secret names
- ✅ Show which one contains the API key
- ✅ Provide instructions if not found

---

## Create Secret (If Needed)

### Option 1: Using gcloud CLI

```bash
export PROJECT_ID=flash-clover-464719-g1

echo -n "your-twenty-api-key-here" | gcloud secrets create twenty-crm-api-key \
  --data-file=- \
  --project=$PROJECT_ID
```

### Option 2: Using GCP Console

1. Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager)
2. Click "CREATE SECRET"
3. Name: `twenty-crm-api-key`
4. Secret value: Your Twenty CRM API key
5. Click "CREATE SECRET"

---

## Verify Configuration

After creating the secret, verify it works:

```bash
# Verify secret exists
python scripts/verify_api_key_secret.py

# Test connection
python scripts/test_twenty_crm_connection.py
```

---

## Troubleshooting

### Secret Not Found

**Error**: `Twenty CRM API key not found in secrets manager`

**Solution**:
1. Run `python scripts/verify_api_key_secret.py` to check what exists
2. Create secret with name `twenty-crm-api-key` (recommended)
3. Verify with verification script

### Wrong Secret Name

**Error**: Secret exists but not found

**Solution**:
1. Check exact secret name in GCP Console
2. Update code to include that name, OR
3. Create new secret with name `twenty-crm-api-key`

### Permission Issues

**Error**: Permission denied accessing secret

**Solution**:
```bash
# Grant access to service account
gcloud secrets add-iam-policy-binding twenty-crm-api-key \
  --member="serviceAccount:your-service-account@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=PROJECT_ID
```

---

## Recommended Setup

**Best Practice**: Use `twenty-crm-api-key` as the secret name.

This is:
- ✅ The first name tried (fastest)
- ✅ Clear and descriptive
- ✅ Follows naming conventions
- ✅ Easy to remember

---

## Status

**✅ API Key Configuration Ready**

- Multiple secret name variations supported ✅
- Verification script available ✅
- Clear error messages ✅
- Helpful setup instructions ✅

**The system will automatically find your API key using any of the supported names!**

---

**Last Updated**: 2026-01-27
