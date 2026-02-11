"""Tests for contact prompt builder."""

from __future__ import annotations

from unittest.mock import Mock

from truth_forge.services.llm.contact_prompt_builder import ContactPromptBuilder


class TestContactPromptBuilder:
    """Test ContactPromptBuilder class."""

    def test_build_contact_context_basic(self) -> None:
        """Test building basic contact context."""
        fetcher = Mock()
        builder = ContactPromptBuilder(fetcher)

        contact = {
            "canonical_name": "John Doe",
            "organization": "Acme Corp",
            "job_title": "Engineer",
        }

        context = builder.build_contact_context(contact)
        assert "John Doe" in context
        assert "Acme Corp" in context
        assert "Engineer" in context

    def test_build_contact_context_with_llm_context(self) -> None:
        """Test building context with LLM context data."""
        fetcher = Mock()
        builder = ContactPromptBuilder(fetcher)

        contact = {
            "canonical_name": "Jane Smith",
            "llm_context": {
                "relationship_arc": "Growing",
                "communication_style": "Formal",
                "key_interests": ["AI", "Python"],
            },
        }

        context = builder.build_contact_context(contact)
        assert "Growing" in context
        assert "Formal" in context
        assert "AI" in context
        assert "Python" in context

    def test_build_contact_context_with_json_strings(self) -> None:
        """Test building context with JSON string fields."""
        import json

        fetcher = Mock()
        builder = ContactPromptBuilder(fetcher)

        contact = {
            "canonical_name": "Test User",
            "llm_context": json.dumps({"relationship_arc": "Stable"}),
            "communication_stats": json.dumps({"last_contact_date": "2026-01-01"}),
        }

        context = builder.build_contact_context(contact)
        assert "Stable" in context
        assert "2026-01-01" in context

    def test_build_contact_context_invalid_json(self) -> None:
        """Test handling invalid JSON strings."""
        fetcher = Mock()
        builder = ContactPromptBuilder(fetcher)

        contact = {
            "canonical_name": "Test User",
            "llm_context": "not valid json",
        }

        # Should not raise, just skip invalid JSON
        context = builder.build_contact_context(contact)
        assert "Test User" in context

    def test_build_prompt_with_contact(self) -> None:
        """Test building prompt with contact context."""
        fetcher = Mock()
        fetcher.fetch_contact.return_value = {
            "canonical_name": "John Doe",
            "organization": "Acme",
        }

        builder = ContactPromptBuilder(fetcher)
        prompt = builder.build_prompt_with_contact("Base prompt", "contact-123")

        assert "Base prompt" in prompt
        assert "Contact Context" in prompt
        assert "John Doe" in prompt

    def test_build_prompt_contact_not_found(self) -> None:
        """Test building prompt when contact not found."""
        fetcher = Mock()
        fetcher.fetch_contact.return_value = None

        builder = ContactPromptBuilder(fetcher)
        prompt = builder.build_prompt_with_contact("Base prompt", "contact-123")

        assert prompt == "Base prompt"  # Returns base prompt unchanged

    def test_build_multi_contact_context(self) -> None:
        """Test building context for multiple contacts."""
        fetcher = Mock()
        fetcher.fetch_contact.side_effect = [
            {"canonical_name": "Contact 1"},
            {"canonical_name": "Contact 2"},
        ]

        builder = ContactPromptBuilder(fetcher)
        context = builder.build_multi_contact_context(["id1", "id2"])

        assert "Contact 1" in context
        assert "Contact 2" in context
        assert "---" in context  # Separator

    def test_build_multi_contact_some_missing(self) -> None:
        """Test building context when some contacts missing."""
        fetcher = Mock()
        fetcher.fetch_contact.side_effect = [
            {"canonical_name": "Contact 1"},
            None,  # Missing
            {"canonical_name": "Contact 3"},
        ]

        builder = ContactPromptBuilder(fetcher)
        context = builder.build_multi_contact_context(["id1", "id2", "id3"])

        assert "Contact 1" in context
        assert "Contact 3" in context
        # Should not include missing contact
