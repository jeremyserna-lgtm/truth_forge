#!/usr/bin/env python3
"""
Shared Validation Module for Pipeline Stages

This module provides common validation functions used across all pipeline stages
to prevent security vulnerabilities, ensure data integrity, and enable fail-fast behavior.

CRITICAL: All stages MUST use these validation functions. No exceptions.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def validate_table_id(table_id: str) -> str:
    """Validate BigQuery table ID to prevent SQL injection.
    
    BigQuery table IDs must match pattern: [project.]dataset.table
    Only allows alphanumeric, underscores, hyphens, and dots.
    
    Args:
        table_id: Table ID to validate
        
    Returns:
        Validated table ID (unchanged if valid)
        
    Raises:
        ValueError: If table_id is invalid or contains dangerous characters
    """
    if not table_id or not isinstance(table_id, str):
        raise ValueError(f"Invalid table_id: must be non-empty string, got {type(table_id)}")
    
    # BigQuery table ID pattern: [project.]dataset.table
    # Allow: alphanumeric, underscores, hyphens, dots
    # Disallow: anything that could be SQL injection
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    
    if not re.match(pattern, table_id):
        raise ValueError(
            f"Invalid table_id format: '{table_id}'. "
            f"Must contain only alphanumeric, underscores, hyphens, and dots. "
            f"Potential SQL injection attempt."
        )
    
    # Additional checks for dangerous patterns
    dangerous_patterns = [
        '--',  # SQL comment
        ';',   # Statement separator
        '/*',  # Multi-line comment
        '*/',  # Multi-line comment end
        'DROP',
        'DELETE',
        'TRUNCATE',
        'ALTER',
        'CREATE',
        'EXEC',
        'EXECUTE',
        'UNION',
        'SELECT',
    ]
    
    table_id_upper = table_id.upper()
    for pattern in dangerous_patterns:
        if pattern in table_id_upper:
            raise ValueError(
                f"Invalid table_id: '{table_id}' contains dangerous pattern '{pattern}'. "
                f"Potential SQL injection attempt."
            )
    
    return table_id


def validate_run_id(run_id: str) -> str:
    """Validate run ID format to prevent injection attacks.
    
    Run IDs should be alphanumeric with hyphens/underscores.
    
    Args:
        run_id: Run ID to validate
        
    Returns:
        Validated run ID
        
    Raises:
        ValueError: If run_id is invalid
    """
    if not run_id or not isinstance(run_id, str):
        raise ValueError(f"Invalid run_id: must be non-empty string, got {type(run_id)}")
    
    # Run ID pattern: alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_\-]+$'
    
    if not re.match(pattern, run_id):
        raise ValueError(
            f"Invalid run_id format: '{run_id}'. "
            f"Must contain only alphanumeric, underscores, and hyphens."
        )
    
    return run_id


def validate_entity_id(entity_id: str) -> str:
    """Validate entity ID format.
    
    Entity IDs can be UUIDs or custom formats. This validates basic safety.
    
    Args:
        entity_id: Entity ID to validate
        
    Returns:
        Validated entity ID
        
    Raises:
        ValueError: If entity_id is invalid
    """
    if not entity_id or not isinstance(entity_id, str):
        raise ValueError(f"Invalid entity_id: must be non-empty string, got {type(entity_id)}")
    
    # Entity IDs can be UUIDs or custom formats - be permissive but safe
    # Disallow obviously dangerous patterns
    if len(entity_id) > 500:  # Reasonable upper bound
        raise ValueError(f"Invalid entity_id: too long ({len(entity_id)} chars)")
    
    # Disallow SQL injection patterns
    dangerous = ['--', ';', '/*', '*/']
    for pattern in dangerous:
        if pattern in entity_id:
            raise ValueError(f"Invalid entity_id: contains dangerous pattern '{pattern}'")
    
    return entity_id


def validate_path(
    path: Path,
    must_exist: bool = True,
    must_be_in_project: bool = True,
    allow_home_directory: bool = False,
    must_be_directory: bool = False,
    allow_symlinks: bool = False,
) -> Path:
    """Validate file path to prevent path traversal attacks.

    Args:
        path: Path to validate
        must_exist: If True, path must exist
        must_be_in_project: If True, path must be within project root
        allow_home_directory: If True, also allow paths within home directory
                              (useful for source directories like ~/.claude/projects)
        must_be_directory: If True, path must be a directory
        allow_symlinks: If True, allow symbolic links. If False (default), reject symlinks
                       to prevent path traversal via symlink attacks.

    Returns:
        Resolved, validated path

    Raises:
        ValueError: If path is invalid or outside allowed boundaries
        FileNotFoundError: If must_exist=True and path doesn't exist
    """
    if not isinstance(path, Path):
        path = Path(path)

    # Resolve to absolute path
    try:
        resolved = path.resolve()
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid path: cannot resolve '{path}': {e}")

    # FIX: Detect symlink path traversal attacks
    # A malicious symlink could point outside allowed directories
    # Check BEFORE the path is resolved to catch symlinks in the path chain
    if not allow_symlinks:
        # Check if the original path (before resolve) contains symlinks
        try:
            # Walk up the path checking each component for symlinks
            check_path = path if path.is_absolute() else Path.cwd() / path
            for parent in [check_path] + list(check_path.parents):
                if parent.is_symlink():
                    raise ValueError(
                        f"Symlink detected in path: '{parent}' is a symbolic link. "
                        f"Symlinks are not allowed to prevent path traversal attacks. "
                        f"Use the actual path or set allow_symlinks=True if this is intentional."
                    )
                if parent == parent.parent:  # Reached root
                    break
        except (OSError, PermissionError) as e:
            # If we can't check for symlinks, fail safely
            raise ValueError(
                f"Cannot verify path safety: '{path}' - {e}. "
                f"Unable to check for symlinks."
            )

    # Check if must exist
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")

    # Check if must be a directory
    if must_be_directory and resolved.exists() and not resolved.is_dir():
        raise ValueError(f"Path is not a directory: {resolved}")

    # Check if must be in project (prevent path traversal)
    if must_be_in_project:
        # Find project root (look for common markers)
        project_root = None
        current = resolved

        for _ in range(20):  # Max 20 levels up
            markers = ['pyproject.toml', 'setup.py', 'requirements.txt', '.git', 'CLAUDE.md']
            if any((current / marker).exists() for marker in markers):
                project_root = current
                break
            if current.parent == current:  # Reached filesystem root
                break
            current = current.parent

        home = Path.home()

        if project_root is None:
            # Fallback: require path to be within home directory if project root not found
            # SECURITY: No environment variable bypass - path must be within home directory
            if not resolved.is_relative_to(home):
                raise ValueError(
                    f"Path traversal detected: '{resolved}' is outside home directory. "
                    f"Cannot determine project root. Ensure path is within {home}."
                )
        else:
            # Check if path is within project root
            in_project = resolved.is_relative_to(project_root)
            # Check if path is within home directory (only if allow_home_directory=True)
            in_home = allow_home_directory and resolved.is_relative_to(home)

            # SECURITY: Path must be in allowed location - no environment variable bypass
            if not in_project and not in_home:
                if allow_home_directory:
                    raise ValueError(
                        f"Path traversal detected: '{resolved}' is outside allowed locations. "
                        f"Must be within project root ({project_root}) or home directory ({home})."
                    )
                else:
                    raise ValueError(
                        f"Path traversal detected: '{resolved}' is outside project root '{project_root}'. "
                        f"All paths must be within the project directory for security."
                    )

    return resolved


def validate_stage_number(stage_num: int) -> int:
    """Validate stage number.
    
    Args:
        stage_num: Stage number to validate
        
    Returns:
        Validated stage number
        
    Raises:
        ValueError: If stage_num is invalid
    """
    if not isinstance(stage_num, int):
        try:
            stage_num = int(stage_num)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid stage number: must be integer, got {type(stage_num)}")
    
    if stage_num < 0:
        raise ValueError(f"Invalid stage number: must be >= 0, got {stage_num}")
    
    if stage_num > 100:  # Reasonable upper bound
        raise ValueError(f"Invalid stage number: must be <= 100, got {stage_num}")
    
    return stage_num


def validate_required_fields(record: Dict[str, Any], required_fields: List[str], record_name: str = "record") -> None:
    """Validate that a record contains all required fields.
    
    Args:
        record: Record to validate
        required_fields: List of required field names
        record_name: Name of record for error messages
        
    Raises:
        ValueError: If any required field is missing or None
    """
    if not isinstance(record, dict):
        raise ValueError(f"{record_name} must be a dictionary, got {type(record)}")
    
    missing = []
    for field in required_fields:
        if field not in record or record[field] is None:
            missing.append(field)
    
    if missing:
        raise ValueError(
            f"{record_name} missing required fields: {', '.join(missing)}. "
            f"Required: {', '.join(required_fields)}"
        )


def validate_batch_size(batch_size: int, min_size: int = 1, max_size: int = 10000) -> int:
    """Validate batch size for processing.
    
    Args:
        batch_size: Batch size to validate
        min_size: Minimum allowed batch size
        max_size: Maximum allowed batch size
        
    Returns:
        Validated batch size
        
    Raises:
        ValueError: If batch_size is out of range
    """
    if not isinstance(batch_size, int):
        try:
            batch_size = int(batch_size)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid batch_size: must be integer, got {type(batch_size)}")
    
    if batch_size < min_size:
        raise ValueError(f"Invalid batch_size: must be >= {min_size}, got {batch_size}")
    
    if batch_size > max_size:
        raise ValueError(f"Invalid batch_size: must be <= {max_size}, got {batch_size}")
    
    return batch_size
