#!/usr/bin/env python3
"""Initialize a new ForgeStack project session. Prints the new project ID."""
import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def slugify(name: str) -> str:
    """Convert an app name to a safe, lowercase folder slug.

    Examples:
        "Pain Tracker App" -> "pain-tracker-app"
        "My SaaS Platform!" -> "my-saas-platform"
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "app"


def unique_output_dir(base_slug: str) -> str:
    """Return output/<slug>, incrementing a suffix if the directory already exists."""
    candidate = Path(f"output/{base_slug}")
    if not candidate.exists():
        return str(candidate)
    counter = 2
    while True:
        candidate = Path(f"output/{base_slug}-{counter}")
        if not candidate.exists():
            return str(candidate)
        counter += 1


def main():
    parser = argparse.ArgumentParser(description="Initialize a new ForgeStack project.")
    parser.add_argument("--name", required=True, help="Short project name")
    parser.add_argument("--description", required=True, help="What the app does")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Where generated code will be written (default: output/<name-slug>)",
    )
    args = parser.parse_args()

    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    output_dir = args.output_dir or unique_output_dir(slugify(args.name))

    session = {
        "id": project_id,
        "name": args.name,
        "description": args.description,
        "status": "intake",
        "output_dir": output_dir,
        "requirements": {},
        "spec": {},
        "tech_stack": {},
        "diagrams": {},
        "backlog": [],
        "last_error": None,
        "created_at": now,
        "updated_at": now,
    }

    sessions_dir = Path(".forgestack/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_path = sessions_dir / f"{project_id}.json"
    session_path.write_text(json.dumps(session, indent=2))

    print(project_id)


if __name__ == "__main__":
    main()
