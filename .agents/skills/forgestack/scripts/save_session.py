#!/usr/bin/env python3
"""Save or update a ForgeStack session field.

Usage:
  # Update a single field (value is JSON-encoded)
  python save_session.py --id PROJECT_ID --field status --data '"architecture"'
  python save_session.py --id PROJECT_ID --field requirements --data '{"features":[]}'

  # Overwrite the entire session with a full JSON object
  python save_session.py --id PROJECT_ID --data '{"id":"...","name":"...",...}'
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Save a ForgeStack session field.")
    parser.add_argument("--id", required=True, help="Project ID")
    parser.add_argument("--field", default=None, help="Field name to update (omit to replace full session)")
    parser.add_argument("--data", required=True, help="JSON value to write")
    args = parser.parse_args()

    session_path = Path(f".forgestack/sessions/{args.id}.json")
    if not session_path.exists():
        print(f"Error: session '{args.id}' not found at {session_path}", flush=True)
        raise SystemExit(1)

    try:
        value = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: --data is not valid JSON: {e}", flush=True)
        raise SystemExit(1)

    if args.field is None:
        # Replace entire session
        if not isinstance(value, dict):
            print("Error: when replacing the full session, --data must be a JSON object", flush=True)
            raise SystemExit(1)
        session = value
    else:
        session = json.loads(session_path.read_text())
        session[args.field] = value

    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    session_path.write_text(json.dumps(session, indent=2))
    print(f"Saved: {args.field or 'full session'} for project {args.id}")


if __name__ == "__main__":
    main()
