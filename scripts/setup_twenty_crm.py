#!/usr/bin/env python3
"""Setup script for Twenty CRM.

Sets up custom fields and data model in Twenty CRM.
Run this once to initialize the CRM.

Usage:
    python scripts/setup_twenty_crm.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Set up Twenty CRM."""
    logger.info("Initializing Twenty CRM service...")

    try:
        with TwentyCRMService() as service:
            logger.info("Setting up custom fields and data model...")
            setup_result = service.setup_crm()

            logger.info("Setup complete!")
            logger.info(f"Person fields created: {len(setup_result.get('person_fields', []))}")
            logger.info(
                f"Company fields created: {len(setup_result.get('company_fields', []))}"
            )

            # Verify setup
            logger.info("Verifying setup...")
            verify_result = service.verify_setup()

            if verify_result["all_complete"]:
                logger.info("✅ All custom fields set up correctly!")
            else:
                logger.warning("⚠️  Some fields missing:")
                if verify_result["person_fields"]["missing"]:
                    logger.warning(
                        f"  Person fields: {verify_result['person_fields']['missing']}"
                    )
                if verify_result["company_fields"]["missing"]:
                    logger.warning(
                        f"  Company fields: {verify_result['company_fields']['missing']}"
                    )

    except Exception as e:
        logger.error(f"Failed to set up Twenty CRM: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
