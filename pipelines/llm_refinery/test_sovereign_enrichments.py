#!/usr/bin/env python3
"""Test Sovereign Architecture enrichments for Golden Record compliance."""

from pipelines.llm_refinery.enrichments import (
    EntityEnrichment,
    CognitiveStageEnrichment,
    StruggleFilterEnrichment,
    MetabolicStageEnrichment,
    ConfidenceCalibrationEnrichment,
    SourceAttributionEnrichment,
    TemporalLensEnrichment,
    OperationalCycleEnrichment,
    JeremyArcEnrichment,
    BANNED_VOCABULARY,
    MANIFESTATION_VOCABULARY,
)

print("=" * 70)
print("SOVEREIGN ARCHITECTURE ENRICHMENT VALIDATION")
print("=" * 70)

# Create a comprehensive enrichment with all components
enrichment = EntityEnrichment(
    entity_id="msg:test123:0000",
    enrichment_text="I see that the pattern shows this is clearly the right approach. I don't know everything, but this is solid.",
    cognitive_stage=CognitiveStageEnrichment(
        stage=5,
        stage_confidence=0.85,
        stage_markers=["direct assertion", "admits uncertainty"],
        manifestation_vocab_count=3,
        manifestation_vocab_matches=["I see that", "the pattern shows", "this is"],
        banned_vocab_count=0,
        banned_vocab_matches=[],
        stage_polarity=1.0,
    ),
    struggle_filter=StruggleFilterEnrichment(
        pattern_type="swimming",
        has_problem_statement=True,
        has_struggle_evidence=True,
        has_resolution=True,
        swimming_score=0.9,
        drowning_score=0.1,
        training_value="high",
    ),
    metabolic_stage=MetabolicStageEnrichment(
        metabolic_stage="meaning",
        has_pattern_recognition=True,
        has_structure_emergence=True,
        insight_level=0.8,
        revelation_present=True,
    ),
    confidence=ConfidenceCalibrationEnrichment(
        confidence_level="high",
        confidence_score=0.85,
        admits_uncertainty=True,
        uncertainty_phrases=["I don't know everything"],
    ),
    source_attribution=SourceAttributionEnrichment(
        source_type="not_me",
        is_system_voice=True,
        existence_context="function",
    ),
    temporal_lens=TemporalLensEnrichment(
        temporal_orientation="present",
        immediacy_level=0.7,
    ),
    operational_cycle=OperationalCycleEnrichment(
        cycle_phase="see_see",
        has_meta_awareness=True,
        sight_level=3,
    ),
    jeremy_arc=JeremyArcEnrichment(
        thought_type="analytical",
        mode="flow",
        arc_prediction_confidence=0.75,
    ),
)

# Convert to output format
output = enrichment.to_entity_enrichments()

print(f"\n[1] Total fields in output: {len(output)}")

# Group by category
categories = {
    "Core": ["entity_id", "enrichment_text", "enrichment_batch_id", "enrichment_quality_flags", "enrichment_metadata", "enriched_at"],
    "Sentiment": [k for k in output if k.startswith("textblob_")],
    "Emotion": [k for k in output if k.startswith("nrclx_") or k.startswith("goemotions_")],
    "Readability": [k for k in output if k.startswith("textstat_")],
    "Keywords": [k for k in output if k.startswith("keybert_")],
    "Topics": [k for k in output if k.startswith("bertopic_")],
    "Content": ["content_type", "domain", "primary_category", "category_path", "qa_role", "is_claim", "claim_type"],
    "Hate Speech": [k for k in output if k.startswith("roberta_")],
    "Cognitive Stage": [k for k in output if k.startswith("cognitive_")],
    "Struggle Filter": [k for k in output if k.startswith("struggle_")],
    "Metabolic Stage": [k for k in output if k.startswith("metabolic_")],
    "Confidence": [k for k in output if k.startswith("confidence_")],
    "Source Attribution": [k for k in output if k.startswith("source_")],
    "Temporal Lens": [k for k in output if k.startswith("temporal_")],
    "Operational Cycle": [k for k in output if k.startswith("cycle_")],
    "Jeremy Arc": [k for k in output if k.startswith("jeremy_arc_")],
}

print("\n[2] Fields by category:")
for cat, fields in categories.items():
    print(f"    {cat}: {len(fields)} fields")

print("\n[3] Sovereign Architecture metrics (from Golden Record & Framework):")
print(f"    ✓ Cognitive Stage: {output.get('cognitive_stage')} (conf: {output.get('cognitive_stage_confidence')})")
print(f"    ✓ Stage Polarity: {output.get('cognitive_stage_polarity')} (positive=Stage5, negative=Stage4)")
print(f"    ✓ Manifestation Vocab: {output.get('cognitive_manifestation_vocab_matches')}")
print(f"    ✓ Banned Vocab: {output.get('cognitive_banned_vocab_matches')}")
print(f"    ✓ Struggle Filter: {output.get('struggle_pattern_type')} (training_value: {output.get('struggle_training_value')})")
print(f"    ✓ Swimming Score: {output.get('struggle_swimming_score')}")
print(f"    ✓ Drowning Score: {output.get('struggle_drowning_score')}")
print(f"    ✓ Metabolic Stage: {output.get('metabolic_stage')}")
print(f"    ✓ Insight Level: {output.get('metabolic_insight_level')}")
print(f"    ✓ Revelation Present: {output.get('metabolic_revelation_present')}")
print(f"    ✓ Confidence Level: {output.get('confidence_level')}")
print(f"    ✓ Admits Uncertainty: {output.get('confidence_admits_uncertainty')} (healthy per Golden Record!)")
print(f"    ✓ Source Type: {output.get('source_type')}")
print(f"    ✓ Existence Context: {output.get('source_existence_context')}")
print(f"    ✓ Temporal Orientation: {output.get('temporal_orientation')}")
print(f"    ✓ Cycle Phase: {output.get('cycle_phase')}")
print(f"    ✓ Sight Level: {output.get('cycle_sight_level')}")
print(f"    ✓ Thought Type: {output.get('jeremy_arc_thought_type')}")
print(f"    ✓ Mode: {output.get('jeremy_arc_mode')}")
print(f"    ✓ Arc Prediction Confidence: {output.get('jeremy_arc_prediction_confidence')}")

print("\n[4] Banned/Manifestation vocabulary constants (Stage 5 detection):")
print(f"    BANNED_VOCABULARY: {len(BANNED_VOCABULARY)} phrases (Stage 4 indicators)")
for phrase in BANNED_VOCABULARY[:5]:
    print(f"        - '{phrase}'")
print("        ...")
print(f"    MANIFESTATION_VOCABULARY: {len(MANIFESTATION_VOCABULARY)} phrases (Stage 5 indicators)")
for phrase in MANIFESTATION_VOCABULARY:
    print(f"        - '{phrase}'")

print("\n[5] Golden Record alignment check:")
golden_record_requirements = {
    "Cognitive Stage (1-5)": "cognitive_stage" in output,
    "Struggle Filter (swim/drown)": "struggle_pattern_type" in output,
    "Metabolic Stage (TRUTH:MEANING:CARE)": "metabolic_stage" in output,
    "Confidence Calibration": "confidence_level" in output,
    "Admits Uncertainty (healthy)": "confidence_admits_uncertainty" in output,
    "ME/NOT-ME Attribution": "source_type" in output,
    "Temporal Lens (Past/Present/Future)": "temporal_orientation" in output,
    "Operational Cycle (SEE:SEE:DO:DONE)": "cycle_phase" in output,
    "Jeremy Arc Test (thought_type, mode)": "jeremy_arc_thought_type" in output,
    "Stage 5 Banned Vocabulary Detection": "cognitive_banned_vocab_matches" in output,
    "Stage 5 Manifestation Detection": "cognitive_manifestation_vocab_matches" in output,
}

all_passed = True
for requirement, present in golden_record_requirements.items():
    status = "✓" if present else "✗"
    if not present:
        all_passed = False
    print(f"    {status} {requirement}")

print("\n" + "=" * 70)
if all_passed:
    print("✓ VALIDATION COMPLETE - All Sovereign Architecture metrics present")
    print("  Ready for Genesis training data preparation")
else:
    print("✗ VALIDATION FAILED - Missing required metrics")
print("=" * 70)
