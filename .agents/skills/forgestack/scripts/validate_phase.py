#!/usr/bin/env python3
"""Validate that session prerequisites are satisfied before a phase begins.

Exits 0 if the phase may proceed.
Exits 1 with a clear, actionable error if prerequisites are not met.

This is a hard gate — agents MUST call this before starting any phase after INTAKE.

Usage:
  python validate_phase.py --id PROJECT_ID --phase spec
  python validate_phase.py --id PROJECT_ID --phase architecture
  python validate_phase.py --id PROJECT_ID --phase planning
  python validate_phase.py --id PROJECT_ID --phase implementation
"""
import argparse
import json
import sys
from pathlib import Path

VALID_PHASES = ("spec", "architecture", "planning", "implementation")

# Each entry: list of (check_fn, error_message, fix_hint) tuples.
# check_fn receives the full session dict and returns True if the check passes.
PREREQUISITES = {
    "spec": [
        (
            lambda s: bool(s.get("requirements")),
            "Requirements not captured.",
            "Complete INTAKE first: interview the user and save requirements via save_session.py --field requirements",
        ),
        (
            lambda s: s.get("requirements", {}).get("confirmed") is True,
            "Requirements not confirmed by user.",
            "Present the requirements to the user and get explicit confirmation before starting SPEC.",
        ),
    ],
    "architecture": [
        (
            lambda s: bool(s.get("spec")),
            "Spec not yet written.",
            "Complete SPEC first: write all F- and M-contracts and save via save_session.py --field spec",
        ),
        (
            lambda s: s.get("spec", {}).get("confirmed") is True,
            "Spec not confirmed by user.",
            "Present the full spec to the user and get explicit confirmation before starting ARCHITECTURE.",
        ),
    ],
    "planning": [
        (
            lambda s: bool(s.get("tech_stack")),
            "Tech stack not defined.",
            "Complete ARCHITECTURE first: recommend a stack, get user confirmation, and save via save_session.py --field tech_stack",
        ),
    ],
    "implementation": [
        (
            lambda s: bool(s.get("backlog")),
            "Backlog is empty.",
            "Complete PLANNING first: decompose the project into tasks and save via save_session.py --field backlog",
        ),
        (
            lambda s: len(s.get("backlog", [])) > 0,
            "Backlog has no tasks.",
            "Add at least one task to the backlog before starting IMPLEMENTATION.",
        ),
    ],
}


def main():
    parser = argparse.ArgumentParser(
        description="Validate ForgeStack phase prerequisites."
    )
    parser.add_argument("--id", required=True, help="Project ID")
    parser.add_argument(
        "--phase", required=True, choices=VALID_PHASES, help="Phase to validate"
    )
    args = parser.parse_args()

    session_path = Path(f".forgestack/sessions/{args.id}.json")
    if not session_path.exists():
        print(f"ERROR: Session '{args.id}' not found at {session_path}", flush=True)
        print("Run init_project.py to create a new project session.", flush=True)
        sys.exit(1)

    session = json.loads(session_path.read_text())
    checks = PREREQUISITES[args.phase]
    failures = []

    for check_fn, error_msg, fix_hint in checks:
        if not check_fn(session):
            failures.append((error_msg, fix_hint))

    if failures:
        print(
            f"BLOCKED: Cannot start {args.phase.upper()} phase for '{session.get('name', args.id)}'.",
            flush=True,
        )
        print("", flush=True)
        for i, (error_msg, fix_hint) in enumerate(failures, 1):
            print(f"  {i}. {error_msg}", flush=True)
            print(f"     Fix: {fix_hint}", flush=True)
            print("", flush=True)
        sys.exit(1)

    print(
        f"OK: {args.phase.upper()} phase prerequisites satisfied for '{session.get('name', args.id)}'.",
        flush=True,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
