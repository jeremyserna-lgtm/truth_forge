#!/usr/bin/env python3
"""
Submit ALL pipeline stages for peer review in parallel.

INDUSTRY STANDARDS:
- Bounded concurrency (default: 8 workers) to prevent resource exhaustion
- Proper timeouts to prevent deadlocks
- Comprehensive error handling and logging
- Complete transparency - reviewers see entire files with no limits

Each stage is submitted to all models (Gemini, Claude, ChatGPT) in parallel.
All stages are submitted concurrently with proper resource management.

CRITICAL DISTINCTION:
- Script execution: Has proper limits (bounded concurrency, timeouts) - industry standards
- Reviewer visibility: NO LIMITS - reviewers see entire files, all code, all parameters
"""

import concurrent.futures
import logging
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.governance.peer_review_service.service import review_object

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def submit_stage(stage_num: int) -> Dict:
    """Submit a single stage for review.
    
    IMPORTANT: This function has proper error handling and validation (industry standards).
    However, the review_object() function ensures reviewers see the ENTIRE file with
    no truncation, no chunking, no filtering - reviewers have NO LIMITS on what they can see.
    
    Args:
        stage_num: Stage number (0-10, or any valid stage number)
        
    Returns:
        Dict with stage info and review result
    """
    # Validate stage number to prevent path traversal
    try:
        stage_num_int = int(stage_num)
        if stage_num_int < 0:
            raise ValueError(f"Invalid stage number: {stage_num_int} (must be >= 0)")
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid stage number: {stage_num}")
        return {
            "stage": stage_num,
            "status": "error",
            "error": f"Invalid stage number: {e}",
        }
    
    stage_path = project_root / f"pipelines/claude_code/scripts/stage_{stage_num}/claude_code_stage_{stage_num}.py"
    
    # Resolve path to prevent path traversal
    try:
        stage_path = stage_path.resolve()
        if not stage_path.is_relative_to(project_root.resolve()):
            raise ValueError(f"Path traversal detected: {stage_path}")
    except (ValueError, OSError) as e:
        logger.error(f"Invalid path for stage {stage_num}: {e}")
        return {
            "stage": stage_num,
            "status": "error",
            "error": f"Invalid path: {e}",
        }
    
    if not stage_path.exists():
        logger.warning(f"Stage {stage_num} file not found: {stage_path}")
        return {
            "stage": stage_num,
            "status": "not_found",
            "error": f"File not found: {stage_path}",
        }
    
    try:
        file_size = stage_path.stat().st_size
        logger.info(f"Submitting Stage {stage_num} ({file_size:,} bytes) - ENTIRE FILE to reviewers")
        
        # Submit for review - review_object ensures reviewers see the ENTIRE file (no limits on visibility)
        # The _auto_discover_related_files() function now automatically includes:
        # - Verification scripts (verify_stage_X.py)
        # - Trust reports (FIDELITY_REPORT.md, HONESTY_REPORT.md, TRUST_REPORT.md)
        # But the script itself has proper limits (timeouts, bounded concurrency, error handling)
        result = review_object(
            object_path=stage_path,
            review_type="code",
            criteria="production_readiness"
        )
        
        return {
            "stage": stage_num,
            "status": "submitted",
            "review_id": result.review_id,
            "file_size": file_size,
            "models_used": [r.model.value for r in result.successful_reviews],
            "status_value": result.status.value,
            "total_reviews": len(result.all_reviews),
            "successful_reviews": len(result.successful_reviews),
            "failed_reviews": len(result.failed_reviews),
        }
        
    except Exception as e:
        logger.error(f"Error submitting stage {stage_num}: {e}", exc_info=True)
        return {
            "stage": stage_num,
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def submit_all_stages_parallel(
    stages: Optional[List[int]] = None,
    max_workers: int = 8,
    submission_timeout_seconds: int = 300
) -> Dict[str, List[Dict]]:
    """Submit all pipeline stages for review in parallel.
    
    INDUSTRY STANDARDS:
    - Uses ThreadPoolExecutor with bounded concurrency (default: 8 workers)
    - Proper timeouts to prevent deadlocks
    - Comprehensive error handling for each submission
    - Complete result tracking and reporting
    
    IMPORTANT: This script has proper limits on execution (timeouts, bounded concurrency).
    However, reviewers themselves have NO LIMITS on what they can see - they see the entire file.
    
    Each stage is submitted concurrently. The review service itself
    handles parallel model execution internally (Gemini, Claude, ChatGPT all run in parallel).
    
    Args:
        stages: List of stage numbers to submit (default: 0-10)
        max_workers: Maximum concurrent thread workers (default: 8 - industry standard)
        submission_timeout_seconds: Timeout per submission in seconds (default: 300 = 5 minutes)
        
    Returns:
        Dict with 'submitted', 'not_found', 'errors' lists
    """
    if stages is None:
        stages = list(range(17))  # Stages 0-16 by default
    
    logger.info("=" * 80)
    logger.info("SUBMITTING ALL PIPELINE STAGES FOR PEER REVIEW")
    logger.info("=" * 80)
    logger.info(f"Stages: {stages}")
    logger.info(f"Each stage will be reviewed by: Gemini, Claude, ChatGPT (all in parallel)")
    logger.info(f"Max workers: {max_workers} (bounded concurrency - industry standard)")
    logger.info(f"Submission timeout: {submission_timeout_seconds}s per stage")
    logger.info("=" * 80)
    
    print("=" * 80)
    print("SUBMITTING ALL PIPELINE STAGES FOR PEER REVIEW")
    print("=" * 80)
    print(f"Stages: {stages}")
    print(f"Each stage will be reviewed by: Gemini, Claude, ChatGPT (all in parallel)")
    print(f"Max concurrent submissions: {max_workers}")
    print(f"Timeout per submission: {submission_timeout_seconds}s")
    print("=" * 80)
    print()
    
    # Submit all stages in parallel with BOUNDED concurrency (industry standard)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all stages immediately - no batching, no limits
        future_to_stage = {
            executor.submit(submit_stage, stage_num): stage_num
            for stage_num in stages
        }
        
        # Collect results as they complete with proper timeouts (industry standard)
        results = []
        total_timeout = submission_timeout_seconds * len(stages)  # Total timeout for all stages
        
        try:
            for future in concurrent.futures.as_completed(future_to_stage, timeout=total_timeout):
                stage_num = future_to_stage[future]
                try:
                    # Get result with per-future timeout
                    result = future.result(timeout=submission_timeout_seconds)
                    results.append(result)
                    
                    if result["status"] == "submitted":
                        print(f"✅ Stage {result['stage']}: Submitted (Review ID: {result['review_id']})")
                        print(f"   File size: {result['file_size']:,} bytes")
                        print(f"   Models: {', '.join(result['models_used'])}")
                        print(f"   Status: {result['status_value']}")
                        print(f"   Reviews: {result['successful_reviews']}/{result['total_reviews']} successful")
                    elif result["status"] == "not_found":
                        print(f"⚠️  Stage {result['stage']}: File not found")
                    else:
                        print(f"❌ Stage {result['stage']}: Error - {result.get('error', 'Unknown')}")
                    print()
                    
                except concurrent.futures.TimeoutError:
                    logger.error(f"Stage {stage_num} timed out after {submission_timeout_seconds}s")
                    print(f"❌ Stage {stage_num}: Timed out after {submission_timeout_seconds}s")
                    results.append({
                        "stage": stage_num,
                        "status": "timeout",
                        "error": f"Submission timed out after {submission_timeout_seconds} seconds",
                    })
                except Exception as e:
                    logger.error(f"Exception processing stage {stage_num}: {e}", exc_info=True)
                    print(f"❌ Stage {stage_num}: Exception - {e}")
                    results.append({
                        "stage": stage_num,
                        "status": "exception",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })
        
        except concurrent.futures.TimeoutError:
            logger.error(f"Overall submission timed out after {total_timeout}s")
            print(f"\n⚠️  Overall submission timed out after {total_timeout}s")
            print("Some stages may still be processing. Check individual review statuses.")
            # Collect any results we have so far
            for future, stage_num in future_to_stage.items():
                if future.done():
                    try:
                        result = future.result()
                        if result not in results:
                            results.append(result)
                    except Exception:
                        pass
    
    # Categorize results
    submitted = [r for r in results if r["status"] == "submitted"]
    not_found = [r for r in results if r["status"] == "not_found"]
    errors = [r for r in results if r["status"] in ["error", "exception"]]
    
    # Summary
    print("=" * 80)
    print("SUBMISSION SUMMARY")
    print("=" * 80)
    
    print(f"✅ Successfully submitted: {len(submitted)} stages")
    print(f"⚠️  Not found: {len(not_found)} stages")
    print(f"❌ Errors: {len(errors)} stages")
    print()
    
    if submitted:
        print("Review IDs:")
        for r in sorted(submitted, key=lambda x: x["stage"]):
            print(f"  Stage {r['stage']}: {r['review_id']}")
    
    if errors:
        print("\nErrors:")
        for r in sorted(errors, key=lambda x: x["stage"]):
            print(f"  Stage {r['stage']}: {r.get('error', 'Unknown error')}")
    
    print()
    logger.info("=" * 80)
    logger.info("All reviews are processing in parallel.")
    logger.info("Check review status with: python3 scripts/peer_review.py get <review_id>")
    logger.info("=" * 80)
    
    print("=" * 80)
    print("All reviews are processing in parallel.")
    print("Check review status with: python3 scripts/peer_review.py get <review_id>")
    print("=" * 80)
    
    return {
        "submitted": submitted,
        "not_found": not_found,
        "errors": errors,
    }


if __name__ == "__main__":
    # Submit all stages (0-10) with proper limits (bounded concurrency, timeouts)
    # But reviewers see everything - no limits on what they can review
    submit_all_stages_parallel()
