#!/usr/bin/env python3
"""Verify Twenty CRM API Key Secret in GCP Secret Manager.

Directly checks GCP Secret Manager to verify the secret exists.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import secretmanager
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function."""
    logger.info("=" * 60)
    logger.info("VERIFYING TWENTY CRM API KEY IN GCP SECRET MANAGER")
    logger.info("=" * 60)
    logger.info("")
    
    project_id = settings.effective_gcp_project
    if not project_id:
        logger.error("GCP_PROJECT_ID is not configured")
        logger.error("Set GCP_PROJECT_ID environment variable or configure in settings")
        return 1
    
    logger.info(f"Project ID: {project_id}")
    logger.info("")
    
    # Secret names to check (actual GCP secret name first)
    secret_names = [
        "Twenty_CRM",              # Actual GCP secret name
        "twenty-crm-api-key",
        "twenty_crm_api_key",
        "twenty_api_key",
        "TWENTY_CRM_API_KEY",
        "TWENTY_API_KEY",
        "twenty-api-key",
    ]
    
    client = secretmanager.SecretManagerServiceClient()
    found_secrets = []
    
    logger.info("Checking secrets in GCP Secret Manager...")
    logger.info("")
    
    for secret_name in secret_names:
        try:
            name = f"projects/{project_id}/secrets/{secret_name}"
            version_name = f"{name}/versions/latest"
            
            # Try to access the secret
            response = client.access_secret_version(request={"name": version_name})
            secret_value = response.payload.data.decode("UTF-8")
            
            logger.info(f"✅ FOUND: {secret_name}")
            logger.info(f"   Value: {secret_value[:20]}... (truncated for security)")
            logger.info(f"   Full path: {version_name}")
            found_secrets.append(secret_name)
            
        except Exception as e:
            error_str = str(e)
            if "not found" in error_str.lower() or "NotFound" in error_str:
                logger.debug(f"   Not found: {secret_name}")
            elif "permission" in error_str.lower() or "PermissionDenied" in error_str:
                logger.warning(f"   Permission denied: {secret_name}")
            else:
                logger.debug(f"   Error checking {secret_name}: {e}")
            continue
    
    logger.info("")
    
    if found_secrets:
        logger.info("=" * 60)
        logger.info("SUCCESS - SECRET FOUND")
        logger.info("=" * 60)
        logger.info(f"Found {len(found_secrets)} secret(s):")
        for secret_name in found_secrets:
            logger.info(f"  ✅ {secret_name}")
        logger.info("")
        logger.info("The sync system will automatically use this secret.")
        logger.info("")
        return 0
    else:
        logger.error("=" * 60)
        logger.error("ERROR - SECRET NOT FOUND")
        logger.error("=" * 60)
        logger.error("")
        logger.error("No API key found in GCP Secret Manager with these names:")
        for secret_name in secret_names:
            logger.error(f"  ❌ {secret_name}")
        logger.error("")
        logger.error("To create the secret, run:")
        logger.error("")
        logger.error(f"  export PROJECT_ID={project_id}")
        logger.error("  echo -n 'your-api-key-here' | gcloud secrets create twenty-crm-api-key \\")
        logger.error("    --data-file=- \\")
        logger.error(f"    --project=$PROJECT_ID")
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
