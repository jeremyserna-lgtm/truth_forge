"""Tests for control plane module."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from truth_forge.governance.control_plane import (
    ControlPlaneError,
    LeaseRequest,
    TaskRequest,
    enqueue_task,
    heartbeat,
    kill_switch_status,
    record_audit,
    renew_lease,
)


class TestTaskRequest:
    """Test TaskRequest dataclass."""

    def test_to_json(self) -> None:
        """Test TaskRequest serialization."""
        task = TaskRequest(
            task_id="test-123",
            parent_id=None,
            payload={"key": "value"},
            ttl_seconds=900,
        )
        json_str = task.to_json()
        data = json.loads(json_str)
        assert data["task_id"] == "test-123"
        assert data["payload"] == {"key": "value"}
        assert data["ttl_seconds"] == 900
        assert "parent_id" not in data  # None values excluded

    def test_to_json_with_parent(self) -> None:
        """Test TaskRequest with parent_id."""
        task = TaskRequest(
            task_id="test-123",
            parent_id="parent-456",
            payload={},
            ttl_seconds=600,
        )
        json_str = task.to_json()
        data = json.loads(json_str)
        assert data["parent_id"] == "parent-456"

    def test_to_json_with_idempotency_key(self) -> None:
        """Test TaskRequest with idempotency_key."""
        task = TaskRequest(
            task_id="test-123",
            parent_id=None,
            payload={},
            idempotency_key="idempotent-key",
        )
        json_str = task.to_json()
        data = json.loads(json_str)
        assert data["idempotency_key"] == "idempotent-key"


class TestLeaseRequest:
    """Test LeaseRequest dataclass."""

    def test_to_json(self) -> None:
        """Test LeaseRequest serialization."""
        lease = LeaseRequest(
            task_id="task-123",
            worker_id="worker-456",
            lease_seconds=120,
        )
        json_str = lease.to_json()
        data = json.loads(json_str)
        assert data["task_id"] == "task-123"
        assert data["worker_id"] == "worker-456"
        assert data["lease_seconds"] == 120


class TestEnqueueTask:
    """Test enqueue_task function."""

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_enqueue_task_success(self, mock_post: Mock) -> None:
        """Test successful task enqueue."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"task_id": "test-123", "status": "queued"}
        mock_post.return_value = mock_response

        task = TaskRequest(task_id="test-123", parent_id=None, payload={})
        result = enqueue_task(task)

        assert result["task_id"] == "test-123"
        assert result["status"] == "queued"
        mock_post.assert_called_once()

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_enqueue_task_error(self, mock_post: Mock) -> None:
        """Test enqueue_task raises error on failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        task = TaskRequest(task_id="test-123", parent_id=None, payload={})
        with pytest.raises(ControlPlaneError, match="400"):
            enqueue_task(task)


class TestRenewLease:
    """Test renew_lease function."""

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_renew_lease_success(self, mock_post: Mock) -> None:
        """Test successful lease renewal."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"lease_id": "lease-123", "expires_at": 1234567890}
        mock_post.return_value = mock_response

        lease = LeaseRequest(task_id="task-123", worker_id="worker-456")
        result = renew_lease(lease)

        assert result["lease_id"] == "lease-123"
        mock_post.assert_called_once()

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_renew_lease_error(self, mock_post: Mock) -> None:
        """Test renew_lease raises error on failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        lease = LeaseRequest(task_id="task-123", worker_id="worker-456")
        with pytest.raises(ControlPlaneError, match="404"):
            renew_lease(lease)


class TestRecordAudit:
    """Test record_audit function."""

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_record_audit_success(self, mock_post: Mock) -> None:
        """Test successful audit recording."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        event = {"event_type": "test", "timestamp": 1234567890}
        record_audit(event)

        mock_post.assert_called_once()

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_record_audit_failure_swallowed(self, mock_post: Mock) -> None:
        """Test audit failures are swallowed."""
        mock_post.side_effect = Exception("Connection failed")

        event = {"event_type": "test"}
        # Should not raise
        record_audit(event)


class TestHeartbeat:
    """Test heartbeat function."""

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_heartbeat_success(self, mock_post: Mock) -> None:
        """Test successful heartbeat."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        result = heartbeat("worker-123", {"key": "value"})

        assert result["status"] == "ok"
        mock_post.assert_called_once()

    @patch("truth_forge.governance.control_plane.requests.post")
    def test_heartbeat_without_payload(self, mock_post: Mock) -> None:
        """Test heartbeat without payload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        result = heartbeat("worker-123")

        assert result["status"] == "ok"


class TestKillSwitchStatus:
    """Test kill_switch_status function."""

    @patch("truth_forge.governance.control_plane.requests.get")
    def test_kill_switch_status_armed(self, mock_get: Mock) -> None:
        """Test kill switch status when armed."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"armed": True}
        mock_get.return_value = mock_response

        result = kill_switch_status()
        assert result is True

    @patch("truth_forge.governance.control_plane.requests.get")
    def test_kill_switch_status_disarmed(self, mock_get: Mock) -> None:
        """Test kill switch status when disarmed."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"armed": False}
        mock_get.return_value = mock_response

        result = kill_switch_status()
        assert result is False

    @patch("truth_forge.governance.control_plane.requests.get")
    def test_kill_switch_status_error(self, mock_get: Mock) -> None:
        """Test kill switch status on error."""
        mock_get.side_effect = Exception("Connection failed")

        result = kill_switch_status()
        assert result is False  # Returns False on error
