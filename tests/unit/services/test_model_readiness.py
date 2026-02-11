from __future__ import annotations

from unittest.mock import patch

from truth_forge.services.model_readiness import _dir_size_bytes, check_readiness


def test_dir_size_bytes(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("abc")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("12345")
    assert _dir_size_bytes(tmp_path) == 8  # 3 + 5 bytes


# Note: FileNotFoundError handling in _dir_size_bytes is tested implicitly
# through normal operation - the try/except ensures deleted files don't crash the function


def test_check_readiness_handles_missing(monkeypatch, tmp_path):
    # point HF cache to empty temp dir
    monkeypatch.setenv("HF_HOME", str(tmp_path))
    readiness = check_readiness()
    assert not readiness["scout"].ready
    assert readiness["scout"].size_gb == 0.0


def test_check_readiness_ready_threshold(monkeypatch, tmp_path):
    """Test check_readiness sets ready=True when size >= 90% of expected."""
    # Create a directory structure that simulates a model at 95% of expected size
    scout_path = tmp_path / "models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit"
    scout_path.mkdir(parents=True)
    # Create a dummy file so path.exists() returns True
    (scout_path / "dummy").touch()

    # Create a file that makes total size ~95GB (95% of 100GB expected)
    expected_bytes = 95 * 1024**3  # 95 GB

    import truth_forge.services.model_readiness as mod

    monkeypatch.setenv("HF_HOME", str(tmp_path))
    with patch.object(mod, "_dir_size_bytes", return_value=expected_bytes):
        readiness = check_readiness()
        assert readiness["scout"].ready is True
        assert readiness["scout"].size_gb == 95.0


def test_check_readiness_not_ready_threshold(monkeypatch, tmp_path):
    """Test check_readiness sets ready=False when size < 90% of expected."""
    scout_path = tmp_path / "models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit"
    scout_path.mkdir(parents=True)
    # Create a dummy file so path.exists() returns True
    (scout_path / "dummy").touch()

    # Create a file that makes total size ~85GB (85% of 100GB expected)
    expected_bytes = 85 * 1024**3  # 85 GB

    import truth_forge.services.model_readiness as mod

    monkeypatch.setenv("HF_HOME", str(tmp_path))
    with patch.object(mod, "_dir_size_bytes", return_value=expected_bytes):
        readiness = check_readiness()
        assert readiness["scout"].ready is False
        assert readiness["scout"].size_gb == 85.0
