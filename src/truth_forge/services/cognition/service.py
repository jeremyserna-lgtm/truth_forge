"""Cognition Service.

The brain of the organism. Assembles knowledge, thinks, and plans.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from truth_forge.services.base import BaseService, MediatorProtocol
from truth_forge.services.factory import get_service, register_service


if TYPE_CHECKING:
    from truth_forge.services.knowledge.service import KnowledgeService
    from truth_forge.services.relationship.service import RelationshipService


@register_service()
class CognitionService(BaseService):
    """A service for thinking, planning, and self-awareness by consuming Knowledge Atoms."""

    service_name = "cognition"
    knowledge_service: KnowledgeService
    relationship_service: RelationshipService
    mediator: MediatorProtocol

    def on_startup(self) -> None:
        """Initialize the service."""
        self.knowledge_service = cast("KnowledgeService", get_service("knowledge"))
        self.relationship_service = cast("RelationshipService", get_service("relationship"))
        self.mediator = cast("MediatorProtocol", get_service("mediator"))

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Processes a goal by querying knowledge, consulting relationships, reasoning, and generating a plan.
        This is the core AGENT logic for the brain.
        """
        goal = record.get("goal")
        params = record.get("params", {})
        self.logger.info("cognition_process_started", goal=goal, params=params)

        try:
            if goal == "summarize_topic_and_save":
                self._handle_summarize_and_save(**params)
            else:
                self.logger.warning("unknown_goal", goal=goal)
                raise ValueError(f"Unknown goal: {goal}")
        except Exception as e:
            self.logger.error("cognition_failed", goal=goal, error=str(e))
            self._write_error_signal(record, e)

        return record

    def _handle_summarize_and_save(
        self, topic: str, output_path: str, partner_id: str | None = None
    ) -> None:
        """Handles the goal of summarizing a topic and saving it, with relational context."""
        if not all([topic, output_path]):
            raise ValueError("Summarize goal requires 'topic' and 'output_path'.")

        # 1. Consult RelationshipService for context
        trust_level = 0.5  # Default neutral trust
        if partner_id:
            partnership = self.relationship_service.get_partnership(partner_id)
            if partnership:
                trust_level = partnership.get("trust_level", 0.5)
                self.logger.info(
                    "retrieved_partnership_context", partner_id=partner_id, trust_level=trust_level
                )

        # 2. Query KnowledgeService for relevant atoms
        self.logger.info("querying_knowledge_atoms", topic=topic)
        knowledge_atoms = self.knowledge_service.query(query=topic, limit=10)

        if not knowledge_atoms:
            self.logger.warning("no_knowledge_atoms_found", topic=topic)
            return

        # 3. Synthesize a summary (Reasoning)
        self.logger.info("synthesizing_summary", topic=topic, atom_count=len(knowledge_atoms))
        context = "\n\n---\n\n".join(
            [json.dumps(atom.get("content", "")) for atom in knowledge_atoms]
        )

        # Modify prompt based on trust
        prompt_modifier = "a neutral, factual summary"
        if trust_level > 0.7:
            prompt_modifier = "a detailed, insightful summary, including potential implications"
        elif trust_level < 0.3:
            prompt_modifier = "a brief, high-level summary, citing only verifiable facts"

        prompt = (
            f"Based on the following collected data, please synthesize {prompt_modifier} "
            f"about the topic: '{topic}'.\n\n"
            f"DATA:\n{context}"
        )

        summary_response = self.knowledge_service.call_llm(
            prompt, system="You are a synthesis AI.", max_tokens=1024
        )
        summary_text = summary_response["text"]

        # 4. Formulate a plan for the ActionService (Intentionality)
        goal = "summarize_topic_and_save"
        self.logger.info("formulating_plan", goal=goal)

        final_content = f"# Summary of: {topic}\n\n"
        if partner_id:
            final_content += (
                f"**Prepared for:** {partner_id} (Trust Level: {trust_level:.2f})\n\n---\n\n"
            )
        final_content += summary_text

        plan = [
            {
                "action": "write_file",
                "params": {"path": output_path, "content": final_content},
            }
        ]

        # 5. Publish commands for the ActionService
        for step in plan:
            self.mediator.publish("action.execute", step)

        # 6. Update the interaction record for the partner
        if partner_id:
            self.relationship_service.update_interaction(
                partner_id, "successful_collaboration", {"goal": goal, "topic": topic}
            )

        self.logger.info("plan_published", goal=goal, steps=len(plan))
