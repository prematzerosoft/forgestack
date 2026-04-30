#!/usr/bin/env python3
"""List all ForgeStack projects in .forgestack/sessions/"""
import json
from pathlib import Path


def main():
    sessions_dir = Path(".forgestack/sessions")
    if not sessions_dir.exists():
        print("No projects found. Use init_project.py to create one.")
        return

    sessions = list(sessions_dir.glob("*.json"))
    if not sessions:
        print("No projects found. Use init_project.py to create one.")
        return

    print(f"{'ID':<40} {'Name':<30} {'Status':<20} {'Updated'}")
    print("-" * 100)
    for path in sorted(sessions):
        try:
            data = json.loads(path.read_text())
            print(
                f"{data.get('id','?'):<40} "
                f"{data.get('name','?'):<30} "
                f"{data.get('status','?'):<20} "
                f"{data.get('updated_at','?')}"
            )
        except Exception as e:
            print(f"{path.stem:<40} [error reading session: {e}]")


if __name__ == "__main__":
    main()
