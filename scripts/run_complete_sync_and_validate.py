#!/usr/bin/env python3
"""Run Complete Sync and Validate - No Exceptions.

This script:
1. Syncs all contacts from BigQuery to all systems
2. Validates each contact exists in all systems
3. Reports any issues
4. Proves complete sync with no exceptions
"""

import sys
from pathlib import Path
import logging
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.validate_complete_sync import SyncValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("complete_sync_validation.log"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run complete sync and validate - no exceptions"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of contacts (for testing)",
    )
    parser.add_argument(
        "--skip-sync",
        action="store_true",
        help="Skip sync, only validate existing data",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("COMPLETE SYNC AND VALIDATION")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This will ensure:")
    logger.info("  ✅ All contacts sync to all systems")
    logger.info("  ✅ All contacts validated in all systems")
    logger.info("  ✅ No exceptions - complete coverage")
    logger.info("")
    
    validator = SyncValidator()
    
    if not args.skip_sync:
        logger.info("Step 1: Syncing all contacts...")
        logger.info("")
        results = validator.validate_all(limit=args.limit)
    else:
        logger.info("Skipping sync, validating existing data...")
        # TODO: Implement validation-only mode
        results = validator.validate_all(limit=args.limit)
    
    logger.info("")
    logger.info("Step 2: Generating validation report...")
    logger.info("")
    validator.generate_report()
    
    # Final status
    if results["errors"] == 0 and len(results["mismatched"]) == 0:
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ SUCCESS - ALL CONTACTS SYNCED AND VALIDATED")
        logger.info("=" * 60)
        logger.info("")
        logger.info(f"Total Contacts: {results['total_contacts']}")
        logger.info(f"Synced: {results['synced']}")
        logger.info(f"Validated: {results['validated']}")
        logger.info("")
        logger.info("✅ NO EXCEPTIONS - ALL DATA IN SYNC")
        logger.info("")
        return 0
    else:
        logger.error("")
        logger.error("=" * 60)
        logger.error("❌ ISSUES FOUND")
        logger.error("=" * 60)
        logger.error("")
        logger.error(f"Errors: {results['errors']}")
        logger.error(f"Validation Issues: {len(results['mismatched'])}")
        logger.error("")
        logger.error("Review errors above and fix issues")
        logger.error("")
        return 1


if __name__ == "__main__":
    sys.exit(main())
