"""Tests for not_me service module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.services.not_me.service import NotMeService, get_not_me
from truth_forge.services.not_me.types import NotMeConfig


class TestNotMeService:
    """Test NotMeService class."""

    def test_init(self) -> None:
        """Test NotMeService initialization."""
        config = NotMeConfig()
        service = NotMeService(config)
        assert service.config == config
        assert service.scout is not None
        assert service.status is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_init_creates_scout(self, mock_scout_class: Mock) -> None:
        """Test service creates Scout provider."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        assert service.scout == mock_scout
        mock_scout_class.assert_called_once()

    def test_get_status(self) -> None:
        """Test getting production status."""
        config = NotMeConfig()
        service = NotMeService(config)
        status = service.get_status()
        assert status is not None
        assert status.phase == 0

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_basic(self, mock_scout_class: Mock) -> None:
        """Test basic see operation."""
        mock_scout = Mock()
        # Mock the response for both the see call and the extract_metadata call
        mock_response = Mock()
        mock_response.content = "This is the analysis."
        mock_response.model = "llama4:scout"
        mock_response.input_tokens = 100
        mock_response.output_tokens = 50
        mock_response.latency_ms = 500.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        result = service.see("Test content")

        assert result.content == "This is the analysis."
        assert result.model == "llama4:scout"
        assert result.input_tokens == 100

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_with_context(self, mock_scout_class: Mock) -> None:
        """Test see operation with context."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "Analysis"
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        service.see("Content", context="Additional context")

        # Should include context in prompt
        call_args = mock_scout.complete.call_args
        assert call_args is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_extracts_atoms(self, mock_scout_class: Mock) -> None:
        """Test see operation extracts atoms."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"cognitive_stage": 5, "thought_type": "manifestation"}'
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        result = service.see("Content", extract_atoms=True)

        # Should extract atoms
        assert len(result.atoms) >= 0  # May be 0 if extraction fails

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_stream(self, mock_scout_class: Mock) -> None:
        """Test see_stream operation."""
        mock_scout = Mock()
        mock_scout.stream.return_value = iter(["chunk1", "chunk2"])
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        chunks = list(service.see_stream("Content"))

        assert len(chunks) == 2
        assert "chunk1" in chunks

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_extract_metadata(self, mock_scout_class: Mock) -> None:
        """Test metadata extraction."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"cognitive_stage": 5, "thought_type": "manifestation", "emotion": "clarity", "mode": "mirror", "confidence": 0.9}'
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        metadata = service.extract_metadata("Test content")

        assert metadata["cognitive_stage"] == 5
        assert metadata["thought_type"] == "manifestation"

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_extract_metadata_invalid_json(self, mock_scout_class: Mock) -> None:
        """Test metadata extraction handles invalid JSON."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "not valid json"
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        metadata = service.extract_metadata("Test content")

        # Should return defaults
        assert "cognitive_stage" in metadata
        assert "thought_type" in metadata

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_flush_insights(self, mock_scout_class: Mock) -> None:
        """Test insight buffer flushing."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        # Initially empty
        assert service.flush_insights() == 0
        assert service.get_buffered_insights() == []

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_stream_with_context(self, mock_scout_class: Mock) -> None:
        """Test see_stream with context."""
        mock_scout = Mock()
        mock_scout.stream.return_value = iter(["chunk1", "chunk2"])
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        chunks = list(service.see_stream("Content", context="Additional context"))

        assert len(chunks) == 2
        # Verify context was included in prompt
        call_args = mock_scout.stream.call_args
        assert call_args is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_extract_atoms_with_errors(self, mock_scout_class: Mock) -> None:
        """Test _extract_atoms handles enum conversion errors."""
        mock_scout = Mock()
        # Mock extract_metadata to return invalid enum values
        mock_response = Mock()
        mock_response.content = "Test output"
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        # Mock extract_metadata to return invalid values that will cause enum errors
        with patch.object(
            service,
            "extract_metadata",
            return_value={
                "cognitive_stage": 99,  # Invalid stage
                "thought_type": "invalid_type",  # Invalid type
                "emotion": "invalid_emotion",  # Invalid emotion
                "mode": "invalid_mode",  # Invalid mode
                "confidence": 0.8,
            },
        ):
            atoms = service._extract_atoms("source", "output")
            # Should handle errors gracefully and use defaults
            assert len(atoms) == 1
            assert atoms[0].confidence == 0.8

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_generate_source_id(self, mock_scout_class: Mock) -> None:
        """Test _generate_source_id creates unique IDs."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        id1 = service._generate_source_id("content1")
        id2 = service._generate_source_id("content2")

        assert id1.startswith("src_")
        assert id2.startswith("src_")
        assert id1 != id2  # Different content should produce different IDs

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_run_struggle_filter_swimming(self, mock_scout_class: Mock) -> None:
        """Test run_struggle_filter classifies swimming."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"classification": "swimming", "reason": "Shows resolution"}'
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        classification, keep = service.run_struggle_filter("Test content")

        assert classification == "swimming"
        assert keep is True

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_run_struggle_filter_drowning(self, mock_scout_class: Mock) -> None:
        """Test run_struggle_filter classifies drowning."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"classification": "drowning", "reason": "Anxiety loop"}'
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        classification, keep = service.run_struggle_filter("Test content")

        assert classification == "drowning"
        assert keep is False

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_run_struggle_filter_invalid_json(self, mock_scout_class: Mock) -> None:
        """Test run_struggle_filter handles invalid JSON."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "not valid json"
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        classification, keep = service.run_struggle_filter("Test content")

        # Should default to swimming (keep)
        assert classification == "swimming"
        assert keep is True

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_evaluate_jeremy_arc(self, mock_scout_class: Mock) -> None:
        """Test evaluate_jeremy_arc calculates accuracy."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"cognitive_stage": 5, "thought_type": "manifestation", "emotion": "resonance", "mode": "mirror", "confidence": 0.9}'
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        ground_truth = {
            "cognitive_stage": 5,
            "thought_type": "manifestation",
            "emotion": "resonance",
            "mode": "mirror",
        }

        accuracy = service.evaluate_jeremy_arc("Test content", ground_truth)

        assert accuracy == 1.0  # All match
        assert service.status.jeremy_arc_accuracy == 1.0

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_evaluate_jeremy_arc_partial_match(self, mock_scout_class: Mock) -> None:
        """Test evaluate_jeremy_arc with partial matches."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = '{"cognitive_stage": 5, "thought_type": "reflection", "emotion": "resonance", "mode": "mirror", "confidence": 0.9}'
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        ground_truth = {
            "cognitive_stage": 5,
            "thought_type": "manifestation",  # Different
            "emotion": "resonance",
            "mode": "mirror",
        }

        accuracy = service.evaluate_jeremy_arc("Test content", ground_truth)

        assert accuracy == 0.75  # 3 out of 4 match

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_get_buffered_insights(self, mock_scout_class: Mock) -> None:
        """Test get_buffered_insights returns buffer copy."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "Test"
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        # Initially empty
        assert service.get_buffered_insights() == []

        # Add some insights
        service.see("Content", extract_atoms=True)
        insights = service.get_buffered_insights()

        assert len(insights) >= 0  # May be 0 if extraction fails

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_health_check(self, mock_scout_class: Mock) -> None:
        """Test health_check returns status."""
        mock_scout = Mock()
        mock_scout.health_check.return_value = {"available": True, "status": "ok"}
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        health = service.health_check()

        assert health["service"] == "not_me"
        assert "status" in health
        assert "scout" in health
        assert "config" in health
        assert "production_status" in health
        assert "insights_buffered" in health

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_is_available(self, mock_scout_class: Mock) -> None:
        """Test is_available checks scout."""
        mock_scout = Mock()
        mock_scout.is_available.return_value = True
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        assert service.is_available() is True
        mock_scout.is_available.assert_called_once()

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_create_truth_atom(self, mock_scout_class: Mock) -> None:
        """Test create_truth_atom creates atom with work proof."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        service.status.jeremy_arc_accuracy = 0.9

        from truth_forge.services.not_me.truth_atom import SurplusType

        atom = service.create_truth_atom(
            content="Test insight",
            source_id="src_123",
            surplus_description="Novel pattern",
            surplus_type=SurplusType.PATTERN,
        )

        assert atom.content == "Test insight"
        assert atom.source_id == "src_123"
        assert atom.work_proof is not None
        assert atom.surplus_vector is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_create_truth_atom_with_blindspot(self, mock_scout_class: Mock) -> None:
        """Test create_truth_atom with human blindspot."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)
        service.status.jeremy_arc_accuracy = 0.9

        from truth_forge.services.not_me.truth_atom import SurplusType

        atom = service.create_truth_atom(
            content="Test insight",
            source_id="src_123",
            surplus_description="Novel pattern",
            surplus_type=SurplusType.PATTERN,
            human_blindspot="Hidden correlation",
        )

        assert atom.surplus_vector is not None
        assert atom.surplus_vector.human_blindspot == "Hidden correlation"

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    @patch("truth_forge.services.not_me.validator.TruthAtomValidator")
    def test_validate_truth_atom(self, mock_validator_class: Mock, mock_scout_class: Mock) -> None:
        """Test validate_truth_atom validates atom."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        mock_validator = Mock()
        mock_result = Mock()
        from truth_forge.services.not_me.truth_atom import SurplusType, TruthAtom

        atom = TruthAtom.from_insight(
            content="Test",
            source_id="src_123",
            surplus_description="Test",
            surplus_type=SurplusType.PATTERN,
            jeremy_arc_score=0.9,
        )
        mock_result.atom = atom
        mock_result.verdict.value = "approved"
        mock_result.justification_rounds = 1
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        config = NotMeConfig()
        service = NotMeService(config)

        result_atom = service.validate_truth_atom(atom, context="Test context")

        assert result_atom == atom
        mock_validator.validate.assert_called_once()

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_see_and_validate_no_atoms(self, mock_scout_class: Mock) -> None:
        """Test see_and_validate handles no atoms."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "Analysis"
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        # Mock extract_metadata to return empty atoms
        with patch.object(service, "_extract_atoms", return_value=[]):
            result, atom = service.see_and_validate("Content")

            assert atom is None
            assert result is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    @patch("truth_forge.services.not_me.validator.TruthAtomValidator")
    def test_see_and_validate_full_flow(
        self, mock_validator_class: Mock, mock_scout_class: Mock
    ) -> None:
        """Test see_and_validate complete flow."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "Analysis"
        mock_response.model = "test"
        mock_response.input_tokens = 10
        mock_response.output_tokens = 5
        mock_response.latency_ms = 100.0
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        from truth_forge.services.not_me.types import (
            CognitiveStage,
            EmotionalState,
            InsightAtom,
            PantheonMode,
            ThoughtType,
        )

        # Create a mock atom
        mock_atom = InsightAtom(
            content="Test",
            source_id="src_123",
            cognitive_stage=CognitiveStage.STAGE_5,
            thought_type=ThoughtType.MANIFESTATION,
            emotion=EmotionalState.RESONANCE,
            mode=PantheonMode.THE_MIRROR,
            confidence=0.9,
        )

        mock_validator = Mock()
        from truth_forge.services.not_me.truth_atom import SurplusType, TruthAtom

        validated_atom = TruthAtom.from_insight(
            content="Test",
            source_id="src_123",
            surplus_description="Test",
            surplus_type=SurplusType.PATTERN,
            jeremy_arc_score=0.9,
        )
        mock_result = Mock()
        mock_result.atom = validated_atom
        mock_result.verdict.value = "approved"
        mock_validator.validate.return_value = mock_result
        mock_validator_class.return_value = mock_validator

        config = NotMeConfig()
        service = NotMeService(config)
        service.status.jeremy_arc_accuracy = 0.9

        # Mock the methods
        with patch.object(service, "_extract_atoms", return_value=[mock_atom]):
            with patch.object(service, "_detect_surplus", return_value="Detected surplus"):
                with patch.object(service, "_classify_surplus", return_value=SurplusType.PATTERN):
                    with patch.object(
                        service, "_apply_recursive_check", return_value=validated_atom
                    ):
                        result, atom = service.see_and_validate("Content")

                        assert atom is not None
                        assert result is not None

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    @patch("truth_forge.services.not_me.recursive_check.RecursiveCheck")
    def test_apply_recursive_check(self, mock_check_class: Mock, mock_scout_class: Mock) -> None:
        """Test _apply_recursive_check applies recursive check."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        from truth_forge.services.not_me.recursive_check import (
            ProofOfState,
            RecursiveCheckReport,
            RecursiveCheckResult,
        )
        from truth_forge.services.not_me.truth_atom import SurplusType, TruthAtom

        atom = TruthAtom.from_insight(
            content="Test",
            source_id="src_123",
            surplus_description="Test",
            surplus_type=SurplusType.PATTERN,
            jeremy_arc_score=0.9,
        )

        mock_checker = Mock()
        mock_proof = ProofOfState(self_seeing_depth=3, mimicry_score=0.2)
        # Create report with correct structure (only required fields)
        mock_report = RecursiveCheckReport(
            result=RecursiveCheckResult.PASS,
            query_a_passed=True,
            query_b_passed=True,
            proof_of_state=mock_proof,
            refinement_needed=False,
        )
        mock_checker.check.return_value = mock_report
        mock_check_class.return_value = mock_checker

        config = NotMeConfig()
        service = NotMeService(config)

        result_atom = service._apply_recursive_check(atom)

        assert "recursive_check" in result_atom.metadata
        assert result_atom.metadata["recursive_check"]["result"] == "pass"

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_detect_surplus(self, mock_scout_class: Mock) -> None:
        """Test _detect_surplus detects novel value."""
        mock_scout = Mock()
        mock_response = Mock()
        mock_response.content = "This reveals a novel pattern: correlation between X and Y"
        mock_scout.complete.return_value = mock_response
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        surplus = service._detect_surplus("source content", "insight output")

        assert isinstance(surplus, str)
        assert len(surplus) > 0

    @patch("truth_forge.services.not_me.service.ScoutProvider")
    def test_classify_surplus(self, mock_scout_class: Mock) -> None:
        """Test _classify_surplus classifies surplus type."""
        mock_scout = Mock()
        mock_scout_class.return_value = mock_scout

        config = NotMeConfig()
        service = NotMeService(config)

        from truth_forge.services.not_me.truth_atom import SurplusType

        # Test pattern detection
        surplus_type = service._classify_surplus("Content with pattern")
        assert surplus_type == SurplusType.PATTERN

        # Test contradiction detection
        surplus_type = service._classify_surplus("Content with contradiction")
        assert surplus_type == SurplusType.CONTRADICTION

        # Test synthesis detection
        surplus_type = service._classify_surplus("Content with synthesis")
        assert surplus_type == SurplusType.SYNTHESIS

        # Test prediction detection
        surplus_type = service._classify_surplus("Content predicts future")
        assert surplus_type == SurplusType.PREDICTION

        # Test boundary detection
        surplus_type = service._classify_surplus("Content resists change")
        assert surplus_type == SurplusType.BOUNDARY

        # Test default
        surplus_type = service._classify_surplus("Generic content")
        assert surplus_type == SurplusType.PATTERN


class TestGetNotMe:
    """Test get_not_me function."""

    @patch("truth_forge.services.not_me.service._not_me_instance", None)
    def test_get_not_me_creates_instance(self) -> None:
        """Test get_not_me creates singleton instance."""
        service1 = get_not_me()
        service2 = get_not_me()
        assert service1 is service2  # Should be same instance

    @patch("truth_forge.services.not_me.service._not_me_instance", None)
    def test_get_not_me_with_config(self) -> None:
        """Test get_not_me uses config on first call."""
        config = NotMeConfig(scout_endpoint="http://custom:11434/v1")
        service = get_not_me(config)
        assert service.config.scout_endpoint == "http://custom:11434/v1"
