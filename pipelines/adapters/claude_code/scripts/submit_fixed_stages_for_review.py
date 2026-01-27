#!/usr/bin/env python3
"""Submit fixed pipeline stages for peer review.

This script submits all recently fixed stages (6, 7, 8, 9, 10) to the peer review system.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.governance.peer_review_service import review_object

# Stages to review
STAGES_TO_REVIEW = [0, 6, 7, 8, 9, 10]

def submit_stage_for_review(stage_num: int) -> bool:
    """Submit a stage for peer review."""
    stage_file = project_root / f"pipelines/claude_code/scripts/stage_{stage_num}/claude_code_stage_{stage_num}.py"
    
    if not stage_file.exists():
        print(f"❌ Stage {stage_num} file not found: {stage_file}")
        return False
    
    print(f"\n{'='*80}")
    print(f"Submitting Stage {stage_num} for peer review...")
    print(f"{'='*80}")
    print(f"File: {stage_file}")
    
    try:
        result = review_object(
            object_path=stage_file,
            review_type="certification_system",
            criteria="production_readiness",
        )
        
        print(f"\n✅ Review completed: {result.review_id}")
        print(f"   Status: {result.status.value}")
        print(f"   Successful reviews: {len(result.successful_reviews)}/{len(result.all_reviews)}")
        
        if result.status.value == "completed":
            print(f"   ✅ All reviews completed successfully")
            return True
        elif result.status.value == "partial":
            print(f"   ⚠️  Some reviews failed (partial success)")
            return True
        else:
            print(f"   ❌ All reviews failed")
            return False
            
    except Exception as e:
        print(f"❌ Error reviewing stage {stage_num}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Submit all fixed stages for review."""
    print("="*80)
    print("SUBMITTING FIXED PIPELINE STAGES FOR PEER REVIEW")
    print("="*80)
    print(f"Stages to review: {', '.join(map(str, STAGES_TO_REVIEW))}")
    print()
    
    results = {}
    for stage_num in STAGES_TO_REVIEW:
        success = submit_stage_for_review(stage_num)
        results[stage_num] = success
    
    print("\n" + "="*80)
    print("REVIEW SUMMARY")
    print("="*80)
    
    successful = [s for s, success in results.items() if success]
    failed = [s for s, success in results.items() if not success]
    
    if successful:
        print(f"✅ Successfully submitted: {', '.join(map(str, successful))}")
    if failed:
        print(f"❌ Failed to submit: {', '.join(map(str, failed))}")
    
    print(f"\nTotal: {len(successful)}/{len(STAGES_TO_REVIEW)} stages submitted successfully")
    
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
