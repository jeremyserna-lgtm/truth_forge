#!/usr/bin/env python3
"""
Factory Leaderboard - View results from all nodes

Shows:
- Best pattern across all nodes
- Per-node performance
- All experiments ranked by Jeremy Arc

Usage:
    python leaderboard.py
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_all_results(results_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load results from all nodes."""
    results_by_node = {}
    
    for results_file in results_dir.glob("*_results.jsonl"):
        node_name = results_file.stem.replace("_results", "")
        
        results = []
        with open(results_file, 'r') as f:
            for line in f:
                results.append(json.loads(line))
        
        results_by_node[node_name] = results
    
    return results_by_node


def display_leaderboard(results_dir: Path = Path("/shared/factory/results")):
    """Display leaderboard of all experiments."""
    print(f"{'='*80}")
    print(f"THE EMPIRE FINE-TUNING FACTORY - LEADERBOARD")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Load results
    results_by_node = load_all_results(results_dir)
    
    if not results_by_node:
        print("⚠️  No results found yet")
        return
    
    # Find global best
    global_best_arc = 0.0
    global_best_node = None
    global_best_pattern = None
    
    for node, results in results_by_node.items():
        if results:
            latest = results[-1]
            if latest["best_jeremy_arc"] > global_best_arc:
                global_best_arc = latest["best_jeremy_arc"]
                global_best_node = node
                global_best_pattern = latest["best_pattern"]
    
    # Display global best
    print(f"🏆 GLOBAL BEST")
    print(f"   Node: {global_best_node}")
    print(f"   Jeremy Arc: {global_best_arc:.1f}%")
    print(f"   Pattern: {global_best_pattern.get('pattern_name', 'unknown')}")
    print()
    
    # Per-node status
    print(f"📊 PER-NODE STATUS")
    print(f"{'-'*80}")
    
    for node in sorted(results_by_node.keys()):
        results = results_by_node[node]
        if not results:
            continue
        
        latest = results[-1]
        print(f"  {node.upper()}")
        print(f"    Iterations: {latest['iteration']}")
        print(f"    Best Arc: {latest['best_jeremy_arc']:.1f}%")
        print(f"    Running: {latest['running_experiments']} experiments")
        print()
    
    print(f"{'='*80}")


def main():
    display_leaderboard()


if __name__ == "__main__":
    main()
