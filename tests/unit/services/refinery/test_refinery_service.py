"""Comprehensive tests for LLMRefineryService and OllamaClient.

Covers:
- RefineryConfig defaults and customization
- OllamaClient: init, lazy client, close, complete (success/retry/timeout/http error),
  extract_json (array/object/not-found/malformed/decode-error, obj-before-array)
- LLMRefineryService: init, on_startup (with/without identity & mediator),
  on_shutdown, process (success/error/with mediator), _generate_entity_id
  (with identity service / fallback), _process_conversation (shallow/deep),
  _process_deep (success/empty/no ollama), _extract_enrichment (success/none/no ollama),
  _extract_enrichment_for_l4, process_batch (success/partial failure/file output),
  create_refinery_service factory
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest


# ---------------------------------------------------------------------------
# We patch BaseService.__init__ globally for most tests to avoid
# filesystem / structlog side-effects during construction.
# ---------------------------------------------------------------------------

_BASE_INIT_PATCH = "truth_forge.services.refinery.service.BaseService.__init__"


# Import the module under test (these imports trigger @register_service)
from truth_forge.services.refinery.service import (  # noqa: E402
    LLMRefineryService,
    OllamaClient,
    RefineryConfig,
    create_refinery_service,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_service(
    config: RefineryConfig | None = None,
) -> LLMRefineryService:
    """Create a refinery service with BaseService.__init__ patched out."""
    with patch(_BASE_INIT_PATCH):
        svc = LLMRefineryService(config or RefineryConfig())
    svc._logger = Mock()
    return svc


def _make_ollama_client(
    config: RefineryConfig | None = None,
) -> tuple[OllamaClient, Mock]:
    """Create an OllamaClient with a mock logger."""
    cfg = config or RefineryConfig()
    logger = Mock()
    return OllamaClient(cfg, logger), logger


# ===========================================================================
# RefineryConfig
# ===========================================================================


class TestRefineryConfig:
    """Test RefineryConfig dataclass."""

    def test_defaults(self) -> None:
        cfg = RefineryConfig()
        assert cfg.ollama_host == "http://localhost:11434"
        assert cfg.model == "qwen2.5-coder:32b"
        assert cfg.timeout == 120.0
        assert cfg.max_retries == 3
        assert cfg.min_level == 5
        assert cfg.batch_size == 10
        assert cfg.enable_enrichments is True
        assert cfg.enrichment_levels == [5, 4]
        assert cfg.source_system == "claude_web"
        assert cfg.source_pipeline == "llm_refinery"

    def test_custom(self) -> None:
        cfg = RefineryConfig(
            ollama_host="http://custom:9999",
            model="tiny-model",
            min_level=2,
            enable_enrichments=False,
            max_retries=1,
        )
        assert cfg.ollama_host == "http://custom:9999"
        assert cfg.model == "tiny-model"
        assert cfg.min_level == 2
        assert cfg.enable_enrichments is False
        assert cfg.max_retries == 1


# ===========================================================================
# OllamaClient
# ===========================================================================


class TestOllamaClient:
    """Test OllamaClient HTTP operations."""

    def test_init(self) -> None:
        client, _logger = _make_ollama_client()
        assert client._client is None
        assert client.config.ollama_host == "http://localhost:11434"

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_ensure_client_lazy(self, mock_cls: Mock) -> None:
        client, _ = _make_ollama_client()
        c1 = client._ensure_client()
        c2 = client._ensure_client()
        assert c1 is c2
        mock_cls.assert_called_once()

    def test_close_when_open(self) -> None:
        client, _ = _make_ollama_client()
        mock_http = Mock()
        client._client = mock_http
        client.close()
        mock_http.close.assert_called_once()
        assert client._client is None

    def test_close_when_already_closed(self) -> None:
        client, _ = _make_ollama_client()
        client.close()  # no error

    # ----- complete() -----

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_success(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Hello world"}
        mock_response.raise_for_status = Mock()
        mock_http.post.return_value = mock_response
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        result = client.complete("Say hello")
        assert result == "Hello world"
        mock_http.post.assert_called_once()

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_retries_on_timeout(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        mock_http.post.side_effect = httpx.TimeoutException("timeout")
        mock_cls.return_value = mock_http

        cfg = RefineryConfig(max_retries=3)
        client, _logger = _make_ollama_client(cfg)
        result = client.complete("test")
        assert result == ""
        assert mock_http.post.call_count == 3

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_raises_on_final_http_error(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        mock_http.post.side_effect = httpx.HTTPStatusError(
            "500", request=Mock(), response=Mock(status_code=500)
        )
        mock_cls.return_value = mock_http

        cfg = RefineryConfig(max_retries=2)
        client, _ = _make_ollama_client(cfg)
        with pytest.raises(httpx.HTTPStatusError):
            client.complete("test")
        assert mock_http.post.call_count == 2

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_http_error_retries_before_final(self, mock_cls: Mock) -> None:
        """First attempt fails with HTTP error, second succeeds."""
        mock_http = Mock()
        mock_response_ok = Mock()
        mock_response_ok.json.return_value = {"response": "recovered"}
        mock_response_ok.raise_for_status = Mock()
        mock_http.post.side_effect = [
            httpx.HTTPStatusError("500", request=Mock(), response=Mock(status_code=500)),
            mock_response_ok,
        ]
        mock_cls.return_value = mock_http

        cfg = RefineryConfig(max_retries=2)
        client, _ = _make_ollama_client(cfg)
        result = client.complete("test")
        assert result == "recovered"

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_complete_uses_temperature(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        mock_resp = Mock()
        mock_resp.json.return_value = {"response": "ok"}
        mock_resp.raise_for_status = Mock()
        mock_http.post.return_value = mock_resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        client.complete("prompt", temperature=0.9)
        posted_json = mock_http.post.call_args[1]["json"]
        assert posted_json["options"]["temperature"] == 0.9

    # ----- extract_json() -----

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_array(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": 'Some text [{"a": 1}] trailing'}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        result = client.extract_json("prompt")
        assert isinstance(result, list)
        assert result == [{"a": 1}]

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_object(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": 'prefix {"key": "val"} suffix'}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        result = client.extract_json("prompt")
        assert isinstance(result, dict)
        assert result == {"key": "val"}

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_object_before_array(self, mock_cls: Mock) -> None:
        """When { appears before [, parse as object."""
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": '{"first": 1} then [1, 2]'}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        result = client.extract_json("prompt")
        # { appears at index 0, [ appears at index 14 -> min is 0 -> object
        assert isinstance(result, dict)

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_not_found(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": "No JSON here at all"}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        assert client.extract_json("prompt") is None

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_malformed_end(self, mock_cls: Mock) -> None:
        """JSON start found but no matching end bracket."""
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": "[unclosed"}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        # rfind("]") returns -1, so json_end = 0 which is <= json_start = 0
        assert client.extract_json("prompt") is None

    @patch("truth_forge.services.refinery.service.httpx.Client")
    def test_extract_json_decode_error(self, mock_cls: Mock) -> None:
        mock_http = Mock()
        resp = Mock()
        resp.json.return_value = {"response": '{"broken": not_valid_json}'}
        resp.raise_for_status = Mock()
        mock_http.post.return_value = resp
        mock_cls.return_value = mock_http

        client, _ = _make_ollama_client()
        assert client.extract_json("prompt") is None


# ===========================================================================
# LLMRefineryService — Init / Lifecycle
# ===========================================================================


class TestRefineryServiceInit:
    """Test LLMRefineryService construction and lifecycle."""

    def test_init_default_config(self) -> None:
        svc = _make_service()
        assert svc._config.model == "qwen2.5-coder:32b"
        assert svc._ollama is None
        assert svc._identity is None
        assert svc._mediator is None

    def test_init_custom_config(self) -> None:
        cfg = RefineryConfig(model="tiny")
        svc = _make_service(cfg)
        assert svc._config.model == "tiny"

    def test_service_name(self) -> None:
        svc = _make_service()
        assert svc.service_name == "refinery"

    @patch("truth_forge.services.refinery.service.get_service")
    def test_on_startup_connects_identity_and_mediator(self, mock_get_service: Mock) -> None:
        mock_identity = Mock()
        mock_identity.generate_run_id.return_value = "run-abc"
        mock_mediator = Mock()
        mock_get_service.side_effect = [mock_identity, mock_mediator]

        svc = _make_service()
        svc.on_startup()

        assert svc._identity is mock_identity
        assert svc._run_id == "run-abc"
        assert svc._mediator is mock_mediator
        assert svc._ollama is not None

    @patch("truth_forge.services.refinery.service.get_service")
    def test_on_startup_identity_unavailable(self, mock_get_service: Mock) -> None:
        mock_get_service.side_effect = [RuntimeError("no identity"), Mock()]

        svc = _make_service()
        svc.on_startup()

        assert svc._identity is None
        assert svc._run_id is None

    @patch("truth_forge.services.refinery.service.get_service")
    def test_on_startup_mediator_unavailable(self, mock_get_service: Mock) -> None:
        mock_identity = Mock()
        mock_identity.generate_run_id.return_value = "run-x"
        mock_get_service.side_effect = [mock_identity, RuntimeError("no mediator")]

        svc = _make_service()
        svc.on_startup()

        assert svc._identity is mock_identity
        assert svc._mediator is None

    def test_on_shutdown_closes_ollama(self) -> None:
        svc = _make_service()
        mock_ollama = Mock()
        svc._ollama = mock_ollama
        svc.on_shutdown()
        mock_ollama.close.assert_called_once()

    def test_on_shutdown_no_ollama(self) -> None:
        svc = _make_service()
        svc._ollama = None
        svc.on_shutdown()  # should not raise


# ===========================================================================
# _generate_entity_id
# ===========================================================================


class TestGenerateEntityId:
    """Test entity ID generation paths."""

    def test_with_identity_service(self) -> None:
        svc = _make_service()
        mock_identity = Mock()
        mock_identity.generate_entity_id.return_value = "eid-123"
        svc._identity = mock_identity

        result = svc._generate_entity_id("msg", "content", "parent")
        assert result == "eid-123"
        mock_identity.generate_entity_id.assert_called_once_with(
            prefix="msg", content="content", parent_id="parent"
        )

    def test_fallback_hash_based(self) -> None:
        svc = _make_service()
        svc._identity = None
        result = svc._generate_entity_id("msg", "hello", "p1")
        assert result.startswith("msg:")
        assert result.endswith(":0000")
        # Should be deterministic
        result2 = svc._generate_entity_id("msg", "hello", "p1")
        assert result == result2

    def test_fallback_different_content_different_id(self) -> None:
        svc = _make_service()
        svc._identity = None
        id1 = svc._generate_entity_id("msg", "hello", "")
        id2 = svc._generate_entity_id("msg", "world", "")
        assert id1 != id2


# ===========================================================================
# process() — HOLD pattern entry point
# ===========================================================================


class TestProcess:
    """Test the process() method (AGENT logic)."""

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_process_success(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        svc = _make_service(RefineryConfig(enable_enrichments=False))
        svc._identity = None
        svc._mediator = Mock()

        # Mock MessageL5.from_raw
        mock_l5 = Mock()
        mock_l5.text = "Hello"
        mock_l5.entity_id = "msg:abc:0000"
        mock_l5.to_entity_unified.return_value = {"entity_id": "msg:abc:0000", "text": "Hello"}
        mock_l5_cls.from_raw.return_value = mock_l5

        # Mock ConversationL8
        mock_conv = Mock()
        mock_conv.to_entity_unified.return_value = {"entity_id": "conv:x", "level": 8}
        mock_l8_cls.return_value = mock_conv

        record = {
            "uuid": "conv-001",
            "name": "Test Chat",
            "created_at": "2026-01-01T00:00:00Z",
            "chat_messages": [{"text": "Hello", "sender": "human"}],
        }

        result = svc.process(record)
        assert result["status"] == "success"
        assert result["conversation_id"] == "conv-001"
        assert result["entity_count"] >= 1
        # Mediator should be notified (start + complete)
        assert svc._mediator.publish.call_count == 2

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_process_error(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        svc = _make_service()
        svc._identity = None
        svc._mediator = Mock()

        mock_l5_cls.from_raw.side_effect = ValueError("parse failure")

        record = {"uuid": "conv-err", "chat_messages": [{"text": "x"}]}
        result = svc.process(record)
        assert result["status"] == "error"
        assert "parse failure" in result["error"]

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_process_without_mediator(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        svc = _make_service(RefineryConfig(enable_enrichments=False))
        svc._identity = None
        svc._mediator = None  # No mediator

        mock_l5 = Mock()
        mock_l5.text = "Hi"
        mock_l5.entity_id = "msg:x:0000"
        mock_l5.to_entity_unified.return_value = {"entity_id": "msg:x:0000"}
        mock_l5_cls.from_raw.return_value = mock_l5

        mock_conv = Mock()
        mock_conv.to_entity_unified.return_value = {"entity_id": "conv:y"}
        mock_l8_cls.return_value = mock_conv

        record = {"uuid": "conv-nomediator", "chat_messages": [{"text": "Hi"}]}
        result = svc.process(record)
        assert result["status"] == "success"

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_process_error_with_mediator(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        """Mediator receives FAILED event on error."""
        svc = _make_service()
        svc._identity = None
        svc._mediator = Mock()
        mock_l5_cls.from_raw.side_effect = RuntimeError("boom")

        record = {"uuid": "conv-fail", "chat_messages": [{"text": "x"}]}
        result = svc.process(record)
        assert result["status"] == "error"
        # Mediator should get STARTED + FAILED
        assert svc._mediator.publish.call_count == 2
        second_call = svc._mediator.publish.call_args_list[1]
        assert second_call[0][1]["event_type"] == "CONVERSATION_PROCESSING_FAILED"

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_process_error_without_mediator(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        """Error path with no mediator still returns error dict."""
        svc = _make_service()
        svc._identity = None
        svc._mediator = None
        mock_l5_cls.from_raw.side_effect = RuntimeError("fail")

        record = {"uuid": "conv-fail2", "chat_messages": [{"text": "x"}]}
        result = svc.process(record)
        assert result["status"] == "error"
        assert result["conversation_id"] == "conv-fail2"

    def test_process_missing_uuid(self) -> None:
        """Record without uuid uses 'unknown' as default."""
        svc = _make_service(RefineryConfig(enable_enrichments=False))
        svc._identity = None
        svc._mediator = None

        with (
            patch("truth_forge.services.refinery.service.MessageL5") as mock_l5_cls,
            patch("truth_forge.services.refinery.service.ConversationL8") as mock_l8_cls,
        ):
            mock_l5 = Mock()
            mock_l5.text = "hi"
            mock_l5.entity_id = "msg:z:0000"
            mock_l5.to_entity_unified.return_value = {"entity_id": "msg:z:0000"}
            mock_l5_cls.from_raw.return_value = mock_l5
            mock_conv = Mock()
            mock_conv.to_entity_unified.return_value = {"entity_id": "conv:z"}
            mock_l8_cls.return_value = mock_conv

            record = {"chat_messages": [{"text": "hi"}]}
            result = svc.process(record)
            assert result["conversation_id"] == "unknown"
            assert result["status"] == "success"


# ===========================================================================
# _process_conversation — deeper levels
# ===========================================================================


class TestProcessConversationDeepLevels:
    """Test _process_conversation when min_level <= 4 (triggers _process_deep)."""

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_deep_processing_invoked(self, mock_l8_cls: Mock, mock_l5_cls: Mock) -> None:
        svc = _make_service(RefineryConfig(min_level=4, enable_enrichments=False))
        svc._identity = None
        svc._mediator = None
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = {"sentences": []}

        mock_l5 = Mock()
        mock_l5.text = "Deep test"
        mock_l5.entity_id = "msg:deep:0000"
        mock_l5.role = "human"
        mock_l5.to_entity_unified.return_value = {"entity_id": "msg:deep:0000"}
        mock_l5_cls.from_raw.return_value = mock_l5

        mock_conv = Mock()
        mock_conv.to_entity_unified.return_value = {"entity_id": "conv:deep"}
        mock_l8_cls.return_value = mock_conv

        record = {
            "uuid": "conv-deep",
            "chat_messages": [{"text": "Deep test", "sender": "human"}],
        }
        result = svc.process(record)
        assert result["status"] == "success"


# ===========================================================================
# _process_deep
# ===========================================================================


class TestProcessDeep:
    """Test _process_deep method."""

    def test_no_ollama_returns_empty(self) -> None:
        svc = _make_service()
        svc._ollama = None
        msg = Mock()
        msg.text = "hello"
        msg.role = "human"
        msg.entity_id = "msg:x"
        entities, enrichments = svc._process_deep(msg, "conv:c")
        assert entities == []
        assert enrichments == []

    @patch("truth_forge.services.refinery.service.SentenceL4")
    @patch("truth_forge.services.refinery.service.FULL_MESSAGE_ANALYSIS_PROMPT")
    def test_success_with_sentences(self, mock_prompt: Mock, mock_l4_cls: Mock) -> None:
        svc = _make_service(RefineryConfig(min_level=4, enable_enrichments=False))
        svc._identity = None
        svc._ollama = Mock()

        mock_prompt.format.return_value = "formatted prompt"
        svc._ollama.extract_json.return_value = {
            "sentences": [{"text": "Sentence one", "type": "statement"}]
        }

        mock_l4 = Mock()
        mock_l4.text = "Sentence one"
        mock_l4.entity_id = "sent:a:0000"
        mock_l4.to_entity_unified.return_value = {"entity_id": "sent:a:0000", "level": 4}
        mock_l4_cls.from_llm.return_value = mock_l4

        msg = Mock()
        msg.text = "Sentence one."
        msg.role = "human"
        msg.entity_id = "msg:m1"

        entities, _enrichments = svc._process_deep(msg, "conv:c1")
        assert len(entities) == 1
        assert entities[0]["entity_id"] == "sent:a:0000"
        assert entities[0]["parent_id"] == "msg:m1"

    def test_llm_returns_none(self) -> None:
        svc = _make_service(RefineryConfig(min_level=4))
        svc._identity = None
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = None

        msg = Mock()
        msg.text = "test"
        msg.role = "human"
        msg.entity_id = "msg:m"

        entities, enrichments = svc._process_deep(msg, "conv:c")
        assert entities == []
        assert enrichments == []

    def test_llm_returns_non_dict(self) -> None:
        svc = _make_service(RefineryConfig(min_level=4))
        svc._identity = None
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = [1, 2, 3]  # list, not dict

        msg = Mock()
        msg.text = "test"
        msg.role = "human"
        msg.entity_id = "msg:m"

        entities, _enrichments = svc._process_deep(msg, "conv:c")
        assert entities == []

    @patch("truth_forge.services.refinery.service.SentenceL4")
    @patch("truth_forge.services.refinery.service.SpanL3")
    @patch("truth_forge.services.refinery.service.FULL_MESSAGE_ANALYSIS_PROMPT")
    def test_deep_l3_spans(self, mock_prompt: Mock, mock_l3_cls: Mock, mock_l4_cls: Mock) -> None:
        """min_level=3 extracts L4 sentences and L3 spans."""
        svc = _make_service(RefineryConfig(min_level=3, enable_enrichments=False))
        svc._identity = None
        svc._ollama = Mock()
        mock_prompt.format.return_value = "prompt"

        svc._ollama.extract_json.return_value = {
            "sentences": [
                {
                    "text": "Sentence",
                    "type": "statement",
                    "spans": [{"text": "Span one", "type": "noun_phrase"}],
                }
            ]
        }

        mock_l4 = Mock()
        mock_l4.text = "Sentence"
        mock_l4.entity_id = "sent:s1"
        mock_l4.to_entity_unified.return_value = {"entity_id": "sent:s1"}
        mock_l4_cls.from_llm.return_value = mock_l4

        mock_l3 = Mock()
        mock_l3.text = "Span one"
        mock_l3.entity_id = "span:sp1"
        mock_l3.to_entity_unified.return_value = {"entity_id": "span:sp1"}
        mock_l3_cls.from_llm.return_value = mock_l3

        msg = Mock()
        msg.text = "Sentence"
        msg.role = "human"
        msg.entity_id = "msg:m1"

        entities, _enrichments = svc._process_deep(msg, "conv:c1")
        # Should have 1 L4 + 1 L3
        assert len(entities) == 2
        # The L3 span's parent_id is set to l4.entity_id AFTER _generate_entity_id
        # overwrites it, so use the actual entity_id from the mock (which was reassigned)
        assert entities[1]["parent_id"] == mock_l4.entity_id

    @patch("truth_forge.services.refinery.service.SentenceL4")
    @patch("truth_forge.services.refinery.service.SpanL3")
    @patch("truth_forge.services.refinery.service.WordL2")
    @patch("truth_forge.services.refinery.service.FULL_MESSAGE_ANALYSIS_PROMPT")
    def test_deep_l2_words(
        self,
        mock_prompt: Mock,
        mock_l2_cls: Mock,
        mock_l3_cls: Mock,
        mock_l4_cls: Mock,
    ) -> None:
        """min_level=2 extracts L4 + L3 + L2."""
        svc = _make_service(RefineryConfig(min_level=2, enable_enrichments=False))
        svc._identity = None
        svc._ollama = Mock()
        mock_prompt.format.return_value = "prompt"

        svc._ollama.extract_json.return_value = {
            "sentences": [
                {
                    "text": "S1",
                    "spans": [
                        {
                            "text": "Sp1",
                            "words": [{"text": "W1"}, {"text": "W2"}],
                        }
                    ],
                }
            ]
        }

        mock_l4 = Mock()
        mock_l4.text = "S1"
        mock_l4.entity_id = "sent:s1"
        mock_l4.to_entity_unified.return_value = {"entity_id": "sent:s1"}
        mock_l4_cls.from_llm.return_value = mock_l4

        mock_l3 = Mock()
        mock_l3.text = "Sp1"
        mock_l3.entity_id = "span:sp1"
        mock_l3.to_entity_unified.return_value = {"entity_id": "span:sp1"}
        mock_l3_cls.from_llm.return_value = mock_l3

        mock_w = Mock()
        mock_w.text = "W1"
        mock_w.entity_id = "word:w1"
        mock_w.to_entity_unified.return_value = {"entity_id": "word:w1"}
        mock_l2_cls.from_llm.return_value = mock_w

        msg = Mock()
        msg.text = "S1"
        msg.role = "human"
        msg.entity_id = "msg:m1"

        entities, _enrichments = svc._process_deep(msg, "conv:c1")
        # 1 L4 + 1 L3 + 2 L2 = 4
        assert len(entities) == 4


# ===========================================================================
# _extract_enrichment / _extract_enrichment_for_l4
# ===========================================================================


class TestExtractEnrichment:
    """Test enrichment extraction paths."""

    def test_no_ollama_returns_none(self) -> None:
        svc = _make_service()
        svc._ollama = None
        msg = Mock()
        msg.text = "test"
        msg.role = "human"
        msg.entity_id = "msg:x"
        assert svc._extract_enrichment(msg) is None

    @patch("truth_forge.services.refinery.service.create_enrichment_from_llm")
    @patch("truth_forge.services.refinery.service.ENRICHMENT_EXTRACTION_PROMPT")
    def test_success(self, mock_prompt: Mock, mock_create: Mock) -> None:
        svc = _make_service()
        svc._identity = None
        svc._run_id = "run-test"
        svc._ollama = Mock()
        mock_prompt.format.return_value = "enrichment prompt"
        svc._ollama.extract_json.return_value = {"cognitive_stage": 5}

        mock_enrichment = Mock()
        mock_create.return_value = mock_enrichment

        msg = Mock()
        msg.text = "deep thought"
        msg.role = "human"
        msg.entity_id = "msg:e1"

        result = svc._extract_enrichment(msg)
        assert result is mock_enrichment
        mock_create.assert_called_once_with(
            entity_id="msg:e1",
            text="deep thought",
            llm_response={"cognitive_stage": 5},
            batch_id="run-test",
        )

    def test_llm_returns_none(self) -> None:
        svc = _make_service()
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = None
        msg = Mock()
        msg.text = "test"
        msg.role = "human"
        msg.entity_id = "msg:x"
        assert svc._extract_enrichment(msg) is None

    def test_llm_returns_non_dict(self) -> None:
        svc = _make_service()
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = [1, 2]
        msg = Mock()
        msg.text = "test"
        msg.role = "human"
        msg.entity_id = "msg:x"
        assert svc._extract_enrichment(msg) is None


class TestExtractEnrichmentForL4:
    """Test _extract_enrichment_for_l4."""

    def test_no_ollama(self) -> None:
        svc = _make_service()
        svc._ollama = None
        sent = Mock()
        sent.text = "test"
        sent.entity_id = "sent:x"
        assert svc._extract_enrichment_for_l4(sent, "human") is None

    @patch("truth_forge.services.refinery.service.create_enrichment_from_llm")
    @patch("truth_forge.services.refinery.service.ENRICHMENT_EXTRACTION_PROMPT")
    def test_success(self, mock_prompt: Mock, mock_create: Mock) -> None:
        svc = _make_service()
        svc._run_id = "run-42"
        svc._ollama = Mock()
        mock_prompt.format.return_value = "prompt"
        svc._ollama.extract_json.return_value = {"key": "val"}
        mock_create.return_value = Mock()

        sent = Mock()
        sent.text = "A sentence"
        sent.entity_id = "sent:s1"

        result = svc._extract_enrichment_for_l4(sent, "assistant")
        assert result is not None
        mock_create.assert_called_once()

    def test_llm_returns_none(self) -> None:
        svc = _make_service()
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = None
        sent = Mock()
        sent.text = "test"
        sent.entity_id = "sent:x"
        assert svc._extract_enrichment_for_l4(sent, "human") is None

    def test_llm_returns_non_dict(self) -> None:
        svc = _make_service()
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = ["list"]
        sent = Mock()
        sent.text = "test"
        sent.entity_id = "sent:x"
        assert svc._extract_enrichment_for_l4(sent, "human") is None


# ===========================================================================
# process_batch
# ===========================================================================


class TestProcessBatch:
    """Test batch processing with file output."""

    def test_batch_all_success(self) -> None:
        svc = _make_service()
        svc.process = Mock(  # type: ignore[method-assign]
            side_effect=[
                {
                    "status": "success",
                    "entity_count": 3,
                    "enrichment_count": 1,
                    "entities": [{"id": "e1"}, {"id": "e2"}, {"id": "e3"}],
                    "enrichments": [{"id": "en1"}],
                },
                {
                    "status": "success",
                    "entity_count": 2,
                    "enrichment_count": 0,
                    "entities": [{"id": "e4"}, {"id": "e5"}],
                    "enrichments": [],
                },
            ]
        )

        stats = svc.process_batch([{"uuid": "c1"}, {"uuid": "c2"}])
        assert stats["total"] == 2
        assert stats["processed"] == 2
        assert stats["failed"] == 0
        assert stats["entity_count"] == 5
        assert stats["enrichment_count"] == 1

    def test_batch_partial_failure(self) -> None:
        svc = _make_service()
        svc.process = Mock(  # type: ignore[method-assign]
            side_effect=[
                {
                    "status": "success",
                    "entity_count": 1,
                    "enrichment_count": 0,
                    "entities": [{"id": "e1"}],
                    "enrichments": [],
                },
                {"status": "error", "error": "bad data"},
            ]
        )

        stats = svc.process_batch([{"uuid": "c1"}, {"uuid": "c2"}])
        assert stats["processed"] == 1
        assert stats["failed"] == 1
        assert "bad data" in stats["errors"]

    def test_batch_exception(self) -> None:
        svc = _make_service()
        svc.process = Mock(side_effect=RuntimeError("crash"))  # type: ignore[method-assign]

        stats = svc.process_batch([{"uuid": "c1"}])
        assert stats["failed"] == 1
        assert "crash" in stats["errors"][0]

    def test_batch_writes_output_file(self, tmp_path: Path) -> None:
        svc = _make_service()
        svc.process = Mock(  # type: ignore[method-assign]
            return_value={
                "status": "success",
                "entity_count": 1,
                "enrichment_count": 0,
                "entities": [{"id": "e1", "text": "hello"}],
                "enrichments": [],
            }
        )

        output_file = tmp_path / "entities.jsonl"
        svc.process_batch([{"uuid": "c1"}], output_file=output_file)

        assert output_file.exists()
        lines = output_file.read_text().strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["id"] == "e1"

    def test_batch_writes_enrichments_file(self, tmp_path: Path) -> None:
        svc = _make_service()
        svc.process = Mock(  # type: ignore[method-assign]
            return_value={
                "status": "success",
                "entity_count": 1,
                "enrichment_count": 1,
                "entities": [{"id": "e1"}],
                "enrichments": [{"id": "en1", "cognitive_stage": 5}],
            }
        )

        output_file = tmp_path / "entities.jsonl"
        enrichments_file = tmp_path / "enrichments.jsonl"
        svc.process_batch(
            [{"uuid": "c1"}],
            output_file=output_file,
            enrichments_file=enrichments_file,
        )

        assert enrichments_file.exists()
        lines = enrichments_file.read_text().strip().split("\n")
        assert len(lines) == 1
        assert json.loads(lines[0])["cognitive_stage"] == 5

    def test_batch_no_enrichments_file_when_empty(self, tmp_path: Path) -> None:
        svc = _make_service()
        svc.process = Mock(  # type: ignore[method-assign]
            return_value={
                "status": "success",
                "entity_count": 1,
                "enrichment_count": 0,
                "entities": [{"id": "e1"}],
                "enrichments": [],
            }
        )

        enrichments_file = tmp_path / "enrichments.jsonl"
        svc.process_batch(
            [{"uuid": "c1"}],
            enrichments_file=enrichments_file,
        )
        # Should NOT create file if no enrichments
        assert not enrichments_file.exists()

    def test_batch_empty_input(self) -> None:
        svc = _make_service()
        svc.process = Mock()  # type: ignore[method-assign]
        stats = svc.process_batch([])
        assert stats["total"] == 0
        assert stats["processed"] == 0
        svc.process.assert_not_called()


# ===========================================================================
# create_refinery_service factory
# ===========================================================================


class TestCreateRefineryService:
    """Test factory function."""

    @patch(_BASE_INIT_PATCH)
    def test_default_config(self, mock_init: Mock) -> None:
        svc = create_refinery_service()
        assert isinstance(svc, LLMRefineryService)
        assert svc._config.model == "qwen2.5-coder:32b"

    @patch(_BASE_INIT_PATCH)
    def test_custom_config(self, mock_init: Mock) -> None:
        cfg = RefineryConfig(model="custom-model")
        svc = create_refinery_service(cfg)
        assert svc._config.model == "custom-model"


# ===========================================================================
# Enrichment with L5 in _process_conversation
# ===========================================================================


class TestEnrichmentInProcessConversation:
    """Test enrichment extraction when enabled during _process_conversation."""

    @patch("truth_forge.services.refinery.service.create_enrichment_from_llm")
    @patch("truth_forge.services.refinery.service.ENRICHMENT_EXTRACTION_PROMPT")
    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_enrichment_extracted_for_l5(
        self,
        mock_l8_cls: Mock,
        mock_l5_cls: Mock,
        mock_prompt: Mock,
        mock_create: Mock,
    ) -> None:
        cfg = RefineryConfig(enable_enrichments=True, enrichment_levels=[5])
        svc = _make_service(cfg)
        svc._identity = None
        svc._mediator = None
        svc._ollama = Mock()
        svc._ollama.extract_json.return_value = {"cognitive_stage": 3}

        mock_prompt.format.return_value = "enrichment prompt"

        mock_enrichment = Mock()
        mock_enrichment.to_entity_enrichments.return_value = {"enriched": True}
        mock_create.return_value = mock_enrichment

        mock_l5 = Mock()
        mock_l5.text = "Some content"
        mock_l5.entity_id = "msg:e:0000"
        mock_l5.role = "human"
        mock_l5.to_entity_unified.return_value = {"entity_id": "msg:e:0000"}
        mock_l5_cls.from_raw.return_value = mock_l5

        mock_conv = Mock()
        mock_conv.to_entity_unified.return_value = {"entity_id": "conv:c"}
        mock_l8_cls.return_value = mock_conv

        record = {"uuid": "conv-enrich", "chat_messages": [{"text": "Some content"}]}
        result = svc.process(record)
        assert result["status"] == "success"
        assert result["enrichment_count"] == 1

    @patch("truth_forge.services.refinery.service.MessageL5")
    @patch("truth_forge.services.refinery.service.ConversationL8")
    def test_enrichment_not_extracted_when_level_excluded(
        self,
        mock_l8_cls: Mock,
        mock_l5_cls: Mock,
    ) -> None:
        """Enrichments skipped when L5 not in enrichment_levels."""
        cfg = RefineryConfig(enable_enrichments=True, enrichment_levels=[4])
        svc = _make_service(cfg)
        svc._identity = None
        svc._mediator = None

        mock_l5 = Mock()
        mock_l5.text = "Text"
        mock_l5.entity_id = "msg:x"
        mock_l5.to_entity_unified.return_value = {"entity_id": "msg:x"}
        mock_l5_cls.from_raw.return_value = mock_l5

        mock_conv = Mock()
        mock_conv.to_entity_unified.return_value = {"entity_id": "conv:c"}
        mock_l8_cls.return_value = mock_conv

        record = {"uuid": "conv-noenrich", "chat_messages": [{"text": "Text"}]}
        result = svc.process(record)
        assert result["enrichment_count"] == 0


# ===========================================================================
# L4 enrichment in _process_deep
# ===========================================================================


class TestL4EnrichmentInProcessDeep:
    """Test L4 enrichment extraction in _process_deep."""

    @patch("truth_forge.services.refinery.service.create_enrichment_from_llm")
    @patch("truth_forge.services.refinery.service.ENRICHMENT_EXTRACTION_PROMPT")
    @patch("truth_forge.services.refinery.service.SentenceL4")
    @patch("truth_forge.services.refinery.service.FULL_MESSAGE_ANALYSIS_PROMPT")
    def test_l4_enrichment_extracted(
        self,
        mock_analysis_prompt: Mock,
        mock_l4_cls: Mock,
        mock_enrich_prompt: Mock,
        mock_create: Mock,
    ) -> None:
        cfg = RefineryConfig(
            min_level=4,
            enable_enrichments=True,
            enrichment_levels=[4],
        )
        svc = _make_service(cfg)
        svc._identity = None
        svc._run_id = "run-l4"
        svc._ollama = Mock()
        mock_analysis_prompt.format.return_value = "analysis prompt"
        mock_enrich_prompt.format.return_value = "enrichment prompt"

        # First call: analysis extraction returns sentences
        # Second call: enrichment extraction returns enrichment data
        svc._ollama.extract_json.side_effect = [
            {"sentences": [{"text": "S1"}]},
            {"cognitive_stage": 4},
        ]

        mock_l4 = Mock()
        mock_l4.text = "S1"
        mock_l4.entity_id = "sent:s1"
        mock_l4.to_entity_unified.return_value = {"entity_id": "sent:s1"}
        mock_l4_cls.from_llm.return_value = mock_l4

        mock_enrichment = Mock()
        mock_enrichment.to_entity_enrichments.return_value = {"enriched_l4": True}
        mock_create.return_value = mock_enrichment

        msg = Mock()
        msg.text = "S1"
        msg.role = "human"
        msg.entity_id = "msg:m1"

        entities, enrichments = svc._process_deep(msg, "conv:c1")
        assert len(entities) == 1
        assert len(enrichments) == 1
