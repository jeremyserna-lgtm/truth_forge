#!/usr/bin/env python3
"""
Relationship Extraction Pipeline v2
The Spine / Truth Forge

Extracts relationships WITHIN conversations, then across them.
Uses LOCAL LLM via Ollama (no cloud API needed).
"""

import asyncio
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import aiohttp
from dotenv import load_dotenv


load_dotenv()

from google.cloud import bigquery


sys.path.insert(0, str(Path(__file__).parent))

from spine.graph import Entity, Relationship, RelationshipType


# ═══════════════════════════════════════════════════════════════════════════════
# LOCAL LLM CLIENT (Ollama)
# ═══════════════════════════════════════════════════════════════════════════════


class OllamaClient:
    """Simple async client for Ollama local inference."""

    def __init__(self, model: str = "qwen2.5-coder:32b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate(self, prompt: str, max_tokens: int = 1000) -> str | None:
        """Generate text using local Ollama model."""
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": max_tokens},
                    },
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
        except Exception as e:
            print(f"   Ollama error: {e}")
        return None


class SmartRelationshipPipeline:
    """
    Smarter relationship extraction that leverages conversation structure.
    """

    def __init__(self, model: str = "qwen2.5-coder:32b"):
        self.bq = bigquery.Client()
        self.project = self.bq.project

        # Local LLM via Ollama
        self.llm = OllamaClient(model=model)
        self.model_name = model

        self.stats = {
            "conversations_processed": 0,
            "entities_processed": 0,
            "relationships_found": 0,
            "relationships_inserted": 0,
        }

    def get_conversations_with_entities(self, limit: int = 10) -> dict[str, list[Entity]]:
        """Get entities grouped by conversation."""

        query = f"""
        SELECT 
            conversation_id,
            entity_id,
            text,
            level,
            entity_mode,
            turn_id,
            created_at
        FROM `{self.project}.spine.entity_unified`
        WHERE text IS NOT NULL
        AND LENGTH(text) > 30
        AND LENGTH(text) < 2000
        AND level >= 4
        AND conversation_id IS NOT NULL
        AND conversation_id IN (
            SELECT conversation_id
            FROM `{self.project}.spine.entity_unified`
            WHERE level >= 4 AND text IS NOT NULL
            GROUP BY conversation_id
            HAVING COUNT(*) BETWEEN 5 AND 50
            LIMIT {limit}
        )
        ORDER BY conversation_id, created_at
        """

        results = self.bq.query(query).result()

        conversations = defaultdict(list)
        for row in results:
            entity = Entity(
                canonical_id=row.entity_id,
                content=row.text,
                entity_type=f"L{row.level}",
                source=row.conversation_id or "",
                timestamp=str(row.created_at) if row.created_at else "",
            )
            # Store additional metadata
            entity.turn_id = row.turn_id
            entity.mode = row.entity_mode
            conversations[row.conversation_id].append(entity)

        return dict(conversations)

    def extract_within_conversation(self, entities: list[Entity]) -> list[Relationship]:
        """Extract relationships within a single conversation."""

        relationships = []

        # Sequential turns are FOLLOWS relationships
        for i in range(len(entities) - 1):
            e1, e2 = entities[i], entities[i + 1]

            # Skip if same turn
            if hasattr(e1, "turn_id") and hasattr(e2, "turn_id"):
                if e1.turn_id == e2.turn_id:
                    continue

            # FOLLOWS relationship
            relationships.append(
                Relationship(
                    id=str(uuid.uuid4()),
                    source_id=e1.canonical_id,
                    target_id=e2.canonical_id,
                    relationship_type=RelationshipType.TEMPORALLY_FOLLOWS.value,
                    confidence=1.0,
                    weight=1.0,
                    extracted_by="conversation_sequence",
                    source_context=e1.content[:200],
                    target_context=e2.content[:200],
                )
            )

        # Look for references (mentions, quotes)
        for i, e1 in enumerate(entities):
            for j, e2 in enumerate(entities):
                if i == j:
                    continue

                # Check for quotes or references
                if self._contains_reference(e1.content, e2.content):
                    relationships.append(
                        Relationship(
                            id=str(uuid.uuid4()),
                            source_id=e1.canonical_id,
                            target_id=e2.canonical_id,
                            relationship_type=RelationshipType.REFERENCES.value,
                            confidence=0.8,
                            weight=0.8,
                            extracted_by="reference_detection",
                            source_context=e1.content[:200],
                            target_context=e2.content[:200],
                        )
                    )

        # Look for contradictions
        for i, e1 in enumerate(entities):
            for j in range(i + 1, len(entities)):
                e2 = entities[j]
                if self._may_contradict(e1.content, e2.content):
                    relationships.append(
                        Relationship(
                            id=str(uuid.uuid4()),
                            source_id=e1.canonical_id,
                            target_id=e2.canonical_id,
                            relationship_type=RelationshipType.CONTRADICTS.value,
                            confidence=0.6,
                            weight=0.6,
                            extracted_by="contradiction_heuristic",
                            source_context=e1.content[:200],
                            target_context=e2.content[:200],
                        )
                    )

        return relationships

    def _contains_reference(self, content1: str, content2: str) -> bool:
        """Check if content1 references content2."""
        c1_lower = content1.lower()

        # Check for direct quotes
        if '"' in c1_lower:
            # Extract quoted text and check if it's in content2
            import re

            quotes = re.findall(r'"([^"]+)"', c1_lower)
            for quote in quotes:
                if len(quote) > 10 and quote in content2.lower():
                    return True

        # Check for "you said" patterns
        reference_patterns = [
            "you said",
            "you mentioned",
            "earlier you",
            "as you noted",
            "your point about",
        ]
        for pattern in reference_patterns:
            if pattern in c1_lower:
                return True

        return False

    def _may_contradict(self, content1: str, content2: str) -> bool:
        """Check if two statements might contradict."""
        c1_lower = content1.lower()
        c2_lower = content2.lower()

        # Look for negation patterns
        negation_pairs = [
            ("is correct", "is incorrect"),
            ("is true", "is false"),
            ("i agree", "i disagree"),
            ("yes", "no"),
            ("always", "never"),
            ("can", "cannot"),
            ("will", "won't"),
        ]

        for pos, neg in negation_pairs:
            if (pos in c1_lower and neg in c2_lower) or (neg in c1_lower and pos in c2_lower):
                return True

        # Check for "but" or "however" that might signal contradiction
        contradiction_signals = ["actually,", "however,", "but ", "on the contrary"]
        for signal in contradiction_signals:
            if signal in c2_lower and len(c1_lower) > 20 and len(c2_lower) > 20:
                # More likely if they share some words
                words1 = set(c1_lower.split())
                words2 = set(c2_lower.split())
                common = words1 & words2
                if len(common) > 3:
                    return True

        return False

    async def extract_with_llm(self, entities: list[Entity]) -> list[Relationship]:
        """Use LOCAL LLM (Ollama) to find semantic relationships."""

        if len(entities) < 2:
            return []

        # Create a sample passage from entities
        passage = "\n\n".join([f"[{i}] {e.content[:300]}" for i, e in enumerate(entities[:10])])

        prompt = f"""Analyze these text segments and identify relationships between them.
For each relationship found, output a JSON object with:
- source_index: int (0-based index of source segment)
- target_index: int (0-based index of target segment)  
- relationship: one of [SUPPORTS, CONTRADICTS, EXTENDS, EXEMPLIFIES, DEFINES]
- confidence: float 0-1
- reason: brief explanation

TEXT SEGMENTS:
{passage}

Output ONLY a JSON array of relationships. If no clear relationships, output [].
"""

        try:
            response = await self.llm.generate(prompt)

            if not response:
                return []

            import json
            import re

            # Extract JSON from response
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                rels = json.loads(json_match.group())

                result = []
                for r in rels:
                    src_idx = r.get("source_index", 0)
                    tgt_idx = r.get("target_index", 1)

                    if src_idx < len(entities) and tgt_idx < len(entities):
                        result.append(
                            Relationship(
                                id=str(uuid.uuid4()),
                                source_id=entities[src_idx].canonical_id,
                                target_id=entities[tgt_idx].canonical_id,
                                relationship_type=r.get("relationship", "RELATED_TO"),
                                confidence=r.get("confidence", 0.7),
                                weight=r.get("confidence", 0.7),
                                extracted_by=f"ollama_{self.model_name}",
                                source_context=entities[src_idx].content[:200],
                                target_context=entities[tgt_idx].content[:200],
                            )
                        )

                return result
        except Exception as e:
            print(f"   LLM extraction error: {e}")

        return []

    def insert_relationships(self, relationships: list[Relationship]) -> int:
        """Insert relationships into BigQuery."""

        if not relationships:
            return 0

        # Deduplicate by source_id + target_id
        seen = set()
        unique = []
        for rel in relationships:
            key = (rel.source_id, rel.target_id, rel.relationship_type)
            if key not in seen:
                seen.add(key)
                unique.append(rel)

        table_id = f"{self.project}.spine.entity_relationships"

        rows = []
        for rel in unique:
            rows.append(
                {
                    "id": rel.id,
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "relationship_type": rel.relationship_type,
                    "confidence": rel.confidence,
                    "weight": rel.weight,
                    "extracted_by": rel.extracted_by,
                    "extracted_at": datetime.utcnow().isoformat(),
                    "source_context": rel.source_context,
                    "target_context": rel.target_context,
                    "verified": False,
                }
            )

        errors = self.bq.insert_rows_json(table_id, rows)

        if errors:
            print(f"   Insert errors: {len(errors)}")
            return len(rows) - len(errors)

        return len(rows)

    async def run(self, num_conversations: int = 10, use_llm: bool = True):
        """Run the extraction pipeline."""

        print("═" * 60)
        print("       SPINE RELATIONSHIP EXTRACTION v2")
        print("       (Using LOCAL models — no cloud API)")
        print("═" * 60)
        print(f"Project: {self.project}")
        print(f"Conversations: {num_conversations}")
        print(f"LLM: {self.model_name if use_llm else 'Pattern matching only'} (Ollama)")
        print()

        # Step 1: Get conversations
        print("1. FETCHING CONVERSATIONS")
        print("-" * 40)

        conversations = self.get_conversations_with_entities(num_conversations)
        print(f"   Found: {len(conversations)} conversations")

        total_entities = sum(len(e) for e in conversations.values())
        print(f"   Total entities: {total_entities}")
        self.stats["entities_processed"] = total_entities
        self.stats["conversations_processed"] = len(conversations)

        if not conversations:
            print("   No conversations found!")
            return

        # Step 2: Extract within each conversation
        print()
        print("2. EXTRACTING RELATIONSHIPS")
        print("-" * 40)

        all_relationships = []

        for i, (conv_id, entities) in enumerate(conversations.items()):
            print(f"   [{i + 1}/{len(conversations)}] {conv_id[:20]}... ({len(entities)} entities)")

            # Structural relationships
            rels = self.extract_within_conversation(entities)
            all_relationships.extend(rels)

            # LLM relationships
            if use_llm and self.llm:
                llm_rels = await self.extract_with_llm(entities)
                all_relationships.extend(llm_rels)

        print(f"   Total found: {len(all_relationships)} relationships")
        self.stats["relationships_found"] = len(all_relationships)

        if all_relationships:
            # Group by type
            by_type = {}
            for rel in all_relationships:
                by_type[rel.relationship_type] = by_type.get(rel.relationship_type, 0) + 1

            print("   By Type:")
            for rel_type, count in sorted(by_type.items(), key=lambda x: -x[1]):
                print(f"     {rel_type}: {count}")

        # Step 3: Insert into BigQuery
        print()
        print("3. INSERTING INTO BIGQUERY")
        print("-" * 40)

        inserted = self.insert_relationships(all_relationships)
        print(f"   Inserted: {inserted} relationships")
        self.stats["relationships_inserted"] = inserted

        # Step 4: Verify
        print()
        print("4. FINAL COUNT")
        print("-" * 40)

        query = f"""
        SELECT relationship_type, COUNT(*) as count
        FROM `{self.project}.spine.entity_relationships`
        GROUP BY relationship_type
        ORDER BY count DESC
        """

        results = self.bq.query(query).result()
        total = 0
        for row in results:
            print(f"   {row.relationship_type}: {row.count}")
            total += row.count

        print(f"   Total in entity_relationships: {total}")

        # Summary
        print()
        print("═" * 60)
        print("       EXTRACTION COMPLETE")
        print("═" * 60)
        print(f"Conversations: {self.stats['conversations_processed']}")
        print(f"Entities: {self.stats['entities_processed']}")
        print(f"Relationships Found: {self.stats['relationships_found']}")
        print(f"Relationships Inserted: {self.stats['relationships_inserted']}")


async def main():
    pipeline = SmartRelationshipPipeline()
    await pipeline.run(num_conversations=50, use_llm=True)


if __name__ == "__main__":
    asyncio.run(main())
