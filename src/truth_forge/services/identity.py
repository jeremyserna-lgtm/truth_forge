"""Identity Service.

Generates unique identifiers for various entities.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from pathlib import Path
from typing import Any

from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


def _generate_hash(content: str, length: int = 16) -> str:
    """Generate truncated SHA-256 hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:length]


def _slugify(text: str) -> str:
    """Convert text to lowercase, hyphenated slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _format_sequence(index: int, width: int = 4) -> str:
    """Zero-pad sequence number."""
    return f"{index:0{width}d}"


@register_service()
class IdentityService(BaseService):
    """Identity service for generating unique IDs."""

    service_name = "identity"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """This service does not process records asynchronously."""
        raise NotImplementedError("IdentityService is a synchronous provider.")

    def create_schema(self) -> str:
        """This service does not have a DuckDB schema."""
        return ""

    def generate_script_id(
        self,
        script_name: str,
        script_path: str | Path,
        version: str = "1.0",
    ) -> str:
        """Generate a canonical script ID."""
        normalized_name = Path(script_name).stem or "script"
        path_hash = _generate_hash(str(script_path))
        return f"script:{normalized_name}:{version}:{path_hash}"

    def generate_document_id(self, file_path: str, metadata: dict[str, Any] | None = None) -> str:
        """Generate L8 document ID from file path and metadata."""
        path_normalized = str(Path(file_path).as_posix())
        content = path_normalized
        if metadata:
            meta_str = json.dumps(metadata, sort_keys=True)
            content += f"|{meta_str}"
        return f"doc:{_generate_hash(content, length=16)}"

    def generate_message_id(self, conversation_id: str, index: int) -> str:
        """Generate L5 message ID."""
        conv_hash = _generate_hash(conversation_id, length=16)
        seq = _format_sequence(index)
        return f"msg:{conv_hash}:{seq}"

    def generate_conversation_id(self, source_type: str, source_id: str) -> str:
        """Generate conversation ID."""
        type_slug = _slugify(source_type)
        content_hash = _generate_hash(source_id, length=16)
        return f"conv:{type_slug}:{content_hash}"

    def generate_sentence_id(self, parent_id: str, index: int) -> str:
        """Generate L4 sentence ID."""
        parent_hash = _generate_hash(parent_id, length=16)
        seq = _format_sequence(index)
        return f"sent:{parent_hash}:{seq}"

    def generate_span_id(self, parent_id: str, index: int) -> str:
        """Generate L3 span ID."""
        parent_hash = _generate_hash(parent_id, length=16)
        seq = _format_sequence(index)
        return f"span:{parent_hash}:{seq}"

    def generate_word_id(self, parent_id: str, index: int) -> str:
        """Generate L2 word ID."""
        parent_hash = _generate_hash(parent_id, length=16)
        seq = _format_sequence(index)
        return f"word:{parent_hash}:{seq}"

    def generate_token_id(self, parent_id: str, index: int) -> str:
        """Generate L1 token ID."""
        parent_hash = _generate_hash(parent_id, length=12)
        seq = _format_sequence(index)
        return f"token:{parent_hash}:{seq}"

    def generate_primitive_id(
        self,
        primitive_type: str = "prim",
        source_id: str | None = None,
    ) -> str:
        """Generate unique ID for a primitive using ULID."""
        try:
            from ulid import ULID

            ulid_str = str(ULID())
        except ImportError:
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4()).replace("-", "")[0:8]
            ulid_str = f"{timestamp}:{unique_id}"

        if source_id:
            source_hash = _generate_hash(source_id, length=16)
            return f"{primitive_type}:{source_hash}:{ulid_str}"
        return f"{primitive_type}:{ulid_str}"

    def generate_run_id(self) -> str:
        """Generate a random run ID using ULID."""
        try:
            from ulid import ULID

            return f"run:{ULID()}"
        except ImportError:
            return f"run:{uuid.uuid4().hex[:8]}"

    def generate_atom_id(
        self,
        source_id: str | None = None,
        source_name: str | None = None,
        content: str | None = None,
    ) -> str:
        """Generate universal knowledge atom ID."""
        seed = ""
        if source_name:
            seed += f"{source_name}|"
        if source_id:
            seed += f"{source_id}|"
        if content:
            seed += f"{content}"
        else:
            seed += str(uuid.uuid4())

        atom_hash = _generate_hash(seed, length=16)
        return f"atom:{atom_hash}"
