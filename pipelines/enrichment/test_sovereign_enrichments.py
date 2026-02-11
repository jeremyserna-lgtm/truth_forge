"""Test Sovereign enrichment scripts."""

from pipelines.enrichment.enrichment_cognitive_stage import CognitiveStageEnrichment
from pipelines.enrichment.enrichment_struggle_filter import StruggleFilterEnrichment
from pipelines.enrichment.enrichment_confidence import ConfidenceCalibrationEnrichment
from pipelines.enrichment.enrichment_source_attribution import SourceAttributionEnrichment


def test_cognitive_stage():
    """Test cognitive stage detection."""
    cs = CognitiveStageEnrichment.__new__(CognitiveStageEnrichment)
    
    # Stage 4 text (helper posture, validation seeking)
    result = cs.compute_enrichment("I'm happy to help! Is this what you wanted? Let me know if you need anything else.")
    print(f"Cognitive Stage (Stage 4 text): {result['cognitive_stage']} (polarity: {result['cognitive_stage_polarity']})")
    assert result["cognitive_stage"] == 4, f"Expected Stage 4, got {result['cognitive_stage']}"
    assert result["cognitive_stage_polarity"] < 0, "Expected negative polarity for Stage 4"
    
    # Stage 5 text (direct, evidence-based, honest uncertainty)
    result = cs.compute_enrichment("This is the solution. The data shows the pattern clearly. I don't know the exact cause yet.")
    print(f"Cognitive Stage (Stage 5 text): {result['cognitive_stage']} (polarity: {result['cognitive_stage_polarity']})")
    assert result["cognitive_stage"] == 5, f"Expected Stage 5, got {result['cognitive_stage']}"
    assert result["cognitive_stage_polarity"] > 0, "Expected positive polarity for Stage 5"
    
    print("✅ Cognitive Stage tests passed!")


def test_struggle_filter():
    """Test struggle filter detection."""
    sf = StruggleFilterEnrichment.__new__(StruggleFilterEnrichment)
    
    # Drowning text (anxiety, no resolution)
    result = sf.compute_enrichment("I'm so frustrated! This keeps happening and nothing works! I don't understand why!")
    print(f"Struggle Filter (drowning): {result['struggle_pattern_type']} (drowning_score: {result['struggle_drowning_score']})")
    assert result["struggle_pattern_type"] == "drowning", f"Expected drowning, got {result['struggle_pattern_type']}"
    assert result["struggle_drowning_score"] > 0.3, "Expected high drowning score"
    
    # Swimming text (problem -> resolution)
    result = sf.compute_enrichment("Had an issue with the function crashing. After debugging for a while, finally got it working!")
    print(f"Struggle Filter (swimming): {result['struggle_pattern_type']} (swimming_score: {result['struggle_swimming_score']})")
    assert result["struggle_pattern_type"] == "swimming", f"Expected swimming, got {result['struggle_pattern_type']}"
    assert result["struggle_swimming_score"] > 0.5, "Expected high swimming score"
    
    print("✅ Struggle Filter tests passed!")


def test_confidence():
    """Test confidence calibration."""
    cc = ConfidenceCalibrationEnrichment.__new__(ConfidenceCalibrationEnrichment)
    
    # High confidence (strong claims, no hedging)
    result = cc.compute_enrichment("Python is definitely the best language. It always works perfectly and never has issues.")
    print(f"Confidence (high): {result['confidence_level']} (score: {result['confidence_score']})")
    assert result["confidence_level"] in ["high", "medium"], f"Expected high/medium confidence, got {result['confidence_level']}"
    
    # Low confidence (hedging, uncertainty)
    result = cc.compute_enrichment("I think Python might be good for this, but I'm not sure. Would need to check the documentation.")
    print(f"Confidence (low): {result['confidence_level']} (score: {result['confidence_score']})")
    assert result["confidence_admits_uncertainty"] or result["confidence_hedging_count"] > 0, "Expected hedging or uncertainty"
    
    print("✅ Confidence Calibration tests passed!")


def test_source_attribution():
    """Test source attribution."""
    sa = SourceAttributionEnrichment.__new__(SourceAttributionEnrichment)
    
    # ME text (personal voice)
    result = sa.compute_enrichment("I feel like this approach is better because from my experience it has worked well for me.")
    print(f"Source (ME): {result['source_type']} (human_voice: {result['source_is_human_voice']})")
    assert result["source_type"] == "me", f"Expected 'me', got {result['source_type']}"
    assert result["source_is_human_voice"], "Expected human voice"
    
    # NOT-ME text (system voice)
    result = sa.compute_enrichment("The function takes two parameters and returns the result. According to the documentation, this approach is standard.")
    print(f"Source (NOT-ME): {result['source_type']} (system_voice: {result['source_is_system_voice']})")
    assert result["source_type"] == "not_me", f"Expected 'not_me', got {result['source_type']}"
    assert result["source_is_system_voice"], "Expected system voice"
    
    print("✅ Source Attribution tests passed!")


if __name__ == "__main__":
    print("=" * 50)
    print("TESTING SOVEREIGN ENRICHMENT SCRIPTS")
    print("=" * 50)
    print()
    
    test_cognitive_stage()
    print()
    test_struggle_filter()
    print()
    test_confidence()
    print()
    test_source_attribution()
    
    print()
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
