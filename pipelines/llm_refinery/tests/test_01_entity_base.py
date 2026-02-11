#!/usr/bin/env python3
"""
Test 1: EntityBase Model Validation

This test file validates the FOUNDATION of the pipeline - the EntityBase class.
Every other model inherits from this. If this is wrong, EVERYTHING is wrong.

WHAT THIS TESTS:
1. EntityBase can be instantiated with required fields
2. EntityBase validates field types correctly
3. to_entity_unified() produces correct output schema
4. to_entity_unified() output matches BigQuery schema EXACTLY
5. Entity ID format is correct
6. Parent chain fields are set correctly
7. Timestamps are valid
8. Sentiment clamping works

RUN THIS TEST BEFORE ANY OTHER TESTS.
"""

import pytest
from datetime import datetime, UTC
from typing import Any

# BigQuery schema - THE SOURCE OF TRUTH
# Copied from: bq query 'SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = "entity_unified"'
BIGQUERY_SCHEMA_COLUMNS = {
    "entity_id",
    "level", 
    "entity_type",
    "entity_mode",
    "parent_id",
    "source_ids",
    "conversation_id",
    "topic_segment_id",
    "turn_id",
    "message_id",
    "sentence_id",
    "span_id",
    "word_id",
    "text",
    "source_pipeline",
    "source_file",
    "source_file_path",
    "source_system",
    "metadata",
    "created_at",
    "updated_at",
    "ingestion_job_id",
    "ingestion_timestamp",
    "validation_status",
    "source_message_timestamp",
    "persona",
    "content_date",
    "canonical_form",
    "l7_count",
    "l6_count",
    "l5_count",
    "l4_count",
    "l3_count",
    "l2_count",
    "role",
}


class TestEntityBaseInstantiation:
    """Test that EntityBase can be created with valid inputs."""
    
    def test_create_with_required_fields(self):
        """EntityBase requires: entity_id, level, entity_type, text"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:abc123:0001",
            level=5,
            entity_type="message",
            text="Hello world"
        )
        
        assert entity.entity_id == "test:abc123:0001"
        assert entity.level == 5
        assert entity.entity_type == "message"
        assert entity.text == "Hello world"
    
    def test_default_source_pipeline(self):
        """source_pipeline defaults to 'llm_refinery'"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        assert entity.source_pipeline == "llm_refinery"
    
    def test_default_parent_id_is_none(self):
        """parent_id defaults to None"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        assert entity.parent_id is None
    
    def test_hierarchy_ids_default_to_none(self):
        """All hierarchy IDs (conversation_id, turn_id, etc.) default to None"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        assert entity.conversation_id is None
        assert entity.topic_segment_id is None
        assert entity.turn_id is None
        assert entity.message_id is None
        assert entity.sentence_id is None
        assert entity.span_id is None
        assert entity.word_id is None
    
    def test_count_fields_default_to_zero(self):
        """All count fields (l2_count through l7_count) default to 0"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        assert entity.l7_count == 0
        assert entity.l6_count == 0
        assert entity.l5_count == 0
        assert entity.l4_count == 0
        assert entity.l3_count == 0
        assert entity.l2_count == 0


class TestEntityBaseValidation:
    """Test that EntityBase validates inputs correctly."""
    
    def test_rejects_missing_entity_id(self):
        """Must raise error if entity_id is missing"""
        from pipelines.llm_refinery.models import EntityBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EntityBase(
                level=5,
                entity_type="message",
                text="Test"
            )
    
    def test_rejects_missing_level(self):
        """Must raise error if level is missing"""
        from pipelines.llm_refinery.models import EntityBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EntityBase(
                entity_id="test:001",
                entity_type="message",
                text="Test"
            )
    
    def test_rejects_missing_entity_type(self):
        """Must raise error if entity_type is missing"""
        from pipelines.llm_refinery.models import EntityBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EntityBase(
                entity_id="test:001",
                level=5,
                text="Test"
            )
    
    def test_rejects_missing_text(self):
        """Must raise error if text is missing"""
        from pipelines.llm_refinery.models import EntityBase
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EntityBase(
                entity_id="test:001",
                level=5,
                entity_type="message"
            )


class TestSentimentClamping:
    """Test the clamp_sentiment helper function."""
    
    def test_clamp_valid_value(self):
        """Values in [-1, 1] should pass through unchanged"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment(0.5) == 0.5
        assert clamp_sentiment(-0.5) == -0.5
        assert clamp_sentiment(0.0) == 0.0
    
    def test_clamp_boundary_values(self):
        """Boundary values -1 and 1 should pass through"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment(1.0) == 1.0
        assert clamp_sentiment(-1.0) == -1.0
    
    def test_clamp_high_value(self):
        """Values > 1 should be clamped to 1"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment(1.5) == 1.0
        assert clamp_sentiment(100.0) == 1.0
    
    def test_clamp_low_value(self):
        """Values < -1 should be clamped to -1"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment(-1.5) == -1.0
        assert clamp_sentiment(-100.0) == -1.0
    
    def test_clamp_none(self):
        """None input should return None"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment(None) is None
    
    def test_clamp_invalid_type(self):
        """Invalid types should return None"""
        from pipelines.llm_refinery.models import clamp_sentiment
        
        assert clamp_sentiment("not a number") is None
        assert clamp_sentiment([1, 2, 3]) is None
        assert clamp_sentiment({"value": 0.5}) is None


class TestEntityIdGeneration:
    """Test the generate_id helper function."""
    
    def test_generate_id_format(self):
        """ID should be in format {prefix}:{hash16}:{index:04d}"""
        from pipelines.llm_refinery.models import generate_id
        
        entity_id = generate_id("msg", "hello world", "parent:001", 5)
        
        parts = entity_id.split(":")
        assert len(parts) == 3
        assert parts[0] == "msg"  # prefix
        assert len(parts[1]) == 16  # hash
        assert parts[2] == "0005"  # index with padding
    
    def test_generate_id_deterministic(self):
        """Same inputs should produce same ID"""
        from pipelines.llm_refinery.models import generate_id
        
        id1 = generate_id("msg", "hello", "parent", 0)
        id2 = generate_id("msg", "hello", "parent", 0)
        
        assert id1 == id2
    
    def test_generate_id_different_content(self):
        """Different content should produce different IDs"""
        from pipelines.llm_refinery.models import generate_id
        
        id1 = generate_id("msg", "hello", "parent", 0)
        id2 = generate_id("msg", "world", "parent", 0)
        
        assert id1 != id2
    
    def test_generate_id_different_parent(self):
        """Different parent should produce different IDs"""
        from pipelines.llm_refinery.models import generate_id
        
        id1 = generate_id("msg", "hello", "parent1", 0)
        id2 = generate_id("msg", "hello", "parent2", 0)
        
        assert id1 != id2
    
    def test_generate_id_different_index(self):
        """Different index should produce different IDs"""
        from pipelines.llm_refinery.models import generate_id
        
        id1 = generate_id("msg", "hello", "parent", 0)
        id2 = generate_id("msg", "hello", "parent", 1)
        
        assert id1 != id2


class TestToEntityUnified:
    """Test to_entity_unified() produces correct BigQuery output."""
    
    def test_output_has_all_bigquery_columns(self):
        """Output must have EXACTLY the columns in BigQuery schema"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:abc123:0001",
            level=5,
            entity_type="message",
            text="Hello world"
        )
        
        output = entity.to_entity_unified(
            ingestion_job_id="test_job_001",
            source_file="test.json",
            source_file_path="/path/to/test.json"
        )
        
        output_columns = set(output.keys())
        
        # Check for missing columns
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        assert not missing, f"Missing BigQuery columns: {missing}"
        
        # Check for extra columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        assert not extra, f"Extra columns not in BigQuery schema: {extra}"
    
    def test_output_entity_id_matches_input(self):
        """entity_id in output must match input"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:abc123:0001",
            level=5,
            entity_type="message",
            text="Hello world"
        )
        
        output = entity.to_entity_unified()
        
        assert output["entity_id"] == "test:abc123:0001"
    
    def test_output_level_matches_input(self):
        """level in output must match input"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert output["level"] == 5
    
    def test_output_entity_type_matches_input(self):
        """entity_type in output must match input"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert output["entity_type"] == "message"
    
    def test_output_text_matches_input(self):
        """text in output must match input"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Hello world test message"
        )
        
        output = entity.to_entity_unified()
        
        assert output["text"] == "Hello world test message"
    
    def test_output_source_pipeline_is_llm_refinery(self):
        """source_pipeline MUST be 'llm_refinery'"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert output["source_pipeline"] == "llm_refinery"
    
    def test_output_entity_mode_is_active(self):
        """entity_mode should be 'active'"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert output["entity_mode"] == "active"
    
    def test_output_timestamps_are_strings(self):
        """Timestamps must be ISO format strings for BigQuery"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        # created_at and updated_at must be strings
        assert isinstance(output["created_at"], str)
        assert isinstance(output["updated_at"], str)
        assert isinstance(output["ingestion_timestamp"], str)
    
    def test_output_count_fields_are_integers(self):
        """Count fields must be integers"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert isinstance(output["l7_count"], int)
        assert isinstance(output["l6_count"], int)
        assert isinstance(output["l5_count"], int)
        assert isinstance(output["l4_count"], int)
        assert isinstance(output["l3_count"], int)
        assert isinstance(output["l2_count"], int)
    
    def test_output_source_ids_is_list(self):
        """source_ids must be a list (for ARRAY<STRING>)"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert isinstance(output["source_ids"], list)
    
    def test_output_metadata_is_dict(self):
        """metadata must be a dict (for JSON type)"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=5,
            entity_type="message",
            text="Test"
        )
        
        output = entity.to_entity_unified()
        
        assert isinstance(output["metadata"], dict)


class TestValidLevelValues:
    """Test that level values are in valid range."""
    
    def test_level_2_is_valid(self):
        """Level 2 (word) should be valid"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=2,
            entity_type="word",
            text="hello"
        )
        
        assert entity.level == 2
    
    def test_level_8_is_valid(self):
        """Level 8 (conversation) should be valid"""
        from pipelines.llm_refinery.models import EntityBase
        
        entity = EntityBase(
            entity_id="test:001",
            level=8,
            entity_type="conversation",
            text="Full conversation"
        )
        
        assert entity.level == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
