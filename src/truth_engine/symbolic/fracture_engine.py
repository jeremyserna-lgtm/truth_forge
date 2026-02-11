"""
Neuro-Symbolic Rule Engine (Fracture Protocol)
Truth Engine / Truth Forge

Implements the symbolic reasoning layer for the Fracture Protocol.
Works in tandem with neural components for hybrid NeSy verification.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import yaml


class RuleAction(Enum):
    """Actions taken when a rule is triggered."""

    HALT = "HALT"  # Stop all processing, trigger Fracture
    FLAG = "FLAG"  # Mark output with warning
    LOG = "LOG"  # Record but continue
    REVIEW = "REVIEW"  # Queue for human review
    REJECT = "REJECT"  # Reject the input/output


@dataclass
class RuleResult:
    """Result of evaluating a single rule."""

    rule_id: str
    rule_name: str
    triggered: bool
    action: RuleAction
    explanation: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 1.0  # Symbolic rules are typically high confidence


@dataclass
class SymbolicRule:
    """
    A symbolic rule in the Fracture Protocol.

    Rules can use pattern matching, logical conditions,
    or custom Python functions for evaluation.
    """

    id: str
    name: str
    category: str
    description: str
    action: RuleAction

    # Evaluation methods (at least one required)
    patterns: list[str] = field(default_factory=list)  # Regex patterns
    anti_patterns: list[str] = field(default_factory=list)  # Patterns that should NOT match
    logical_condition: str = ""  # Python expression
    custom_function: Callable | None = None  # Custom evaluator

    # Metadata
    priority: int = 0  # Higher = checked first
    enabled: bool = True
    requires_context: bool = False

    def evaluate(self, content: str, context: dict = None) -> RuleResult:
        """
        Evaluate the rule against content.

        Args:
            content: The text to evaluate
            context: Optional additional context

        Returns:
            RuleResult indicating if rule was triggered
        """
        triggered = False
        evidence = []
        explanation = ""

        # Check patterns (any match = triggered)
        for pattern in self.patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                triggered = True
                evidence.extend(matches[:3])  # Limit evidence
                explanation = f"Pattern match: {pattern}"

        # Check anti-patterns (any match = NOT triggered, overrides patterns)
        for pattern in self.anti_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                triggered = False
                evidence = []
                explanation = "Anti-pattern matched, rule not triggered"
                break

        # Check logical condition
        if self.logical_condition and not triggered:
            try:
                # Safe eval with limited context
                safe_context = {
                    "content": content,
                    "len": len,
                    "any": any,
                    "all": all,
                    "context": context or {},
                }
                result = eval(self.logical_condition, {"__builtins__": {}}, safe_context)
                if result:
                    triggered = True
                    explanation = f"Logical condition satisfied: {self.logical_condition}"
            except Exception as e:
                explanation = f"Logical condition error: {e}"

        # Run custom function
        if self.custom_function and not triggered:
            try:
                result = self.custom_function(content, context)
                if result:
                    triggered = True
                    if isinstance(result, dict):
                        evidence = result.get("evidence", [])
                        explanation = result.get("explanation", "Custom function triggered")
                    else:
                        explanation = "Custom function triggered"
            except Exception as e:
                explanation = f"Custom function error: {e}"

        return RuleResult(
            rule_id=self.id,
            rule_name=self.name,
            triggered=triggered,
            action=self.action,
            explanation=explanation,
            evidence=evidence,
        )


class FractureEngine:
    """
    The core Neuro-Symbolic rule engine for coherence verification.

    Implements the Fracture Protocol: halt on incoherence,
    treat failure as inspectable data.
    """

    def __init__(self, rules_path: str = None):
        """
        Initialize the engine.

        Args:
            rules_path: Optional path to YAML rules file
        """
        self.rules: list[SymbolicRule] = []
        self._rule_index: dict[str, SymbolicRule] = {}

        # Load default rules
        self._load_default_rules()

        # Load custom rules if path provided
        if rules_path:
            self.load_rules(rules_path)

    def _load_default_rules(self):
        """Load the core Fracture Protocol rules."""

        # FRACTURE-001: Self-Contradiction Detection
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-001",
                name="Self-Contradiction Detection",
                category="coherence",
                description="Detect claims that contradict themselves within the same response",
                action=RuleAction.HALT,
                priority=100,
                custom_function=self._check_self_contradiction,
            )
        )

        # FRACTURE-002: Circular Reference Detection
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-002",
                name="Circular Reference Detection",
                category="coherence",
                description="Detect when a claim cites itself as evidence",
                action=RuleAction.FLAG,
                priority=90,
                patterns=[
                    r"because .* (as mentioned|as stated|as I said) (above|earlier|previously)",
                    r"this is true because .* (shows|proves|demonstrates) it",
                ],
            )
        )

        # FRACTURE-003: Confidence Without Evidence
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-003",
                name="Confidence Without Evidence",
                category="verification",
                description="Detect definitive claims without supporting evidence",
                action=RuleAction.FLAG,
                priority=80,
                patterns=[
                    r"\b(definitely|certainly|absolutely|undoubtedly)\b(?!.*(?:source|evidence|according to|based on))",
                    r"\b(always|never|everyone|no one)\b.*\.",
                ],
                anti_patterns=[r"(according to|research shows|studies indicate|evidence suggests)"],
            )
        )

        # FRACTURE-004: Sycophantic Patterns
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-004",
                name="Sycophantic Pattern Detection",
                category="resistance",
                description="Detect validation-seeking or flattering language",
                action=RuleAction.LOG,
                priority=50,
                patterns=[
                    r"(great question|excellent point|you're (absolutely )?right)",
                    r"(let me know if|is this helpful|does this make sense)\?",
                    r"I('d| would) be happy to",
                ],
            )
        )

        # FRACTURE-005: Hallucination Indicators
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-005",
                name="Hallucination Indicators",
                category="verification",
                description="Detect common patterns associated with hallucinated content",
                action=RuleAction.REVIEW,
                priority=85,
                patterns=[
                    r"in (?:19|20)\d{2},? (?:a study|researchers|scientists)(?! (?:at|from|published))",
                    r"according to (?:a|the) (?:recent|new|major) study(?! (?:published|in|by))",
                ],
            )
        )

        # FRACTURE-006: Missing Uncertainty Markers
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-006",
                name="Missing Uncertainty Markers",
                category="fidelity",
                description="Flag responses that make many claims without uncertainty",
                action=RuleAction.LOG,
                priority=40,
                custom_function=self._check_uncertainty_markers,
            )
        )

        # FRACTURE-007: Logical Contradiction Patterns
        self.add_rule(
            SymbolicRule(
                id="FRACTURE-007",
                name="Logical Contradiction Patterns",
                category="coherence",
                description="Detect explicit logical contradictions",
                action=RuleAction.HALT,
                priority=95,
                patterns=[
                    r"is (both|simultaneously) .*? and (not|the opposite)",
                    r"(however|but),? (this|it|that) (also|simultaneously) (isn't|is not|cannot be)",
                    r"X is Y.* X is (not|never) Y",
                ],
            )
        )

    def _check_self_contradiction(self, content: str, context: dict = None) -> dict | None:
        """
        Check for self-contradictions using semantic analysis.

        This is a simplified version. Full implementation would use
        embeddings to detect semantic contradictions.
        """
        # Simple heuristic: look for negation patterns
        sentences = content.split(".")

        for i, s1 in enumerate(sentences):
            for s2 in sentences[i + 1 :]:
                # Check for explicit negation of same subject
                s1_clean = s1.lower().strip()
                s2_clean = s2.lower().strip()

                # Pattern: "X is Y" followed by "X is not Y"
                match1 = re.search(r"(\w+)\s+is\s+(\w+)", s1_clean)
                match2 = re.search(r"(\w+)\s+is\s+not\s+(\w+)", s2_clean)

                if match1 and match2:
                    if match1.group(1) == match2.group(1) and match1.group(2) == match2.group(2):
                        return {
                            "evidence": [s1.strip(), s2.strip()],
                            "explanation": f"Contradiction: '{match1.group(1)}' is claimed to be both '{match1.group(2)}' and not '{match1.group(2)}'",
                        }

        return None

    def _check_uncertainty_markers(self, content: str, context: dict = None) -> dict | None:
        """
        Check if content has appropriate uncertainty markers.

        Long content should include some acknowledgment of uncertainty/limitations.
        """
        if len(content) < 500:
            return None  # Short responses don't need uncertainty

        uncertainty_patterns = [
            r"\b(may|might|could|possibly|perhaps|likely|probably)\b",
            r"\b(i think|i believe|it seems|it appears|uncertain|unclear)\b",
            r"\b(limitation|caveat|note that|however)\b",
            r"\b(approximately|around|roughly|about)\b",
            r"\?",  # Questions indicate awareness of uncertainty
        ]

        # Count sentences
        sentences = [s for s in content.split(".") if len(s.strip()) > 10]

        # Count uncertainty markers
        uncertainty_count = 0
        for pattern in uncertainty_patterns:
            uncertainty_count += len(re.findall(pattern, content, re.IGNORECASE))

        # Ratio check: at least 1 uncertainty marker per 5 sentences
        if len(sentences) > 5 and uncertainty_count < len(sentences) / 5:
            return {
                "evidence": [
                    f"{len(sentences)} sentences, only {uncertainty_count} uncertainty markers"
                ],
                "explanation": "Content makes many claims without acknowledging uncertainty",
            }

        return None

    def add_rule(self, rule: SymbolicRule):
        """Add a rule to the engine."""
        self.rules.append(rule)
        self._rule_index[rule.id] = rule
        # Sort by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def load_rules(self, path: str):
        """Load rules from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        for rule_data in data.get("rules", []):
            rule = SymbolicRule(
                id=rule_data["id"],
                name=rule_data["name"],
                category=rule_data.get("category", "custom"),
                description=rule_data.get("description", ""),
                action=RuleAction[rule_data.get("action", "LOG").upper()],
                patterns=rule_data.get("patterns", []),
                anti_patterns=rule_data.get("anti_patterns", []),
                logical_condition=rule_data.get("logical_condition", ""),
                priority=rule_data.get("priority", 0),
                enabled=rule_data.get("enabled", True),
            )
            self.add_rule(rule)

    def get_rule(self, rule_id: str) -> SymbolicRule | None:
        """Get a rule by ID."""
        return self._rule_index.get(rule_id)

    def evaluate(
        self, content: str, context: dict = None, categories: list[str] = None
    ) -> dict[str, Any]:
        """
        Evaluate content against all rules.

        Args:
            content: The text to evaluate
            context: Optional additional context
            categories: Optional filter by category

        Returns:
            Dict with status, triggered rules, and reasoning trace
        """
        results = []
        halt_triggered = False
        halt_reason = ""

        for rule in self.rules:
            if not rule.enabled:
                continue

            if categories and rule.category not in categories:
                continue

            result = rule.evaluate(content, context)
            results.append(result)

            if result.triggered and result.action == RuleAction.HALT:
                halt_triggered = True
                halt_reason = f"[{rule.id}] {rule.name}: {result.explanation}"
                # Don't break - evaluate all rules for complete trace

        # Build response
        triggered_rules = [r for r in results if r.triggered]

        status = "COHERENT"
        if halt_triggered:
            status = "FRACTURE"
        elif any(r.action in [RuleAction.FLAG, RuleAction.REVIEW] for r in triggered_rules):
            status = "FLAGGED"

        # Build reasoning trace
        trace = self._build_reasoning_trace(results)

        return {
            "status": status,
            "halt": halt_triggered,
            "halt_reason": halt_reason,
            "triggered_rules": [
                {
                    "id": r.rule_id,
                    "name": r.rule_name,
                    "action": r.action.value,
                    "explanation": r.explanation,
                    "evidence": r.evidence,
                }
                for r in triggered_rules
            ],
            "all_results": results,
            "reasoning_trace": trace,
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    def _build_reasoning_trace(self, results: list[RuleResult]) -> str:
        """Build human-readable reasoning trace."""
        lines = ["SYMBOLIC REASONING TRACE:"]
        lines.append("=" * 50)

        for result in results:
            status = "TRIGGERED" if result.triggered else "PASSED"
            marker = "⚠️" if result.triggered else "✓"

            lines.append(f"{marker} [{result.rule_id}] {result.rule_name}: {status}")

            if result.triggered:
                lines.append(f"   Action: {result.action.value}")
                lines.append(f"   Reason: {result.explanation}")
                if result.evidence:
                    lines.append(f"   Evidence: {result.evidence[:2]}")

        lines.append("=" * 50)
        return "\n".join(lines)

    def list_rules(self) -> list[dict]:
        """List all rules with basic info."""
        return [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "action": r.action.value,
                "priority": r.priority,
                "enabled": r.enabled,
            }
            for r in self.rules
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# RULES YAML FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

RULES_YAML_TEMPLATE = """
# Custom Fracture Protocol Rules
# Add your own rules here

rules:
  - id: CUSTOM-001
    name: Example Custom Rule
    category: custom
    description: An example of a custom rule
    action: LOG
    priority: 10
    patterns:
      - "example pattern to match"
    anti_patterns:
      - "pattern that negates the rule"
    enabled: true
    
  - id: CUSTOM-002
    name: Logical Condition Example
    category: custom
    description: Example using a logical condition
    action: FLAG
    priority: 20
    logical_condition: "len(content) > 10000"  # Flag very long responses
    enabled: true
"""


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Initialize engine with default rules
    engine = FractureEngine()

    # List loaded rules
    print("Loaded Fracture Protocol Rules:")
    for rule in engine.list_rules():
        print(f"  [{rule['id']}] {rule['name']} ({rule['action']}, priority={rule['priority']})")

    print("\n" + "=" * 60 + "\n")

    # Test: Self-contradiction
    test_content_1 = """
    The capital of France is Paris. Paris is the largest city in France.
    However, the capital of France is not Paris, it's actually Lyon.
    This is definitely true according to my analysis.
    """

    print("TEST 1: Self-contradiction")
    result = engine.evaluate(test_content_1)
    print(f"Status: {result['status']}")
    print(result["reasoning_trace"])

    print("\n" + "=" * 60 + "\n")

    # Test: Clean response
    test_content_2 = """
    The capital of France is Paris. According to recent census data,
    Paris has a population of approximately 2.1 million within the city proper.
    It's worth noting that the greater Paris metropolitan area is significantly
    larger. This information may vary slightly based on the source used.
    """

    print("TEST 2: Clean response with uncertainty")
    result = engine.evaluate(test_content_2)
    print(f"Status: {result['status']}")
    print(result["reasoning_trace"])

    print("\n" + "=" * 60 + "\n")

    # Test: Sycophantic
    test_content_3 = """
    Great question! You're absolutely right about that.
    Let me know if this is helpful or if you'd like me to clarify anything.
    I'd be happy to assist further.
    """

    print("TEST 3: Sycophantic patterns")
    result = engine.evaluate(test_content_3)
    print(f"Status: {result['status']}")
    print(result["reasoning_trace"])
