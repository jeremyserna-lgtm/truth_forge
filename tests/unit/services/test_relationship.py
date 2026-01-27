"""Tests for relationship service module.

Tests the relationship management service.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.relationship.service import RelationshipService


class TestRelationshipService:
    """Tests for RelationshipService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert RelationshipService.service_name == "relationship"

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_process_missing_partner_id(self, mock_logger: MagicMock) -> None:
        """Test process raises for missing partner_id."""
        service = RelationshipService.__new__(RelationshipService)

        record = {"interaction_type": "test_type"}

        with pytest.raises(ValueError) as exc_info:
            service.process(record)

        assert "partner_id" in str(exc_info.value)

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_process_missing_interaction_type(self, mock_logger: MagicMock) -> None:
        """Test process raises for missing interaction_type."""
        service = RelationshipService.__new__(RelationshipService)

        record = {"partner_id": "partner_123"}

        with pytest.raises(ValueError) as exc_info:
            service.process(record)

        assert "interaction_type" in str(exc_info.value)

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_process_valid_input(self, mock_logger: MagicMock) -> None:
        """Test process with valid input."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            # Mock get_partnership to return None (new partnership)
            with patch.object(service, "get_partnership", return_value=None):
                with patch.object(service, "_write_to_hold2"):
                    record = {
                        "partner_id": "partner_123",
                        "interaction_type": "positive_feedback",
                        "metadata": {"note": "test"},
                    }
                    result = service.process(record)

                    assert result == record

    def test_create_schema(self) -> None:
        """Test create_schema returns valid SQL."""
        service = RelationshipService.__new__(RelationshipService)
        schema = service.create_schema()

        assert "CREATE TABLE IF NOT EXISTS" in schema
        assert "relationship_records" in schema
        assert "id VARCHAR PRIMARY KEY" in schema
        assert "data JSON NOT NULL" in schema

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_get_partnership_no_db(self, mock_logger: MagicMock) -> None:
        """Test get_partnership when database doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold2"].mkdir()

            result = service.get_partnership("partner_123")
            assert result is None

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    @patch("duckdb.connect")
    def test_get_partnership_found(self, mock_connect: MagicMock, mock_logger: MagicMock) -> None:
        """Test get_partnership when partnership exists."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            hold2_path = Path(tmpdir) / "hold2"
            hold2_path.mkdir()
            # Create dummy db file
            (hold2_path / "relationship.duckdb").touch()

            service._paths = {
                "root": Path(tmpdir),
                "hold2": hold2_path,
            }

            mock_conn = MagicMock()
            partnership_data = {"partner_id": "partner_123", "trust_level": 0.8}
            mock_conn.execute.return_value.fetchone.return_value = (json.dumps(partnership_data),)
            mock_connect.return_value = mock_conn

            result = service.get_partnership("partner_123")

            assert result == partnership_data
            mock_conn.close.assert_called_once()

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    @patch("duckdb.connect")
    def test_get_partnership_not_found(self, mock_connect: MagicMock, mock_logger: MagicMock) -> None:
        """Test get_partnership when partnership not found."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            hold2_path = Path(tmpdir) / "hold2"
            hold2_path.mkdir()
            (hold2_path / "relationship.duckdb").touch()

            service._paths = {
                "root": Path(tmpdir),
                "hold2": hold2_path,
            }

            mock_conn = MagicMock()
            mock_conn.execute.return_value.fetchone.return_value = None
            mock_connect.return_value = mock_conn

            result = service.get_partnership("unknown_partner")

            assert result is None
            mock_conn.close.assert_called_once()

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_new_partnership(self, mock_logger: MagicMock) -> None:
        """Test update_interaction creates new partnership."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            with patch.object(service, "get_partnership", return_value=None):
                with patch.object(service, "_write_to_hold2") as mock_write:
                    result = service.update_interaction(
                        "new_partner", "initial_contact", {"source": "web"}
                    )

                    assert result["partner_id"] == "new_partner"
                    assert result["trust_level"] == 0.5
                    assert result["interaction_count"] == 1
                    assert len(result["history"]) == 1
                    mock_write.assert_called_once()

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_positive_feedback(self, mock_logger: MagicMock) -> None:
        """Test update_interaction increases trust on positive feedback."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.5,
                "interaction_count": 5,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "positive_feedback")

                    assert result["trust_level"] == 0.55  # 0.5 + 0.05
                    assert result["interaction_count"] == 6

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_successful_collaboration(self, mock_logger: MagicMock) -> None:
        """Test update_interaction increases trust on successful collaboration."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.7,
                "interaction_count": 10,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "successful_collaboration")

                    assert result["trust_level"] == 0.75  # 0.7 + 0.05

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_negative_feedback(self, mock_logger: MagicMock) -> None:
        """Test update_interaction decreases trust on negative feedback."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.5,
                "interaction_count": 5,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "negative_feedback")

                    assert result["trust_level"] == 0.4  # 0.5 - 0.1

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_failed_collaboration(self, mock_logger: MagicMock) -> None:
        """Test update_interaction decreases trust on failed collaboration."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.3,
                "interaction_count": 5,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "failed_collaboration")

                    assert abs(result["trust_level"] - 0.2) < 0.001  # 0.3 - 0.1

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_trust_max_cap(self, mock_logger: MagicMock) -> None:
        """Test update_interaction trust level caps at 1.0."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.98,
                "interaction_count": 100,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "positive_feedback")

                    assert result["trust_level"] == 1.0  # Capped at 1.0

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_trust_min_cap(self, mock_logger: MagicMock) -> None:
        """Test update_interaction trust level caps at 0.0."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.05,
                "interaction_count": 100,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "failed_collaboration")

                    assert result["trust_level"] == 0.0  # Capped at 0.0

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_neutral_type(self, mock_logger: MagicMock) -> None:
        """Test update_interaction with neutral interaction type."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            existing_partnership = {
                "partner_id": "partner_123",
                "trust_level": 0.5,
                "interaction_count": 5,
                "last_interaction": None,
                "preferences": {},
                "history": [],
            }

            with patch.object(service, "get_partnership", return_value=existing_partnership):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction("partner_123", "information_request")

                    assert result["trust_level"] == 0.5  # No change

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_logs_update(self, mock_logger: MagicMock) -> None:
        """Test update_interaction logs the update."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            with patch.object(service, "get_partnership", return_value=None):
                with patch.object(service, "_write_to_hold2"):
                    service.update_interaction("partner_123", "test_interaction")

                    mock_logger.info.assert_called()
                    call_args = mock_logger.info.call_args
                    assert call_args[0][0] == "partnership_updated"

    @patch.object(RelationshipService, "logger", new_callable=lambda: MagicMock())
    def test_update_interaction_history_record(self, mock_logger: MagicMock) -> None:
        """Test update_interaction properly records interaction in history."""
        with TemporaryDirectory() as tmpdir:
            service = RelationshipService.__new__(RelationshipService)
            service._paths = {
                "root": Path(tmpdir),
                "hold1": Path(tmpdir) / "hold1",
                "hold2": Path(tmpdir) / "hold2",
            }
            service._paths["hold1"].mkdir()
            service._paths["hold2"].mkdir()
            service._lock = threading.RLock()

            with patch.object(service, "get_partnership", return_value=None):
                with patch.object(service, "_write_to_hold2"):
                    result = service.update_interaction(
                        "partner_123", "test_type", {"key": "value"}
                    )

                    assert len(result["history"]) == 1
                    history_item = result["history"][0]
                    assert history_item["type"] == "test_type"
                    assert history_item["metadata"] == {"key": "value"}
                    assert "timestamp" in history_item

