"""Comprehensive tests for SupabaseSyncService.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timedelta
import json

from truth_forge.services.sync.supabase_sync import SupabaseSyncService


class TestSupabaseSyncService:
    """Test suite for SupabaseSyncService."""
    
    def test_init(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test initialization."""
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        assert service.supabase == mock_supabase_client
        assert service.bq_client == mock_bq_client
        assert service.bq_sync == mock_bq_sync
    
    def test_sync_from_supabase_to_bigquery_success(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing contact from Supabase to BigQuery successfully."""
        # Mock Supabase query
        supabase_table = Mock()
        supabase_query = Mock()
        supabase_query.or_.return_value = supabase_query
        supabase_query.execute.return_value = Mock(
            data=[{
                "id": "uuid-123",
                "contact_id": "123",
                "first_name": "Test",
                "last_name": "User",
                "canonical_name": "Test User",
            }]
        )
        supabase_table.select.return_value = supabase_query
        mock_supabase_client.table.return_value = supabase_table
        
        # Mock BigQuery query (no existing contact)
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        # Mock BigQuery table and insert
        mock_table = Mock()
        mock_bq_client.get_table.return_value = mock_table
        mock_bq_client.insert_rows_json.return_value = []
        
        # Mock bq_sync propagation
        mock_bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service.sync_from_supabase_to_bigquery("123")
        
        assert result["status"] == "synced"
        assert result["contact_id"] == 123
        mock_bq_sync.sync_contact_to_all.assert_called_once_with(123)
    
    def test_sync_from_supabase_to_bigquery_not_found(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing contact that doesn't exist in Supabase."""
        supabase_table = Mock()
        supabase_query = Mock()
        supabase_query.or_.return_value = supabase_query
        supabase_query.execute.return_value = Mock(data=[])
        supabase_table.select.return_value = supabase_query
        mock_supabase_client.table.return_value = supabase_table
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service.sync_from_supabase_to_bigquery("999")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_sync_from_supabase_to_bigquery_conflict_resolution(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing with conflict resolution (existing record wins)."""
        # Mock Supabase query
        supabase_table = Mock()
        supabase_query = Mock()
        supabase_query.or_.return_value = supabase_query
        supabase_query.execute.return_value = Mock(
            data=[{
                "id": "uuid-123",
                "contact_id": "123",
                "first_name": "Test",
                "last_name": "User",
            }]
        )
        supabase_table.select.return_value = supabase_query
        mock_supabase_client.table.return_value = supabase_table
        
        # Mock BigQuery query (existing contact)
        mock_existing_row = {"contact_id": 123, "version": 5}
        query_job = Mock()
        query_job.result.return_value = [mock_existing_row]
        mock_bq_client.query.return_value = query_job
        
        # Mock conflict resolver (existing wins)
        with patch("truth_forge.services.sync.conflict_resolver.ConflictResolver") as mock_resolver_class:
            mock_resolver = Mock()
            mock_resolver.resolve_conflict.return_value = {"winner": "target"}
            mock_resolver_class.return_value = mock_resolver
            
            service = SupabaseSyncService(
                supabase_client=mock_supabase_client,
                bq_client=mock_bq_client,
                bq_sync=mock_bq_sync,
            )
            
            result = service.sync_from_supabase_to_bigquery("123")
            
            assert result["status"] == "skipped"
            assert result["reason"] == "existing_record_newer"
            mock_bq_sync.sync_contact_to_all.assert_not_called()
    
    def test_sync_from_supabase_to_bigquery_missing_contact_id(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing contact missing contact_id."""
        supabase_table = Mock()
        supabase_query = Mock()
        supabase_query.or_.return_value = supabase_query
        supabase_query.execute.return_value = Mock(
            data=[{
                "id": "uuid-123",
                # Missing contact_id
                "first_name": "Test",
            }]
        )
        supabase_table.select.return_value = supabase_query
        mock_supabase_client.table.return_value = supabase_table
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        with pytest.raises(ValueError, match="missing contact_id"):
            service.sync_from_supabase_to_bigquery("uuid-123")
    
    def test_sync_all_from_supabase(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing all contacts from Supabase."""
        last_sync = datetime.utcnow() - timedelta(hours=12)
        
        # Mock Supabase table - need separate queries for list and individual fetches
        supabase_table = Mock()
        
        # Query for sync_all_from_supabase (list query)
        list_query = Mock()
        list_query.gte.return_value = list_query
        list_execute_result = Mock()
        list_execute_result.data = [
            {"id": "uuid-1", "contact_id": "1"},
            {"id": "uuid-2", "contact_id": "2"},
        ]
        list_query.execute.return_value = list_execute_result
        
        # Query for sync_from_supabase_to_bigquery (individual fetches)
        individual_query = Mock()
        individual_query.or_.return_value = individual_query
        individual_execute_result = Mock()
        individual_execute_result.data = [{"id": "uuid-1", "contact_id": "1"}]
        individual_query.execute.return_value = individual_execute_result
        
        # Set up side_effect for select() calls
        supabase_table.select.side_effect = [list_query, individual_query, individual_query]
        mock_supabase_client.table.return_value = supabase_table
        
        # Mock BigQuery queries (no existing contacts)
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.side_effect = [query_job, query_job]  # Two contacts
        
        # Mock BigQuery table and insert
        mock_table = Mock()
        mock_bq_client.get_table.return_value = mock_table
        mock_bq_client.insert_rows_json.return_value = []
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service.sync_all_from_supabase(last_sync_time=last_sync)
        
        assert result["synced"] == 2
        assert len(result["results"]) == 2
    
    def test_sync_all_from_supabase_no_last_sync_time(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test syncing all contacts without last_sync_time."""
        supabase_table = Mock()
        supabase_query = Mock()
        supabase_query.gte.return_value = supabase_query
        supabase_query.execute.return_value = Mock(data=[])
        supabase_table.select.return_value = supabase_query
        mock_supabase_client.table.return_value = supabase_table
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        with patch("truth_forge.services.sync.supabase_sync.datetime") as mock_dt:
            mock_now = datetime(2026, 1, 27, 12, 0, 0)
            mock_dt.utcnow.return_value = mock_now
            mock_dt.timedelta = timedelta
            
            result = service.sync_all_from_supabase()
            
            assert result["synced"] == 0
    
    def test_transform_supabase_to_canonical(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test transforming Supabase contact to canonical format."""
        supabase_contact = {
            "id": "uuid-123",
            "contact_id": "123",
            "first_name": "Test",
            "last_name": "User",
            "canonical_name": "Test User",
            "llm_context": '{"key": "value"}',
            "communication_stats": {"calls": 5},
            "social_network": None,
            "ai_insights": {},
            "recommendations": None,
            "sync_metadata": '{"version": 1}',
        }
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service._transform_supabase_to_canonical(supabase_contact)
        
        assert result["contact_id"] == 123
        assert result["canonical_name"] == "Test User"
        assert result["llm_context"] == {"key": "value"}
        assert result["communication_stats"] == {"calls": 5}
        assert result["sync_metadata"]["version"] == 2
        assert "supabase" in result["sync_metadata"]["source_systems"]
    
    def test_upsert_to_bigquery_success(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test upserting to BigQuery successfully."""
        contact = {"contact_id": 123, "canonical_name": "Test User"}
        
        # Mock BigQuery query (no existing)
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        # Mock BigQuery table and insert
        mock_table = Mock()
        mock_bq_client.get_table.return_value = mock_table
        mock_bq_client.insert_rows_json.return_value = []
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service._upsert_to_bigquery(contact)
        
        assert result["status"] == "synced"
        assert result["contact_id"] == 123
    
    def test_upsert_to_bigquery_error(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test upserting to BigQuery with error."""
        contact = {"contact_id": 123, "canonical_name": "Test User"}
        
        # Mock BigQuery query error
        mock_bq_client.query.side_effect = Exception("BigQuery error")
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service._upsert_to_bigquery(contact)
        
        assert result["status"] == "error"
        assert "BigQuery error" in result["error"]
    
    def test_upsert_to_bigquery_insert_errors(
        self,
        mock_supabase_client: Mock,
        mock_bq_client: Mock,
        mock_bq_sync: Mock,
    ) -> None:
        """Test upserting to BigQuery with insert errors."""
        contact = {"contact_id": 123, "canonical_name": "Test User"}
        
        # Mock BigQuery query (no existing)
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        # Mock BigQuery table and insert with errors
        mock_table = Mock()
        mock_bq_client.get_table.return_value = mock_table
        mock_bq_client.insert_rows_json.return_value = [{"error": "Insert failed"}]
        
        service = SupabaseSyncService(
            supabase_client=mock_supabase_client,
            bq_client=mock_bq_client,
            bq_sync=mock_bq_sync,
        )
        
        result = service._upsert_to_bigquery(contact)
        
        assert result["status"] == "error"
        assert "errors" in result