"""Migration utilities for truth_forge.

Provides:
- Checkpoint validation after each phase
- Rollback procedures
- Health checks
- Code transformation utilities
"""

from truth_forge.migration.checkpoints import (
    CheckpointResult,
    validate_all_checkpoints,
    validate_checkpoint,
)
from truth_forge.migration.health import (
    check_all_services_health,
    check_service_health,
    verify_hold_sync,
)
from truth_forge.migration.rollback import (
    cleanup_old_backups,
    create_backup,
    list_backups,
    rollback_to_backup,
)
from truth_forge.migration.transform import (
    TransformResult,
    generate_migration_report,
    transform_directory,
    transform_file,
)


__all__ = [
    # Checkpoints
    "CheckpointResult",
    "validate_checkpoint",
    "validate_all_checkpoints",
    # Rollback
    "create_backup",
    "rollback_to_backup",
    "list_backups",
    "cleanup_old_backups",
    # Health
    "check_service_health",
    "check_all_services_health",
    "verify_hold_sync",
    # Transform
    "transform_file",
    "transform_directory",
    "generate_migration_report",
    "TransformResult",
]
