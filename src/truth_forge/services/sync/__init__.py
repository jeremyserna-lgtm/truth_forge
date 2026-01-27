"""Multi-source contact sync services.

This package provides synchronization between:
- BigQuery (canonical source)
- Supabase (application database)
- Local database (SQLite/Postgres)
- CRM Twenty (visibility layer)

Includes:
- Contacts sync
- Businesses sync
- People-business relationships sync
- Complete error tracking (nothing hidden)
"""

from .bigquery_sync import BigQuerySyncService
from .supabase_sync import SupabaseSyncService
# LocalSyncService is optional - import only if needed
try:
    from .local_sync import LocalSyncService
except ImportError:
    LocalSyncService = None  # type: ignore
from .crm_twenty_sync import CRMTwentySyncService
from .conflict_resolver import ConflictResolver
from .error_reporter import ErrorReporter, ErrorType
from .business_sync import BusinessSyncService
from .relationship_sync import RelationshipSyncService
from .people_relationship_sync import PeopleRelationshipSyncService
from .twenty_crm_client import TwentyCRMClient
from .twenty_crm_service import TwentyCRMService
from .twenty_crm_setup import TwentyCRMSetup
from .auto_sync_service import AutoSyncService
from .webhook_sync import WebhookSyncHandler
from .cdc_sync_service import CDCSyncService, ChangeEvent, ChangeType
from .event_driven_sync import EventDrivenSyncService, SyncEvent, EventPriority
from .industry_standard_sync import IndustryStandardSyncService
from .health_monitor import SyncHealthMonitor

__all__ = [
    "BigQuerySyncService",
    "SupabaseSyncService",
    "CRMTwentySyncService",
    "ConflictResolver",
    "ErrorReporter",
    "ErrorType",
    "BusinessSyncService",
    "RelationshipSyncService",
    "PeopleRelationshipSyncService",
    "TwentyCRMClient",
    "TwentyCRMService",
    "TwentyCRMSetup",
    "AutoSyncService",
    "WebhookSyncHandler",
    "CDCSyncService",
    "ChangeEvent",
    "ChangeType",
    "EventDrivenSyncService",
    "SyncEvent",
    "EventPriority",
    "IndustryStandardSyncService",
    "SyncHealthMonitor",
]
