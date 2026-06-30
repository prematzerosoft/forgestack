#!/usr/bin/env python3
"""Print a compact awareness summary of a ForgeStack session.

Inject this output at the start of every agent phase to restore full context
without dumping the entire session JSON. Also shows which phase docs exist
and what files to load for the next phase.

NEW: --slice flag for lazy-load context (80% smaller):
  --slice full         (default) → entire session + context
  --slice context_only → status, tech_stack, diagrams only
  --slice backlog_pending → next N pending tasks only
  --slice task_only    → current task + relevant spec sections
"""
import argparse
import json
from pathlib import Path

# What each phase needs loaded before starting
PHASE_CONTEXT = {
    "intake":          {"load": [], "writes": "docs/requirements.md"},
    "spec":            {"load": ["docs/requirements.md"], "writes": "docs/spec.md"},
    "architecture":    {"load": ["docs/spec.md"], "writes": "docs/architecture.md"},
    "planning":        {"load": ["docs/spec.md", "docs/architecture.md"], "writes": "docs/backlog.md"},
    "implementation":  {"load": ["docs/spec.md (task spec_refs sections only)"], "writes": "task code files"},
    "complete":        {"load": [], "writes": "—"},
}


def slice_context_only(s: dict) -> dict:
    """Lazy-load: only status + tech_stack + diagrams (80% smaller).
    
    Use when: need to know current phase but not full backlog.
    Token savings: ~2KB → ~400 bytes
    """
    return {
        "id": s.get("id"),
        "name": s.get("name"),
        "status": s.get("status"),
        "tech_stack": s.get("tech_stack", {}),
        "diagrams": s.get("diagrams", {}),
        "output_dir": s.get("output_dir"),
    }


def slice_backlog_pending(s: dict, limit: int = 5) -> dict:
    """Lazy-load: only next N pending tasks (not full backlog).
    
    Use when: need to see upcoming work but not historical tasks.
    Token savings: ~5KB → ~1KB (for typical backlog)
    """
    backlog = s.get("backlog", [])
    pending = [t for t in backlog if t.get("status") == "pending"][:limit]
    in_progress = [t for t in backlog if t.get("status") == "in_progress"]
    
    return {
        "id": s.get("id"),
        "name": s.get("name"),
        "status": s.get("status"),
        "backlog": {
            "pending": pending,
            "in_progress": in_progress,
            "total_tasks": len(backlog),
        },
        "output_dir": s.get("output_dir"),
    }


def slice_task_only(s: dict) -> dict:
    """Lazy-load: current task + relevant spec sections only.
    
    Use when: implementing a single task, need task details + spec_refs.
    Token savings: ~5KB → ~800 bytes (depends on task size)
    """
    backlog = s.get("backlog", [])
    pending = [t for t in backlog if t.get("status") == "pending"]
    current_task = pending[0] if pending else None
    
    return {
        "id": s.get("id"),
        "name": s.get("name"),
        "status": s.get("status"),
        "current_task": current_task,
        "spec_refs": current_task.get("spec_refs", []) if current_task else [],
        "tech_stack": s.get("tech_stack", {}),
        "output_dir": s.get("output_dir"),
        "note": "Load spec.md for contract details; sections referenced in spec_refs",
    }


def main():
    parser = argparse.ArgumentParser(description="Get ForgeStack session context summary.")
    parser.add_argument("--id", required=True, help="Project ID")
    parser.add_argument(
        "--slice",
        choices=["full", "context_only", "backlog_pending", "task_only"],
        default="full",
        help="Context slicing strategy (lazy-load to reduce tokens)",
    )
    args = parser.parse_args()

    session_path = Path(f".forgestack/sessions/{args.id}.json")
    if not session_path.exists():
        print(f"Error: session '{args.id}' not found", flush=True)
        raise SystemExit(1)

    s = json.loads(session_path.read_text())
    
    # Apply slicing if requested
    if args.slice != "full":
        sliced = None
        if args.slice == "context_only":
            sliced = slice_context_only(s)
        elif args.slice == "backlog_pending":
            sliced = slice_backlog_pending(s)
        elif args.slice == "task_only":
            sliced = slice_task_only(s)
        
        if sliced:
            print(f"[SLICE: {args.slice}]", flush=True)
            print(json.dumps(sliced, indent=2), flush=True)
            return

    # Full context (original behavior)

    backlog = s.get("backlog", [])
    total = len(backlog)
    completed = [t for t in backlog if t.get("status") == "complete"]
    failed = [t for t in backlog if t.get("status") == "failed"]
    pending = [t for t in backlog if t.get("status") == "pending"]
    in_progress = [t for t in backlog if t.get("status") == "in_progress"]
    next_task = pending[0] if pending else (in_progress[0] if in_progress else None)

    # Tech stack
    stack = s.get("tech_stack", {})
    stack_str = (
        f"{stack.get('language','?')} / {stack.get('backend','?')} / "
        f"{stack.get('frontend','?')} / {stack.get('database','?')}"
        if stack else "Not yet defined"
    )

    # Requirements summary
    req = s.get("requirements", {})
    features = req.get("features", [])
    features_str = ", ".join(features[:5]) + ("..." if len(features) > 5 else "") if features else "Not yet defined"

    # Spec summary
    spec = s.get("spec", {})
    spec_str = (
        f"{len(spec.get('feature_contracts', []))} feature contracts, "
        f"{len(spec.get('model_contracts', []))} model contracts"
        if spec else "Not yet written"
    )

    print("=" * 60)
    print(f"FORGESTACK CONTEXT — {s.get('name', '?')}")
    print("=" * 60)
    print(f"ID:          {s.get('id')}")
    print(f"Status:      {s.get('status', '?')}")
    print(f"Output Dir:  {s.get('output_dir', '?')}")
    print(f"Stack:       {stack_str}")
    print(f"Features:    {features_str}")
    print(f"Spec:        {spec_str}")
    print(f"Scaling:     {req.get('scaling', 'not set')}")
    print(f"Auth:        {req.get('auth_required', 'not set')}")
    print()
    print(f"Backlog:     {total} tasks total")
    print(f"  Complete:  {len(completed)}")
    print(f"  Failed:    {len(failed)}")
    print(f"  Pending:   {len(pending)}")
    if next_task:
        print()
        print(f"Next Task:   [{next_task.get('id')}] {next_task.get('title')}")
        print(f"  Layer:     {next_task.get('layer')}")
        print(f"  Points:    {next_task.get('story_points')}")
        print(f"  Test:      {next_task.get('test_command')}")
        refs = next_task.get("spec_refs", [])
        if refs:
            print(f"  Spec Refs: {', '.join(refs)}")
        deps = next_task.get("dependencies", [])
        if deps:
            print(f"  Depends:   {', '.join(deps)}")
    if failed:
        print()
        print("Failed Tasks:")
        for t in failed:
            print(f"  [{t.get('id')}] {t.get('title')}")
    if s.get("last_error"):
        print()
        print(f"Last Error:  {s['last_error']}")

    # Phase docs on disk
    output_dir = Path(s.get("output_dir", f"output/{s.get('id')}"))
    docs_dir = output_dir / "docs"
    existing_docs = [f.name for f in sorted(docs_dir.glob("*.md"))] if docs_dir.exists() else []

    print()
    print("Phase Docs:")
    if existing_docs:
        for doc in existing_docs:
            print(f"  ✓ {docs_dir / doc}")
    else:
        print("  (none written yet)")

    # Context discipline hint
    current_status = s.get("status", "intake")
    phase_info = PHASE_CONTEXT.get(current_status, {})
    load_list = phase_info.get("load", [])
    if load_list:
        print()
        print("Context for this phase — load these files:")
        for f in load_list:
            print(f"  → {output_dir / f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
