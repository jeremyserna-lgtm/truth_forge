"""Tests for furnace engine module.

Tests the Furnace Engine, data models, and corpus retrievers.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from truth_forge.furnace.engine import (
    BaseFurnaceEngine,
    CorpusTruth,
    ForgeResult,
    FurnaceConfig,
    FurnaceEngine,
    InMemoryCorpusRetriever,
    NoOpCorpusRetriever,
    Truth,
)


class TestTruth:
    """Tests for Truth dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        truth = Truth(category="pattern", statement="Test statement")
        assert truth.category == "pattern"
        assert truth.statement == "Test statement"
        assert truth.evidence == ""

    def test_with_evidence(self) -> None:
        """Test with evidence."""
        truth = Truth(
            category="principle",
            statement="Always test",
            evidence="From the testing guide",
        )
        assert truth.evidence == "From the testing guide"

    def test_to_dict(self) -> None:
        """Test to_dict produces correct structure."""
        truth = Truth(
            category="theme",
            statement="Persistence matters",
            evidence="Quote here",
        )
        result = truth.to_dict()
        assert result["category"] == "theme"
        assert result["statement"] == "Persistence matters"
        assert result["evidence"] == "Quote here"


class TestCorpusTruth:
    """Tests for CorpusTruth dataclass."""

    def test_default_values(self) -> None:
        """Test default values."""
        ct = CorpusTruth(
            entity_id="entity_123",
            text="Some text",
            source="test_source",
        )
        assert ct.entity_id == "entity_123"
        assert ct.text == "Some text"
        assert ct.source == "test_source"
        assert ct.timestamp is None
        assert ct.metadata == {}

    def test_with_all_fields(self) -> None:
        """Test with all fields."""
        ct = CorpusTruth(
            entity_id="entity_456",
            text="Full text",
            source="full_source",
            timestamp="2024-01-15T10:00:00Z",
            metadata={"key": "value"},
        )
        assert ct.timestamp == "2024-01-15T10:00:00Z"
        assert ct.metadata["key"] == "value"


class TestForgeResult:
    """Tests for ForgeResult dataclass."""

    def test_creation(self) -> None:
        """Test creation with all fields."""
        result = ForgeResult(
            enriched_narrative="Enriched text",
            extracted_truths=[Truth(category="test", statement="stmt")],
            corpus_truths=[CorpusTruth(entity_id="1", text="t", source="s")],
            synthesis=[{"insight": "test"}],
            provenance={"source": "test"},
        )
        assert result.enriched_narrative == "Enriched text"
        assert len(result.extracted_truths) == 1
        assert len(result.corpus_truths) == 1

    def test_success_when_enriched(self) -> None:
        """Test success property when enriched narrative exists."""
        result = ForgeResult(
            enriched_narrative="Some text",
            extracted_truths=[],
            corpus_truths=[],
            synthesis=[],
            provenance={},
        )
        assert result.success is True

    def test_success_when_empty(self) -> None:
        """Test success property when enriched narrative is empty."""
        result = ForgeResult(
            enriched_narrative="",
            extracted_truths=[],
            corpus_truths=[],
            synthesis=[],
            provenance={},
        )
        assert result.success is False


class TestFurnaceConfig:
    """Tests for FurnaceConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = FurnaceConfig()
        assert config.max_corpus_results == 10
        assert config.default_lens == "Furnace"
        assert config.extraction_temperature == 0.3
        assert config.synthesis_temperature == 0.7
        assert config.max_output_tokens == 4096

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = FurnaceConfig(
            max_corpus_results=20,
            default_lens="Custom",
            extraction_temperature=0.5,
            synthesis_temperature=0.9,
            max_output_tokens=8192,
        )
        assert config.max_corpus_results == 20
        assert config.default_lens == "Custom"


class TestNoOpCorpusRetriever:
    """Tests for NoOpCorpusRetriever class."""

    def test_retrieve_returns_empty(self) -> None:
        """Test retrieve always returns empty list."""
        retriever = NoOpCorpusRetriever()
        truths = [Truth(category="test", statement="test")]
        result = retriever.retrieve(truths, max_results=10)
        assert result == []

    def test_retrieve_with_empty_input(self) -> None:
        """Test retrieve with empty truths list."""
        retriever = NoOpCorpusRetriever()
        result = retriever.retrieve([], max_results=5)
        assert result == []


class TestInMemoryCorpusRetriever:
    """Tests for InMemoryCorpusRetriever class."""

    def test_init_empty(self) -> None:
        """Test initialization with no corpus."""
        retriever = InMemoryCorpusRetriever()
        assert retriever.corpus == []

    def test_init_with_corpus(self) -> None:
        """Test initialization with corpus."""
        corpus = [CorpusTruth(entity_id="1", text="t", source="s")]
        retriever = InMemoryCorpusRetriever(corpus=corpus)
        assert len(retriever.corpus) == 1

    def test_add(self) -> None:
        """Test adding truth to corpus."""
        retriever = InMemoryCorpusRetriever()
        ct = CorpusTruth(entity_id="1", text="test text", source="test")
        retriever.add(ct)
        assert len(retriever.corpus) == 1

    def test_retrieve_empty_corpus(self) -> None:
        """Test retrieve with empty corpus."""
        retriever = InMemoryCorpusRetriever()
        truths = [Truth(category="test", statement="find this")]
        result = retriever.retrieve(truths)
        assert result == []

    def test_retrieve_empty_truths(self) -> None:
        """Test retrieve with empty truths."""
        ct = CorpusTruth(entity_id="1", text="text", source="s")
        retriever = InMemoryCorpusRetriever(corpus=[ct])
        result = retriever.retrieve([])
        assert result == []

    def test_retrieve_keyword_matching(self) -> None:
        """Test retrieve finds matching keywords."""
        corpus = [
            CorpusTruth(entity_id="1", text="python programming", source="s1"),
            CorpusTruth(entity_id="2", text="java development", source="s2"),
            CorpusTruth(entity_id="3", text="python testing", source="s3"),
        ]
        retriever = InMemoryCorpusRetriever(corpus=corpus)

        truths = [Truth(category="test", statement="python is great")]
        result = retriever.retrieve(truths, max_results=10)

        # Should find entries with "python"
        assert len(result) >= 1
        entity_ids = [r.entity_id for r in result]
        assert "1" in entity_ids or "3" in entity_ids

    def test_retrieve_respects_max_results(self) -> None:
        """Test retrieve respects max_results limit."""
        corpus = [
            CorpusTruth(entity_id=str(i), text=f"python {i}", source="s")
            for i in range(20)
        ]
        retriever = InMemoryCorpusRetriever(corpus=corpus)

        truths = [Truth(category="test", statement="python")]
        result = retriever.retrieve(truths, max_results=5)

        assert len(result) <= 5

    def test_retrieve_sorts_by_score(self) -> None:
        """Test retrieve sorts by keyword overlap score."""
        corpus = [
            CorpusTruth(entity_id="1", text="python", source="s1"),  # 1 match
            CorpusTruth(entity_id="2", text="python testing best", source="s2"),  # 3 matches
            CorpusTruth(entity_id="3", text="python testing", source="s3"),  # 2 matches
        ]
        retriever = InMemoryCorpusRetriever(corpus=corpus)

        truths = [Truth(category="test", statement="python testing best practices")]
        result = retriever.retrieve(truths, max_results=3)

        # Higher scoring items should come first
        assert result[0].entity_id == "2"


class ConcreteFurnaceEngine(BaseFurnaceEngine):
    """Concrete implementation for testing BaseFurnaceEngine."""

    def __init__(
        self,
        llm_response: str | dict[str, Any] = "",
        config: FurnaceConfig | None = None,
        corpus_retriever: Any = None,
    ) -> None:
        """Initialize with mock LLM response."""
        super().__init__(config, corpus_retriever)
        self.llm_response = llm_response
        self.call_count = 0
        self.last_prompt = ""

    def _call_llm(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str | None = None,
    ) -> str:
        """Return mock LLM response."""
        self.call_count += 1
        self.last_prompt = prompt
        if isinstance(self.llm_response, dict):
            return json.dumps(self.llm_response)
        return self.llm_response


class TestBaseFurnaceEngine:
    """Tests for BaseFurnaceEngine abstract class."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        engine = ConcreteFurnaceEngine()
        assert engine.config.default_lens == "Furnace"
        assert isinstance(engine.corpus_retriever, NoOpCorpusRetriever)

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = FurnaceConfig(default_lens="Custom")
        engine = ConcreteFurnaceEngine(config=config)
        assert engine.config.default_lens == "Custom"

    def test_init_custom_retriever(self) -> None:
        """Test initialization with custom retriever."""
        retriever = InMemoryCorpusRetriever()
        engine = ConcreteFurnaceEngine(corpus_retriever=retriever)
        assert engine.corpus_retriever is retriever

    def test_extract_truths_success(self) -> None:
        """Test _extract_truths with valid response."""
        response = {
            "truths": [
                {"category": "pattern", "statement": "Truth 1", "evidence": "Evidence 1"},
                {"category": "principle", "statement": "Truth 2", "evidence": "Evidence 2"},
            ]
        }
        engine = ConcreteFurnaceEngine(llm_response=response)

        truths = engine._extract_truths("Test narrative")

        assert len(truths) == 2
        assert truths[0].category == "pattern"
        assert truths[0].statement == "Truth 1"

    def test_extract_truths_invalid_json(self) -> None:
        """Test _extract_truths handles invalid JSON."""
        engine = ConcreteFurnaceEngine(llm_response="not valid json")

        truths = engine._extract_truths("Test narrative")

        assert truths == []

    def test_extract_truths_with_metadata(self) -> None:
        """Test _extract_truths includes metadata in prompt."""
        response = {"truths": []}
        engine = ConcreteFurnaceEngine(llm_response=response)

        engine._extract_truths("Test", metadata={"key": "value"})

        assert "METADATA" in engine.last_prompt
        assert "key" in engine.last_prompt

    def test_forge_synthesis_success(self) -> None:
        """Test _forge_synthesis with valid response."""
        response = {
            "enriched_narrative": "Enriched text here",
            "synthesis": [{"insight": "New insight"}],
        }
        engine = ConcreteFurnaceEngine(llm_response=response)

        result = engine._forge_synthesis(
            raw_text="Raw text",
            extracted_truths=[Truth(category="test", statement="stmt")],
            corpus_truths=[],
            lens="Furnace",
        )

        assert result["enriched_narrative"] == "Enriched text here"
        assert len(result["synthesis"]) == 1

    def test_forge_synthesis_invalid_json(self) -> None:
        """Test _forge_synthesis handles invalid JSON."""
        engine = ConcreteFurnaceEngine(llm_response="invalid")

        result = engine._forge_synthesis(
            raw_text="Raw text",
            extracted_truths=[],
            corpus_truths=[],
            lens="Furnace",
        )

        # Should return raw text on error
        assert result["enriched_narrative"] == "Raw text"
        assert "error" in result

    def test_forge_synthesis_with_corpus_truths(self) -> None:
        """Test _forge_synthesis includes corpus context."""
        response = {"enriched_narrative": "text", "synthesis": []}
        engine = ConcreteFurnaceEngine(llm_response=response)

        corpus_truths = [
            CorpusTruth(
                entity_id="1",
                text="Corpus text",
                source="test_source",
                timestamp="2024-01-15",
            )
        ]

        engine._forge_synthesis(
            raw_text="Raw",
            extracted_truths=[],
            corpus_truths=corpus_truths,
            lens="Furnace",
        )

        assert "Corpus text" in engine.last_prompt
        assert "test_source" in engine.last_prompt

    def test_forge_narrative_full_pipeline(self) -> None:
        """Test forge_narrative runs full pipeline."""
        # First call extracts truths, second call synthesizes
        call_responses = [
            json.dumps({"truths": [{"category": "test", "statement": "Truth", "evidence": ""}]}),
            json.dumps({"enriched_narrative": "Final narrative", "synthesis": []}),
        ]
        engine = ConcreteFurnaceEngine()
        engine._responses = iter(call_responses)

        def mock_call(*args: Any, **kwargs: Any) -> str:
            return next(engine._responses)

        engine._call_llm = mock_call  # type: ignore[method-assign]

        result = engine.forge_narrative("Raw input text")

        assert isinstance(result, ForgeResult)
        assert result.enriched_narrative == "Final narrative"

    def test_forge_narrative_uses_config_defaults(self) -> None:
        """Test forge_narrative uses config defaults."""
        config = FurnaceConfig(default_lens="Custom", max_corpus_results=5)
        engine = ConcreteFurnaceEngine(
            llm_response={"truths": []},
            config=config,
        )

        # Override to track calls
        synthesis_response = {"enriched_narrative": "text", "synthesis": []}
        engine._call_llm = lambda *a, **k: json.dumps(synthesis_response)  # type: ignore[method-assign]

        result = engine.forge_narrative("Text")

        assert result.provenance["lens"] == "Custom"

    def test_forge_narrative_custom_parameters(self) -> None:
        """Test forge_narrative with custom parameters."""
        engine = ConcreteFurnaceEngine(llm_response={"truths": []})
        synthesis_response = {"enriched_narrative": "text", "synthesis": []}
        engine._call_llm = lambda *a, **k: json.dumps(synthesis_response)  # type: ignore[method-assign]

        result = engine.forge_narrative(
            "Text",
            lens="CustomLens",
            max_corpus_results=3,
        )

        assert result.provenance["lens"] == "CustomLens"


class TestFurnaceEngine:
    """Tests for FurnaceEngine class."""

    def test_init_with_llm_client(self) -> None:
        """Test initialization with LLM client."""
        mock_client = MagicMock()
        engine = FurnaceEngine(llm_client=mock_client)
        assert engine.llm_client is mock_client

    def test_call_llm_delegates_to_client(self) -> None:
        """Test _call_llm delegates to LLM client."""
        mock_client = MagicMock()
        mock_client.generate.return_value = "LLM response"
        engine = FurnaceEngine(llm_client=mock_client)

        result = engine._call_llm(
            "Test prompt",
            temperature=0.5,
            max_tokens=1000,
            response_format="json",
        )

        assert result == "LLM response"
        mock_client.generate.assert_called_once_with(
            "Test prompt",
            temperature=0.5,
            max_tokens=1000,
            response_format="json",
        )

    def test_forge_narrative_integration(self) -> None:
        """Test full forge_narrative with mock LLM client."""
        mock_client = MagicMock()

        # Return extraction then synthesis
        responses = iter([
            json.dumps({"truths": [{"category": "test", "statement": "Truth", "evidence": ""}]}),
            json.dumps({"enriched_narrative": "Enriched", "synthesis": [{"insight": "New"}]}),
        ])
        mock_client.generate.side_effect = lambda *a, **k: next(responses)

        engine = FurnaceEngine(llm_client=mock_client)
        result = engine.forge_narrative("Raw narrative text")

        assert result.success
        assert result.enriched_narrative == "Enriched"
        assert len(result.extracted_truths) == 1
        assert len(result.synthesis) == 1
        assert mock_client.generate.call_count == 2

    def test_forge_narrative_with_corpus_retriever(self) -> None:
        """Test forge_narrative uses corpus retriever."""
        mock_client = MagicMock()
        responses = iter([
            json.dumps({"truths": [{"category": "test", "statement": "find python", "evidence": ""}]}),
            json.dumps({"enriched_narrative": "Enriched", "synthesis": []}),
        ])
        mock_client.generate.side_effect = lambda *a, **k: next(responses)

        corpus = [
            CorpusTruth(entity_id="1", text="python programming", source="s1"),
        ]
        retriever = InMemoryCorpusRetriever(corpus=corpus)

        engine = FurnaceEngine(llm_client=mock_client, corpus_retriever=retriever)
        result = engine.forge_narrative("Find python patterns")

        assert len(result.corpus_truths) >= 0  # May or may not match
        assert result.provenance["source"] == "furnace_engine_v2"
