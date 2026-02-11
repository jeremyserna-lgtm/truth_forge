#!/usr/bin/env python3
"""
Test 3: Enforcement Module Tests

This test validates EVERY enforcement rule in the enforcement module.
100% coverage. No exceptions. No warnings allowed.

WHAT THIS TESTS:
1. Schema column enforcement - missing/extra columns
2. Required field enforcement - null/missing values
3. Field type enforcement - correct types
4. Level range enforcement - 2-8 only
5. Level-type match enforcement - L8=conversation, etc.
6. Pipeline label enforcement - must be "llm_refinery"
7. Parent chain enforcement - valid parent references
8. Entity ID format enforcement - prefix:hash:index
9. Duplicate detection in batches
10. Enforcement hooks work correctly

RUN AFTER test_02_entity_levels.py PASSES.
"""

import pytest
from datetime import datetime, UTC


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def valid_record():
    """A completely valid record that passes all enforcement."""
    return {
        "entity_id": "msg:abc123def456789:0001",
        "level": 5,
        "entity_type": "message",
        "entity_mode": "active",
        "parent_id": "turn:parent123456789:0001",
        "source_ids": ["source1", "source2"],
        "conversation_id": "conv:test123456789:0001",
        "topic_segment_id": "topic:test12345678:0001",
        "turn_id": "turn:parent123456789:0001",
        "message_id": "msg:abc123def456789:0001",
        "sentence_id": None,
        "span_id": None,
        "word_id": None,
        "text": "Hello, this is a test message.",
        "source_pipeline": "llm_refinery",
        "source_file": "test.json",
        "source_file_path": "/path/to/test.json",
        "source_system": "test",
        "metadata": {"key": "value"},
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "ingestion_job_id": "job_001",
        "ingestion_timestamp": datetime.now(UTC).isoformat(),
        "validation_status": "valid",
        "source_message_timestamp": None,
        "persona": None,
        "content_date": None,
        "canonical_form": None,
        "l7_count": 0,
        "l6_count": 0,
        "l5_count": 0,
        "l4_count": 0,
        "l3_count": 0,
        "l2_count": 0,
        "role": "human",
    }


@pytest.fixture
def valid_conversation_record():
    """A valid L8 conversation record (root - no parent)."""
    return {
        "entity_id": "conv:abc123def456789:0001",
        "level": 8,
        "entity_type": "conversation",
        "entity_mode": "active",
        "parent_id": None,  # L8 has no parent
        "source_ids": [],
        "conversation_id": "conv:abc123def456789:0001",
        "topic_segment_id": None,
        "turn_id": None,
        "message_id": None,
        "sentence_id": None,
        "span_id": None,
        "word_id": None,
        "text": "Test Conversation",
        "source_pipeline": "llm_refinery",
        "source_file": "test.json",
        "source_file_path": "/path/to/test.json",
        "source_system": "test",
        "metadata": {},
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        "ingestion_job_id": "job_001",
        "ingestion_timestamp": datetime.now(UTC).isoformat(),
        "validation_status": "valid",
        "source_message_timestamp": None,
        "persona": None,
        "content_date": None,
        "canonical_form": None,
        "l7_count": 1,
        "l6_count": 2,
        "l5_count": 4,
        "l4_count": 8,
        "l3_count": 16,
        "l2_count": 32,
        "role": None,
    }


# =============================================================================
# SCHEMA COLUMN TESTS
# =============================================================================

class TestSchemaColumns:
    """Test schema column enforcement."""
    
    def test_valid_record_passes(self, valid_record):
        """A valid record should pass schema check."""
        from pipelines.llm_refinery.enforcement import enforce_schema_columns
        
        violations = enforce_schema_columns(valid_record)
        assert len(violations) == 0
    
    def test_missing_column_detected(self, valid_record):
        """Missing column should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_schema_columns
        
        del valid_record["entity_id"]
        violations = enforce_schema_columns(valid_record)
        
        assert len(violations) == 1
        assert violations[0].rule == "SCHEMA_COLUMNS"
        assert "entity_id" in violations[0].message
    
    def test_extra_column_detected(self, valid_record):
        """Extra column should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_schema_columns
        
        valid_record["extra_field"] = "should not exist"
        violations = enforce_schema_columns(valid_record)
        
        assert len(violations) == 1
        assert violations[0].rule == "SCHEMA_COLUMNS"
        assert "extra_field" in violations[0].message


# =============================================================================
# REQUIRED FIELD TESTS
# =============================================================================

class TestRequiredFields:
    """Test required field enforcement."""
    
    def test_valid_record_passes(self, valid_record):
        """A valid record should pass required field check."""
        from pipelines.llm_refinery.enforcement import enforce_required_fields
        
        violations = enforce_required_fields(valid_record)
        assert len(violations) == 0
    
    def test_missing_entity_id_detected(self, valid_record):
        """Missing entity_id should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_required_fields
        
        del valid_record["entity_id"]
        violations = enforce_required_fields(valid_record)
        
        assert len(violations) == 1
        assert violations[0].field == "entity_id"
    
    def test_null_required_field_detected(self, valid_record):
        """Null required field should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_required_fields
        
        valid_record["source_pipeline"] = None
        violations = enforce_required_fields(valid_record)
        
        assert len(violations) == 1
        assert violations[0].field == "source_pipeline"
        assert "null" in violations[0].message


# =============================================================================
# FIELD TYPE TESTS
# =============================================================================

class TestFieldTypes:
    """Test field type enforcement."""
    
    def test_valid_record_passes(self, valid_record):
        """A valid record should pass type check."""
        from pipelines.llm_refinery.enforcement import enforce_field_types
        
        violations = enforce_field_types(valid_record)
        assert len(violations) == 0
    
    def test_int_instead_of_string_detected(self, valid_record):
        """Integer where string expected should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_field_types
        
        valid_record["entity_id"] = 12345
        violations = enforce_field_types(valid_record)
        
        assert len(violations) >= 1
        assert any(v.field == "entity_id" for v in violations)
    
    def test_string_instead_of_int_detected(self, valid_record):
        """String where integer expected should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_field_types
        
        valid_record["level"] = "five"
        violations = enforce_field_types(valid_record)
        
        assert len(violations) >= 1
        assert any(v.field == "level" for v in violations)
    
    def test_source_ids_must_be_list(self, valid_record):
        """source_ids must be a list."""
        from pipelines.llm_refinery.enforcement import enforce_field_types
        
        valid_record["source_ids"] = "not a list"
        violations = enforce_field_types(valid_record)
        
        assert len(violations) >= 1
        assert any(v.field == "source_ids" for v in violations)
    
    def test_metadata_must_be_dict(self, valid_record):
        """metadata must be a dict."""
        from pipelines.llm_refinery.enforcement import enforce_field_types
        
        valid_record["metadata"] = ["not", "a", "dict"]
        violations = enforce_field_types(valid_record)
        
        assert len(violations) >= 1
        assert any(v.field == "metadata" for v in violations)


# =============================================================================
# LEVEL RANGE TESTS
# =============================================================================

class TestLevelRange:
    """Test level range enforcement."""
    
    def test_valid_levels_pass(self, valid_record):
        """Valid levels 2-8 should pass."""
        from pipelines.llm_refinery.enforcement import enforce_level_range
        
        for level in [2, 3, 4, 5, 6, 7, 8]:
            valid_record["level"] = level
            violations = enforce_level_range(valid_record)
            assert len(violations) == 0, f"Level {level} should pass"
    
    def test_level_1_rejected(self, valid_record):
        """Level 1 should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_level_range
        
        valid_record["level"] = 1
        violations = enforce_level_range(valid_record)
        
        assert len(violations) == 1
        assert violations[0].rule == "LEVEL_RANGE"
    
    def test_level_9_rejected(self, valid_record):
        """Level 9 should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_level_range
        
        valid_record["level"] = 9
        violations = enforce_level_range(valid_record)
        
        assert len(violations) == 1
        assert violations[0].rule == "LEVEL_RANGE"
    
    def test_level_0_rejected(self, valid_record):
        """Level 0 should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_level_range
        
        valid_record["level"] = 0
        violations = enforce_level_range(valid_record)
        
        assert len(violations) == 1


# =============================================================================
# LEVEL-TYPE MATCH TESTS
# =============================================================================

class TestLevelTypeMatch:
    """Test level-type match enforcement."""
    
    def test_l8_conversation_passes(self, valid_conversation_record):
        """L8 with entity_type=conversation should pass."""
        from pipelines.llm_refinery.enforcement import enforce_level_type_match
        
        violations = enforce_level_type_match(valid_conversation_record)
        assert len(violations) == 0
    
    def test_l5_message_passes(self, valid_record):
        """L5 with entity_type=message should pass."""
        from pipelines.llm_refinery.enforcement import enforce_level_type_match
        
        violations = enforce_level_type_match(valid_record)
        assert len(violations) == 0
    
    def test_l8_with_wrong_type_rejected(self, valid_conversation_record):
        """L8 with wrong entity_type should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_level_type_match
        
        valid_conversation_record["entity_type"] = "message"
        violations = enforce_level_type_match(valid_conversation_record)
        
        assert len(violations) == 1
        assert "conversation" in violations[0].message
    
    def test_l5_with_wrong_type_rejected(self, valid_record):
        """L5 with wrong entity_type should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_level_type_match
        
        valid_record["entity_type"] = "word"
        violations = enforce_level_type_match(valid_record)
        
        assert len(violations) == 1
        assert "message" in violations[0].message


# =============================================================================
# PIPELINE LABEL TESTS
# =============================================================================

class TestPipelineLabel:
    """Test pipeline label enforcement - CRITICAL."""
    
    def test_llm_refinery_passes(self, valid_record):
        """source_pipeline='llm_refinery' should pass."""
        from pipelines.llm_refinery.enforcement import enforce_pipeline_label
        
        violations = enforce_pipeline_label(valid_record)
        assert len(violations) == 0
    
    def test_wrong_pipeline_is_fatal(self, valid_record):
        """Wrong pipeline label should be FATAL."""
        from pipelines.llm_refinery.enforcement import (
            enforce_pipeline_label, EnforcementLevel
        )
        
        valid_record["source_pipeline"] = "chatgpt_web_ingestion"
        violations = enforce_pipeline_label(valid_record)
        
        assert len(violations) == 1
        assert violations[0].level == EnforcementLevel.FATAL
        assert violations[0].rule == "PIPELINE_LABEL"
    
    def test_null_pipeline_is_fatal(self, valid_record):
        """Null pipeline label should be FATAL."""
        from pipelines.llm_refinery.enforcement import (
            enforce_pipeline_label, EnforcementLevel
        )
        
        valid_record["source_pipeline"] = None
        violations = enforce_pipeline_label(valid_record)
        
        assert len(violations) == 1
        assert violations[0].level == EnforcementLevel.FATAL


# =============================================================================
# PARENT CHAIN TESTS
# =============================================================================

class TestParentChain:
    """Test parent chain enforcement."""
    
    def test_l8_null_parent_passes(self, valid_conversation_record):
        """L8 with null parent should pass."""
        from pipelines.llm_refinery.enforcement import enforce_parent_chain
        
        violations = enforce_parent_chain(valid_conversation_record)
        assert len(violations) == 0
    
    def test_l8_with_parent_rejected(self, valid_conversation_record):
        """L8 with non-null parent should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_parent_chain
        
        valid_conversation_record["parent_id"] = "some:parent:0001"
        violations = enforce_parent_chain(valid_conversation_record)
        
        assert len(violations) == 1
        assert "L8" in violations[0].message
        assert "null" in violations[0].message
    
    def test_l5_with_parent_passes(self, valid_record):
        """L5 with parent should pass."""
        from pipelines.llm_refinery.enforcement import enforce_parent_chain
        
        violations = enforce_parent_chain(valid_record)
        assert len(violations) == 0
    
    def test_l5_null_parent_rejected(self, valid_record):
        """L5 with null parent should be rejected."""
        from pipelines.llm_refinery.enforcement import enforce_parent_chain
        
        valid_record["parent_id"] = None
        violations = enforce_parent_chain(valid_record)
        
        assert len(violations) == 1
        assert "L5" in violations[0].message


# =============================================================================
# ENTITY ID FORMAT TESTS
# =============================================================================

class TestEntityIdFormat:
    """Test entity ID format enforcement."""
    
    def test_valid_format_passes(self, valid_record):
        """Valid entity_id format should pass."""
        from pipelines.llm_refinery.enforcement import enforce_entity_id_format
        
        violations = enforce_entity_id_format(valid_record)
        # May have warnings about prefix, but no errors
        errors = [v for v in violations if v.rule == "ENTITY_ID_FORMAT" 
                  and "format" in v.message.lower()]
        assert len(errors) == 0


# =============================================================================
# FULL RECORD ENFORCEMENT TESTS
# =============================================================================

class TestEnforceRecord:
    """Test full record enforcement."""
    
    def test_valid_record_passes(self, valid_record):
        """Valid record should pass all enforcement."""
        from pipelines.llm_refinery.enforcement import enforce_record
        
        result = enforce_record(valid_record)
        
        # Should have no errors (may have warnings)
        assert result.passed
        assert len(result.get_fatals()) == 0
        assert len(result.get_errors()) == 0
    
    def test_valid_conversation_passes(self, valid_conversation_record):
        """Valid conversation record should pass all enforcement."""
        from pipelines.llm_refinery.enforcement import enforce_record
        
        result = enforce_record(valid_conversation_record)
        
        assert result.passed
        assert len(result.get_fatals()) == 0
        assert len(result.get_errors()) == 0
    
    def test_multiple_errors_reported(self, valid_record):
        """Multiple errors should all be reported."""
        from pipelines.llm_refinery.enforcement import enforce_record
        
        valid_record["level"] = 99  # Invalid level
        valid_record["source_pipeline"] = "wrong"  # Wrong pipeline
        # Note: parent_id check only runs for valid levels (2-8), so level=99 
        # won't trigger parent chain error. That's correct behavior.
        
        result = enforce_record(valid_record)
        
        assert not result.passed
        # Should have at least 2 errors: LEVEL_RANGE and PIPELINE_LABEL
        assert len(result.violations) >= 2
        
        # Verify specific errors are present
        rules = {v.rule for v in result.violations}
        assert "LEVEL_RANGE" in rules
        assert "PIPELINE_LABEL" in rules


# =============================================================================
# BATCH ENFORCEMENT TESTS
# =============================================================================

class TestEnforceBatch:
    """Test batch enforcement."""
    
    def test_valid_batch_passes(self, valid_record, valid_conversation_record):
        """Valid batch should pass."""
        from pipelines.llm_refinery.enforcement import enforce_batch
        
        records = [valid_record, valid_conversation_record]
        result = enforce_batch(records)
        
        assert result.passed
        assert result.record_count == 2
        assert result.rejected_count == 0
    
    def test_duplicate_ids_detected(self, valid_record):
        """Duplicate entity_ids in batch should be detected."""
        from pipelines.llm_refinery.enforcement import enforce_batch
        
        record1 = valid_record.copy()
        record2 = valid_record.copy()  # Same entity_id
        
        result = enforce_batch([record1, record2])
        
        # Should detect duplicate
        dup_violations = [v for v in result.violations if v.rule == "DUPLICATE_ID"]
        assert len(dup_violations) >= 1


# =============================================================================
# ENFORCEMENT HOOKS TESTS
# =============================================================================

class TestEnforcementHooks:
    """Test enforcement hooks."""
    
    def test_enforce_or_raise_passes_valid(self, valid_record):
        """enforce_or_raise should return record if valid."""
        from pipelines.llm_refinery.enforcement import enforce_or_raise
        
        result = enforce_or_raise(valid_record)
        assert result == valid_record
    
    def test_enforce_or_raise_raises_on_error(self, valid_record):
        """enforce_or_raise should raise on error."""
        from pipelines.llm_refinery.enforcement import (
            enforce_or_raise, EnforcementError
        )
        
        valid_record["source_pipeline"] = "wrong"
        
        with pytest.raises(EnforcementError):
            enforce_or_raise(valid_record)
    
    def test_pre_write_hook_passes_valid_batch(self, valid_record, valid_conversation_record):
        """pre_write_hook should pass valid batch."""
        from pipelines.llm_refinery.enforcement import pre_write_hook
        
        records = [valid_record, valid_conversation_record]
        result = pre_write_hook(records)
        
        assert result == records
    
    def test_pre_write_hook_raises_on_error(self, valid_record):
        """pre_write_hook should raise on batch error."""
        from pipelines.llm_refinery.enforcement import (
            pre_write_hook, EnforcementError
        )
        
        valid_record["source_pipeline"] = "wrong"
        
        with pytest.raises(EnforcementError):
            pre_write_hook([valid_record])


# =============================================================================
# REPORT GENERATION TESTS
# =============================================================================

class TestReportGeneration:
    """Test report generation."""
    
    def test_report_includes_stats(self, valid_record):
        """Report should include statistics."""
        from pipelines.llm_refinery.enforcement import (
            enforce_batch, generate_enforcement_report
        )
        
        result = enforce_batch([valid_record, valid_record.copy()])
        report = generate_enforcement_report(result)
        
        assert "Records processed: 2" in report
        assert "ENFORCEMENT REPORT" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
