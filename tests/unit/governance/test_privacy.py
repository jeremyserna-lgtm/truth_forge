"""Tests for privacy module."""

from __future__ import annotations

from truth_forge.governance.privacy import scrub_messages, scrub_text


class TestScrubText:
    """Test scrub_text function."""

    def test_scrub_email(self) -> None:
        """Test email scrubbing."""
        text = "Contact me at test@example.com for details"
        scrubbed = scrub_text(text)
        assert "test@example.com" not in scrubbed
        assert "[redacted-email]" in scrubbed

    def test_scrub_phone(self) -> None:
        """Test phone number scrubbing."""
        text = "Call me at 555-123-4567"
        scrubbed = scrub_text(text)
        assert "555-123-4567" not in scrubbed
        assert "[redacted-phone]" in scrubbed

    def test_scrub_phone_variants(self) -> None:
        """Test various phone number formats."""
        variants = [
            "555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "+1 555-123-4567",
        ]
        for phone in variants:
            scrubbed = scrub_text(f"Call {phone}")
            assert phone not in scrubbed
            assert "[redacted-phone]" in scrubbed

    def test_scrub_ssn(self) -> None:
        """Test SSN scrubbing."""
        text = "SSN: 123-45-6789"
        scrubbed = scrub_text(text)
        assert "123-45-6789" not in scrubbed
        assert "[redacted-ssn]" in scrubbed

    def test_scrub_multiple_pii(self) -> None:
        """Test scrubbing multiple PII types."""
        text = "Email: test@example.com, Phone: 555-123-4567, SSN: 123-45-6789"
        scrubbed = scrub_text(text)
        assert "[redacted-email]" in scrubbed
        assert "[redacted-phone]" in scrubbed
        assert "[redacted-ssn]" in scrubbed

    def test_no_pii_unchanged(self) -> None:
        """Test text without PII is unchanged."""
        text = "This is a normal message with no sensitive data"
        scrubbed = scrub_text(text)
        assert scrubbed == text


class TestScrubMessages:
    """Test scrub_messages function."""

    def test_scrub_single_message(self) -> None:
        """Test scrubbing single message."""
        messages = [{"role": "user", "content": "Email: test@example.com"}]
        scrubbed = scrub_messages(messages)
        assert len(scrubbed) == 1
        assert "[redacted-email]" in scrubbed[0]["content"]
        assert "test@example.com" not in scrubbed[0]["content"]

    def test_scrub_multiple_messages(self) -> None:
        """Test scrubbing multiple messages."""
        messages = [
            {"role": "user", "content": "Email: test@example.com"},
            {"role": "assistant", "content": "Phone: 555-123-4567"},
        ]
        scrubbed = scrub_messages(messages)
        assert len(scrubbed) == 2
        assert "[redacted-email]" in scrubbed[0]["content"]
        assert "[redacted-phone]" in scrubbed[1]["content"]

    def test_preserves_other_fields(self) -> None:
        """Test preserves non-content fields."""
        messages = [
            {"role": "user", "content": "test", "timestamp": 1234567890},
        ]
        scrubbed = scrub_messages(messages)
        assert scrubbed[0]["role"] == "user"
        assert scrubbed[0]["timestamp"] == 1234567890

    def test_message_without_content(self) -> None:
        """Test message without content field."""
        messages = [{"role": "user", "timestamp": 1234567890}]
        scrubbed = scrub_messages(messages)
        assert len(scrubbed) == 1
        assert "content" not in scrubbed[0]
