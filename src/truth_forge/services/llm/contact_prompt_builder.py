"""Contact prompt builder for LLM dynamic prompting system."""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ContactPromptBuilder:
    """Builds LLM prompts from contact data.
    
    Transforms rich contact data into structured context strings
    optimized for LLM model calls.
    """

    def __init__(self, contact_fetcher: Any) -> None:
        """Initialize prompt builder.
        
        Args:
            contact_fetcher: Service to fetch contacts (from any source)
        """
        self.contact_fetcher = contact_fetcher

    def build_contact_context(self, contact: Dict[str, Any]) -> str:
        """Build rich context string for LLM prompts.
        
        Args:
            contact: Contact record (canonical format)
            
        Returns:
            Formatted context string
        """
        parts = []

        # Basic Info
        parts.append(f"**Contact**: {contact.get('canonical_name', 'Unknown')}")
        if contact.get("organization"):
            parts.append(f"**Organization**: {contact['organization']}")
        if contact.get("job_title"):
            parts.append(f"**Title**: {contact['job_title']}")

        # Relationship Context
        if contact.get("category_code"):
            rel_category = contact.get("relationship_category", "unknown")
            parts.append(f"**Category**: {contact['category_code']} ({rel_category})")
        if contact.get("subcategory_code"):
            parts.append(f"**Subcategory**: {contact['subcategory_code']}")

        # LLM Context
        llm_ctx = contact.get("llm_context", {})
        if isinstance(llm_ctx, str):
            import json
            try:
                llm_ctx = json.loads(llm_ctx)
            except json.JSONDecodeError:
                llm_ctx = {}

        if llm_ctx.get("relationship_arc"):
            parts.append(f"**Relationship Arc**: {llm_ctx['relationship_arc']}")
        if llm_ctx.get("communication_style"):
            parts.append(f"**Communication Style**: {llm_ctx['communication_style']}")
        if llm_ctx.get("key_interests"):
            interests = (
                llm_ctx["key_interests"]
                if isinstance(llm_ctx["key_interests"], list)
                else []
            )
            parts.append(f"**Interests**: {', '.join(interests)}")
        if llm_ctx.get("current_state"):
            parts.append(f"**Current State**: {llm_ctx['current_state']}")
        if llm_ctx.get("how_met"):
            parts.append(f"**How We Met**: {llm_ctx['how_met']}")
        if llm_ctx.get("personality_notes"):
            parts.append(f"**Personality Notes**: {llm_ctx['personality_notes']}")

        # Communication Stats
        comm_stats = contact.get("communication_stats", {})
        if isinstance(comm_stats, str):
            import json
            try:
                comm_stats = json.loads(comm_stats)
            except json.JSONDecodeError:
                comm_stats = {}

        if comm_stats.get("last_contact_date"):
            parts.append(f"**Last Contact**: {comm_stats['last_contact_date']}")
        if comm_stats.get("relationship_health"):
            parts.append(f"**Relationship Health**: {comm_stats['relationship_health']}")
        if comm_stats.get("total_messages"):
            parts.append(f"**Total Messages**: {comm_stats['total_messages']}")

        # AI Insights
        ai_insights = contact.get("ai_insights", {})
        if isinstance(ai_insights, str):
            import json
            try:
                ai_insights = json.loads(ai_insights)
            except json.JSONDecodeError:
                ai_insights = {}

        if ai_insights.get("primary_topics"):
            topics = (
                ai_insights["primary_topics"]
                if isinstance(ai_insights["primary_topics"], list)
                else []
            )
            parts.append(f"**Common Topics**: {', '.join(topics)}")
        if ai_insights.get("sentiment_when_discussed"):
            sentiment = ai_insights["sentiment_when_discussed"]
            parts.append(f"**Sentiment**: {sentiment:.2f}")

        # Recommendations
        recommendations = contact.get("recommendations", {})
        if isinstance(recommendations, str):
            import json
            try:
                recommendations = json.loads(recommendations)
            except json.JSONDecodeError:
                recommendations = {}

        if recommendations.get("conversation_topics"):
            topics = (
                recommendations["conversation_topics"]
                if isinstance(recommendations["conversation_topics"], list)
                else []
            )
            parts.append(f"**Suggested Topics**: {', '.join(topics)}")
        if recommendations.get("contact_cadence"):
            parts.append(f"**Contact Cadence**: {recommendations['contact_cadence']}")

        # Social Network
        social_network = contact.get("social_network", {})
        if isinstance(social_network, str):
            import json
            try:
                social_network = json.loads(social_network)
            except json.JSONDecodeError:
                social_network = {}

        if social_network.get("groups"):
            groups = (
                social_network["groups"]
                if isinstance(social_network["groups"], list)
                else []
            )
            parts.append(f"**Groups**: {', '.join(groups)}")

        return "\n".join(parts)

    def build_prompt_with_contact(
        self, base_prompt: str, contact_id: str, source: str = "bigquery"
    ) -> str:
        """Build full prompt with contact context.
        
        Args:
            base_prompt: Base prompt text
            contact_id: Contact ID to fetch
            source: Source system (bigquery, supabase, local)
            
        Returns:
            Full prompt with contact context
        """
        contact = self.contact_fetcher.fetch_contact(contact_id, source)
        if not contact:
            logger.warning(f"Contact {contact_id} not found in {source}")
            return base_prompt

        contact_context = self.build_contact_context(contact)

        return f"""{base_prompt}

## Contact Context
{contact_context}
"""

    def build_multi_contact_context(
        self, contact_ids: list[str], source: str = "bigquery"
    ) -> str:
        """Build context for multiple contacts.
        
        Args:
            contact_ids: List of contact IDs
            source: Source system
            
        Returns:
            Combined context string
        """
        contexts = []
        for contact_id in contact_ids:
            contact = self.contact_fetcher.fetch_contact(contact_id, source)
            if contact:
                context = self.build_contact_context(contact)
                contexts.append(context)

        return "\n\n---\n\n".join(contexts)
