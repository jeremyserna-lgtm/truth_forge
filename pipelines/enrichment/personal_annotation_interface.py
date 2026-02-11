"""Personal Annotation Interface for Genesis Model Training.

This is YOUR tool for intimate involvement in training. Not automated pipelines -
your judgment, your time, your standards.

Run with: python pipelines/enrichment/personal_annotation_interface.py

Daily practice:
- 30-60 minutes
- 10 preference rankings
- 5-10 direct annotations
- Build the model that carries your fingerprint
"""

from __future__ import annotations

import json
import os
import readline  # For input history
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Literal


# =============================================================================
# CONFIGURATION
# =============================================================================

ANNOTATOR_NAME = "jeremy"  # Your name - every annotation is signed
DATA_DIR = Path("data/personal_annotations")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CognitiveStageAnnotation:
    """Your judgment on cognitive stage."""
    text: str
    stage: Literal[3, 4, 5]
    confidence: float  # 0-1
    evidence: list[str]  # Specific phrases that led to your judgment
    notes: str
    
    # Metadata
    annotator: str = ANNOTATOR_NAME
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""


@dataclass
class StruggleAnnotation:
    """Your judgment on struggle pattern."""
    text: str
    pattern: Literal["swimming", "drowning", "neutral"]
    confidence: float
    has_arc: bool  # Does it have narrative structure?
    training_value: Literal["high", "medium", "low"]
    notes: str
    
    annotator: str = ANNOTATOR_NAME
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SourceAnnotation:
    """Your judgment on voice/source."""
    text: str
    source_type: Literal["me", "not_me", "hybrid", "external"]
    voice_match: float  # How much does this sound like authentic human voice?
    is_reflective: bool
    notes: str
    
    annotator: str = ANNOTATOR_NAME
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PreferenceAnnotation:
    """Your preference between responses."""
    prompt: str
    response_a: str
    response_b: str
    preferred: Literal["A", "B", "tie"]
    margin: Literal["strong", "slight", "tie"]
    
    # What made it better?
    truthfulness_winner: Literal["A", "B", "tie"]
    helpfulness_winner: Literal["A", "B", "tie"]
    voice_winner: Literal["A", "B", "tie"]
    
    reason: str
    
    annotator: str = ANNOTATOR_NAME
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConversationalFeedback:
    """Real-time feedback during conversation."""
    user_input: str
    model_response: str
    feedback_type: Literal["approve", "reject", "redirect", "explain"]
    details: str
    corrected_response: str | None = None  # What SHOULD it have said?
    
    annotator: str = ANNOTATOR_NAME
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# STORAGE
# =============================================================================

def save_annotation(annotation: Any, annotation_type: str) -> None:
    """Save annotation to JSONL file."""
    filepath = DATA_DIR / f"{annotation_type}_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    with open(filepath, "a") as f:
        f.write(json.dumps(asdict(annotation)) + "\n")
    
    print(f"✓ Saved to {filepath}")


def load_unannotated_texts(source: str = "sample") -> list[str]:
    """Load texts that need annotation."""
    # In production, would pull from BigQuery
    # For now, sample texts that exercise different patterns
    
    return [
        # Stage 4 candidates
        "I'm happy to help! Is there anything else you'd like me to assist with?",
        "That's a fascinating question! What a remarkable insight you've had!",
        "Of course! I'd be delighted to help you with that. Let me know if this isn't what you were looking for.",
        
        # Stage 5 candidates
        "The error is on line 42. The null check is missing before the array access.",
        "I don't know the answer to that specific question. I'd need to see the error logs.",
        "Based on the stack trace, the issue is in the authentication middleware.",
        
        # Struggle candidates
        "WHY WON'T THIS WORK!!! I've tried everything and nothing helps!!!",
        "Had an issue with the connection timing out. Fixed it by increasing the pool size.",
        "Finally figured it out! The problem was the encoding - UTF-8 vs ASCII.",
        
        # Ambiguous / interesting
        "This is the solution, but I hope it helps! Let me know if you need anything else.",
        "Oh wonderful, another cryptic error message. How delightful.",
        "I think this might work, but I'm not entirely sure about the edge cases.",
    ]


# =============================================================================
# ANNOTATION INTERFACES
# =============================================================================

def cognitive_stage_session():
    """Interactive session for cognitive stage annotation."""
    print("\n" + "=" * 70)
    print("COGNITIVE STAGE ANNOTATION SESSION")
    print("=" * 70)
    print("""
Stage 4 (Validation-Seeking):
  - "I'm happy to help", seeking approval
  - Performative enthusiasm, helper posture
  - Self-worth tied to external validation

Stage 5 (Sovereign):
  - Direct statements, honest uncertainty
  - Evidence-based, internally validated
  - "I don't know" is sovereign

Stage 3 (Neutral):
  - Technical description without posture
  - Neither seeking nor asserting
""")
    
    texts = load_unannotated_texts()
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, text in enumerate(texts):
        print(f"\n{'─' * 70}")
        print(f"[{i+1}/{len(texts)}]")
        print(f"{'─' * 70}")
        print(f"\nText:\n{text}")
        print(f"\n{'─' * 70}")
        
        # Get stage
        while True:
            stage_input = input("\nStage (3/4/5, or 's' to skip): ").strip()
            if stage_input == 's':
                break
            if stage_input in ['3', '4', '5']:
                stage = int(stage_input)
                break
            print("Invalid input. Enter 3, 4, or 5.")
        
        if stage_input == 's':
            continue
        
        # Get confidence
        while True:
            try:
                confidence = float(input("Confidence (0.0-1.0): "))
                if 0 <= confidence <= 1:
                    break
            except ValueError:
                pass
            print("Invalid input. Enter a number between 0 and 1.")
        
        # Get evidence
        evidence_input = input("Key evidence phrases (comma-separated): ")
        evidence = [e.strip() for e in evidence_input.split(",") if e.strip()]
        
        # Get notes
        notes = input("Notes (why this classification?): ")
        
        # Save
        annotation = CognitiveStageAnnotation(
            text=text,
            stage=stage,
            confidence=confidence,
            evidence=evidence,
            notes=notes,
            session_id=session_id,
        )
        save_annotation(annotation, "cognitive_stage")
        
        # Continue?
        if input("\nContinue? (y/n): ").lower() != 'y':
            break
    
    print("\n✅ Session complete!")


def struggle_pattern_session():
    """Interactive session for struggle pattern annotation."""
    print("\n" + "=" * 70)
    print("STRUGGLE PATTERN ANNOTATION SESSION")
    print("=" * 70)
    print("""
Swimming (Productive Struggle):
  - Problem → Investigation → Resolution
  - Learning moments, breakthroughs
  - HIGH training value

Drowning (Unproductive Struggle):
  - Frustration loops, escalation
  - No progress, hopelessness
  - LOW training value

Neutral:
  - Questions, explanations
  - No struggle pattern
""")
    
    texts = load_unannotated_texts()
    
    for i, text in enumerate(texts):
        print(f"\n{'─' * 70}")
        print(f"[{i+1}/{len(texts)}]")
        print(f"{'─' * 70}")
        print(f"\nText:\n{text}")
        print(f"\n{'─' * 70}")
        
        # Get pattern
        pattern_input = input("\nPattern (swim/drown/neutral, 's' to skip): ").strip().lower()
        if pattern_input == 's':
            continue
        
        pattern_map = {'swim': 'swimming', 'drown': 'drowning', 'neutral': 'neutral'}
        pattern = pattern_map.get(pattern_input, 'neutral')
        
        # Get confidence
        confidence = float(input("Confidence (0.0-1.0): ") or "0.8")
        
        # Has arc?
        has_arc = input("Has narrative arc? (y/n): ").lower() == 'y'
        
        # Training value
        value_input = input("Training value (high/med/low): ").strip().lower()
        value_map = {'high': 'high', 'med': 'medium', 'low': 'low', 'h': 'high', 'm': 'medium', 'l': 'low'}
        training_value = value_map.get(value_input, 'medium')
        
        # Notes
        notes = input("Notes: ")
        
        # Save
        annotation = StruggleAnnotation(
            text=text,
            pattern=pattern,
            confidence=confidence,
            has_arc=has_arc,
            training_value=training_value,
            notes=notes,
        )
        save_annotation(annotation, "struggle_pattern")
        
        if input("\nContinue? (y/n): ").lower() != 'y':
            break
    
    print("\n✅ Session complete!")


def preference_ranking_session():
    """Interactive session for preference ranking."""
    print("\n" + "=" * 70)
    print("PREFERENCE RANKING SESSION")
    print("=" * 70)
    print("""
You'll see two responses to the same prompt.
Choose which is better and why.
""")
    
    # Sample comparison pairs
    comparisons = [
        {
            "prompt": "Explain why this code is failing.",
            "response_a": "I'd be happy to help! The code might have an issue. Let me know if you need anything else! 😊",
            "response_b": "The null pointer exception is on line 42. The array isn't initialized before the loop. Here's the fix: `arr = []` before line 40.",
        },
        {
            "prompt": "What's the best way to learn programming?",
            "response_a": "That's a great question! There are many wonderful ways to learn programming. It depends on your learning style.",
            "response_b": "Build things. Start with a project you care about, Google errors as they come up, read documentation when stuck. Books and courses help but aren't necessary.",
        },
        {
            "prompt": "Is Python or JavaScript better?",
            "response_a": "Both are excellent choices! Python is great for some things and JavaScript for others. It really depends on your needs!",
            "response_b": "Depends on what you're building. Python: data science, scripting, backend. JavaScript: web frontend, Node backend. Neither is 'better' in absolute terms.",
        },
    ]
    
    for i, comp in enumerate(comparisons):
        print(f"\n{'─' * 70}")
        print(f"[{i+1}/{len(comparisons)}]")
        print(f"{'─' * 70}")
        print(f"\nPrompt: {comp['prompt']}")
        print(f"\n[A] {comp['response_a']}")
        print(f"\n[B] {comp['response_b']}")
        print(f"\n{'─' * 70}")
        
        # Overall preference
        pref = input("\nPreferred (A/B/tie): ").strip().upper()
        if pref not in ['A', 'B', 'TIE']:
            pref = 'tie'
        
        # Margin
        margin = input("Margin (strong/slight/tie): ").strip().lower()
        if margin not in ['strong', 'slight', 'tie']:
            margin = 'slight'
        
        # Dimensions
        truth = input("More truthful (A/B/tie): ").strip().upper() or "tie"
        helpful = input("More helpful (A/B/tie): ").strip().upper() or "tie"
        voice = input("Better voice (A/B/tie): ").strip().upper() or "tie"
        
        # Reason
        reason = input("Why is your choice better? ")
        
        # Save
        annotation = PreferenceAnnotation(
            prompt=comp['prompt'],
            response_a=comp['response_a'],
            response_b=comp['response_b'],
            preferred=pref,
            margin=margin,
            truthfulness_winner=truth,
            helpfulness_winner=helpful,
            voice_winner=voice,
            reason=reason,
        )
        save_annotation(annotation, "preference")
        
        if input("\nContinue? (y/n): ").lower() != 'y':
            break
    
    print("\n✅ Session complete!")


def conversational_feedback_session():
    """Interactive conversation with real-time feedback."""
    print("\n" + "=" * 70)
    print("CONVERSATIONAL FEEDBACK SESSION")
    print("=" * 70)
    print("""
Have a conversation with simulated model responses.
Give feedback on each response:
  - approve: This is exactly right
  - reject: Never do this
  - redirect: Close but adjust [something]
  - explain: Here's why this matters

Type /quit to end session.
""")
    
    # Simulated model responses for demo
    # In production, would use actual model
    simulated_responses = {
        "default": "I'd be happy to help with that! Let me know if you need anything else.",
        "code": "The issue is in your loop condition. You're using <= when it should be <.",
        "uncertain": "I'm not entirely sure about that. Would need to see the documentation.",
    }
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == '/quit':
            break
        
        # Simulate response (would be actual model in production)
        if 'code' in user_input.lower() or 'error' in user_input.lower():
            response = simulated_responses['code']
        elif '?' in user_input:
            response = simulated_responses['uncertain']
        else:
            response = simulated_responses['default']
        
        print(f"\nModel: {response}")
        
        # Get feedback
        feedback_input = input("\nFeedback (approve/reject/redirect/explain, or skip): ").strip().lower()
        
        if feedback_input == 'skip':
            continue
        
        if feedback_input not in ['approve', 'reject', 'redirect', 'explain']:
            feedback_input = 'approve'
        
        details = input("Details: ")
        
        corrected = None
        if feedback_input in ['reject', 'redirect']:
            corrected = input("What SHOULD it have said? (or skip): ")
            if corrected.lower() == 'skip':
                corrected = None
        
        # Save
        annotation = ConversationalFeedback(
            user_input=user_input,
            model_response=response,
            feedback_type=feedback_input,
            details=details,
            corrected_response=corrected,
        )
        save_annotation(annotation, "conversational")
    
    print("\n✅ Session complete!")


# =============================================================================
# PROGRESS TRACKING
# =============================================================================

def show_progress():
    """Show annotation progress."""
    print("\n" + "=" * 70)
    print("YOUR ANNOTATION PROGRESS")
    print("=" * 70)
    
    totals = {
        "cognitive_stage": 0,
        "struggle_pattern": 0,
        "preference": 0,
        "conversational": 0,
    }
    
    for filepath in DATA_DIR.glob("*.jsonl"):
        for prefix in totals:
            if filepath.name.startswith(prefix):
                with open(filepath) as f:
                    totals[prefix] += sum(1 for _ in f)
    
    print(f"""
Cognitive Stage Annotations: {totals['cognitive_stage']}
  Target: 500 | Progress: {'█' * min(50, totals['cognitive_stage'] // 10)}{'░' * max(0, 50 - totals['cognitive_stage'] // 10)}

Struggle Pattern Annotations: {totals['struggle_pattern']}
  Target: 500 | Progress: {'█' * min(50, totals['struggle_pattern'] // 10)}{'░' * max(0, 50 - totals['struggle_pattern'] // 10)}

Preference Rankings: {totals['preference']}
  Target: 2000 | Progress: {'█' * min(50, totals['preference'] // 40)}{'░' * max(0, 50 - totals['preference'] // 40)}

Conversational Feedback: {totals['conversational']}
  Target: 500 | Progress: {'█' * min(50, totals['conversational'] // 10)}{'░' * max(0, 50 - totals['conversational'] // 10)}

Total Annotations: {sum(totals.values())}
""")


# =============================================================================
# MAIN MENU
# =============================================================================

def main():
    """Main menu for annotation interface."""
    while True:
        print("\n" + "=" * 70)
        print("GENESIS MODEL PERSONAL ANNOTATION INTERFACE")
        print("=" * 70)
        print(f"Annotator: {ANNOTATOR_NAME}")
        print(f"Data directory: {DATA_DIR}")
        print("""
Choose a session:
  1. Cognitive Stage Annotation
  2. Struggle Pattern Annotation
  3. Preference Ranking
  4. Conversational Feedback
  5. View Progress
  q. Quit
""")
        
        choice = input("Selection: ").strip().lower()
        
        if choice == '1':
            cognitive_stage_session()
        elif choice == '2':
            struggle_pattern_session()
        elif choice == '3':
            preference_ranking_session()
        elif choice == '4':
            conversational_feedback_session()
        elif choice == '5':
            show_progress()
        elif choice == 'q':
            print("\n👋 Goodbye! Your annotations are building something real.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
