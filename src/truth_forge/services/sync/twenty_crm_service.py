"""Twenty CRM Service - Main service for CRM operations.

Initializes clients and provides high-level sync operations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
import logging

from google.cloud import bigquery

from truth_forge.services.sync.twenty_crm_client import TwentyCRMClient

if TYPE_CHECKING:
    from supabase import Client
else:
    try:
        from supabase import create_client, Client
    except ImportError:
        create_client = None
        Client = Any
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.business_sync import BusinessSyncService
from truth_forge.services.sync.people_relationship_sync import PeopleRelationshipSyncService
from truth_forge.services.sync.relationship_sync import RelationshipSyncService
from truth_forge.services.sync.error_reporter import ErrorReporter
from truth_forge.services.secret.service import SecretService
from truth_forge.core.settings import settings

logger = logging.getLogger(__name__)


class TwentyCRMService:
    """Main service for Twenty CRM operations.
    
    Provides:
    - Initialization with secrets manager
    - Setup of custom fields
    - Sync operations
    - Error reporting
    """

    def __init__(
        self,
        bq_client: Optional[bigquery.Client] = None,
        supabase_client: Optional[Any] = None,
        local_db: Optional[Any] = None,
    ) -> None:
        """Initialize Twenty CRM service.
        
        Args:
            bq_client: BigQuery client (optional, will create if not provided)
            supabase_client: Supabase client (optional, will create if not provided)
            local_db: Local database connection (optional)
        """
        # Initialize secret service
        self.secret_service = SecretService()

        # Initialize Twenty CRM client (gets API key from secrets manager)
        self.crm_client = TwentyCRMClient(secret_service=self.secret_service)

        # Initialize BigQuery client
        if bq_client:
            self.bq_client = bq_client
        else:
            self.bq_client = bigquery.Client(project=settings.effective_gcp_project)

        # Initialize Supabase client
        if supabase_client:
            self.supabase = supabase_client
        elif create_client:
            try:
                # Get Supabase credentials from secrets manager
                supabase_url = self.secret_service.get_secret("supabase-url")
                supabase_key = self.secret_service.get_secret("supabase-anon-key")
                self.supabase = create_client(supabase_url, supabase_key)
            except Exception as e:
                logger.warning(f"Supabase not available: {e}")
                self.supabase = None
        else:
            logger.warning("Supabase library not installed, skipping Supabase sync")
            self.supabase = None

        # Initialize local DB (if provided)
        self.local_db = local_db

        # Initialize error reporter
        self.error_reporter = ErrorReporter(self.bq_client)

        # Initialize sync services
        self.bq_sync = BigQuerySyncService(
            self.bq_client, self.supabase, self.local_db, self.crm_client
        )

        self.business_sync = BusinessSyncService(
            self.bq_client,
            self.supabase,
            self.local_db,
            self.crm_client,
            self.error_reporter,
        )

        self.people_relationship_sync = PeopleRelationshipSyncService(
            self.bq_client,
            self.supabase,
            self.local_db,
            self.crm_client,
            self.error_reporter,
        )

        self.relationship_sync = RelationshipSyncService(
            self.bq_client,
            self.supabase,
            self.local_db,
            self.crm_client,
            self.error_reporter,
        )

    def setup_crm(self) -> Dict[str, Any]:
        """Set up Twenty CRM with custom fields and data model.
        
        Returns:
            Setup results
        """
        from truth_forge.services.sync.twenty_crm_setup import TwentyCRMSetup

        setup = TwentyCRMSetup(client=self.crm_client)
        return setup.setup_all()

    def verify_setup(self) -> Dict[str, Any]:
        """Verify CRM setup is complete.
        
        Returns:
            Verification results
        """
        from truth_forge.services.sync.twenty_crm_setup import TwentyCRMSetup

        setup = TwentyCRMSetup(client=self.crm_client)
        return setup.verify_setup()

    def sync_contact_from_crm(self, crm_contact_id: str) -> Dict[str, Any]:
        """Sync a contact from CRM to BigQuery and all systems.
        
        Args:
            crm_contact_id: Contact ID in Twenty CRM
            
        Returns:
            Sync result
        """
        from truth_forge.services.sync.crm_twenty_sync import CRMTwentySyncService

        crm_sync = CRMTwentySyncService(
            self.crm_client, self.bq_client, self.bq_sync
        )
        return crm_sync.sync_from_crm_to_bigquery(crm_contact_id)

    def sync_business_from_crm(self, crm_company_id: str) -> Dict[str, Any]:
        """Sync a business from CRM to BigQuery and all systems.
        
        Args:
            crm_company_id: Company ID in Twenty CRM
            
        Returns:
            Sync result
        """
        try:
            # Fetch from CRM
            company = self.crm_client.get_company(crm_company_id)
            
            # Get business_id from customFields
            business_id = company.get("customFields", {}).get("business_id")
            if not business_id:
                return {"status": "error", "error": "Company missing business_id in customFields"}
            
            # Sync business (which propagates to all systems)
            result = self.business_sync.sync_business_to_all(business_id)
            return result
        except Exception as e:
            logger.error(f"Failed to sync business from CRM: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

    def sync_all_from_crm(
        self, last_sync_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync all contacts and companies from CRM.
        
        Args:
            last_sync_time: Last sync timestamp
            
        Returns:
            Sync summary
        """
        from truth_forge.services.sync.crm_twenty_sync import CRMTwentySyncService

        crm_sync = CRMTwentySyncService(
            self.crm_client, self.bq_client, self.bq_sync
        )

        # Sync contacts
        contacts_result = crm_sync.sync_all_from_crm(last_sync_time)

        # Sync companies
        companies = self.crm_client.list_companies(updated_since=last_sync_time)
        companies_result = {"synced": 0, "results": []}
        for company in companies:
            try:
                # Get business_id from customFields
                business_id = company.get("customFields", {}).get("business_id")
                if business_id:
                    result = self.business_sync.sync_business_to_all(business_id)
                    companies_result["results"].append(result)
                    if result.get("crm_twenty", {}).get("status") == "synced":
                        companies_result["synced"] += 1
            except Exception as e:
                logger.error(f"Failed to sync company {company.get('id')}: {e}", exc_info=True)
                companies_result["results"].append({"status": "error", "error": str(e)})

        return {
            "contacts": contacts_result,
            "companies": companies_result,
        }

    def close(self) -> None:
        """Close all clients."""
        self.crm_client.close()

    def __enter__(self) -> "TwentyCRMService":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
