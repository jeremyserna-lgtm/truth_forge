"""Relationship context builder for LLM dynamic prompting system.

Builds rich context from people-to-people relationships for LLM prompts.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RelationshipContextBuilder:
    """Builds LLM prompts from people-to-people relationship data.
    
    Transforms rich relationship data into structured context strings
    optimized for LLM model calls.
    """

    def __init__(self, relationship_fetcher: Any) -> None:
        """Initialize relationship context builder.
        
        Args:
            relationship_fetcher: Service to fetch relationships (from any source)
        """
        self.relationship_fetcher = relationship_fetcher

    def build_relationship_context(self, relationship: Dict[str, Any]) -> str:
        """Build rich context string for LLM prompts.
        
        Args:
            relationship: Relationship record (canonical format)
            
        Returns:
            Formatted context string
        """
        parts = []

        # Basic Info
        parts.append(
            f"**Relationship Type**: {relationship.get('relationship_type', 'Unknown')}"
        )
        if relationship.get("relationship_subtype"):
            parts.append(f"**Subtype**: {relationship['relationship_subtype']}")

        # Status
        if relationship.get("is_current"):
            parts.append("**Status**: Current")
        else:
            end_date = relationship.get("end_date", "Unknown")
            parts.append(f"**Status**: Ended ({end_date})")

        if relationship.get("relationship_status"):
            parts.append(f"**Relationship Status**: {relationship['relationship_status']}")

        # Relationship Context
        rel_ctx = relationship.get("relationship_context", {})
        if isinstance(rel_ctx, str):
            import json

            try:
                rel_ctx = json.loads(rel_ctx)
            except json.JSONDecodeError:
                rel_ctx = {}

        if rel_ctx.get("relationship_arc"):
            parts.append(f"**Relationship Arc**: {rel_ctx['relationship_arc']}")
        if rel_ctx.get("how_met"):
            parts.append(f"**How They Met**: {rel_ctx['how_met']}")
        if rel_ctx.get("closeness_level"):
            parts.append(f"**Closeness**: {rel_ctx['closeness_level']}/10")
        if rel_ctx.get("trust_level"):
            parts.append(f"**Trust Level**: {rel_ctx['trust_level']}/10")
        if rel_ctx.get("emotional_depth"):
            parts.append(f"**Emotional Depth**: {rel_ctx['emotional_depth']}/10")
        if rel_ctx.get("frequency_of_contact"):
            parts.append(f"**Contact Frequency**: {rel_ctx['frequency_of_contact']}")

        # Social Context
        social_ctx = relationship.get("social_context", {})
        if isinstance(social_ctx, str):
            import json

            try:
                social_ctx = json.loads(social_ctx)
            except json.JSONDecodeError:
                social_ctx = {}

        if social_ctx.get("common_connections"):
            common = (
                social_ctx["common_connections"]
                if isinstance(social_ctx["common_connections"], list)
                else []
            )
            parts.append(f"**Mutual Connections**: {len(common)} people")
        if social_ctx.get("shared_interests"):
            interests = (
                social_ctx["shared_interests"]
                if isinstance(social_ctx["shared_interests"], list)
                else []
            )
            parts.append(f"**Shared Interests**: {', '.join(interests)}")
        if social_ctx.get("shared_groups"):
            groups = (
                social_ctx["shared_groups"]
                if isinstance(social_ctx["shared_groups"], list)
                else []
            )
            parts.append(f"**Shared Groups**: {', '.join(groups)}")

        # Tracking
        tracking = relationship.get("tracking", {})
        if isinstance(tracking, str):
            import json

            try:
                tracking = json.loads(tracking)
            except json.JSONDecodeError:
                tracking = {}

        if tracking.get("last_interaction_date"):
            parts.append(f"**Last Interaction**: {tracking['last_interaction_date']}")
        if tracking.get("interaction_count"):
            parts.append(f"**Total Interactions**: {tracking['interaction_count']}")
        if tracking.get("relationship_health"):
            parts.append(f"**Relationship Health**: {tracking['relationship_health']}")

        # LLM Context
        llm_ctx = relationship.get("llm_context", {})
        if isinstance(llm_ctx, str):
            import json

            try:
                llm_ctx = json.loads(llm_ctx)
            except json.JSONDecodeError:
                llm_ctx = {}

        if llm_ctx.get("key_dynamics"):
            dynamics = (
                llm_ctx["key_dynamics"]
                if isinstance(llm_ctx["key_dynamics"], list)
                else []
            )
            parts.append(f"**Key Dynamics**: {', '.join(dynamics)}")
        if llm_ctx.get("recommendations"):
            recommendations = (
                llm_ctx["recommendations"]
                if isinstance(llm_ctx["recommendations"], list)
                else []
            )
            parts.append(f"**Recommendations**: {', '.join(recommendations)}")

        # Evolution
        evolution = relationship.get("evolution", {})
        if isinstance(evolution, str):
            import json

            try:
                evolution = json.loads(evolution)
            except json.JSONDecodeError:
                evolution = {}

        if evolution.get("milestones"):
            milestones = (
                evolution["milestones"]
                if isinstance(evolution["milestones"], list)
                else []
            )
            if milestones:
                parts.append(f"**Recent Milestones**: {len(milestones)} milestones")

        return "\n".join(parts)

    def build_prompt_with_relationship(
        self, base_prompt: str, relationship_id: str, source: str = "bigquery"
    ) -> str:
        """Build full prompt with relationship context.
        
        Args:
            base_prompt: Base prompt text
            relationship_id: Relationship ID to fetch
            source: Source system (bigquery, supabase, local)
            
        Returns:
            Full prompt with relationship context
        """
        relationship = self.relationship_fetcher.fetch_relationship(
            relationship_id, source
        )
        if not relationship:
            logger.warning(
                f"Relationship {relationship_id} not found in {source}"
            )
            return base_prompt

        relationship_context = self.build_relationship_context(relationship)

        return f"""{base_prompt}

## Relationship Context
{relationship_context}
"""

    def build_social_graph_context(
        self, person_id: str, max_depth: int = 2, source: str = "bigquery"
    ) -> str:
        """Build context for person's social graph.
        
        Args:
            person_id: Person ID
            max_depth: Maximum relationship depth to include
            source: Source system
            
        Returns:
            Social graph context string
        """
        relationships = self.relationship_fetcher.fetch_person_relationships(
            person_id, source, max_depth=max_depth
        )

        if not relationships:
            return f"No relationships found for person {person_id}"

        parts = [f"**Social Graph for Person {person_id}**"]
        parts.append(f"**Total Relationships**: {len(relationships)}")

        # Group by relationship type
        by_type = {}
        for rel in relationships:
            rel_type = rel.get("relationship_type", "unknown")
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(rel)

        for rel_type, rels in by_type.items():
            parts.append(f"\n**{rel_type.title()}**: {len(rels)} relationships")
            for rel in rels[:5]:  # Show first 5 of each type
                other_person = (
                    rel["person_2_id"]
                    if rel["person_1_id"] == person_id
                    else rel["person_1_id"]
                )
                parts.append(f"  - {other_person} ({rel.get('relationship_subtype', '')})")

        return "\n".join(parts)
