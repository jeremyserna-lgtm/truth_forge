#!/usr/bin/env python3
"""Test enrichment extraction from LLM Refinery.

Validates that entity_enrichments output matches the expected schema.
"""

import sys
sys.path.insert(0, "/Users/jeremyserna/truth_forge")
sys.path.insert(0, "/Users/jeremyserna/truth_forge/src")

import json


def test_enrichment_models():
    """Test the enrichment data classes."""
    print("=" * 70)
    print("ENRICHMENT MODELS TEST")
    print("=" * 70)
    
    from pipelines.llm_refinery.enrichments import (
        EntityEnrichment,
        SentimentEnrichment,
        EmotionEnrichment,
        ReadabilityEnrichment,
        KeywordEnrichment,
        TopicEnrichment,
        ContentClassification,
        HateSpeechEnrichment,
    )
    
    print("\n[1] Creating enrichment components...")
    
    sentiment = SentimentEnrichment(polarity=0.3, subjectivity=0.6)
    print(f"    ✓ Sentiment: polarity={sentiment.polarity}, subjectivity={sentiment.subjectivity}")
    
    emotion = EmotionEnrichment(
        nrclx_emotions={"joy": 0.8, "trust": 0.6, "anticipation": 0.4},
        nrclx_top_emotion="joy",
        nrclx_top_count=80,
        goemotions_top_emotions=["admiration", "approval", "gratitude"],
        goemotions_primary_emotion="admiration",
        goemotions_primary_score=0.85,
    )
    print(f"    ✓ Emotion: top={emotion.nrclx_top_emotion}, goemo={emotion.goemotions_top_emotions}")
    
    readability = ReadabilityEnrichment(
        flesch_reading_ease=65.0,
        flesch_kincaid_grade=8.5,
        lexicon_count=25,
        sentence_count=2,
        char_count=150,
    )
    print(f"    ✓ Readability: grade={readability.flesch_kincaid_grade}, words={readability.lexicon_count}")
    
    keywords = KeywordEnrichment(
        top_keyword="logging",
        top_score=0.95,
        top_5_keywords=["logging", "configuration", "service", "structured", "output"],
    )
    print(f"    ✓ Keywords: top={keywords.top_keyword}, all={keywords.top_5_keywords}")
    
    topics = TopicEnrichment(
        topic_id=42,
        topic_probability=0.87,
        topic_words=["logging", "debug", "trace", "output"],
        topic_label="Logging & Debugging",
    )
    print(f"    ✓ Topics: label={topics.topic_label}, words={topics.topic_words}")
    
    content = ContentClassification(
        content_type="question",
        domain="programming",
        qa_role="question",
        is_claim=False,
    )
    print(f"    ✓ Content: type={content.content_type}, domain={content.domain}")
    
    print("\n[2] Creating full EntityEnrichment...")
    
    enrichment = EntityEnrichment(
        entity_id="msg:test123:0000",
        enrichment_text="How do I configure the logging service for structured output?",
        sentiment=sentiment,
        emotion=emotion,
        readability=readability,
        keywords=keywords,
        topics=topics,
        content=content,
        enrichment_batch_id="run:test-batch-001",
        enrichment_quality_flags=["llm_extracted", "validated"],
    )
    
    print(f"    ✓ EntityEnrichment created for {enrichment.entity_id}")
    
    print("\n[3] Converting to entity_enrichments schema...")
    
    output = enrichment.to_entity_enrichments()
    
    print(f"    ✓ Output has {len(output)} fields")
    
    # Check key fields
    expected_fields = [
        "entity_id",
        "enrichment_text",
        "textblob_polarity",
        "textblob_subjectivity",
        "nrclx_emotions",
        "nrclx_top_emotion",
        "goemotions_top_emotions",
        "textstat_flesch_reading_ease",
        "textstat_lexicon_count",
        "keybert_top_keyword",
        "keybert_top_5_keywords",
        "bertopic_topic_label",
        "bertopic_topic_words",
        "content_type",
        "domain",
        "qa_role",
        "is_claim",
    ]
    
    missing = [f for f in expected_fields if f not in output]
    if missing:
        print(f"    ✗ Missing fields: {missing}")
    else:
        print("    ✓ All expected fields present")
    
    print("\n[4] Sample output (first 20 fields):")
    for i, (k, v) in enumerate(list(output.items())[:20]):
        print(f"    {k}: {v}")
    
    # Assert instead of return (pytest requirement)
    assert output is not None, "Output should not be None"
    assert len(output) > 0, "Output should have fields"
    assert not missing, f"Missing required fields: {missing}"


def test_enrichment_service():
    """Test enrichment extraction via service."""
    print()
    print("=" * 70)
    print("ENRICHMENT SERVICE TEST")
    print("=" * 70)
    
    from pipelines.llm_refinery.service import LLMRefineryService, RefineryConfig
    
    print("\n[1] Creating service with enrichments enabled...")
    
    config = RefineryConfig(
        model="qwen2.5-coder:32b",
        min_level=5,
        enable_enrichments=True,
        enrichment_levels=[5],  # Only enrich L5 messages for speed
    )
    
    service = LLMRefineryService(config)
    print(f"    ✓ Service created with enrichments={config.enable_enrichments}")
    print(f"    ✓ Enrichment levels: {config.enrichment_levels}")
    
    print("\n[2] Processing test conversation...")
    
    test_conversation = {
        "uuid": "test-enrichment-001",
        "name": "Logging Configuration Discussion",
        "chat_messages": [
            {
                "sender": "human",
                "text": "How do I configure the logging service for structured JSON output? I'm frustrated because the default format is hard to parse.",
                "created_at": "2026-02-01T10:00:00Z",
            },
            {
                "sender": "assistant",
                "text": "Great question! You can configure structured logging by using structlog. It provides JSON output by default and integrates well with our service architecture.",
                "created_at": "2026-02-01T10:00:10Z",
            },
        ],
    }
    
    try:
        result = service.process(test_conversation)
        
        print(f"    ✓ Processed successfully")
        print(f"    ✓ Entities: {result['entity_count']}")
        print(f"    ✓ Enrichments: {result.get('enrichment_count', 0)}")
        
        if result.get("enrichments"):
            print("\n[3] Sample enrichment output:")
            enrichment = result["enrichments"][0]
            
            print(f"\n    Entity ID: {enrichment.get('entity_id')}")
            print(f"    Text: {enrichment.get('enrichment_text', '')[:60]}...")
            print(f"    Sentiment: polarity={enrichment.get('textblob_polarity')}, subj={enrichment.get('textblob_subjectivity')}")
            print(f"    Top Emotion: {enrichment.get('nrclx_top_emotion')}")
            print(f"    GoEmotions: {enrichment.get('goemotions_top_emotions')}")
            print(f"    Keywords: {enrichment.get('keybert_top_5_keywords')}")
            print(f"    Topic: {enrichment.get('bertopic_topic_label')}")
            print(f"    Content Type: {enrichment.get('content_type')}")
            print(f"    Domain: {enrichment.get('domain')}")
            print(f"    QA Role: {enrichment.get('qa_role')}")
            print(f"    Is Claim: {enrichment.get('is_claim')}")
            
            print(f"\n    Full enrichment ({len(enrichment)} fields):")
            print(json.dumps(enrichment, indent=2, default=str))
        else:
            print("\n    ⚠ No enrichments generated (LLM may have timed out)")
            
    except Exception as e:
        print(f"    ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        service.on_shutdown()
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_enrichment_models()
    test_enrichment_service()
