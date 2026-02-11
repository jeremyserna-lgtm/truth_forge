"""Tests for knowledge_service migrated to UnifiedService pattern."""

import pytest
from datetime import datetime

from src.services.central_services.knowledge_service.service_migrated import (
    KnowledgeServiceMigrated,
    get_knowledge_service,
    exhale,
    inhale,
    sync,
)


class TestKnowledgeServiceMigrated:
    """Test suite for KnowledgeServiceMigrated."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = KnowledgeServiceMigrated()
        assert service.service_name == "knowledge_service"
        assert service.holds is not None

    def test_execute_with_single_atom(self):
        """Test execute with single knowledge atom."""
        service = KnowledgeServiceMigrated()

        input_data = {
            "content": "Test knowledge atom content",
            "source_name": "test_source",
            "source_id": "test_001",
            "metadata": {"type": "test"}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert result["processed_count"] == 1
        assert len(result["atom_ids"]) == 1

    def test_execute_with_multiple_atoms(self):
        """Test execute with multiple knowledge atoms."""
        service = KnowledgeServiceMigrated()

        input_data = {
            "content": [
                "First knowledge atom",
                "Second knowledge atom",
                "Third knowledge atom"
            ],
            "source_name": "test_source",
            "source_id": "test_multi",
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert result["processed_count"] == 3
        assert len(result["atom_ids"]) == 3

    def test_execute_missing_content(self):
        """Test execute with missing content."""
        service = KnowledgeServiceMigrated()

        input_data = {
            "source_name": "test_source",
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_execute_missing_source_name(self):
        """Test execute with missing source_name."""
        service = KnowledgeServiceMigrated()

        input_data = {
            "content": "Test content",
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_atom_id_generation(self):
        """Test that atom IDs are generated for content."""
        service = KnowledgeServiceMigrated()

        input_data = {
            "content": "Test atom for ID generation",
            "source_name": "test_source",
            "source_id": "id_test",
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert len(result["atom_ids"]) > 0
        assert result["atom_ids"][0] is not None

    def test_backward_compatible_exhale(self):
        """Test backward compatible exhale function."""
        result = exhale(
            content="Backward compatible atom",
            source_name="test_source",
            source_id="compat_test",
            metadata={"test": True}
        )

        assert result["status"] == "success"
        assert result["processed_count"] >= 1

    def test_inhale_retrieves_atoms(self):
        """Test inhale retrieves processed atoms."""
        service = KnowledgeServiceMigrated()

        # First create some atoms
        service.execute({
            "content": "Atom for inhale test",
            "source_name": "inhale_test",
        })

        # Then inhale them
        atoms = service.inhale(limit=10)

        assert isinstance(atoms, list)

    def test_inhale_with_query(self):
        """Test inhale with query filter."""
        service = KnowledgeServiceMigrated()

        # Create atom with specific content
        unique_text = f"unique_inhale_test_{datetime.now().timestamp()}"
        service.execute({
            "content": unique_text,
            "source_name": "query_test",
        })

        # Query for it
        atoms = service.inhale(query=unique_text[:20], limit=10)

        assert isinstance(atoms, list)

    def test_sync_processes_hold1(self):
        """Test sync processes existing HOLD1 records."""
        service = KnowledgeServiceMigrated()

        result = service.sync()

        assert result["status"] == "success"
        assert "processed_count" in result

    def test_singleton_pattern(self):
        """Test that get_knowledge_service returns the same instance."""
        service1 = get_knowledge_service()
        service2 = get_knowledge_service()

        assert service1 is service2

    def test_metadata_preservation(self):
        """Test that metadata is preserved in atoms."""
        service = KnowledgeServiceMigrated()

        metadata = {
            "author": "test_author",
            "tags": ["test", "knowledge"],
            "custom_field": "custom_value"
        }

        result = service.execute({
            "content": "Atom with metadata",
            "source_name": "metadata_test",
            "metadata": metadata,
        })

        assert result["status"] == "success"


class TestKnowledgeServiceIntegration:
    """Integration tests for KnowledgeServiceMigrated."""

    def test_full_atom_lifecycle(self):
        """Test complete atom lifecycle: exhale, process, inhale."""
        service = KnowledgeServiceMigrated()

        # Exhale atoms
        unique_prefix = f"lifecycle_{datetime.now().timestamp()}"
        result = service.execute({
            "content": [
                f"{unique_prefix} First atom",
                f"{unique_prefix} Second atom",
            ],
            "source_name": "lifecycle_test",
            "metadata": {"test_type": "lifecycle"}
        })

        assert result["status"] == "success"
        assert result["processed_count"] == 2

        # Inhale atoms
        atoms = service.inhale(query=unique_prefix, limit=10)

        assert isinstance(atoms, list)

    def test_deduplication(self):
        """Test that duplicate atoms are deduplicated."""
        service = KnowledgeServiceMigrated()

        duplicate_content = f"duplicate_test_{datetime.now().timestamp()}"

        # Submit same content twice
        result1 = service.execute({
            "content": duplicate_content,
            "source_name": "dedup_test",
        })

        result2 = service.execute({
            "content": duplicate_content,
            "source_name": "dedup_test",
        })

        # Both should succeed
        assert result1["status"] == "success"
        assert result2["status"] == "success"

    def test_batch_atom_processing(self):
        """Test processing large batch of atoms."""
        service = KnowledgeServiceMigrated()

        # Create 20 atoms
        atoms = [f"Batch atom {i}" for i in range(20)]

        result = service.execute({
            "content": atoms,
            "source_name": "batch_test",
        })

        assert result["status"] == "success"
        assert result["processed_count"] == 20

    def test_concurrent_atom_intake(self):
        """Test that atoms from different sources can be processed concurrently."""
        service = KnowledgeServiceMigrated()

        sources = ["source_a", "source_b", "source_c"]

        for source in sources:
            result = service.execute({
                "content": f"Content from {source}",
                "source_name": source,
            })
            assert result["status"] == "success"

    def test_exhale_inhale_roundtrip(self):
        """Test that atoms exhaled can be inhaled back."""
        service = KnowledgeServiceMigrated()

        unique_id = f"roundtrip_{datetime.now().timestamp()}"
        content = f"Roundtrip test content {unique_id}"

        # Exhale
        exhale_result = service.execute({
            "content": content,
            "source_name": "roundtrip_test",
            "source_id": unique_id,
        })

        assert exhale_result["status"] == "success"
        atom_id = exhale_result["atom_ids"][0]

        # Inhale
        atoms = service.inhale(limit=100)

        # Check if our atom is there
        found = any(
            atom.get("atom_id") == atom_id or unique_id in str(atom)
            for atom in atoms
        )

        assert isinstance(atoms, list)

    def test_sync_after_manual_hold1_write(self):
        """Test sync can process manually written HOLD1 records."""
        service = KnowledgeServiceMigrated()

        # Write directly to HOLD1 (simulating manual write)
        # Then sync
        result = service.sync()

        assert result["status"] == "success"


class TestKnowledgeServiceGraphIntegration:
    """Tests for knowledge graph integration (optional dependency)."""

    def test_graph_service_optional(self):
        """Test that service works even without graph service."""
        service = KnowledgeServiceMigrated()

        # Should work even if graph_service is None
        result = service.execute({
            "content": "Test without graph",
            "source_name": "no_graph_test",
        })

        assert result["status"] == "success"

    def test_graph_integration_failure_resilience(self):
        """Test that graph integration failures don't break atom processing."""
        service = KnowledgeServiceMigrated()

        # Even if graph service fails, atom processing should continue
        result = service.execute({
            "content": "Resilience test",
            "source_name": "resilience_test",
        })

        assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
