"""Rollback procedures for migration.

RISK MITIGATION: Provides backup and rollback capabilities to recover
from failed migration phases.

Usage:
    from truth_forge.migration.rollback import create_backup, rollback_to_backup

    # Before migration
    backup_path = create_backup("pre_migration")

    # If something goes wrong
    rollback_to_backup(backup_path)
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def create_backup(name: str = "backup") -> Path:
    """Create a full backup before migration.

    Creates:
    - Git branch for code rollback
    - Copy of data/services/
    - Copy of .truth_engine/ (if exists)

    Args:
        name: Prefix for backup naming.

    Returns:
        Path to backup directory.

    Example:
        >>> backup_path = create_backup("pre_phase_4")
        >>> print(f"Backup at: {backup_path}")
    """
    from truth_forge.core.paths import DATA_ROOT, PROJECT_ROOT

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{name}_{timestamp}"
    backup_dir = PROJECT_ROOT / "backups" / backup_name

    backup_dir.mkdir(parents=True, exist_ok=True)

    # Create git branch for code state
    try:
        subprocess.run(
            ["git", "branch", "-c", "HEAD", backup_name],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
        (backup_dir / "git_branch.txt").write_text(backup_name)
    except subprocess.CalledProcessError:
        # Git might not be available or repo not initialized
        pass

    # Backup data/services/
    services_dir = DATA_ROOT / "services"
    if services_dir.exists():
        shutil.copytree(
            services_dir,
            backup_dir / "services",
            dirs_exist_ok=True,
        )

    # Backup .truth_engine/ (legacy)
    legacy_dir = PROJECT_ROOT / "Truth_Engine" / ".truth_engine"
    if legacy_dir.exists():
        shutil.copytree(
            legacy_dir,
            backup_dir / "truth_engine_hidden",
            dirs_exist_ok=True,
        )

    # Backup src/truth_forge/
    src_dir = PROJECT_ROOT / "src" / "truth_forge"
    if src_dir.exists():
        shutil.copytree(
            src_dir,
            backup_dir / "src_truth_forge",
            dirs_exist_ok=True,
        )

    # Write backup manifest
    manifest = {
        "name": backup_name,
        "timestamp": timestamp,
        "contents": [str(p.relative_to(backup_dir)) for p in backup_dir.rglob("*") if p.is_file()],
    }

    import json

    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    return backup_dir


def rollback_to_backup(backup_dir: Path, restore_git: bool = True) -> None:
    """Rollback to a previous backup.

    Args:
        backup_dir: Path to backup directory (from create_backup).
        restore_git: Whether to checkout the git branch.

    Raises:
        ValueError: If backup directory is invalid.
    """
    from truth_forge.core.paths import DATA_ROOT, PROJECT_ROOT

    if not backup_dir.exists():
        raise ValueError(f"Backup directory does not exist: {backup_dir}")

    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("Invalid backup: missing manifest.json")

    # Restore git branch if requested
    if restore_git:
        git_branch_file = backup_dir / "git_branch.txt"
        if git_branch_file.exists():
            branch_name = git_branch_file.read_text().strip()
            try:
                subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=PROJECT_ROOT,
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to checkout git branch: {e}") from e

    # Restore data/services/
    services_backup = backup_dir / "services"
    if services_backup.exists():
        services_dir = DATA_ROOT / "services"
        if services_dir.exists():
            shutil.rmtree(services_dir)
        shutil.copytree(services_backup, services_dir)

    # Restore src/truth_forge/
    src_backup = backup_dir / "src_truth_forge"
    if src_backup.exists():
        src_dir = PROJECT_ROOT / "src" / "truth_forge"
        if src_dir.exists():
            shutil.rmtree(src_dir)
        shutil.copytree(src_backup, src_dir)


def list_backups() -> list[dict[str, str]]:
    """List all available backups.

    Returns:
        List of backup info dictionaries.
    """
    import json

    from truth_forge.core.paths import PROJECT_ROOT

    backups: list[dict[str, str]] = []
    backup_root = PROJECT_ROOT / "backups"

    if not backup_root.exists():
        return backups

    for backup_dir in sorted(backup_root.iterdir(), reverse=True):
        if backup_dir.is_dir():
            manifest_path = backup_dir / "manifest.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                manifest["path"] = str(backup_dir)
                backups.append(manifest)

    return backups


def cleanup_old_backups(keep: int = 5) -> list[Path]:
    """Remove old backups, keeping the most recent.

    Args:
        keep: Number of recent backups to keep.

    Returns:
        List of removed backup paths.
    """
    from truth_forge.core.paths import PROJECT_ROOT

    backup_root = PROJECT_ROOT / "backups"
    if not backup_root.exists():
        return []

    # Sort by modification time, newest first
    backups = sorted(
        [d for d in backup_root.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    removed = []
    for backup in backups[keep:]:
        shutil.rmtree(backup)
        removed.append(backup)

    return removed
