#!/usr/bin/env python3
"""Verify Twenty CRM API Key Secret Name.

Checks what secret names exist in the secrets manager and verifies
which one contains the Twenty CRM API key.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.secret.service import SecretService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function."""
    logger.info("=" * 60)
    logger.info("VERIFYING TWENTY CRM API KEY SECRET NAME")
    logger.info("=" * 60)
    logger.info("")
    
    secret_service = SecretService()
    
    # List of secret names to try (actual GCP secret name first)
    secret_names = [
        "Twenty_CRM",              # Actual GCP secret name
        "twenty-crm-api-key",
        "twenty_api_key",
        "TWENTY_CRM_API_KEY",
        "twenty-api-key",
        "twenty_crm_api_key",
        "TWENTY_API_KEY",
    ]
    
    logger.info("Checking secret names in secrets manager...")
    logger.info("")
    
    found_secrets = []
    
    for secret_name in secret_names:
        try:
            api_key = secret_service.get_secret(secret_name)
            if api_key and not api_key.startswith("mock_"):
                logger.info(f"✅ FOUND: {secret_name}")
                logger.info(f"   Value: {api_key[:20]}... (truncated for security)")
                found_secrets.append(secret_name)
            elif api_key and api_key.startswith("mock_"):
                logger.warning(f"⚠️  MOCK: {secret_name} (returns mock value)")
            else:
                logger.debug(f"   Empty: {secret_name}")
        except Exception as e:
            logger.debug(f"   Not found: {secret_name}")
            continue
    
    logger.info("")
    
    if found_secrets:
        logger.info("=" * 60)
        logger.info("SUCCESS - API KEY FOUND")
        logger.info("=" * 60)
        logger.info(f"Found {len(found_secrets)} secret(s) with API key:")
        for secret_name in found_secrets:
            logger.info(f"  ✅ {secret_name}")
        logger.info("")
        logger.info("The sync system will use the first found secret.")
        logger.info("")
        return 0
    else:
        logger.error("=" * 60)
        logger.error("ERROR - API KEY NOT FOUND")
        logger.error("=" * 60)
        logger.error("")
        logger.error("No API key found in secrets manager with these names:")
        for secret_name in secret_names:
            logger.error(f"  ❌ {secret_name}")
        logger.error("")
        logger.error("To create the secret, run:")
        logger.error("")
        logger.error("  export PROJECT_ID=flash-clover-464719-g1")
        logger.error("  echo -n 'your-api-key-here' | gcloud secrets create twenty-crm-api-key \\")
        logger.error("    --data-file=- \\")
        logger.error("    --project=$PROJECT_ID")
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
