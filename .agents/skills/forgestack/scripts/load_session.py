#!/usr/bin/env python3
"""Load and print a ForgeStack session as JSON."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Load a ForgeStack session.")
    parser.add_argument("--id", required=True, help="Project ID")
    args = parser.parse_args()

    session_path = Path(f".forgestack/sessions/{args.id}.json")
    if not session_path.exists():
        print(f"Error: session '{args.id}' not found at {session_path}", flush=True)
        raise SystemExit(1)

    data = json.loads(session_path.read_text())
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
