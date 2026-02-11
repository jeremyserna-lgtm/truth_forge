#!/usr/bin/env python3
"""
Test 2: Entity Hierarchy Levels L2-L8

This test validates EACH entity level in the hierarchy.
Tests are numbered in order - L2 first (leaf), L8 last (root).

WHAT THIS TESTS:
1. Each level class exists and can be instantiated
2. Each level has correct default level value
3. Each level has correct default entity_type
4. Each level's to_entity_unified() produces correct schema
5. Parent chain rules are enforced
6. Count computation works at each level

RUN AFTER test_01_entity_base.py PASSES.
"""

import pytest
from datetime import datetime, UTC

# BigQuery schema - THE SOURCE OF TRUTH
BIGQUERY_SCHEMA_COLUMNS = {
    "entity_id", "level", "entity_type", "entity_mode", "parent_id",
    "source_ids", "conversation_id", "topic_segment_id", "turn_id",
    "message_id", "sentence_id", "span_id", "word_id", "text",
    "source_pipeline", "source_file", "source_file_path", "source_system",
    "metadata", "created_at", "updated_at", "ingestion_job_id",
    "ingestion_timestamp", "validation_status", "source_message_timestamp",
    "persona", "content_date", "canonical_form", "l7_count", "l6_count",
    "l5_count", "l4_count", "l3_count", "l2_count", "role",
}


# =============================================================================
# L2: WORD LEVEL TESTS
# =============================================================================

class TestWordL2:
    """Test L2 Word entity - the leaf node."""
    
    def test_word_default_level_is_2(self):
        """WordL2 level must be 2"""
        from pipelines.llm_refinery.models import WordL2
        
        word = WordL2(
            entity_id="word:test:0001",
            text="hello",
            parent_id="span:parent:0001"
        )
        
        assert word.level == 2
    
    def test_word_default_entity_type(self):
        """WordL2 entity_type must be 'word'"""
        from pipelines.llm_refinery.models import WordL2
        
        word = WordL2(
            entity_id="word:test:0001",
            text="hello",
            parent_id="span:parent:0001"
        )
        
        assert word.entity_type == "word"
    
    def test_word_to_entity_unified_schema(self):
        """WordL2 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import WordL2
        
        word = WordL2(
            entity_id="word:test:0001",
            text="hello",
            parent_id="span:parent:0001"
        )
        
        output = word.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"
    
    def test_word_from_llm_creates_valid_entity(self):
        """from_llm() should create valid WordL2"""
        from pipelines.llm_refinery.models import WordL2
        
        word = WordL2.from_llm(
            word="programming",
            parent_id="span:parent:0001",
            index=0,
            llm_attrs={
                "word_type": "noun",
                "is_key_term": True,
                "canonical_form": "program"
            },
            hierarchy_ids={
                "conversation_id": "conv:test:0001",
                "span_id": "span:parent:0001"
            }
        )
        
        assert word.level == 2
        assert word.entity_type == "word"
        assert word.text == "programming"
        assert word.word_type == "noun"
        assert word.is_key_term is True
        assert word.canonical_form == "program"
    
    def test_word_has_no_children(self):
        """L2 is a leaf - no children attribute"""
        from pipelines.llm_refinery.models import WordL2
        
        word = WordL2(
            entity_id="word:test:0001",
            text="hello",
            parent_id="span:parent:0001"
        )
        
        # WordL2 should not have a children attribute
        assert not hasattr(word, "children") or getattr(word, "children", None) is None


# =============================================================================
# L3: SPAN LEVEL TESTS
# =============================================================================

class TestSpanL3:
    """Test L3 Span entity - phrase chunks."""
    
    def test_span_default_level_is_3(self):
        """SpanL3 level must be 3"""
        from pipelines.llm_refinery.models import SpanL3
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id="sent:parent:0001"
        )
        
        assert span.level == 3
    
    def test_span_default_entity_type(self):
        """SpanL3 entity_type must be 'span'"""
        from pipelines.llm_refinery.models import SpanL3
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id="sent:parent:0001"
        )
        
        assert span.entity_type == "span"
    
    def test_span_to_entity_unified_schema(self):
        """SpanL3 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import SpanL3
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id="sent:parent:0001"
        )
        
        output = span.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"
    
    def test_span_computes_l2_count(self):
        """SpanL3 should count its WordL2 children"""
        from pipelines.llm_refinery.models import SpanL3, WordL2
        
        words = [
            WordL2(entity_id=f"word:test:{i:04d}", text=w, parent_id="span:test:0001")
            for i, w in enumerate(["hello", "world"])
        ]
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id="sent:parent:0001",
            children=words
        )
        
        counts = span.compute_counts()
        assert counts["l2_count"] == 2


# =============================================================================
# L4: SENTENCE LEVEL TESTS
# =============================================================================

class TestSentenceL4:
    """Test L4 Sentence entity - grammatical units."""
    
    def test_sentence_default_level_is_4(self):
        """SentenceL4 level must be 4"""
        from pipelines.llm_refinery.models import SentenceL4
        
        sent = SentenceL4(
            entity_id="sent:test:0001",
            text="Hello world.",
            parent_id="msg:parent:0001"
        )
        
        assert sent.level == 4
    
    def test_sentence_default_entity_type(self):
        """SentenceL4 entity_type must be 'sentence'"""
        from pipelines.llm_refinery.models import SentenceL4
        
        sent = SentenceL4(
            entity_id="sent:test:0001",
            text="Hello world.",
            parent_id="msg:parent:0001"
        )
        
        assert sent.entity_type == "sentence"
    
    def test_sentence_to_entity_unified_schema(self):
        """SentenceL4 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import SentenceL4
        
        sent = SentenceL4(
            entity_id="sent:test:0001",
            text="Hello world.",
            parent_id="msg:parent:0001"
        )
        
        output = sent.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"


# =============================================================================
# L5: MESSAGE LEVEL TESTS
# =============================================================================

class TestMessageL5:
    """Test L5 Message entity - single speaker utterance."""
    
    def test_message_default_level_is_5(self):
        """MessageL5 level must be 5"""
        from pipelines.llm_refinery.models import MessageL5
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello, how are you?",
            parent_id="turn:parent:0001",
            role="human"
        )
        
        assert msg.level == 5
    
    def test_message_default_entity_type(self):
        """MessageL5 entity_type must be 'message'"""
        from pipelines.llm_refinery.models import MessageL5
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello, how are you?",
            parent_id="turn:parent:0001",
            role="human"
        )
        
        assert msg.entity_type == "message"
    
    def test_message_requires_role(self):
        """MessageL5 must have role field"""
        from pipelines.llm_refinery.models import MessageL5
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            MessageL5(
                entity_id="msg:test:0001",
                text="Hello",
                parent_id="turn:parent:0001"
                # Missing role
            )
    
    def test_message_to_entity_unified_schema(self):
        """MessageL5 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import MessageL5
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello, how are you?",
            parent_id="turn:parent:0001",
            role="human"
        )
        
        output = msg.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"
    
    def test_message_role_in_output(self):
        """MessageL5 role should appear in to_entity_unified output"""
        from pipelines.llm_refinery.models import MessageL5
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello",
            parent_id="turn:parent:0001",
            role="assistant"
        )
        
        output = msg.to_entity_unified()
        assert output["role"] == "assistant"


# =============================================================================
# L6: TURN LEVEL TESTS
# =============================================================================

class TestTurnL6:
    """Test L6 Turn entity - speaker change boundary."""
    
    def test_turn_default_level_is_6(self):
        """TurnL6 level must be 6"""
        from pipelines.llm_refinery.models import TurnL6
        
        turn = TurnL6(
            entity_id="turn:test:0001",
            text="User asks a question and gets a response.",
            parent_id="topic:parent:0001",
            speaker="human"
        )
        
        assert turn.level == 6
    
    def test_turn_default_entity_type(self):
        """TurnL6 entity_type must be 'turn'"""
        from pipelines.llm_refinery.models import TurnL6
        
        turn = TurnL6(
            entity_id="turn:test:0001",
            text="A turn",
            parent_id="topic:parent:0001",
            speaker="human"
        )
        
        assert turn.entity_type == "turn"
    
    def test_turn_requires_speaker(self):
        """TurnL6 must have speaker field"""
        from pipelines.llm_refinery.models import TurnL6
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            TurnL6(
                entity_id="turn:test:0001",
                text="A turn",
                parent_id="topic:parent:0001"
                # Missing speaker
            )
    
    def test_turn_to_entity_unified_schema(self):
        """TurnL6 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import TurnL6
        
        turn = TurnL6(
            entity_id="turn:test:0001",
            text="A turn",
            parent_id="topic:parent:0001",
            speaker="human"
        )
        
        output = turn.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"


# =============================================================================
# L7: TOPIC SEGMENT LEVEL TESTS
# =============================================================================

class TestTopicSegmentL7:
    """Test L7 TopicSegment entity - semantic groupings."""
    
    def test_topic_segment_default_level_is_7(self):
        """TopicSegmentL7 level must be 7"""
        from pipelines.llm_refinery.models import TopicSegmentL7
        
        segment = TopicSegmentL7(
            entity_id="topic:test:0001",
            text="Discussion about Python programming",
            parent_id="conv:parent:0001",
            topic_label="Python Basics"
        )
        
        assert segment.level == 7
    
    def test_topic_segment_default_entity_type(self):
        """TopicSegmentL7 entity_type must be 'topic_segment'"""
        from pipelines.llm_refinery.models import TopicSegmentL7
        
        segment = TopicSegmentL7(
            entity_id="topic:test:0001",
            text="Discussion about Python",
            parent_id="conv:parent:0001",
            topic_label="Python"
        )
        
        assert segment.entity_type == "topic_segment"
    
    def test_topic_segment_requires_topic_label(self):
        """TopicSegmentL7 must have topic_label field"""
        from pipelines.llm_refinery.models import TopicSegmentL7
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            TopicSegmentL7(
                entity_id="topic:test:0001",
                text="Discussion",
                parent_id="conv:parent:0001"
                # Missing topic_label
            )
    
    def test_topic_segment_to_entity_unified_schema(self):
        """TopicSegmentL7 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import TopicSegmentL7
        
        segment = TopicSegmentL7(
            entity_id="topic:test:0001",
            text="Discussion",
            parent_id="conv:parent:0001",
            topic_label="Test Topic"
        )
        
        output = segment.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"


# =============================================================================
# L8: CONVERSATION LEVEL TESTS
# =============================================================================

class TestConversationL8:
    """Test L8 Conversation entity - the root."""
    
    def test_conversation_default_level_is_8(self):
        """ConversationL8 level must be 8"""
        from pipelines.llm_refinery.models import ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="My Conversation",
            source_uuid="abc123-def456"
        )
        
        assert conv.level == 8
    
    def test_conversation_default_entity_type(self):
        """ConversationL8 entity_type must be 'conversation'"""
        from pipelines.llm_refinery.models import ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="My Conversation",
            source_uuid="abc123"
        )
        
        assert conv.entity_type == "conversation"
    
    def test_conversation_requires_source_uuid(self):
        """ConversationL8 must have source_uuid field"""
        from pipelines.llm_refinery.models import ConversationL8
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ConversationL8(
                entity_id="conv:test:0001",
                text="Conversation"
                # Missing source_uuid
            )
    
    def test_conversation_to_entity_unified_schema(self):
        """ConversationL8 output must match BigQuery schema"""
        from pipelines.llm_refinery.models import ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="My Conversation",
            source_uuid="abc123"
        )
        
        output = conv.to_entity_unified()
        output_columns = set(output.keys())
        
        missing = BIGQUERY_SCHEMA_COLUMNS - output_columns
        extra = output_columns - BIGQUERY_SCHEMA_COLUMNS
        
        assert not missing, f"Missing columns: {missing}"
        assert not extra, f"Extra columns: {extra}"
    
    def test_conversation_parent_id_is_none(self):
        """ConversationL8 (root) must have parent_id = None"""
        from pipelines.llm_refinery.models import ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="My Conversation",
            source_uuid="abc123"
        )
        
        assert conv.parent_id is None
        
        output = conv.to_entity_unified()
        assert output["parent_id"] is None
    
    def test_conversation_from_raw(self):
        """from_raw() should create valid ConversationL8"""
        from pipelines.llm_refinery.models import ConversationL8
        
        raw_data = {
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test Conversation",
            "summary": "A test",
            "created_at": "2026-02-02T10:00:00Z",
            "chat_messages": [
                {"sender": "human", "text": "Hello"},
                {"sender": "assistant", "text": "Hi there!"}
            ]
        }
        
        conv = ConversationL8.from_raw(raw_data)
        
        assert conv.level == 8
        assert conv.entity_type == "conversation"
        assert conv.source_uuid == "550e8400-e29b-41d4-a716-446655440000"
        assert conv.title == "Test Conversation"
        assert "human" in conv.participants
        assert "assistant" in conv.participants


# =============================================================================
# PARENT CHAIN VALIDATION TESTS
# =============================================================================

class TestParentChainRules:
    """Test that parent chain rules are correct."""
    
    def test_l2_parent_should_be_l3(self):
        """L2 (word) parent should be L3 (span) entity_id"""
        from pipelines.llm_refinery.models import WordL2, SpanL3
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id="sent:test:0001"
        )
        
        word = WordL2(
            entity_id="word:test:0001",
            text="hello",
            parent_id=span.entity_id  # Parent is L3
        )
        
        assert word.parent_id == "span:test:0001"
    
    def test_l3_parent_should_be_l4(self):
        """L3 (span) parent should be L4 (sentence) entity_id"""
        from pipelines.llm_refinery.models import SpanL3, SentenceL4
        
        sent = SentenceL4(
            entity_id="sent:test:0001",
            text="Hello world.",
            parent_id="msg:test:0001"
        )
        
        span = SpanL3(
            entity_id="span:test:0001",
            text="hello world",
            parent_id=sent.entity_id  # Parent is L4
        )
        
        assert span.parent_id == "sent:test:0001"
    
    def test_l4_parent_should_be_l5(self):
        """L4 (sentence) parent should be L5 (message) entity_id"""
        from pipelines.llm_refinery.models import SentenceL4, MessageL5
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello world.",
            parent_id="turn:test:0001",
            role="human"
        )
        
        sent = SentenceL4(
            entity_id="sent:test:0001",
            text="Hello world.",
            parent_id=msg.entity_id  # Parent is L5
        )
        
        assert sent.parent_id == "msg:test:0001"
    
    def test_l5_parent_should_be_l6(self):
        """L5 (message) parent should be L6 (turn) entity_id"""
        from pipelines.llm_refinery.models import MessageL5, TurnL6
        
        turn = TurnL6(
            entity_id="turn:test:0001",
            text="A turn",
            parent_id="topic:test:0001",
            speaker="human"
        )
        
        msg = MessageL5(
            entity_id="msg:test:0001",
            text="Hello",
            parent_id=turn.entity_id,  # Parent is L6
            role="human"
        )
        
        assert msg.parent_id == "turn:test:0001"
    
    def test_l6_parent_should_be_l7(self):
        """L6 (turn) parent should be L7 (topic_segment) entity_id"""
        from pipelines.llm_refinery.models import TurnL6, TopicSegmentL7
        
        segment = TopicSegmentL7(
            entity_id="topic:test:0001",
            text="Topic",
            parent_id="conv:test:0001",
            topic_label="Test Topic"
        )
        
        turn = TurnL6(
            entity_id="turn:test:0001",
            text="A turn",
            parent_id=segment.entity_id,  # Parent is L7
            speaker="human"
        )
        
        assert turn.parent_id == "topic:test:0001"
    
    def test_l7_parent_should_be_l8(self):
        """L7 (topic_segment) parent should be L8 (conversation) entity_id"""
        from pipelines.llm_refinery.models import TopicSegmentL7, ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="Conversation",
            source_uuid="abc123"
        )
        
        segment = TopicSegmentL7(
            entity_id="topic:test:0001",
            text="Topic",
            parent_id=conv.entity_id,  # Parent is L8
            topic_label="Test"
        )
        
        assert segment.parent_id == "conv:test:0001"
    
    def test_l8_parent_must_be_none(self):
        """L8 (conversation) is root - parent_id must be None"""
        from pipelines.llm_refinery.models import ConversationL8
        
        conv = ConversationL8(
            entity_id="conv:test:0001",
            text="Conversation",
            source_uuid="abc123",
            parent_id=None
        )
        
        assert conv.parent_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
