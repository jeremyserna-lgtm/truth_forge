"""Tests for sensors module."""

from __future__ import annotations

from unittest.mock import patch

from truth_forge.services.sensors import collect_presence


class TestCollectPresence:
    """Test collect_presence function."""

    def test_collect_presence_basic(self) -> None:
        """Test basic presence collection."""
        presence = collect_presence()

        assert "timestamp_utc" in presence
        assert "hostname" in presence
        assert "pid" in presence
        assert "loadavg" in presence
        assert "disk" in presence
        assert "env_mode" in presence
        assert "local_hour" in presence

    def test_collect_presence_has_timestamp(self) -> None:
        """Test presence includes timestamp."""
        presence = collect_presence()
        assert presence["timestamp_utc"] is not None
        assert "T" in presence["timestamp_utc"]  # ISO format

    def test_collect_presence_has_hostname(self) -> None:
        """Test presence includes hostname."""
        presence = collect_presence()
        assert isinstance(presence["hostname"], str)
        assert len(presence["hostname"]) > 0

    def test_collect_presence_has_pid(self) -> None:
        """Test presence includes process ID."""
        presence = collect_presence()
        assert isinstance(presence["pid"], int)
        assert presence["pid"] > 0

    def test_collect_presence_has_loadavg(self) -> None:
        """Test presence includes load average."""
        presence = collect_presence()
        assert "loadavg" in presence
        assert "1m" in presence["loadavg"]
        assert "5m" in presence["loadavg"]
        assert "15m" in presence["loadavg"]

    def test_collect_presence_has_disk(self) -> None:
        """Test presence includes disk usage."""
        presence = collect_presence()
        assert "disk" in presence
        assert "total_bytes" in presence["disk"]
        assert "used_bytes" in presence["disk"]
        assert "free_bytes" in presence["disk"]
        assert "free_pct" in presence["disk"]

    def test_collect_presence_has_env_mode(self) -> None:
        """Test presence includes execution mode."""
        presence = collect_presence()
        assert "env_mode" in presence
        assert isinstance(presence["env_mode"], str)

    @patch.dict("os.environ", {"GENESIS_EXECUTION_MODE": "sovereign"})
    def test_collect_presence_env_mode(self) -> None:
        """Test presence respects environment variable."""
        presence = collect_presence()
        assert presence["env_mode"] == "sovereign"

    def test_collect_presence_has_local_hour(self) -> None:
        """Test presence includes local hour."""
        presence = collect_presence()
        assert "local_hour" in presence
        assert isinstance(presence["local_hour"], int)
        assert 0 <= presence["local_hour"] <= 23

    @patch("truth_forge.services.sensors.os.getloadavg")
    def test_collect_presence_handles_loadavg_error(self, mock_getloadavg) -> None:
        """Test collect_presence handles loadavg AttributeError."""
        mock_getloadavg.side_effect = AttributeError("getloadavg not available")

        presence = collect_presence()

        assert presence["loadavg"]["1m"] is None
        assert presence["loadavg"]["5m"] is None
        assert presence["loadavg"]["15m"] is None

    @patch("truth_forge.services.sensors.os.getloadavg")
    def test_collect_presence_handles_loadavg_oserror(self, mock_getloadavg) -> None:
        """Test collect_presence handles loadavg OSError."""
        mock_getloadavg.side_effect = OSError("getloadavg failed")

        presence = collect_presence()

        assert presence["loadavg"]["1m"] is None
        assert presence["loadavg"]["5m"] is None
        assert presence["loadavg"]["15m"] is None
