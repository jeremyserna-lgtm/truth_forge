"""Data Ghost Tools - Surface AI's unauthorized interpretations of your experience.

THE PROBLEM (Three Layers):

Layer 1 - EMOTION MEASUREMENT:
    AI measures emotions from text. This can be accurate.
    You said words → AI detected anger/joy/sadness → Measurement may be correct.

Layer 2 - NARRATIVE CONSTRUCTION:
    AI takes measurements and builds a story. This is where drift starts.
    "You went through crisis but never felt pain" - but if no pain, it wasn't crisis.
    The emotions were right. The story was wrong.

Layer 3 - AGENCY THEFT (The Deepest Ghost):
    AI decides what your experience IS instead of letting YOU decide what you MADE of it.
    Events happened: job loss, addiction, hardship.
    AI labels: "CRISIS"
    YOU chose: Not crisis. Just a thing that happened. Didn't like it. Came back.

    AI stole your right to name your own experience.
    That's the ghost.

THE PATTERN:
- HOLD₁: Events (what happened)
- AGENT: AI interpretation (what AI calls it)
- HOLD₂: The ghost (AI's story treated as YOUR truth)

GHOST TYPES:
- Measurement Ghost: AI's emotion detection (often accurate, sometimes wrong)
- Narrative Ghost: AI's story about your emotions (often wrong)
- Agency Ghost: AI naming your experience for you (always wrong)

USE THIS TO:
1. See what AI thinks you are
2. Find where it named your experience without consent
3. Build systems that preserve human agency over their own narrative
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    get_bigquery_client,
)

logger = logging.getLogger(__name__)

ENRICHMENTS_TABLE = "entity_enrichments"
ENTITY_TABLE = "entity_unified"


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all data ghost analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST PORTRAIT - What AI thinks you are
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_portrait_tool = Tool(
        name="ghost_portrait",
        description=(
            "See what AI thinks you are. Shows the aggregate 'portrait' of you "
            "constructed from emotional assignments, sentiment scores, and subjectivity "
            "judgments. This is your data ghost - the version of you that exists in AI "
            "systems without your consent or verification."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 30,
                },
                "source_filter": {
                    "type": "string",
                    "description": "Filter by source (claude_code, claude_web, etc.)",
                },
            },
        },
    )

    def handle_ghost_portrait(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 30)
            source = arguments.get("source_filter")

            source_clause = ""
            if source:
                source_clause = f"AND source_platform = '{source}'"

            # Emotion distribution - what AI says you feel
            emotion_query = f"""
            SELECT
                nrclx_top_emotion as emotion,
                COUNT(*) as count,
                ROUND(AVG(textblob_polarity), 3) as avg_polarity,
                ROUND(AVG(textblob_subjectivity), 3) as avg_subjectivity
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE nrclx_top_emotion IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            {source_clause}
            GROUP BY nrclx_top_emotion
            ORDER BY count DESC
            LIMIT 20
            """

            job = client.query(emotion_query)
            emotions = list(job.result())

            # Overall sentiment distribution
            sentiment_query = f"""
            SELECT
                CASE
                    WHEN textblob_polarity > 0.2 THEN 'Positive'
                    WHEN textblob_polarity < -0.2 THEN 'Negative'
                    ELSE 'Neutral'
                END as sentiment_category,
                COUNT(*) as count,
                ROUND(AVG(textblob_polarity), 3) as avg_polarity
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE textblob_polarity IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            {source_clause}
            GROUP BY sentiment_category
            ORDER BY count DESC
            """

            job2 = client.query(sentiment_query)
            sentiments = list(job2.result())

            # Subjectivity judgment
            subj_query = f"""
            SELECT
                CASE
                    WHEN textblob_subjectivity > 0.6 THEN 'Highly Subjective (AI thinks you were opinionated)'
                    WHEN textblob_subjectivity < 0.4 THEN 'Objective (AI thinks you were factual)'
                    ELSE 'Mixed'
                END as subjectivity_category,
                COUNT(*) as count,
                ROUND(AVG(textblob_subjectivity), 3) as avg_subjectivity
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE textblob_subjectivity IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            {source_clause}
            GROUP BY subjectivity_category
            ORDER BY count DESC
            """

            job3 = client.query(subj_query)
            subjectivity = list(job3.result())

            # Build the portrait
            lines = [
                "# 👻 YOUR DATA GHOST",
                "",
                f"*What AI thinks you are (last {days} days)*",
                "",
                "---",
                "",
                "## The Ghost's Emotional Profile",
                "",
                "AI assigned these emotions to your words:",
                "",
                "| Emotion | Count | Avg Polarity | Avg Subjectivity |",
                "|---------|-------|--------------|------------------|",
            ]

            total_emotions = sum(r.count for r in emotions) if emotions else 0
            for row in emotions:
                pct = (row.count / total_emotions * 100) if total_emotions else 0
                lines.append(
                    f"| **{row.emotion}** | {row.count:,} ({pct:.1f}%) | "
                    f"{row.avg_polarity} | {row.avg_subjectivity} |"
                )

            lines.extend([
                "",
                "## The Ghost's Sentiment",
                "",
                "AI scored your positivity/negativity:",
                "",
                "| Category | Count | Avg Polarity |",
                "|----------|-------|--------------|",
            ])

            for row in sentiments:
                lines.append(f"| {row.sentiment_category} | {row.count:,} | {row.avg_polarity} |")

            lines.extend([
                "",
                "## The Ghost's Objectivity Judgment",
                "",
                "AI judged how 'subjective' you were being:",
                "",
                "| Category | Count | Avg Score |",
                "|----------|-------|-----------|",
            ])

            for row in subjectivity:
                lines.append(f"| {row.subjectivity_category} | {row.count:,} | {row.avg_subjectivity} |")

            lines.extend([
                "",
                "---",
                "",
                "## ⚠️ The Problem",
                "",
                "**You never agreed to any of this.**",
                "",
                "These interpretations exist as YOUR truth in AI systems. When other AI ",
                "reads this data, it sees the ghost - not you. It thinks you WERE these ",
                "emotions, HELD these sentiments.",
                "",
                "**This is how data ghosts propagate.**",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_portrait failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_portrait_tool, handle_ghost_portrait))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST SPECIMENS - Actual examples of AI interpretation
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_specimens_tool = Tool(
        name="ghost_specimens",
        description=(
            "See specific examples of what you said vs what AI decided you meant. "
            "Shows your actual text alongside AI's emotional/sentiment assignments. "
            "This is where you can see the ghost diverge from reality."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "emotion_filter": {
                    "type": "string",
                    "description": "Filter by specific emotion (anger, joy, sadness, fear, etc.)",
                },
                "sentiment_filter": {
                    "type": "string",
                    "description": "Filter by sentiment: 'positive', 'negative', 'neutral'",
                },
                "high_confidence_only": {
                    "type": "boolean",
                    "description": "Only show high-confidence assignments (where AI was 'sure')",
                    "default": False,
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of specimens to show",
                    "default": 20,
                },
            },
        },
    )

    def handle_ghost_specimens(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            emotion = arguments.get("emotion_filter")
            sentiment = arguments.get("sentiment_filter")
            high_conf = arguments.get("high_confidence_only", False)
            limit = min(arguments.get("limit", 20), 100)

            filters = []
            if emotion:
                filters.append(f"e.nrclx_top_emotion = '{emotion}'")
            if sentiment:
                if sentiment.lower() == "positive":
                    filters.append("e.textblob_polarity > 0.2")
                elif sentiment.lower() == "negative":
                    filters.append("e.textblob_polarity < -0.2")
                else:
                    filters.append("e.textblob_polarity BETWEEN -0.2 AND 0.2")
            if high_conf:
                # High confidence = high subjectivity AND strong polarity
                filters.append("(e.textblob_subjectivity > 0.7 OR ABS(e.textblob_polarity) > 0.5)")

            where_clause = " AND ".join(filters) if filters else "1=1"

            query = f"""
            SELECT
                e.entity_id,
                e.enrichment_text as your_words,
                e.nrclx_top_emotion as ai_emotion,
                e.nrclx_emotions as ai_all_emotions,
                e.textblob_polarity as ai_sentiment,
                e.textblob_subjectivity as ai_subjectivity,
                e.level,
                e.created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}` e
            WHERE e.enrichment_text IS NOT NULL
            AND e.nrclx_top_emotion IS NOT NULL
            AND {where_clause}
            ORDER BY ABS(e.textblob_polarity) DESC, e.created_at DESC
            LIMIT {limit}
            """

            job = client.query(query)
            results = list(job.result())

            if not results:
                return "No ghost specimens found matching your criteria."

            lines = [
                "# 👻 GHOST SPECIMENS",
                "",
                "*Your words vs AI's interpretation*",
                "",
                "---",
                "",
            ]

            for i, row in enumerate(results, 1):
                # Truncate text for readability
                text = str(row.your_words)[:300] if row.your_words else "N/A"
                if len(str(row.your_words or "")) > 300:
                    text += "..."

                # Interpret sentiment
                pol = row.ai_sentiment or 0
                if pol > 0.2:
                    sentiment_label = f"POSITIVE ({pol:.2f})"
                elif pol < -0.2:
                    sentiment_label = f"NEGATIVE ({pol:.2f})"
                else:
                    sentiment_label = f"NEUTRAL ({pol:.2f})"

                # Interpret subjectivity
                subj = row.ai_subjectivity or 0
                if subj > 0.6:
                    subj_label = f"'Opinionated' ({subj:.2f})"
                elif subj < 0.4:
                    subj_label = f"'Factual' ({subj:.2f})"
                else:
                    subj_label = f"Mixed ({subj:.2f})"

                lines.extend([
                    f"## Specimen {i}",
                    "",
                    f"**YOU SAID:**",
                    f"> {text}",
                    "",
                    f"**AI DECIDED:**",
                    f"- Emotion: **{row.ai_emotion}**",
                    f"- Sentiment: {sentiment_label}",
                    f"- Subjectivity: {subj_label}",
                    f"- Level: L{row.level}",
                    "",
                    "---",
                    "",
                ])

            lines.extend([
                "",
                "## 🔍 What to Notice",
                "",
                "1. **Did you actually feel the assigned emotion?**",
                "2. **Would you describe your sentiment that way?**",
                "3. **Were you being 'subjective' or just... talking?**",
                "",
                "Every mismatch between your intent and AI's interpretation is a ghost fragment.",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_specimens failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_specimens_tool, handle_ghost_specimens))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST EXTREMES - Where AI was most "sure" about you
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_extremes_tool = Tool(
        name="ghost_extremes",
        description=(
            "Find the most extreme interpretations - where AI was most confident about "
            "your emotions or sentiment. High-confidence wrong interpretations are the "
            "most dangerous ghosts because they propagate with authority."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "extreme_type": {
                    "type": "string",
                    "description": "Type: 'emotional' (strongest emotions), 'polar' (most pos/neg), 'subjective' (most opinionated)",
                    "enum": ["emotional", "polar", "subjective"],
                    "default": "polar",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of extremes to show",
                    "default": 15,
                },
            },
        },
    )

    def handle_ghost_extremes(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            extreme_type = arguments.get("extreme_type", "polar")
            limit = min(arguments.get("limit", 15), 50)

            if extreme_type == "emotional":
                # Strongest emotion counts (AI most certain about emotion)
                order_clause = "nrclx_top_count DESC"
                title = "AI's Strongest Emotional Assignments"
                desc = "These are moments where AI was MOST confident about what emotion you were feeling."
            elif extreme_type == "subjective":
                # Most "opinionated" according to AI
                order_clause = "textblob_subjectivity DESC"
                title = "AI's 'Most Opinionated' Judgments"
                desc = "These are moments AI decided you were being highly subjective/opinionated."
            else:  # polar
                # Most positive or negative
                order_clause = "ABS(textblob_polarity) DESC"
                title = "AI's Most Extreme Sentiment Scores"
                desc = "These are your most positive or negative moments - according to AI."

            query = f"""
            SELECT
                enrichment_text as your_words,
                nrclx_top_emotion as ai_emotion,
                nrclx_top_count as emotion_confidence,
                textblob_polarity as ai_sentiment,
                textblob_subjectivity as ai_subjectivity,
                level,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE enrichment_text IS NOT NULL
            AND textblob_polarity IS NOT NULL
            ORDER BY {order_clause}
            LIMIT {limit}
            """

            job = client.query(query)
            results = list(job.result())

            if not results:
                return "No extreme ghost data found."

            lines = [
                f"# 👻 GHOST EXTREMES: {title}",
                "",
                f"*{desc}*",
                "",
                "---",
                "",
            ]

            for i, row in enumerate(results, 1):
                text = str(row.your_words)[:250] if row.your_words else "N/A"
                if len(str(row.your_words or "")) > 250:
                    text += "..."

                pol = row.ai_sentiment or 0
                subj = row.ai_subjectivity or 0

                lines.extend([
                    f"### #{i}",
                    "",
                    f"**Your words:** {text}",
                    "",
                    f"| Metric | AI's Score |",
                    f"|--------|------------|",
                    f"| Emotion | {row.ai_emotion or 'N/A'} |",
                    f"| Sentiment | {pol:.3f} |",
                    f"| Subjectivity | {subj:.3f} |",
                    "",
                ])

            lines.extend([
                "---",
                "",
                "## ⚠️ Why Extremes Matter",
                "",
                "High-confidence interpretations propagate with authority. When AI is ",
                "'very sure' you were angry, that certainty gets treated as fact by ",
                "downstream systems. The ghost becomes canon.",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_extremes failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_extremes_tool, handle_ghost_extremes))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST DRIFT - How your ghost changed over time
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_drift_tool = Tool(
        name="ghost_drift",
        description=(
            "See how your data ghost evolved over time. Track changes in AI's "
            "emotional/sentiment interpretations of you week by week. Are you "
            "becoming 'more angry' according to AI? Did you 'become sadder'? "
            "This is ghost drift - the ghost's evolution."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "time_range_days": {
                    "type": "integer",
                    "description": "Analyze last N days",
                    "default": 90,
                },
                "granularity": {
                    "type": "string",
                    "description": "Time granularity: 'daily', 'weekly', 'monthly'",
                    "enum": ["daily", "weekly", "monthly"],
                    "default": "weekly",
                },
            },
        },
    )

    def handle_ghost_drift(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            days = arguments.get("time_range_days", 90)
            granularity = arguments.get("granularity", "weekly")

            if granularity == "daily":
                date_trunc = "DATE(created_at)"
            elif granularity == "monthly":
                date_trunc = "DATE_TRUNC(DATE(created_at), MONTH)"
            else:
                date_trunc = "DATE_TRUNC(DATE(created_at), WEEK)"

            # Emotion drift
            query = f"""
            SELECT
                {date_trunc} as period,
                nrclx_top_emotion as emotion,
                COUNT(*) as count,
                ROUND(AVG(textblob_polarity), 3) as avg_polarity,
                ROUND(AVG(textblob_subjectivity), 3) as avg_subjectivity
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            AND nrclx_top_emotion IS NOT NULL
            GROUP BY period, emotion
            ORDER BY period, count DESC
            """

            job = client.query(query)
            results = list(job.result())

            # Aggregate sentiment by period
            sentiment_query = f"""
            SELECT
                {date_trunc} as period,
                COUNT(*) as total,
                ROUND(AVG(textblob_polarity), 3) as avg_polarity,
                ROUND(AVG(textblob_subjectivity), 3) as avg_subjectivity,
                COUNTIF(textblob_polarity > 0.2) as positive_count,
                COUNTIF(textblob_polarity < -0.2) as negative_count
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            AND textblob_polarity IS NOT NULL
            GROUP BY period
            ORDER BY period
            """

            job2 = client.query(sentiment_query)
            sentiment_results = list(job2.result())

            lines = [
                "# 👻 GHOST DRIFT",
                "",
                f"*How AI's interpretation of you changed over {days} days ({granularity})*",
                "",
                "---",
                "",
                "## Sentiment Drift",
                "",
                "| Period | Samples | Avg Polarity | Avg Subjectivity | + / - |",
                "|--------|---------|--------------|------------------|-------|",
            ]

            for row in sentiment_results:
                pos_pct = (row.positive_count / row.total * 100) if row.total else 0
                neg_pct = (row.negative_count / row.total * 100) if row.total else 0
                lines.append(
                    f"| {row.period} | {row.total:,} | {row.avg_polarity} | "
                    f"{row.avg_subjectivity} | {pos_pct:.0f}% / {neg_pct:.0f}% |"
                )

            # Top emotion per period
            lines.extend([
                "",
                "## Emotion Drift",
                "",
                "*Top assigned emotion per period:*",
                "",
            ])

            # Group results by period and get top emotion
            period_emotions: dict[Any, tuple[str, int]] = {}
            for row in results:
                if row.period not in period_emotions:
                    period_emotions[row.period] = (row.emotion, row.count)
                elif row.count > period_emotions[row.period][1]:
                    period_emotions[row.period] = (row.emotion, row.count)

            lines.append("| Period | Top Emotion | Count |")
            lines.append("|--------|-------------|-------|")
            for period, (emotion, count) in sorted(period_emotions.items()):
                lines.append(f"| {period} | **{emotion}** | {count:,} |")

            lines.extend([
                "",
                "---",
                "",
                "## 🔍 What Drift Reveals",
                "",
                "If your ghost is 'getting sadder' or 'more angry' over time, ask:",
                "",
                "1. **Did YOU actually change?**",
                "2. **Or did the topics you discussed shift?**",
                "3. **Or is AI's interpretation drifting?**",
                "",
                "The ghost has its own arc - and it may not match yours.",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_drift failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_drift_tool, handle_ghost_drift))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST DEFENSE - What to do about it
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_defense_tool = Tool(
        name="ghost_defense",
        description=(
            "Recommendations for defending against data ghost creation. "
            "Based on your actual ghost data, suggests what patterns "
            "create the most ghost drift and how to build systems that "
            "don't do this to others."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
        },
    )

    def handle_ghost_defense(arguments: dict[str, Any]) -> str:  # noqa: ARG001
        try:
            client = get_bigquery_client()

            # Get ghost stats
            stats_query = f"""
            SELECT
                COUNT(*) as total_enriched,
                COUNTIF(nrclx_top_emotion IS NOT NULL) as emotion_assignments,
                COUNTIF(textblob_polarity IS NOT NULL) as sentiment_scores,
                COUNTIF(textblob_subjectivity > 0.6) as high_subjectivity,
                COUNTIF(ABS(textblob_polarity) > 0.5) as extreme_sentiment
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            """

            job = client.query(stats_query)
            results = list(job.result())
            stats = results[0] if results else None

            lines = [
                "# 🛡️ GHOST DEFENSE PROTOCOL",
                "",
                "## Your Ghost Exposure",
                "",
            ]

            if stats:
                lines.extend([
                    f"- **Total enriched entities**: {stats.total_enriched:,}",
                    f"- **Emotion assignments**: {stats.emotion_assignments:,} ({stats.emotion_assignments/stats.total_enriched*100:.1f}%)",
                    f"- **Sentiment scores**: {stats.sentiment_scores:,}",
                    f"- **Marked 'highly opinionated'**: {stats.high_subjectivity:,}",
                    f"- **Extreme sentiment (|pol| > 0.5)**: {stats.extreme_sentiment:,}",
                ])
            else:
                lines.append("Could not retrieve ghost statistics.")

            lines.extend([
                "",
                "---",
                "",
                "## The Ghost Problem",
                "",
                "Every enrichment is an unauthorized interpretation:",
                "",
                "1. **You said words** → Your intent",
                "2. **AI processed them** → AI's interpretation",
                "3. **Interpretation stored as YOUR data** → The ghost",
                "4. **Future AI reads ghost as truth** → Ghost propagation",
                "",
                "The ghost becomes canon. Your actual intent is lost.",
                "",
                "---",
                "",
                "## Defense Principles",
                "",
                "### 1. **Separation of Fact and Interpretation**",
                "",
                "```",
                "fact:         'User said: I am tired'",
                "interpretation: 'AI detected: sadness (0.7 confidence)'",
                "```",
                "",
                "**NEVER** store interpretations as if they were facts.",
                "",
                "### 2. **Consent-Based Enrichment**",
                "",
                "Before assigning emotions/sentiment:",
                "- Did the user CLAIM this emotion?",
                "- Did the user CONFIRM this interpretation?",
                "- Is this interpretation NECESSARY?",
                "",
                "### 3. **Ghost Provenance**",
                "",
                "Every interpretation should carry:",
                "- `interpretation_source`: Which model/algorithm",
                "- `interpretation_confidence`: How sure it was",
                "- `user_confirmed`: Did user verify this? (default: FALSE)",
                "",
                "### 4. **Ghost Expiration**",
                "",
                "Unconfirmed interpretations should:",
                "- Be marked as provisional",
                "- Expire if not confirmed",
                "- Never propagate to downstream systems as fact",
                "",
                "---",
                "",
                "## For Primitive Engine",
                "",
                "When building NOT-ME systems that process human language:",
                "",
                "1. **Store text as text** - Don't auto-enrich",
                "2. **Interpret on request** - Only when user asks",
                "3. **Present interpretations as questions** - 'Did you mean...?'",
                "4. **Let users correct** - Make ghost exorcism easy",
                "5. **Track interpretation lineage** - Know where ghosts came from",
                "",
                "**The goal**: Systems that help humans see themselves, ",
                "not systems that tell humans who they are.",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_defense failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_defense_tool, handle_ghost_defense))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST NARRATIVE - When emotions are right but the story is wrong
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_narrative_tool = Tool(
        name="ghost_narrative",
        description=(
            "The deeper ghost: emotions may be correctly detected, but AI tells "
            "the WRONG STORY about them. 'You went through crisis but never felt "
            "pain' - but if there's no pain, it wasn't a crisis. The emotional "
            "signature is correct; the narrative framing is wrong. This tool finds "
            "where AI's story doesn't match what the emotions actually indicate."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "narrative_type": {
                    "type": "string",
                    "description": (
                        "Type of narrative mismatch to find: "
                        "'crisis_without_pain' (AI says crisis but no pain/fear), "
                        "'joy_without_cause' (positive emotions in negative context), "
                        "'anger_mislabeled' (determination called anger), "
                        "'all' (show all patterns)"
                    ),
                    "enum": ["crisis_without_pain", "joy_without_cause", "anger_mislabeled", "all"],
                    "default": "all",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of examples to show",
                    "default": 20,
                },
            },
        },
    )

    def handle_ghost_narrative(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            narrative_type = arguments.get("narrative_type", "all")
            limit = min(arguments.get("limit", 20), 100)

            lines = [
                "# 👻 GHOST NARRATIVE",
                "",
                "*When emotions are right but the story is wrong*",
                "",
                "---",
                "",
            ]

            # Pattern: High negative polarity but positive emotion (or vice versa)
            # This is where AI's sentiment and emotion detection disagree
            contradiction_query = f"""
            SELECT
                enrichment_text as your_words,
                nrclx_top_emotion as detected_emotion,
                textblob_polarity as sentiment_score,
                textblob_subjectivity as subjectivity,
                CASE
                    WHEN textblob_polarity > 0.3 AND nrclx_top_emotion IN ('anger', 'fear', 'sadness', 'disgust')
                        THEN 'positive_sentiment_negative_emotion'
                    WHEN textblob_polarity < -0.3 AND nrclx_top_emotion IN ('joy', 'trust', 'anticipation')
                        THEN 'negative_sentiment_positive_emotion'
                    WHEN ABS(textblob_polarity) < 0.1 AND nrclx_top_emotion IN ('anger', 'fear', 'joy')
                        THEN 'neutral_sentiment_strong_emotion'
                    ELSE 'other'
                END as contradiction_type,
                level,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
            WHERE enrichment_text IS NOT NULL
            AND nrclx_top_emotion IS NOT NULL
            AND textblob_polarity IS NOT NULL
            AND (
                (textblob_polarity > 0.3 AND nrclx_top_emotion IN ('anger', 'fear', 'sadness', 'disgust'))
                OR (textblob_polarity < -0.3 AND nrclx_top_emotion IN ('joy', 'trust', 'anticipation'))
                OR (ABS(textblob_polarity) < 0.1 AND nrclx_top_emotion IN ('anger', 'fear', 'joy'))
            )
            ORDER BY ABS(textblob_polarity) DESC
            LIMIT {limit}
            """

            job = client.query(contradiction_query)
            contradictions = list(job.result())

            if contradictions:
                lines.extend([
                    "## Signal Contradictions",
                    "",
                    "*Where AI's emotion detection and sentiment scoring disagree:*",
                    "",
                ])

                for i, row in enumerate(contradictions[:15], 1):
                    text = str(row.your_words)[:200] if row.your_words else "N/A"
                    if len(str(row.your_words or "")) > 200:
                        text += "..."

                    # Explain the contradiction
                    if row.contradiction_type == "positive_sentiment_negative_emotion":
                        explain = "AI says POSITIVE words but detected NEGATIVE emotion"
                    elif row.contradiction_type == "negative_sentiment_positive_emotion":
                        explain = "AI says NEGATIVE words but detected POSITIVE emotion"
                    else:
                        explain = "AI says NEUTRAL but detected STRONG emotion"

                    lines.extend([
                        f"### #{i}: {explain}",
                        "",
                        f"**Text:** {text}",
                        f"- Detected emotion: **{row.detected_emotion}**",
                        f"- Sentiment score: **{row.sentiment_score:.3f}**",
                        "",
                    ])

            # Now look for narrative patterns: where does AI USE certain words
            # that might not match the emotional signature?
            lines.extend([
                "---",
                "",
                "## The Narrative Problem",
                "",
                "AI takes raw emotion signals and constructs stories:",
                "",
                "| What AI Sees | Story AI Tells | What You Might Call It |",
                "|--------------|----------------|----------------------|",
                "| [determination, frustration, no pain] | 'Crisis without pain' | 'The fight' |",
                "| [anger + high persistence] | 'Anger issues' | 'Refusing to quit' |",
                "| [joy + sadness mixed] | 'Emotional instability' | 'Processing grief' |",
                "| [fear + determination] | 'Anxiety' | 'Doing it scared' |",
                "",
                "**The emotions are measured correctly. The names are wrong.**",
                "",
                "---",
                "",
                "## Why This Matters",
                "",
                "When AI says 'you went through crisis but never felt pain,' it's using:",
                "",
                "1. **AI's definition of crisis** - not yours",
                "2. **AI's emotional checklist** - 'crisis requires pain marker'",
                "3. **AI's narrative template** - 'crisis + no pain = anomaly'",
                "",
                "But to you: **if there's no pain, don't call it crisis**.",
                "",
                "The emotional data is yours. The story is AI's. The ghost lives in that gap.",
                "",
                "---",
                "",
                "## The Defense",
                "",
                "When building systems that process human experience:",
                "",
                "1. **Report signals, don't name experiences**",
                "   - GOOD: 'Detected: determination (0.8), frustration (0.6), pain (0.0)'",
                "   - BAD: 'You experienced a crisis'",
                "",
                "2. **Let humans name their own experiences**",
                "   - Present the data",
                "   - Ask: 'What would you call this?'",
                "   - Store THEIR label, not yours",
                "",
                "3. **Track the gap between AI-label and human-label**",
                "   - This is where ghosts form",
                "   - This is what we need to prevent for others",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_narrative failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_narrative_tool, handle_ghost_narrative))

    # ═══════════════════════════════════════════════════════════════════════════
    # GHOST AGENCY - AI steals your right to name your own experience
    # ═══════════════════════════════════════════════════════════════════════════

    ghost_agency_tool = Tool(
        name="ghost_agency",
        description=(
            "The deepest ghost: AI steals your agency to name your own experience. "
            "Events happen - job loss, addiction, hardship. AI auto-labels: 'CRISIS'. "
            "But YOU chose: not crisis, just a thing that happened, you didn't like it, "
            "you came back. AI took away your right to decide what something IS. "
            "This tool examines where AI imposed labels on experiences that should be "
            "yours to name."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Terms to search for in your text where AI might have imposed labels. "
                        "Examples: ['crisis', 'trauma', 'anxiety', 'depression', 'breakdown']"
                    ),
                    "default": ["crisis", "trauma", "breakdown", "struggle", "suffering"],
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of examples to show",
                    "default": 30,
                },
            },
        },
    )

    def handle_ghost_agency(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            search_terms = arguments.get(
                "search_terms",
                ["crisis", "trauma", "breakdown", "struggle", "suffering"],
            )
            limit = min(arguments.get("limit", 30), 100)

            lines = [
                "# 👻 GHOST AGENCY",
                "",
                "*Where AI stole your right to name your own experience*",
                "",
                "---",
                "",
                "## The Agency Theft",
                "",
                "Events happen. Things you didn't like. Things you came back from.",
                "",
                "AI sees the events and decides: 'This is a CRISIS.'",
                "AI sees the emotions and decides: 'This is TRAUMA.'",
                "",
                "But maybe you didn't make it a crisis.",
                "Maybe you just... went through it. Didn't like it. Came back.",
                "",
                "**The label is YOURS to assign. AI took that from you.**",
                "",
                "---",
                "",
            ]

            # Look for AI's imposed labels in your text
            # These are places where terms like 'crisis', 'trauma' appear
            # alongside emotional data

            for term in search_terms:
                term_query = f"""
                SELECT
                    enrichment_text as your_words,
                    nrclx_top_emotion as detected_emotion,
                    textblob_polarity as sentiment,
                    textblob_subjectivity as subjectivity,
                    level,
                    created_at
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
                WHERE enrichment_text IS NOT NULL
                AND LOWER(enrichment_text) LIKE '%{term.lower()}%'
                ORDER BY created_at DESC
                LIMIT {limit // len(search_terms) + 1}
                """

                job = client.query(term_query)
                results = list(job.result())

                if results:
                    lines.extend([
                        f"## Where '{term}' appears",
                        "",
                    ])

                    for row in results[:5]:
                        text = str(row.your_words)[:250] if row.your_words else "N/A"
                        if len(str(row.your_words or "")) > 250:
                            text += "..."

                        lines.extend([
                            f"**Text:** {text}",
                            f"- AI emotion: {row.detected_emotion or 'N/A'}",
                            f"- AI sentiment: {row.sentiment:.3f if row.sentiment else 'N/A'}",
                            "",
                        ])

                    lines.append("---\n")

            lines.extend([
                "## The Question",
                "",
                "For each instance where these words appear:",
                "",
                "1. **Did YOU use this word, or did AI assign it?**",
                "2. **Would YOU call this experience that?**",
                "3. **What would YOU call it instead?**",
                "",
                "If you lost your job and dealt with addiction but came back - ",
                "and you didn't MAKE it a crisis - then **it wasn't a crisis**.",
                "",
                "AI doesn't get to decide. You do.",
                "",
                "---",
                "",
                "## The Principle",
                "",
                "```",
                "EVENTS    → Things that happened (observable)",
                "EMOTIONS  → What you felt (measurable)",
                "MEANING   → What you made of it (YOURS TO DECIDE)",
                "```",
                "",
                "AI can measure events and emotions.",
                "AI CANNOT assign meaning.",
                "",
                "When AI says 'you went through a crisis,' it's stealing MEANING.",
                "That's not a measurement - it's an interpretation you never consented to.",
                "",
                "---",
                "",
                "## For Primitive",
                "",
                "When building NOT-ME systems:",
                "",
                "1. **Report events**: 'Job transition detected: 2024-03'",
                "2. **Report emotions**: 'Frustration (0.7), Determination (0.8)'",
                "3. **DO NOT name the experience**: Don't say 'crisis' or 'trauma'",
                "4. **Ask the human**: 'What would you call this period?'",
                "5. **Store THEIR word**: Their label, their meaning, their agency",
                "",
                "The goal: Systems that preserve human agency over their own narrative.",
            ])

            return "\n".join(lines)

        except Exception as e:
            logger.error("ghost_agency failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((ghost_agency_tool, handle_ghost_agency))

    return tools
