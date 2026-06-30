#!/usr/bin/env python3
"""Split large tasks into micro-tasks (≤ 3 points each).

Reduces token usage by making each task small enough for Haiku to handle,
avoiding expensive Sonnet/Opus calls for task implementation.

Usage:
    python micro_plan.py --id PROJECT_ID
    python micro_plan.py --id PROJECT_ID --keep-originals

Output:
    Updated backlog where tasks > 3 points are split into subtasks.
    Each subtask: 1–3 points, inherits spec_refs/layer/test_command from parent.
"""
import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


MICRO_TASK_RULES = {
    "0": {"max": 1, "desc": "scaffold"},
    "1": {"max": 2, "desc": "database"},
    "2": {"max": 2, "desc": "models"},
    "3": {"max": 3, "desc": "services"},
    "4": {"max": 3, "desc": "api endpoints"},
    "5": {"max": 2, "desc": "auth"},
    "6": {"max": 2, "desc": "frontend scaffold"},
    "7": {"max": 3, "desc": "components"},
    "8": {"max": 3, "desc": "integration"},
    "9": {"max": 5, "desc": "e2e tests"},
    "10": {"max": 3, "desc": "infra/docker"},
    "11": {"max": 3, "desc": "ci/cd"},
}


def split_task(task: Dict[str, Any], parent_index: int) -> List[Dict[str, Any]]:
    """Split a large task into micro-tasks (≤ 3 points).
    
    Args:
        task: Task dict with story_points, spec_refs, etc.
        parent_index: Index in original backlog (for generating IDs)
    
    Returns:
        List of micro-tasks if points > 3, else [original task]
    """
    points = task.get("story_points", 1)
    
    # No split needed
    if points <= 3:
        return [task]
    
    # Estimate number of subtasks
    subtasks_count = (points + 2) // 3  # Round up: 5→2, 8→3, 13→5
    
    # Distribute points across subtasks (target: each ≤ 3)
    points_distribution = []
    remaining = points
    for i in range(subtasks_count):
        # Greedy: assign up to 3 points to each
        assigned = min(3, remaining)
        points_distribution.append(assigned)
        remaining -= assigned
    
    # Generate subtasks
    subtasks = []
    parent_id = task.get("id", f"t{parent_index:02d}")
    
    for i, sub_points in enumerate(points_distribution):
        subtask = {
            "id": f"{parent_id}{'abcdefghij'[i]}",  # t01 → t01a, t01b, ...
            "title": f"{task.get('title', 'Task')} (part {i+1}/{len(points_distribution)})",
            "description": task.get("description", ""),
            "layer": task.get("layer", "unknown"),
            "story_points": sub_points,
            "spec_refs": task.get("spec_refs", []),
            "test_command": task.get("test_command", ""),
            "acceptance_criteria": task.get("acceptance_criteria", []),
            "dependencies": task.get("dependencies", []),
            "status": "pending",
            "parent_id": parent_id,  # Link back to original task
            "is_micro": True,
        }
        subtasks.append(subtask)
    
    # Mark original as "meta" (not executable, just for reference)
    task["is_meta"] = True
    task["subtask_ids"] = [st["id"] for st in subtasks]
    task["status"] = "meta"
    
    # Return meta + subtasks
    return [task] + subtasks


def micro_plan(backlog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply micro-task splitting to backlog.
    
    Args:
        backlog: Original task backlog
    
    Returns:
        Expanded backlog with large tasks split into micro-tasks
    """
    result = []
    
    for i, task in enumerate(backlog):
        split = split_task(task, i)
        result.extend(split)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Split large tasks into micro-tasks.")
    parser.add_argument("--id", required=True, help="Project ID")
    parser.add_argument(
        "--keep-originals",
        action="store_true",
        help="Keep original large tasks (marked as meta) in backlog",
    )
    args = parser.parse_args()
    
    session_path = Path(f".forgestack/sessions/{args.id}.json")
    if not session_path.exists():
        print(f"Error: session '{args.id}' not found", flush=True)
        raise SystemExit(1)
    
    session = json.loads(session_path.read_text())
    backlog = session.get("backlog", [])
    
    # Apply micro-planning
    expanded = micro_plan(backlog)
    
    # Update session
    session["backlog"] = expanded
    session["backlog_status"] = {
        "original_tasks": len(backlog),
        "micro_tasks": len([t for t in expanded if t.get("is_micro")]),
        "meta_tasks": len([t for t in expanded if t.get("is_meta")]),
        "total_tasks": len(expanded),
    }
    
    # Save
    session_path.write_text(json.dumps(session, indent=2))
    
    # Print summary
    stats = session["backlog_status"]
    print(
        f"✅ Micro-planning complete\n"
        f"   Original tasks: {stats['original_tasks']}\n"
        f"   Micro-tasks: {stats['micro_tasks']}\n"
        f"   Meta tasks: {stats['meta_tasks']}\n"
        f"   Total: {stats['total_tasks']}\n",
        flush=True,
    )
    
    # Show first 10 tasks
    print("First 10 tasks:", flush=True)
    for task in expanded[:10]:
        marker = "  (meta)" if task.get("is_meta") else "  (micro)" if task.get("is_micro") else ""
        print(
            f"  {task['id']:8} {task['points']:1}pt {task.get('layer', '?'):12} "
            f"{task['title'][:40]:40}{marker}",
            flush=True,
        )
    
    print(f"\n→ Backlog saved to .forgestack/sessions/{args.id}.json", flush=True)


if __name__ == "__main__":
    main()
