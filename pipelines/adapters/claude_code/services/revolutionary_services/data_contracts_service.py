"""Data Contracts Service

Manages data contracts with semantic versioning,
ensuring data quality and safe schema evolution.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import bigquery

from shared.revolutionary_features import (
    define_data_contract,
    validate_against_contract,
    ensure_data_contract_table,
    DATA_CONTRACT_TABLE,
)
from shared.constants import PROJECT_ID, DATASET_ID


class DataContractsService:
    """Service for managing data contracts."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Data Contracts Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
        ensure_data_contract_table(self.client)
    
    def create_contract(
        self,
        contract_name: str,
        stage: int,
        required_fields: List[str],
        quality_rules: Dict[str, Any],
        semantic_rules: Optional[Dict[str, Any]] = None,
        compatibility: str = "BACKWARD_COMPATIBLE",
    ) -> Dict[str, Any]:
        """Create a data contract.
        
        Args:
            contract_name: Name of contract
            stage: Pipeline stage
            required_fields: Required field names
            quality_rules: Quality validation rules
            semantic_rules: Semantic validation rules
            compatibility: Compatibility mode
        
        Returns:
            Contract dictionary
        """
        contract = define_data_contract(
            contract_name=contract_name,
            stage=stage,
            required_fields=required_fields,
            quality_rules=quality_rules,
            semantic_rules=semantic_rules,
            compatibility=compatibility,
        )
        
        # Store contract
        from src.services.central_services.core.bigquery_client import get_bigquery_client
        bq_client = get_bigquery_client()
        bq_client.load_rows_to_table(DATA_CONTRACT_TABLE, [contract])
        
        return contract
    
    def validate_data(
        self,
        data: Dict[str, Any],
        contract_id: str,
    ) -> Tuple[bool, List[str]]:
        """Validate data against contract.
        
        Args:
            data: Data to validate
            contract_id: Contract ID
        
        Returns:
            (is_valid, errors)
        """
        return validate_against_contract(
            client=self.client,
            data=data,
            contract_id=contract_id,
        )
    
    def get_contract(
        self,
        contract_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get contract by ID.
        
        Args:
            contract_id: Contract ID
        
        Returns:
            Contract dictionary or None
        """
        query = f"""
        SELECT *
        FROM `{DATA_CONTRACT_TABLE}`
        WHERE contract_id = '{contract_id}'
          AND active = TRUE
        """
        
        result = list(self.client.query(query).result())
        
        if result:
            contract = dict(result[0])
            contract["contract_terms"] = json.loads(contract["contract_terms"])
            contract["migration_rules"] = json.loads(contract.get("migration_rules", "{}"))
            return contract
        
        return None
    
    def get_contracts_for_stage(
        self,
        stage: int,
    ) -> List[Dict[str, Any]]:
        """Get all contracts for a stage.
        
        Args:
            stage: Pipeline stage
        
        Returns:
            List of contracts
        """
        query = f"""
        SELECT *
        FROM `{DATA_CONTRACT_TABLE}`
        WHERE stage = {stage}
          AND active = TRUE
        ORDER BY created_at DESC
        """
        
        result = list(self.client.query(query).result())
        contracts = []
        
        for row in result:
            contract = dict(row)
            contract["contract_terms"] = json.loads(contract["contract_terms"])
            contract["migration_rules"] = json.loads(contract.get("migration_rules", "{}"))
            contracts.append(contract)
        
        return contracts
    
    def create_pipeline_contracts(self) -> Dict[str, str]:
        """Create data contracts for all pipeline stages.
        
        Returns:
            Dictionary mapping stage to contract_id
        """
        contracts = {}
        
        # Stage 5 (L8 Conversations)
        contracts["stage_5"] = self.create_contract(
            contract_name="claude_code_l8_conversations",
            stage=5,
            required_fields=["entity_id", "level", "conversation_id", "session_id", "text"],
            quality_rules={
                "level": "== 8",
                "text": "not_null",
            },
            semantic_rules={
                "conversation_id": "must_match_entity_id",
            },
        )["contract_id"]
        
        # Stage 6 (L6 Turns)
        contracts["stage_6"] = self.create_contract(
            contract_name="claude_code_l6_turns",
            stage=6,
            required_fields=["entity_id", "level", "parent_id", "conversation_id", "turn_id"],
            quality_rules={
                "level": "== 6",
                "parent_id": "not_null",
            },
            semantic_rules={
                "conversation_id": "must_exist_in_l8",
            },
        )["contract_id"]
        
        # Stage 7 (L5 Messages)
        contracts["stage_7"] = self.create_contract(
            contract_name="claude_code_l5_messages",
            stage=7,
            required_fields=["entity_id", "level", "parent_id", "conversation_id", "turn_id", "message_id", "role"],
            quality_rules={
                "level": "== 5",
                "role": "in ['user', 'assistant', 'tool', 'system']",
                "text": "not_null",
            },
            semantic_rules={
                "conversation_id": "must_exist_in_l8",
                "turn_id": "must_exist_in_l6",
            },
        )["contract_id"]
        
        # Add more stages as needed...
        
        return contracts
