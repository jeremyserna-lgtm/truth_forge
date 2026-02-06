"""Tests for relationship context builder."""

from __future__ import annotations

from unittest.mock import Mock

from truth_forge.services.llm.relationship_context_builder import RelationshipContextBuilder


class TestRelationshipContextBuilder:
    """Test RelationshipContextBuilder class."""

    def test_build_relationship_context_basic(self) -> None:
        """Test building basic relationship context."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "relationship_subtype": "Close",
            "is_current": True,
        }

        context = builder.build_relationship_context(relationship)
        assert "Friend" in context
        assert "Close" in context
        assert "Current" in context

    def test_build_relationship_context_ended(self) -> None:
        """Test building context for ended relationship."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Colleague",
            "is_current": False,
            "end_date": "2025-12-31",
        }

        context = builder.build_relationship_context(relationship)
        assert "Ended" in context
        assert "2025-12-31" in context

    def test_build_relationship_context_with_json_strings(self) -> None:
        """Test building context with JSON string fields."""
        import json

        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "relationship_context": json.dumps({"relationship_arc": "Growing"}),
            "social_context": json.dumps({"shared_interests": ["AI", "Python"]}),
        }

        context = builder.build_relationship_context(relationship)
        assert "Growing" in context
        assert "AI" in context
        assert "Python" in context

    def test_build_prompt_with_relationship(self) -> None:
        """Test building prompt with relationship context."""
        fetcher = Mock()
        fetcher.fetch_relationship.return_value = {
            "relationship_type": "Friend",
            "is_current": True,
        }

        builder = RelationshipContextBuilder(fetcher)
        prompt = builder.build_prompt_with_relationship("Base prompt", "rel-123")

        assert "Base prompt" in prompt
        assert "Relationship Context" in prompt
        assert "Friend" in prompt

    def test_build_prompt_relationship_not_found(self) -> None:
        """Test building prompt when relationship not found."""
        fetcher = Mock()
        fetcher.fetch_relationship.return_value = None

        builder = RelationshipContextBuilder(fetcher)
        prompt = builder.build_prompt_with_relationship("Base prompt", "rel-123")

        assert prompt == "Base prompt"  # Returns base prompt unchanged

    def test_build_social_graph_context(self) -> None:
        """Test building social graph context."""
        fetcher = Mock()
        fetcher.fetch_person_relationships.return_value = [
            {
                "person_1_id": "person-123",
                "person_2_id": "person-456",
                "relationship_type": "Friend",
                "relationship_subtype": "Close",
            },
            {
                "person_1_id": "person-789",
                "person_2_id": "person-123",
                "relationship_type": "Colleague",
            },
        ]

        builder = RelationshipContextBuilder(fetcher)
        context = builder.build_social_graph_context("person-123", max_depth=2)

        assert "person-123" in context
        assert "Total Relationships" in context
        assert "Friend" in context
        assert "Colleague" in context

    def test_build_social_graph_no_relationships(self) -> None:
        """Test building social graph when no relationships."""
        fetcher = Mock()
        fetcher.fetch_person_relationships.return_value = []

        builder = RelationshipContextBuilder(fetcher)
        context = builder.build_social_graph_context("person-123")

        assert "No relationships found" in context

    def test_build_relationship_context_all_fields(self) -> None:
        """Test building context with all possible fields."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "relationship_subtype": "Close",
            "relationship_status": "Active",
            "is_current": True,
            "relationship_context": {
                "relationship_arc": "Growing",
                "how_met": "College",
                "closeness_level": 8,
                "trust_level": 9,
                "emotional_depth": 7,
                "frequency_of_contact": "Weekly",
            },
            "social_context": {
                "common_connections": ["Alice", "Bob"],
                "shared_interests": ["AI", "Python"],
                "shared_groups": ["Tech Group"],
            },
            "tracking": {
                "last_interaction_date": "2026-01-15",
                "interaction_count": 50,
                "relationship_health": "Strong",
            },
            "llm_context": {
                "key_dynamics": ["Mutual support", "Shared goals"],
                "recommendations": ["Stay in touch", "Plan meetup"],
            },
            "evolution": {
                "relationship_timeline": ["Met in 2020", "Became close in 2021"],
            },
        }

        context = builder.build_relationship_context(relationship)
        assert "Friend" in context
        assert "Growing" in context
        assert "College" in context
        assert "8" in context  # closeness_level
        assert "Weekly" in context
        assert "2 people" in context  # common_connections count
        assert "AI" in context
        assert "Tech Group" in context
        assert "2026-01-15" in context
        assert "50" in context
        assert "Mutual support" in context
        assert "Stay in touch" in context

    def test_build_relationship_context_invalid_json(self) -> None:
        """Test building context handles invalid JSON strings."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "relationship_context": "not valid json {",
            "social_context": "also invalid {",
            "tracking": "invalid json",
            "llm_context": "bad json",
            "evolution": "not json",
        }

        context = builder.build_relationship_context(relationship)
        # Should handle gracefully without crashing
        assert "Friend" in context

    def test_build_relationship_context_list_fields(self) -> None:
        """Test building context with list fields."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "social_context": {
                "common_connections": ["Alice", "Bob", "Charlie"],
                "shared_interests": ["AI", "Python", "ML"],
                "shared_groups": ["Group1", "Group2"],
            },
            "llm_context": {
                "key_dynamics": ["Dynamic1", "Dynamic2", "Dynamic3"],
                "recommendations": ["Rec1", "Rec2"],
            },
            "evolution": {
                "relationship_timeline": ["Event1", "Event2"],
            },
        }

        context = builder.build_relationship_context(relationship)
        assert "3 people" in context  # common_connections count
        assert "AI, Python, ML" in context
        assert "Group1, Group2" in context
        assert "Dynamic1, Dynamic2, Dynamic3" in context
        assert "Rec1, Rec2" in context

    def test_build_relationship_context_non_list_fields(self) -> None:
        """Test building context handles non-list fields gracefully."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "social_context": {
                "common_connections": "not a list",  # Should be handled
                "shared_interests": 123,  # Should be handled
                "shared_groups": None,  # Should be handled
            },
            "llm_context": {
                "key_dynamics": "string not list",
                "recommendations": None,
            },
        }

        context = builder.build_relationship_context(relationship)
        # Should handle gracefully without crashing
        assert "Friend" in context

    def test_build_social_graph_with_depth(self) -> None:
        """Test building social graph with max_depth parameter."""
        fetcher = Mock()
        fetcher.fetch_person_relationships.return_value = [
            {
                "person_1_id": "person-123",
                "person_2_id": "person-456",
                "relationship_type": "Friend",
            },
        ]

        builder = RelationshipContextBuilder(fetcher)
        context = builder.build_social_graph_context("person-123", max_depth=1)

        assert "person-123" in context
        assert "Total Relationships" in context

    def test_build_relationship_context_empty_dicts(self) -> None:
        """Test building context with empty nested dicts."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "relationship_context": {},
            "social_context": {},
            "tracking": {},
            "llm_context": {},
            "evolution": {},
        }

        context = builder.build_relationship_context(relationship)
        assert "Friend" in context
        # Should not crash on empty dicts

    def test_build_relationship_context_milestones(self) -> None:
        """Test building context with milestones."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "evolution": {
                "milestones": ["Milestone1", "Milestone2", "Milestone3"],
            },
        }

        context = builder.build_relationship_context(relationship)
        assert "3 milestones" in context

    def test_build_relationship_context_timeline(self) -> None:
        """Test building context with timeline."""
        fetcher = Mock()
        builder = RelationshipContextBuilder(fetcher)

        relationship = {
            "relationship_type": "Friend",
            "evolution": {
                "relationship_timeline": ["Event1", "Event2"],
            },
        }

        context = builder.build_relationship_context(relationship)
        # Timeline is included in the context
        assert "Friend" in context
