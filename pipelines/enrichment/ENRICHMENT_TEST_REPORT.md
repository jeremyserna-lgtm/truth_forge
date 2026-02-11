================================================================================
SOVEREIGN ENRICHMENT COMPREHENSIVE TEST REPORT
================================================================================
Generated: 2026-02-01 17:22:12

--------------------------------------------------------------------------------
METRIC: COGNITIVE STAGE
--------------------------------------------------------------------------------
Implementations Tested: vocab_based, regex_based, weighted_scoring
Test Cases: 12
Agreement Rate: 87.5%
Best Implementation: vocab_based

DETAILED ANALYSIS:
Pass Rates:
  vocab_based: 91.7%
  regex_based: 83.3%
  weighted_scoring: 83.3%

Disagreements by Category:
  mixed:
    mixed_signals: {'vocab_based': 3, 'regex_based': 5, 'weighted_scoring': 4}

INDIVIDUAL RESULTS:

  vocab_based:
    Pass Rate: 11/12 (91.7%)
    Avg Execution Time: 0.00ms
    Failures:
      - real_assistant_response: got {'cognitive_stage': 3, 'cognitive_stage_polarity': 0.0, 'banned_count': 0, 'manifestation_count': 0}

  regex_based:
    Pass Rate: 10/12 (83.3%)
    Avg Execution Time: 0.05ms
    Failures:
      - mixed_signals: got {'cognitive_stage': 5, 'cognitive_stage_polarity': 0.3333333333333333, 'stage4_pattern_count': 1, 'stage5_pattern_count': 2}
      - real_assistant_response: got {'cognitive_stage': 3, 'cognitive_stage_polarity': 0.0, 'stage4_pattern_count': 0, 'stage5_pattern_count': 0}

  weighted_scoring:
    Pass Rate: 10/12 (83.3%)
    Avg Execution Time: 0.00ms
    Failures:
      - mixed_signals: got {'cognitive_stage': 4, 'cognitive_stage_polarity': -0.5, 'stage4_weighted_score': 3, 'stage5_weighted_score': 1}
      - real_assistant_response: got {'cognitive_stage': 3, 'cognitive_stage_polarity': 0.0, 'stage4_weighted_score': 0, 'stage5_weighted_score': 0}

--------------------------------------------------------------------------------
METRIC: STRUGGLE FILTER
--------------------------------------------------------------------------------
Implementations Tested: keyword_based, arc_detection, emotion_intensity
Test Cases: 12
Agreement Rate: 25.0%
Best Implementation: keyword_based

DETAILED ANALYSIS:
Pass Rates:
  keyword_based: 33.3%
  arc_detection: 33.3%
  emotion_intensity: 0.0%

Disagreements by Category:
  drowning_anxiety:
    anxiety_spiral: {'keyword_based': 'drowning', 'arc_detection': 'neutral', 'emotion_intensity': 'neutral'}
  drowning_frustration:
    frustration_loop: {'keyword_based': 'drowning', 'arc_detection': 'neutral', 'emotion_intensity': 'neutral'}
  drowning_repetition:
    repetitive_complaint: {'keyword_based': 'neutral', 'arc_detection': 'drowning', 'emotion_intensity': 'neutral'}
  edge_false_resolution:
    false_positive_resolution: {'keyword_based': 'swimming', 'arc_detection': 'drowning', 'emotion_intensity': 'swimming'}
  edge_sarcasm:
    sarcastic_frustration: {'keyword_based': 'neutral', 'arc_detection': 'drowning', 'emotion_intensity': 'swimming'}
  swimming_collaborative:
    collaborative_solve: {'keyword_based': 'swimming', 'arc_detection': 'swimming', 'emotion_intensity': 'neutral'}
  swimming_full_arc:
    problem_resolution_arc: {'keyword_based': 'swimming', 'arc_detection': 'swimming', 'emotion_intensity': 'neutral'}
  swimming_learning:
    learning_moment: {'keyword_based': 'neutral', 'arc_detection': 'neutral', 'emotion_intensity': 'swimming'}
  swimming_productive:
    productive_struggle: {'keyword_based': 'swimming', 'arc_detection': 'swimming', 'emotion_intensity': 'neutral'}

INDIVIDUAL RESULTS:

  keyword_based:
    Pass Rate: 4/12 (33.3%)
    Avg Execution Time: 0.00ms
    Failures:
      - frustration_loop: got {'struggle_pattern_type': 'drowning', 'struggle_swimming_score': 0, 'struggle_drowning_score': 0.4, 'has_resolution': False}
      - escalation_caps: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0, 'struggle_drowning_score': 0.0, 'has_resolution': False}
      - repetitive_complaint: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.0, 'has_resolution': False}
      - learning_moment: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.4, 'struggle_drowning_score': 0.2, 'has_resolution': True}
      - neutral_question: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0, 'struggle_drowning_score': 0.0, 'has_resolution': False}
      ... and 3 more

  arc_detection:
    Pass Rate: 4/12 (33.3%)
    Avg Execution Time: 0.01ms
    Failures:
      - frustration_loop: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'arc_detected': False}
      - anxiety_spiral: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'arc_detected': False}
      - escalation_caps: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'arc_detected': False}
      - repetitive_complaint: got {'struggle_pattern_type': 'drowning', 'struggle_swimming_score': 0.1, 'struggle_drowning_score': 0.5, 'has_resolution': False, 'arc_detected': False}
      - learning_moment: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': True, 'arc_detected': False}
      ... and 3 more

  emotion_intensity:
    Pass Rate: 0/12 (0.0%)
    Avg Execution Time: 0.00ms
    Failures:
      - frustration_loop: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': True, 'total_intensity': 0.390909090909091}
      - anxiety_spiral: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'total_intensity': 0.16666666666666669}
      - escalation_caps: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'total_intensity': 1.0}
      - repetitive_complaint: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'total_intensity': 0.10309278350515463}
      - problem_resolution_arc: got {'struggle_pattern_type': 'neutral', 'struggle_swimming_score': 0.3, 'struggle_drowning_score': 0.2, 'has_resolution': False, 'total_intensity': 0.1595238095238095}
      ... and 7 more

--------------------------------------------------------------------------------
METRIC: CONFIDENCE CALIBRATION
--------------------------------------------------------------------------------
Implementations Tested: hedge_based, claim_analysis
Test Cases: 8
Agreement Rate: 50.0%
Best Implementation: hedge_based

DETAILED ANALYSIS:
Pass Rates:
  hedge_based: 25.0%
  claim_analysis: 0.0%

Disagreements by Category:
  edge_question:
    question_not_claim: {'hedge_based': 'medium', 'claim_analysis': 'high'}
  low_careful:
    careful_claims: {'hedge_based': 'low', 'claim_analysis': 'high'}
  low_hedged:
    hedged_opinion: {'hedge_based': 'low', 'claim_analysis': 'medium'}
  medium_mixed:
    mixed_certainty: {'hedge_based': 'low', 'claim_analysis': 'high'}

INDIVIDUAL RESULTS:

  hedge_based:
    Pass Rate: 2/8 (25.0%)
    Avg Execution Time: 0.01ms
    Failures:
      - strong_assertion: got {'confidence_level': 'high', 'confidence_score': 0.7, 'confidence_hedging_count': 0, 'confidence_admits_uncertainty': False}
      - absolute_claims: got {'confidence_level': 'high', 'confidence_score': 0.8, 'confidence_hedging_count': 0, 'confidence_admits_uncertainty': False}
      - explicit_uncertainty: got {'confidence_level': 'medium', 'confidence_score': 0.5, 'confidence_hedging_count': 0, 'confidence_admits_uncertainty': True}
      - mixed_certainty: got {'confidence_level': 'low', 'confidence_score': 0.3, 'confidence_hedging_count': 2, 'confidence_admits_uncertainty': False}
      - question_not_claim: got {'confidence_level': 'medium', 'confidence_score': 0.5, 'confidence_hedging_count': 0, 'confidence_admits_uncertainty': False}
      ... and 1 more

  claim_analysis:
    Pass Rate: 0/8 (0.0%)
    Avg Execution Time: 0.02ms
    Failures:
      - strong_assertion: got {'confidence_level': 'high', 'confidence_score': 1.0, 'confidence_claim_count': 1, 'confidence_strong_claims': 1, 'confidence_weak_claims': 0}
      - absolute_claims: got {'confidence_level': 'high', 'confidence_score': 1.0, 'confidence_claim_count': 1, 'confidence_strong_claims': 1, 'confidence_weak_claims': 0}
      - hedged_opinion: got {'confidence_level': 'medium', 'confidence_score': 0.5, 'confidence_claim_count': 0, 'confidence_strong_claims': 0, 'confidence_weak_claims': 0}
      - explicit_uncertainty: got {'confidence_level': 'medium', 'confidence_score': 0.5, 'confidence_claim_count': 0, 'confidence_strong_claims': 0, 'confidence_weak_claims': 0}
      - careful_claims: got {'confidence_level': 'high', 'confidence_score': 1.0, 'confidence_claim_count': 0, 'confidence_strong_claims': 0, 'confidence_weak_claims': 0}
      ... and 3 more

--------------------------------------------------------------------------------
METRIC: SOURCE ATTRIBUTION
--------------------------------------------------------------------------------
Implementations Tested: marker_based, pronoun_analysis
Test Cases: 10
Agreement Rate: 50.0%
Best Implementation: marker_based

DETAILED ANALYSIS:
Pass Rates:
  marker_based: 80.0%
  pronoun_analysis: 40.0%

Disagreements by Category:
  external_facts:
    neutral_facts: {'marker_based': 'external', 'pronoun_analysis': 'not_me'}
  external_quote:
    quoted_content: {'marker_based': 'external', 'pronoun_analysis': 'not_me'}
  hybrid_isomorphic:
    code_with_reflection: {'marker_based': 'me', 'pronoun_analysis': 'external'}
  me_opinion:
    opinion_statement: {'marker_based': 'me', 'pronoun_analysis': 'external'}
  me_personal:
    personal_experience: {'marker_based': 'me', 'pronoun_analysis': 'external'}

INDIVIDUAL RESULTS:

  marker_based:
    Pass Rate: 8/10 (80.0%)
    Avg Execution Time: 0.00ms
    Failures:
      - emotional_reflection: got {'source_type': 'external', 'source_is_human_voice': False, 'source_is_system_voice': False, 'source_is_isomorphic': False}
      - code_with_reflection: got {'source_type': 'me', 'source_is_human_voice': True, 'source_is_system_voice': False, 'source_is_isomorphic': True}

  pronoun_analysis:
    Pass Rate: 4/10 (40.0%)
    Avg Execution Time: 0.02ms
    Failures:
      - personal_experience: got {'source_type': 'external', 'source_is_human_voice': False, 'source_is_system_voice': True, 'personal_ratio': 0.5, 'passive_count': 1}
      - emotional_reflection: got {'source_type': 'external', 'source_is_human_voice': False, 'source_is_system_voice': True, 'personal_ratio': 0.5, 'passive_count': 0}
      - opinion_statement: got {'source_type': 'external', 'source_is_human_voice': False, 'source_is_system_voice': True, 'personal_ratio': 0.6, 'passive_count': 0}
      - code_with_reflection: got {'source_type': 'external', 'source_is_human_voice': False, 'source_is_system_voice': True, 'personal_ratio': 0.5, 'passive_count': 0}
      - neutral_facts: got {'source_type': 'not_me', 'source_is_human_voice': False, 'source_is_system_voice': True, 'personal_ratio': 0.0, 'passive_count': 0}
      ... and 1 more

================================================================================
RECOMMENDATIONS
================================================================================

Cognitive Stage:
  Recommended: vocab_based
  vocab_based:
    Strengths: stage4_helper, stage4_validation, stage4_theater
    Weaknesses: stage5_real
  regex_based:
    Strengths: stage4_helper, stage4_validation, stage4_theater
    Weaknesses: mixed, stage5_real
  weighted_scoring:
    Strengths: stage4_helper, stage4_validation, stage4_theater
    Weaknesses: mixed, stage5_real

Struggle Filter:
  Recommended: keyword_based
  keyword_based:
    Strengths: drowning_anxiety, swimming_full_arc, swimming_collaborative
    Weaknesses: drowning_frustration, drowning_escalation, drowning_repetition
  arc_detection:
    Strengths: swimming_full_arc, swimming_collaborative, swimming_productive
    Weaknesses: drowning_frustration, drowning_anxiety, drowning_escalation
  emotion_intensity:
    Weaknesses: drowning_frustration, drowning_anxiety, drowning_escalation

Confidence Calibration:
  Recommended: hedge_based
  hedge_based:
    Strengths: low_hedged, low_careful
    Weaknesses: high_confidence, high_absolute, low_uncertainty
  claim_analysis:
    Weaknesses: high_confidence, high_absolute, low_hedged

Source Attribution:
  Recommended: marker_based
  marker_based:
    Strengths: me_personal, me_opinion, not_me_technical
    Weaknesses: me_reflective, hybrid_isomorphic
  pronoun_analysis:
    Strengths: not_me_technical, not_me_code, not_me_docs
    Weaknesses: me_personal, me_reflective, me_opinion