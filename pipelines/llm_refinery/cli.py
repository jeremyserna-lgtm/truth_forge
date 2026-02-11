#!/usr/bin/env python3
"""CLI for processing conversations with LLM Refinery.

Usage:
    # Process all conversations and load to BigQuery
    python -m pipelines.llm_refinery.cli --input data/web_exports/claude_web/conversations.json
    
    # Process with specific model
    python -m pipelines.llm_refinery.cli --input data.json --model llama4:scout
    
    # Process subset with full depth
    python -m pipelines.llm_refinery.cli --input data.json --limit 5 --min-level 2
    
    # Quick processing (L5 only)
    python -m pipelines.llm_refinery.cli --input data.json --min-level 5
    
    # Skip BigQuery loading (local only)
    python -m pipelines.llm_refinery.cli --input data.json --no-bigquery
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, UTC

from .processor import LLMRefineryProcessor, ProcessorConfig
from .bigquery_loader import (
    get_bigquery_client, 
    load_jsonl_file, 
    load_to_bigquery,
    FULL_TABLE_ID,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process conversations into L2-L8 hierarchy using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process Claude web conversations
    python -m pipelines.llm_refinery.cli \\
        --input data/web_exports/claude_web/conversations.json
    
    # Use Llama4 Scout for highest quality
    python -m pipelines.llm_refinery.cli \\
        --input data.json --model llama4:scout
    
    # Quick processing (messages only, no deep analysis)
    python -m pipelines.llm_refinery.cli \\
        --input data.json --min-level 5 --limit 10
        """,
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Path to conversations.json file",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory (default: data/llm_refinery_output)",
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="qwen2.5-coder:32b",
        help="Ollama model to use (default: qwen2.5-coder:32b)",
    )
    
    parser.add_argument(
        "--min-level",
        type=int,
        default=5,
        choices=[2, 3, 4, 5],
        help="Minimum level to process (2=words, 5=messages only)",
    )
    
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of conversations to process",
    )
    
    parser.add_argument(
        "--ollama-host",
        type=str,
        default="http://localhost:11434",
        help="Ollama API host",
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Timeout for LLM calls in seconds",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    parser.add_argument(
        "--no-bigquery",
        action="store_true",
        help="Skip BigQuery loading (process locally only)",
    )
    
    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Number of conversations to skip at start",
    )
    
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing even if a conversation fails",
    )
    
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Configure processor
    config = ProcessorConfig(
        ollama_host=args.ollama_host,
        model=args.model,
        timeout=args.timeout,
        min_level=args.min_level,
        output_dir=args.output or Path("data/llm_refinery_output"),
    )
    
    logger.info("=" * 60)
    logger.info("LLM REFINERY PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Input:     {args.input}")
    logger.info(f"Model:     {config.model}")
    logger.info(f"Min Level: L{config.min_level}")
    logger.info(f"Output:    {config.output_dir}")
    logger.info(f"BigQuery:  {'DISABLED' if args.no_bigquery else FULL_TABLE_ID}")
    logger.info("=" * 60)
    
    # Initialize BigQuery client if loading enabled
    bq_client = None
    if not args.no_bigquery:
        try:
            bq_client = get_bigquery_client()
            logger.info(f"BigQuery connected: {FULL_TABLE_ID}")
        except Exception as e:
            logger.warning(f"BigQuery connection failed: {e}")
            logger.warning("Continuing with local-only processing")
            args.no_bigquery = True
    
    # Check Ollama connectivity
    import httpx
    try:
        response = httpx.get(f"{config.ollama_host}/api/tags", timeout=5.0)
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        logger.info(f"Ollama models available: {', '.join(model_names)}")
        
        if config.model not in model_names and not any(config.model in m for m in model_names):
            logger.warning(f"Model '{config.model}' may not be available")
    except Exception as e:
        logger.error(f"Cannot connect to Ollama at {config.ollama_host}: {e}")
        return 1
    
    # Process conversations
    processor = LLMRefineryProcessor(config)
    
    try:
        processed = 0
        total_bq_loaded = 0
        all_entities_path = config.output_dir / "all_entities.jsonl"
        
        skipped = 0
        failed = 0
        
        with open(all_entities_path, "w", encoding="utf-8") as all_f:
            for conv in processor.process_file(args.input, skip=args.skip):
                try:
                    # Export individual conversation
                    conv_path = processor.export_entities(conv)
                    logger.info(f"  Exported: {conv_path.name}")
                    
                    # Also write to combined file
                    with open(conv_path, "r", encoding="utf-8") as conv_f:
                        all_f.write(conv_f.read())
                    
                    # Load to BigQuery immediately after processing
                    if bq_client and not args.no_bigquery:
                        records = load_jsonl_file(conv_path)
                        loaded, errors = load_to_bigquery(bq_client, records)
                        if errors:
                            logger.warning(f"  BigQuery errors: {errors[:2]}")
                        else:
                            logger.info(f"  → BigQuery: {loaded} entities")
                            total_bq_loaded += loaded
                    
                    processed += 1
                    
                except Exception as e:
                    failed += 1
                    logger.error(f"  FAILED: {e}")
                    if not args.continue_on_error:
                        raise
                    logger.info("  Continuing to next conversation...")
                    continue
                
                if args.limit and processed >= args.limit:
                    logger.info(f"Reached limit of {args.limit} conversations")
                    break
        
        # Print summary
        stats = processor.stats
        logger.info("=" * 60)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Conversations: {stats['conversations_processed']}")
        logger.info(f"Messages:      {stats['messages_processed']}")
        logger.info(f"LLM Calls:     {stats['llm_calls']}")
        logger.info(f"Errors:        {stats['errors']}")
        logger.info(f"Skipped:       {skipped}")
        logger.info(f"Failed:        {failed}")
        logger.info(f"Local Output:  {all_entities_path}")
        if not args.no_bigquery:
            logger.info(f"BigQuery:      {total_bq_loaded} entities → {FULL_TABLE_ID}")
        logger.info("=" * 60)
        
        # Write stats
        stats_path = config.output_dir / "processing_stats.json"
        with open(stats_path, "w") as f:
            json.dump({
                "timestamp": datetime.now(UTC).isoformat(),
                "input_file": str(args.input),
                "model": config.model,
                "min_level": config.min_level,
                "bigquery_loaded": total_bq_loaded if not args.no_bigquery else 0,
                "bigquery_table": FULL_TABLE_ID if not args.no_bigquery else None,
                **stats,
            }, f, indent=2)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Processing failed: {e}")
        return 1
    finally:
        processor.close()


if __name__ == "__main__":
    sys.exit(main())
