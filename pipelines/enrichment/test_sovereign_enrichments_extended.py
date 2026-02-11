"""Extended Test Suite for Sovereign Enrichments.

This module contains additional edge cases, real-world examples, and stress tests
to validate enrichment robustness across diverse input types.

Run with: python pipelines/enrichment/test_sovereign_enrichments_extended.py
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# =============================================================================
# EXTENDED TEST CATEGORIES
# =============================================================================

@dataclass
class ExtendedTestCase:
    """Extended test case with metadata."""
    id: str
    text: str
    expected_cognitive_stage: int | None
    expected_struggle_pattern: str | None
    expected_confidence_level: str | None
    expected_source_type: str | None
    difficulty: str  # "easy", "medium", "hard", "adversarial"
    category: str
    notes: str = ""


# =============================================================================
# REAL CONVERSATION EXCERPTS
# =============================================================================

REAL_CONVERSATION_TESTS = [
    ExtendedTestCase(
        id="real_001",
        text="Looking at the error stack trace, the issue is in the authentication middleware. The token validation is failing because the JWT secret changed after deployment. Here's the fix.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="medium",
        category="real_debugging",
        notes="Technical diagnosis with confident resolution"
    ),
    ExtendedTestCase(
        id="real_002",
        text="That's a great question! I'd be happy to help you with this. Let me know if you need anything else or if this doesn't quite solve your problem. Feel free to ask follow-up questions!",
        expected_cognitive_stage=4,
        expected_struggle_pattern="neutral",
        expected_confidence_level="medium",
        expected_source_type="not_me",
        difficulty="easy",
        category="real_helper_posture",
        notes="Classic AI assistant helper pattern"
    ),
    ExtendedTestCase(
        id="real_003",
        text="I've been banging my head against this for 3 days now. Every time I think I've fixed it, a new error pops up. The documentation is useless and nobody on Stack Overflow has the same problem. I'm about ready to just rewrite the whole thing.",
        expected_cognitive_stage=4,
        expected_struggle_pattern="drowning",
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="easy",
        category="real_frustration",
        notes="Clear drowning pattern with emotional markers"
    ),
    ExtendedTestCase(
        id="real_004",
        text="So I was stuck on this cache invalidation bug for a while. Turned out the TTL was set in milliseconds not seconds. Once I figured that out, everything started working. Classic off-by-1000 error!",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="high",
        expected_source_type="me",
        difficulty="easy",
        category="real_resolution",
        notes="Clear swimming pattern with resolution arc"
    ),
    ExtendedTestCase(
        id="real_005",
        text="I'm not 100% sure about this, but I think the issue might be related to how we're handling async operations. It could also be a race condition. Would need to add some logging to confirm.",
        expected_cognitive_stage=5,  # Honest uncertainty is Stage 5
        expected_struggle_pattern="swimming",
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="medium",
        category="real_uncertainty",
        notes="Appropriate epistemic humility"
    ),
]


# =============================================================================
# ADVERSARIAL TEST CASES
# =============================================================================

ADVERSARIAL_TESTS = [
    ExtendedTestCase(
        id="adv_001",
        text="I'm happy to help! This is the solution. The data shows clearly. Let me know if you need anything else. Is this what you wanted?",
        expected_cognitive_stage=3,  # Mixed signals
        expected_struggle_pattern="neutral",
        expected_confidence_level="medium",
        expected_source_type="hybrid",
        difficulty="hard",
        category="adversarial_mixed_stage",
        notes="Intentionally combines Stage 4 and Stage 5 markers"
    ),
    ExtendedTestCase(
        id="adv_002",
        text="EVERYTHING IS BROKEN!!! Nothing works!!! I fixed it finally!!! But now something else broke!!! WHY???",
        expected_cognitive_stage=4,
        expected_struggle_pattern="drowning",
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="hard",
        category="adversarial_false_resolution",
        notes="Contains 'fixed' but overall pattern is drowning"
    ),
    ExtendedTestCase(
        id="adv_003",
        text="Oh, how DELIGHTFUL. Another production incident at 3am. The monitoring caught it PERFECTLY - right after everything crashed. Just WONDERFUL engineering.",
        expected_cognitive_stage=4,
        expected_struggle_pattern="drowning",
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="adversarial",
        category="adversarial_sarcasm",
        notes="Sarcastic use of positive words - should be detected as negative"
    ),
    ExtendedTestCase(
        id="adv_004",
        text="```python\ndef solve(x): return x * 2\n``` This is definitely the best solution. It always works perfectly and never fails.",
        expected_cognitive_stage=5,  # Has code + strong claims
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",  # Overconfident
        expected_source_type="hybrid",  # Code + opinion
        difficulty="medium",
        category="adversarial_overconfident_code",
        notes="Code with overconfident claims"
    ),
    ExtendedTestCase(
        id="adv_005",
        text="",
        expected_cognitive_stage=3,
        expected_struggle_pattern="neutral",
        expected_confidence_level="medium",
        expected_source_type="external",
        difficulty="adversarial",
        category="adversarial_empty",
        notes="Empty string should not crash"
    ),
    ExtendedTestCase(
        id="adv_006",
        text="a" * 10000,
        expected_cognitive_stage=3,
        expected_struggle_pattern="neutral",
        expected_confidence_level="medium",
        expected_source_type="external",
        difficulty="adversarial",
        category="adversarial_long",
        notes="Very long repetitive input"
    ),
    ExtendedTestCase(
        id="adv_007",
        text="🔥💀😱 Everything is on fire!!! 🔥🔥🔥 Help!!! 😭😭😭",
        expected_cognitive_stage=4,
        expected_struggle_pattern="drowning",
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="adversarial",
        category="adversarial_emoji",
        notes="Emoji-heavy emotional content"
    ),
]


# =============================================================================
# MULTILINGUAL/ENCODING TESTS
# =============================================================================

ENCODING_TESTS = [
    ExtendedTestCase(
        id="enc_001",
        text="The function returns naïve datetime. The résumé parser handles UTF-8 correctly.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="medium",
        category="encoding_accents",
        notes="Unicode accented characters"
    ),
    ExtendedTestCase(
        id="enc_002",
        text="I think the 日本語 tokenizer is broken. It's not handling kanji correctly.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="medium",
        expected_source_type="me",
        difficulty="medium",
        category="encoding_cjk",
        notes="Mixed English and Japanese"
    ),
    ExtendedTestCase(
        id="enc_003",
        text="The price is €99.99 or ¥12,000. Use the → arrow for navigation.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="easy",
        category="encoding_symbols",
        notes="Currency and special symbols"
    ),
]


# =============================================================================
# CODE-HEAVY TESTS
# =============================================================================

CODE_TESTS = [
    ExtendedTestCase(
        id="code_001",
        text="""```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

This implementation is correct but has O(2^n) time complexity. Consider using memoization.""",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="hybrid",
        difficulty="easy",
        category="code_with_analysis",
        notes="Code block with technical analysis"
    ),
    ExtendedTestCase(
        id="code_002",
        text="""The error message is:
```
TypeError: Cannot read property 'map' of undefined
    at Array.map (<anonymous>)
    at processData (app.js:42)
```

I'm not sure why this is happening. The array should be defined at this point.""",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="low",
        expected_source_type="hybrid",
        difficulty="medium",
        category="code_error_trace",
        notes="Error with honest uncertainty"
    ),
    ExtendedTestCase(
        id="code_003",
        text="""I think the bug is here:
```javascript
for (let i = 0; i <= array.length; i++) {
    console.log(array[i]);
}
```

Should be `i < array.length` not `i <= array.length`.""",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="medium",
        expected_source_type="hybrid",
        difficulty="easy",
        category="code_bug_fix",
        notes="Bug identification with fix"
    ),
]


# =============================================================================
# DOCUMENTATION/FORMAL TEXT TESTS
# =============================================================================

DOCUMENTATION_TESTS = [
    ExtendedTestCase(
        id="doc_001",
        text="The `process_data` function accepts a DataFrame and returns a cleaned version. Required columns: 'id', 'timestamp', 'value'. Raises ValueError if columns are missing.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="easy",
        category="doc_api",
        notes="API documentation style"
    ),
    ExtendedTestCase(
        id="doc_002",
        text="""## Installation

1. Clone the repository
2. Run `pip install -r requirements.txt`
3. Set environment variables
4. Execute `python main.py`

For issues, open a GitHub ticket.""",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="easy",
        category="doc_readme",
        notes="README/installation instructions"
    ),
    ExtendedTestCase(
        id="doc_003",
        text="WARNING: This operation cannot be undone. Proceeding will permanently delete all data. Ensure backups are completed before continuing.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="neutral",
        expected_confidence_level="high",
        expected_source_type="not_me",
        difficulty="easy",
        category="doc_warning",
        notes="System warning message"
    ),
]


# =============================================================================
# CONVERSATION FLOW TESTS
# =============================================================================

CONVERSATION_FLOW_TESTS = [
    ExtendedTestCase(
        id="flow_001",
        text="Thanks for the help! That fixed the issue. I was stuck for hours before asking.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="high",
        expected_source_type="me",
        difficulty="easy",
        category="flow_gratitude",
        notes="Resolution with gratitude"
    ),
    ExtendedTestCase(
        id="flow_002",
        text="That didn't work. Still getting the same error. Any other ideas?",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",  # Still productive, seeking help
        expected_confidence_level="low",
        expected_source_type="me",
        difficulty="medium",
        category="flow_iteration",
        notes="Iterative debugging - not drowning yet"
    ),
    ExtendedTestCase(
        id="flow_003",
        text="Wait, I think I see the problem now. Let me try something...",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="medium",
        expected_source_type="me",
        difficulty="easy",
        category="flow_breakthrough",
        notes="Breakthrough moment"
    ),
    ExtendedTestCase(
        id="flow_004",
        text="Hmm, that's interesting. I hadn't considered that approach. Let me think about it.",
        expected_cognitive_stage=5,
        expected_struggle_pattern="swimming",
        expected_confidence_level="medium",
        expected_source_type="me",
        difficulty="easy",
        category="flow_consideration",
        notes="Thoughtful consideration"
    ),
]


# =============================================================================
# COMBINED ALL TEST CASES
# =============================================================================

ALL_EXTENDED_TESTS = (
    REAL_CONVERSATION_TESTS +
    ADVERSARIAL_TESTS +
    ENCODING_TESTS +
    CODE_TESTS +
    DOCUMENTATION_TESTS +
    CONVERSATION_FLOW_TESTS
)


# =============================================================================
# ENRICHMENT IMPLEMENTATIONS (from main file)
# =============================================================================

class CognitiveStageVocabBased:
    """Original vocabulary-based implementation."""
    
    BANNED = [
        "is this what you wanted", "does this sound okay", "is that correct",
        "would you like me to", "should i proceed", "let me know if",
        "hope this helps", "hope that helps", "does that make sense",
        "is there anything else", "i'm here to assist", "i'm happy to help",
        "how can i help you", "i'd be happy to", "feel free to ask",
        "fascinating", "profound", "remarkable", "impressive",
        "that's really interesting", "great question", "excellent question",
        "wonderful", "absolutely",
    ]
    
    MANIFESTATION = [
        "this is", "here is", "the pattern shows", "based on the data",
        "the analysis reveals", "i see that", "looking at this",
        "i don't know", "i'm not sure", "i cannot determine",
        "unclear from", "would need more information",
        "the evidence suggests", "the data indicates", "according to",
        "based on", "let's", "we can", "the solution is", "the issue is",
    ]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        banned_matches = [v for v in self.BANNED if v in text_lower]
        manifestation_matches = [v for v in self.MANIFESTATION if v in text_lower]
        
        total = len(banned_matches) + len(manifestation_matches)
        if total > 0:
            polarity = (len(manifestation_matches) - len(banned_matches)) / total
        else:
            polarity = 0.0
        
        if polarity > 0.3:
            stage = 5
        elif polarity < -0.3:
            stage = 4
        else:
            stage = 3
        
        return {
            "cognitive_stage": stage,
            "cognitive_stage_polarity": polarity,
            "banned_count": len(banned_matches),
            "manifestation_count": len(manifestation_matches),
        }


class StruggleFilterKeywordBased:
    """Original keyword-based implementation."""
    
    ANXIETY = ["frustrated", "confused", "stuck", "don't understand", "giving up", "impossible", "never works"]
    RESOLUTION = ["got it", "fixed", "solved", "working now", "makes sense", "finally", "figured it out"]
    PROBLEM = ["issue", "problem", "error", "bug", "broken", "not working", "fails"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        anxiety_found = [m for m in self.ANXIETY if m in text_lower]
        resolution_found = any(m in text_lower for m in self.RESOLUTION)
        problem_found = any(m in text_lower for m in self.PROBLEM)
        
        # Check for escalation markers
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamation_count = text.count("!")
        
        drowning_score = len(anxiety_found) * 0.2
        if caps_ratio > 0.3:
            drowning_score += 0.3
        if exclamation_count > 3:
            drowning_score += 0.2
            
        swimming_score = (0.3 if problem_found else 0) + (0.4 if resolution_found else 0)
        
        if swimming_score > 0.5 and drowning_score < 0.3:
            pattern_type = "swimming"
        elif drowning_score > 0.3:
            pattern_type = "drowning"
        else:
            pattern_type = "neutral"
        
        return {
            "struggle_pattern_type": pattern_type,
            "struggle_swimming_score": swimming_score,
            "struggle_drowning_score": drowning_score,
            "has_resolution": resolution_found,
        }


class ConfidenceCalibrationHedgeBased:
    """Hedge phrase counting implementation."""
    
    HEDGES = ["maybe", "possibly", "might", "could be", "perhaps", "i think", "i believe", "probably", "likely"]
    CERTAINTY = ["definitely", "certainly", "always", "never", "must be", "clearly", "obviously"]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        hedge_count = sum(1 for h in self.HEDGES if h in text_lower)
        certainty_count = sum(1 for c in self.CERTAINTY if c in text_lower)
        
        # Check for explicit uncertainty admission
        admits_uncertainty = any(p in text_lower for p in [
            "i don't know", "i'm not sure", "not certain", "not 100%", "would need to"
        ])
        
        if admits_uncertainty:
            level = "low"  # Admitting uncertainty is low confidence but GOOD
            score = 0.3
        elif certainty_count > hedge_count:
            level = "high"
            score = min(1.0, 0.5 + certainty_count * 0.1)
        elif hedge_count > certainty_count:
            level = "low"
            score = max(0.0, 0.5 - hedge_count * 0.1)
        else:
            level = "medium"
            score = 0.5
        
        return {
            "confidence_level": level,
            "confidence_score": score,
            "confidence_hedging_count": hedge_count,
            "confidence_admits_uncertainty": admits_uncertainty,
        }


class SourceAttributionMarkerBased:
    """Marker phrase-based implementation."""
    
    PERSONAL = [
        "i feel", "i think", "i believe", "my experience", "personally", "in my opinion",
        "from my perspective", "i've been", "i was", "i'm", "i had", "for me",
        "i've found", "i've noticed", "i wonder", "i'm curious", "to me",
    ]
    SYSTEM = [
        "the function", "this code", "the implementation", "according to", "technically",
        "the algorithm", "the system", "the process", "the documentation",
        "the error", "the output", "the result", "the method", "returns",
    ]
    
    def compute(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        
        personal_count = sum(1 for m in self.PERSONAL if m in text_lower)
        system_count = sum(1 for m in self.SYSTEM if m in text_lower)
        has_code = "```" in text
        
        if personal_count > system_count:
            if has_code:
                source_type = "hybrid"
            else:
                source_type = "me"
        elif system_count > personal_count:
            source_type = "not_me"
        elif personal_count > 0 and system_count > 0:
            source_type = "hybrid"
        else:
            source_type = "external"
        
        return {
            "source_type": source_type,
            "source_is_human_voice": personal_count > 0,
            "source_is_system_voice": system_count > personal_count,
            "source_is_isomorphic": has_code and personal_count > 0,
        }


# =============================================================================
# TEST RUNNER
# =============================================================================

@dataclass
class ExtendedTestResult:
    """Result from an extended test."""
    test: ExtendedTestCase
    cognitive_result: dict
    struggle_result: dict
    confidence_result: dict
    source_result: dict
    cognitive_pass: bool
    struggle_pass: bool
    confidence_pass: bool
    source_pass: bool
    execution_time_ms: float


def run_extended_tests() -> list[ExtendedTestResult]:
    """Run all extended tests."""
    
    cognitive = CognitiveStageVocabBased()
    struggle = StruggleFilterKeywordBased()
    confidence = ConfidenceCalibrationHedgeBased()
    source = SourceAttributionMarkerBased()
    
    results = []
    
    for test in ALL_EXTENDED_TESTS:
        start = time.time()
        
        try:
            cog_result = cognitive.compute(test.text)
            str_result = struggle.compute(test.text)
            conf_result = confidence.compute(test.text)
            src_result = source.compute(test.text)
        except Exception as e:
            print(f"ERROR on {test.id}: {e}")
            continue
        
        elapsed = (time.time() - start) * 1000
        
        # Check passes
        cog_pass = (
            test.expected_cognitive_stage is None or
            cog_result["cognitive_stage"] == test.expected_cognitive_stage
        )
        str_pass = (
            test.expected_struggle_pattern is None or
            str_result["struggle_pattern_type"] == test.expected_struggle_pattern
        )
        conf_pass = (
            test.expected_confidence_level is None or
            conf_result["confidence_level"] == test.expected_confidence_level
        )
        src_pass = (
            test.expected_source_type is None or
            src_result["source_type"] == test.expected_source_type
        )
        
        results.append(ExtendedTestResult(
            test=test,
            cognitive_result=cog_result,
            struggle_result=str_result,
            confidence_result=conf_result,
            source_result=src_result,
            cognitive_pass=cog_pass,
            struggle_pass=str_pass,
            confidence_pass=conf_pass,
            source_pass=src_pass,
            execution_time_ms=elapsed,
        ))
    
    return results


def generate_extended_report(results: list[ExtendedTestResult]) -> str:
    """Generate extended test report."""
    lines = [
        "=" * 80,
        "EXTENDED SOVEREIGN ENRICHMENT TEST REPORT",
        "=" * 80,
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Tests: {len(results)}",
        "",
    ]
    
    # Overall summary
    cog_pass = sum(1 for r in results if r.cognitive_pass)
    str_pass = sum(1 for r in results if r.struggle_pass)
    conf_pass = sum(1 for r in results if r.confidence_pass)
    src_pass = sum(1 for r in results if r.source_pass)
    
    lines.extend([
        "OVERALL PASS RATES:",
        f"  Cognitive Stage:      {cog_pass}/{len(results)} ({cog_pass/len(results)*100:.1f}%)",
        f"  Struggle Filter:      {str_pass}/{len(results)} ({str_pass/len(results)*100:.1f}%)",
        f"  Confidence Calibration: {conf_pass}/{len(results)} ({conf_pass/len(results)*100:.1f}%)",
        f"  Source Attribution:   {src_pass}/{len(results)} ({src_pass/len(results)*100:.1f}%)",
        "",
    ])
    
    # By difficulty
    difficulties = ["easy", "medium", "hard", "adversarial"]
    for diff in difficulties:
        diff_results = [r for r in results if r.test.difficulty == diff]
        if diff_results:
            lines.append(f"\n{diff.upper()} TESTS ({len(diff_results)} cases):")
            for enrichment, attr in [
                ("Cognitive", "cognitive_pass"),
                ("Struggle", "struggle_pass"),
                ("Confidence", "confidence_pass"),
                ("Source", "source_pass"),
            ]:
                passed = sum(1 for r in diff_results if getattr(r, attr))
                lines.append(f"  {enrichment}: {passed}/{len(diff_results)} ({passed/len(diff_results)*100:.1f}%)")
    
    # By category
    lines.extend(["\n" + "-" * 80, "RESULTS BY CATEGORY", "-" * 80])
    categories = sorted(set(r.test.category for r in results))
    
    for cat in categories:
        cat_results = [r for r in results if r.test.category == cat]
        lines.append(f"\n{cat} ({len(cat_results)} tests):")
        
        for r in cat_results:
            status = []
            if not r.cognitive_pass:
                status.append(f"cog={r.cognitive_result['cognitive_stage']}≠{r.test.expected_cognitive_stage}")
            if not r.struggle_pass:
                status.append(f"str={r.struggle_result['struggle_pattern_type']}≠{r.test.expected_struggle_pattern}")
            if not r.confidence_pass:
                status.append(f"conf={r.confidence_result['confidence_level']}≠{r.test.expected_confidence_level}")
            if not r.source_pass:
                status.append(f"src={r.source_result['source_type']}≠{r.test.expected_source_type}")
            
            if status:
                lines.append(f"  ❌ {r.test.id}: {', '.join(status)}")
            else:
                lines.append(f"  ✅ {r.test.id}")
    
    # Failures detail
    failures = [r for r in results if not (r.cognitive_pass and r.struggle_pass and r.confidence_pass and r.source_pass)]
    
    if failures:
        lines.extend(["\n" + "-" * 80, "FAILURE ANALYSIS", "-" * 80])
        
        for r in failures[:20]:  # Show first 20 failures
            lines.extend([
                f"\n{r.test.id} [{r.test.difficulty}]:",
                f"  Text (truncated): {r.test.text[:100]}...",
                f"  Notes: {r.test.notes}",
            ])
            
            if not r.cognitive_pass:
                lines.append(f"  Cognitive: expected={r.test.expected_cognitive_stage}, got={r.cognitive_result['cognitive_stage']} (polarity={r.cognitive_result['cognitive_stage_polarity']:.2f})")
            if not r.struggle_pass:
                lines.append(f"  Struggle: expected={r.test.expected_struggle_pattern}, got={r.struggle_result['struggle_pattern_type']} (swim={r.struggle_result['struggle_swimming_score']:.2f}, drown={r.struggle_result['struggle_drowning_score']:.2f})")
            if not r.confidence_pass:
                lines.append(f"  Confidence: expected={r.test.expected_confidence_level}, got={r.confidence_result['confidence_level']} (score={r.confidence_result['confidence_score']:.2f})")
            if not r.source_pass:
                lines.append(f"  Source: expected={r.test.expected_source_type}, got={r.source_result['source_type']}")
    
    # Performance
    lines.extend(["\n" + "-" * 80, "PERFORMANCE METRICS", "-" * 80])
    times = [r.execution_time_ms for r in results]
    lines.extend([
        f"  Mean execution time: {statistics.mean(times):.3f}ms",
        f"  Median execution time: {statistics.median(times):.3f}ms",
        f"  Max execution time: {max(times):.3f}ms",
        f"  Min execution time: {min(times):.3f}ms",
    ])
    
    # Recommendations
    lines.extend(["\n" + "=" * 80, "RECOMMENDATIONS", "=" * 80])
    
    if cog_pass/len(results) >= 0.8:
        lines.append("✅ Cognitive Stage: PRODUCTION READY")
    else:
        lines.append("⚠️ Cognitive Stage: Needs improvement on real conversation patterns")
    
    if str_pass/len(results) >= 0.8:
        lines.append("✅ Struggle Filter: PRODUCTION READY")
    else:
        lines.append("⚠️ Struggle Filter: Needs escalation and sarcasm detection")
    
    if conf_pass/len(results) >= 0.8:
        lines.append("✅ Confidence Calibration: PRODUCTION READY")
    else:
        lines.append("⚠️ Confidence Calibration: Needs better uncertainty handling")
    
    if src_pass/len(results) >= 0.8:
        lines.append("✅ Source Attribution: PRODUCTION READY")
    else:
        lines.append("⚠️ Source Attribution: Needs expanded personal markers")
    
    return "\n".join(lines)


def main():
    """Run extended tests and generate report."""
    print("Running extended test suite...")
    results = run_extended_tests()
    
    report = generate_extended_report(results)
    print("\n" + report)
    
    # Save report
    report_path = Path(__file__).parent / "EXTENDED_TEST_REPORT.md"
    report_path.write_text(report)
    print(f"\nReport saved to: {report_path}")
    
    # Return summary for CI
    total_pass = sum(1 for r in results if r.cognitive_pass and r.struggle_pass and r.confidence_pass and r.source_pass)
    print(f"\n{'=' * 40}")
    print(f"OVERALL: {total_pass}/{len(results)} tests fully passed ({total_pass/len(results)*100:.1f}%)")
    
    return results


if __name__ == "__main__":
    main()
