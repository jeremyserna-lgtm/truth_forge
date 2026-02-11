"""Cascade Pipeline — the full transformation loop.

HOLD:AGENT:HOLD at every stage:

Stage 1: ATOMIZE  — Signals → Knowledge Atoms (Scout)
Stage 2: SYNTHESIZE — Knowledge Atoms → New Insights (Maverick)
Stage 3: FORGE — Insights → Enriched Narratives (Maverick + Scout)

Each stage feeds the next. The cascade loops until saturation
(information gain drops below threshold).

This is NOT-ME's metabolism. Jeremy's life signals go in.
Knowledge, insights, and narratives come out.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import structlog


if TYPE_CHECKING:
    from truth_forge.pipeline.signals import LifeSignal


logger = structlog.get_logger(service="cascade")


@dataclass
class KnowledgeAtom:
    """An irreducible unit of knowledge.

    Extracted from life signals by Scout's 10M context window.

    Attributes:
        id: Content-based hash for dedup.
        atom_type: Classification of the knowledge.
        content: The atomic statement.
        confidence: How confident the model is (0.0-1.0).
        sources: Where this atom came from.
        entities: People, systems, concepts mentioned.
        themes: High-level themes this relates to.
    """

    atom_type: str  # fact, concept, relationship, directive, pattern, reference
    content: str
    confidence: float = 0.8
    sources: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    id: str = ""

    def __post_init__(self) -> None:
        """Generate content-based ID."""
        if not self.id:
            import hashlib

            self.id = hashlib.sha256(self.content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "atom_type": self.atom_type,
            "content": self.content,
            "confidence": self.confidence,
            "sources": self.sources,
            "entities": self.entities,
            "themes": self.themes,
        }


@dataclass
class CascadeResult:
    """Result of a complete cascade run.

    Attributes:
        cycles: Number of cascade cycles executed.
        atoms_created: Total atoms extracted across all cycles.
        insights_generated: New insights synthesized.
        narratives_forged: Enriched narratives produced.
        saturated: Whether information gain dropped below threshold.
        total_gain: Cumulative information gain.
        duration_seconds: Total time taken.
    """

    cycles: int = 0
    atoms_created: int = 0
    insights_generated: int = 0
    narratives_forged: int = 0
    saturated: bool = False
    total_gain: float = 0.0
    duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cycles": self.cycles,
            "atoms_created": self.atoms_created,
            "insights_generated": self.insights_generated,
            "narratives_forged": self.narratives_forged,
            "saturated": self.saturated,
            "total_gain": round(self.total_gain, 4),
            "duration_seconds": round(self.duration_seconds, 2),
            "errors": self.errors,
        }


@dataclass
class CascadeConfig:
    """Configuration for the cascade pipeline.

    Attributes:
        max_cycles: Maximum cascade iterations before stopping.
        saturation_threshold: Minimum information gain to continue (0.0-1.0).
        scout_endpoint: Ollama endpoint for Scout.
        scout_model: Scout model name.
        exo_endpoint: EXO endpoint for Maverick/R1.
        maverick_model: Maverick model name.
        atomize_temperature: Temperature for knowledge extraction.
        synthesize_temperature: Temperature for synthesis.
        max_atoms_per_signal: Maximum atoms to extract per signal.
    """

    max_cycles: int = 5
    saturation_threshold: float = 0.05
    scout_endpoint: str = "http://localhost:11434"
    scout_model: str = "llama4:scout"
    exo_endpoint: str = "http://localhost:8000"
    maverick_model: str = "llama4:maverick"
    atomize_temperature: float = 0.3
    synthesize_temperature: float = 0.7
    max_atoms_per_signal: int = 20


class CascadePipeline:
    """The full transformation cascade.

    INHALE: Life signals enter
    ATOMIZE: Scout extracts knowledge atoms
    SYNTHESIZE: Maverick connects atoms to existing knowledge
    FORGE: Maverick + Scout create enriched narratives
    EXHALE: Knowledge, insights, narratives available

    Loops until saturation or max_cycles reached.
    """

    def __init__(self, config: CascadeConfig | None = None) -> None:
        """Initialize cascade pipeline.

        Args:
            config: Pipeline configuration. Uses defaults if None.
        """
        self.config = config or CascadeConfig()
        self._logger = structlog.get_logger(service="cascade_pipeline")
        self._previous_atom_count = 0

    async def run(self, signals: list[LifeSignal]) -> CascadeResult:
        """Execute the full cascade on a batch of life signals.

        Args:
            signals: Life signals to process.

        Returns:
            CascadeResult with metrics from the run.
        """
        start_time = time.time()
        result = CascadeResult()

        if not signals:
            self._logger.info("cascade_skipped", reason="no_signals")
            return result

        self._logger.info(
            "cascade_started",
            signal_count=len(signals),
            max_cycles=self.config.max_cycles,
        )

        # Stage 1: ATOMIZE — extract knowledge atoms from signals
        all_atoms: list[KnowledgeAtom] = []
        for signal in signals:
            try:
                atoms = await self._atomize(signal)
                all_atoms.extend(atoms)
                result.atoms_created += len(atoms)
            except Exception as e:
                error_msg = f"Atomize failed for signal {signal.id}: {e}"
                result.errors.append(error_msg)
                self._logger.error(
                    "atomize_failed",
                    signal_id=signal.id,
                    error=str(e),
                )

        if not all_atoms:
            self._logger.info("cascade_empty", reason="no_atoms_extracted")
            result.duration_seconds = time.time() - start_time
            return result

        # Stage 2: SYNTHESIZE — connect atoms to existing knowledge
        cycle = 0
        while cycle < self.config.max_cycles:
            cycle += 1

            try:
                insights = await self._synthesize(all_atoms, cycle)
                result.insights_generated += len(insights)
            except Exception as e:
                error_msg = f"Synthesize failed at cycle {cycle}: {e}"
                result.errors.append(error_msg)
                self._logger.error(
                    "synthesize_failed",
                    cycle=cycle,
                    error=str(e),
                )
                break

            # Stage 3: FORGE — create enriched narratives
            try:
                narratives = await self._forge(all_atoms, insights, cycle)
                result.narratives_forged += len(narratives)
            except Exception as e:
                error_msg = f"Forge failed at cycle {cycle}: {e}"
                result.errors.append(error_msg)
                self._logger.error(
                    "forge_failed",
                    cycle=cycle,
                    error=str(e),
                )

            # Check information gain (saturation detection)
            gain = self._measure_gain(all_atoms, cycle)
            result.total_gain += gain

            self._logger.info(
                "cascade_cycle_completed",
                cycle=cycle,
                atoms=len(all_atoms),
                gain=round(gain, 4),
            )

            if gain < self.config.saturation_threshold:
                result.saturated = True
                self._logger.info(
                    "saturation_reached",
                    cycle=cycle,
                    gain=round(gain, 4),
                    threshold=self.config.saturation_threshold,
                )
                break

        result.cycles = cycle
        result.duration_seconds = time.time() - start_time

        self._logger.info(
            "cascade_completed",
            **result.to_dict(),
        )

        return result

    async def _atomize(self, signal: LifeSignal) -> list[KnowledgeAtom]:
        """Stage 1: Extract knowledge atoms from a life signal.

        Uses Scout (10M context) for extraction.

        Args:
            signal: The life signal to atomize.

        Returns:
            List of extracted KnowledgeAtoms.
        """
        prompt = f"""Extract knowledge atoms from this content. Each atom is an irreducible unit of meaning.

For each atom, provide:
- type: one of [fact, concept, relationship, directive, pattern, reference]
- content: the atomic statement (one sentence)
- confidence: 0.0-1.0
- entities: people, systems, or concepts mentioned
- themes: high-level themes

Return as JSON array. Maximum {self.config.max_atoms_per_signal} atoms.

CONTENT (source: {signal.source.value}):
{signal.content[:8000]}

Return ONLY valid JSON array:"""

        try:
            response = await self._call_scout(prompt)
            atoms = self._parse_atoms(response, signal)
            return atoms
        except Exception as e:
            self._logger.error(
                "atomize_llm_failed",
                signal_id=signal.id,
                error=str(e),
            )
            return []

    async def _synthesize(
        self,
        atoms: list[KnowledgeAtom],
        cycle: int,
    ) -> list[dict[str, Any]]:
        """Stage 2: Synthesize atoms into new insights.

        Uses Maverick (128 experts) for cross-domain reasoning.

        Args:
            atoms: Knowledge atoms to synthesize.
            cycle: Current cascade cycle number.

        Returns:
            List of insight dictionaries.
        """
        atom_texts = "\n".join(f"- [{a.atom_type}] {a.content}" for a in atoms[:50])

        prompt = f"""Given these knowledge atoms (cycle {cycle}), identify cross-domain connections and generate new insights.

KNOWLEDGE ATOMS:
{atom_texts}

For each insight:
- connection: what atoms connect
- insight: the new understanding
- confidence: 0.0-1.0
- implications: what this means

Return as JSON array. Focus on non-obvious connections.

Return ONLY valid JSON array:"""

        try:
            response = await self._call_maverick(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            self._logger.error(
                "synthesize_llm_failed",
                cycle=cycle,
                error=str(e),
            )
            return []

    async def _forge(
        self,
        atoms: list[KnowledgeAtom],
        insights: list[dict[str, Any]],
        cycle: int,
    ) -> list[dict[str, Any]]:
        """Stage 3: Forge enriched narratives from atoms and insights.

        Uses Maverick for narrative generation.

        Args:
            atoms: Knowledge atoms.
            insights: Synthesized insights.
            cycle: Current cascade cycle number.

        Returns:
            List of narrative dictionaries.
        """
        atom_summary = "\n".join(f"- {a.content}" for a in atoms[:30])
        insight_summary = "\n".join(f"- {i.get('insight', str(i))}" for i in insights[:10])

        prompt = f"""Forge an enriched narrative from these atoms and insights (cycle {cycle}).

The narrative should:
1. Connect the dots between atoms
2. Surface the deeper meaning
3. Be suitable for podcast discussion
4. Include specific claims with evidence

ATOMS:
{atom_summary}

INSIGHTS:
{insight_summary}

Create a structured narrative with:
- title: narrative title
- summary: 2-3 sentence overview
- body: the full narrative (500-1000 words)
- key_claims: list of specific claims made
- questions: open questions for further exploration

Return as JSON object:"""

        try:
            response = await self._call_maverick(prompt)
            parsed = self._parse_json_response(response)
            if isinstance(parsed, dict):
                return [parsed]
            return parsed if isinstance(parsed, list) else []
        except Exception as e:
            self._logger.error(
                "forge_llm_failed",
                cycle=cycle,
                error=str(e),
            )
            return []

    async def _call_scout(self, prompt: str) -> str:
        """Call Scout via Ollama.

        Args:
            prompt: The prompt to send.

        Returns:
            Model response text.
        """
        import urllib.request

        payload = json.dumps(
            {
                "model": self.config.scout_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.atomize_temperature,
                "stream": False,
            }
        ).encode()

        req = urllib.request.Request(
            f"{self.config.scout_endpoint}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            return data.get("message", {}).get("content", "")

    async def _call_maverick(self, prompt: str) -> str:
        """Call Maverick via EXO (OpenAI-compatible API).

        Falls back to Scout if EXO is unavailable.

        Args:
            prompt: The prompt to send.

        Returns:
            Model response text.
        """
        import urllib.request

        # Try EXO first
        try:
            payload = json.dumps(
                {
                    "model": self.config.maverick_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.config.synthesize_temperature,
                    "max_tokens": 4096,
                }
            ).encode()

            req = urllib.request.Request(
                f"{self.config.exo_endpoint}/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode())
                return data["choices"][0]["message"]["content"]
        except Exception:
            # Fall back to Scout
            self._logger.info("maverick_unavailable_falling_back_to_scout")
            return await self._call_scout(prompt)

    def _parse_atoms(
        self,
        response: str,
        signal: LifeSignal,
    ) -> list[KnowledgeAtom]:
        """Parse LLM response into KnowledgeAtoms.

        Args:
            response: Raw LLM response text.
            signal: Original signal (for source attribution).

        Returns:
            List of parsed KnowledgeAtoms.
        """
        atoms: list[KnowledgeAtom] = []

        try:
            parsed = self._extract_json(response)
            if not isinstance(parsed, list):
                parsed = [parsed]

            for item in parsed:
                if not isinstance(item, dict):
                    continue
                atom = KnowledgeAtom(
                    atom_type=item.get("type", "fact"),
                    content=item.get("content", ""),
                    confidence=float(item.get("confidence", 0.8)),
                    sources=[signal.metadata.get("file_path", signal.source.value)],
                    entities=item.get("entities", []),
                    themes=item.get("themes", []),
                )
                if atom.content:
                    atoms.append(atom)
        except Exception as e:
            self._logger.warning(
                "atom_parse_failed",
                error=str(e),
                response_preview=response[:200],
            )

        return atoms

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from an LLM response, handling markdown fences.

        Args:
            response: Raw LLM response.

        Returns:
            Parsed JSON data.
        """
        return self._extract_json(response)

    def _extract_json(self, text: str) -> Any:
        """Extract JSON from text, handling markdown code fences.

        Args:
            text: Text potentially containing JSON.

        Returns:
            Parsed JSON data.
        """
        # Strip markdown code fences
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        return json.loads(cleaned)

    def _measure_gain(
        self,
        atoms: list[KnowledgeAtom],
        cycle: int,
    ) -> float:
        """Measure information gain for saturation detection.

        Uses unique atom count delta as a simple gain metric.

        Args:
            atoms: Current atom set.
            cycle: Current cycle number.

        Returns:
            Information gain ratio (0.0-1.0).
        """
        current_count = len(atoms)
        if self._previous_atom_count == 0:
            gain = 1.0
        else:
            gain = (current_count - self._previous_atom_count) / max(self._previous_atom_count, 1)
        self._previous_atom_count = current_count
        return max(gain, 0.0)
