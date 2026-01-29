#!/usr/bin/env python3
"""
Extract conversations from BigQuery entities_unified for Genesis training

Queries entities_unified to get:
- All L5 (message) level entities
- Grouped by conversation_id
- From specified data sources (claude_code, gemini_web, etc.)
- Exports to JSONL for metadata enrichment pipeline

Usage:
    python extract_from_entities_unified.py --sources claude_code,gemini_web --output raw_conversations.jsonl
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from google.cloud import bigquery


# BigQuery configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.entity_unified"


def extract_conversations(
    sources: List[str],
    output_path: Path,
    limit: int = None,
    min_messages: int = 5,
    max_messages: int = 1000
) -> Dict[str, Any]:
    """
    Extract conversations from entities_unified.
    
    Args:
        sources: List of source_pipeline values (e.g., ['claude_code', 'gemini_web'])
        output_path: Path to write JSONL output
        limit: Optional limit on number of conversations
        min_messages: Minimum messages per conversation to include
        max_messages: Maximum messages per conversation to include
        
    Returns:
        Statistics about extraction
    """
    client = bigquery.Client(project=PROJECT_ID)
    
    # Build source filter
    source_filter = ", ".join([f"'{s}'" for s in sources])
    
    # Query to get L5 messages grouped by conversation
    query = f"""
    WITH messages AS (
        SELECT
            conversation_id,
            entity_id,
            text,
            metadata,
            source_pipeline,
            source_file,
            content_date,
            source_message_timestamp,
            created_at,
            ROW_NUMBER() OVER (
                PARTITION BY conversation_id 
                ORDER BY source_message_timestamp, entity_id
            ) as message_index
        FROM `{TABLE_ID}`
        WHERE 
            level = 5  -- L5 messages only
            AND source_pipeline IN ({source_filter})
            AND text IS NOT NULL
            AND LENGTH(text) > 10
    ),
    conversation_stats AS (
        SELECT
            conversation_id,
            COUNT(*) as message_count,
            MIN(source_message_timestamp) as start_time,
            MAX(source_message_timestamp) as end_time,
            ANY_VALUE(source_pipeline) as source_pipeline
        FROM messages
        GROUP BY conversation_id
        HAVING 
            COUNT(*) >= {min_messages}
            AND COUNT(*) <= {max_messages}
    )
    SELECT
        m.conversation_id,
        m.entity_id,
        m.message_index,
        m.text,
        m.metadata,
        m.source_pipeline,
        m.source_file,
        m.content_date,
        m.source_message_timestamp,
        cs.message_count as conv_message_count,
        cs.start_time as conv_start_time,
        cs.end_time as conv_end_time
    FROM messages m
    INNER JOIN conversation_stats cs 
        ON m.conversation_id = cs.conversation_id
    ORDER BY 
        m.conversation_id, 
        m.message_index
    {f'LIMIT {limit}' if limit else ''}
    """
    
    print(f"Querying entities_unified for sources: {sources}")
    print(f"Min messages per conversation: {min_messages}")
    print(f"Max messages per conversation: {max_messages}")
    
    query_job = client.query(query)
    results = query_job.result()
    
    # Group messages by conversation
    conversations = {}
    total_messages = 0
    
    for row in results:
        conv_id = row.conversation_id
        
        if conv_id not in conversations:
            conversations[conv_id] = {
                "conversation_id": conv_id,
                "source_pipeline": row.source_pipeline,
                "message_count": row.conv_message_count,
                "start_time": row.conv_start_time.isoformat() if row.conv_start_time else None,
                "end_time": row.conv_end_time.isoformat() if row.conv_end_time else None,
                "messages": []
            }
        
        # Parse metadata JSON
        metadata = {}
        if row.metadata:
            try:
                metadata = json.loads(row.metadata) if isinstance(row.metadata, str) else row.metadata
            except:
                pass
        
        message = {
            "entity_id": row.entity_id,
            "message_index": row.message_index,
            "text": row.text,
            "role": metadata.get("role"),
            "message_type": metadata.get("message_type"),
            "text_original": metadata.get("text_original"),  # If Gemini cleaning was applied
            "source_file": row.source_file,
            "content_date": row.content_date.isoformat() if row.content_date else None,
            "timestamp": row.source_message_timestamp.isoformat() if row.source_message_timestamp else None,
            "metadata": metadata
        }
        
        conversations[conv_id]["messages"].append(message)
        total_messages += 1
    
    # Write to JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for conv in conversations.values():
            f.write(json.dumps(conv) + '\n')
    
    # Statistics
    stats = {
        "timestamp": datetime.now().isoformat(),
        "sources": sources,
        "total_conversations": len(conversations),
        "total_messages": total_messages,
        "avg_messages_per_conv": total_messages / len(conversations) if conversations else 0,
        "output_file": str(output_path),
        "query_bytes_processed": query_job.total_bytes_processed,
        "query_bytes_billed": query_job.total_bytes_billed,
    }
    
    print(f"\n✅ Extraction complete!")
    print(f"   Conversations: {stats['total_conversations']:,}")
    print(f"   Messages: {stats['total_messages']:,}")
    print(f"   Avg messages/conv: {stats['avg_messages_per_conv']:.1f}")
    print(f"   Output: {output_path}")
    print(f"   BigQuery bytes billed: {stats['query_bytes_billed']:,}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Extract conversations from entities_unified")
    parser.add_argument(
        "--sources",
        type=str,
        required=True,
        help="Comma-separated list of sources (e.g., claude_code,gemini_web)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/genesis_corpus/raw_conversations.jsonl"),
        help="Output JSONL file path"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of conversations (for testing)"
    )
    parser.add_argument(
        "--min-messages",
        type=int,
        default=5,
        help="Minimum messages per conversation"
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=1000,
        help="Maximum messages per conversation"
    )
    
    args = parser.parse_args()
    
    sources = [s.strip() for s in args.sources.split(',')]
    
    stats = extract_conversations(
        sources=sources,
        output_path=args.output,
        limit=args.limit,
        min_messages=args.min_messages,
        max_messages=args.max_messages
    )
    
    # Write stats
    stats_path = args.output.parent / f"{args.output.stem}_stats.json"
    with open(stats_path, 'w') as f:
        json.dumps(stats, indent=2, fp=f)
    
    print(f"   Stats: {stats_path}")


if __name__ == "__main__":
    main()
