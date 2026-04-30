"""Tests for all ForgeStack session management scripts.

Each test runs scripts as subprocesses against a temporary directory,
testing the actual CLI surface a user (or agent) would invoke.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / ".agents/skills/forgestack/scripts"


def run(script: str, *args, cwd: Path):
    """Run a ForgeStack script and return the CompletedProcess result."""
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


# ---------------------------------------------------------------------------
# init_project.py
# ---------------------------------------------------------------------------

def test_init_creates_session(tmp_path):
    result = run("init_project.py", "--name", "TestApp", "--description", "A test", cwd=tmp_path)
    assert result.returncode == 0
    project_id = result.stdout.strip()
    assert len(project_id) == 36, "Expected a UUID"
    session_file = tmp_path / ".forgestack" / "sessions" / f"{project_id}.json"
    assert session_file.exists()
    session = json.loads(session_file.read_text())
    assert session["name"] == "TestApp"
    assert session["description"] == "A test"
    assert session["status"] == "intake"
    assert session["spec"] == {}
    assert session["requirements"] == {}
    assert session["backlog"] == []


def test_init_creates_output_dir_field(tmp_path):
    result = run("init_project.py", "--name", "MyApp", "--description", "Desc", cwd=tmp_path)
    pid = result.stdout.strip()
    session = json.loads(
        (tmp_path / ".forgestack" / "sessions" / f"{pid}.json").read_text()
    )
    assert "output_dir" in session
    assert pid in session["output_dir"]


# ---------------------------------------------------------------------------
# list_projects.py
# ---------------------------------------------------------------------------

def test_list_projects_empty(tmp_path):
    result = run("list_projects.py", cwd=tmp_path)
    assert result.returncode == 0
    assert "No projects found" in result.stdout


def test_list_projects_finds_created_project(tmp_path):
    run("init_project.py", "--name", "MyApp", "--description", "Test", cwd=tmp_path)
    result = run("list_projects.py", cwd=tmp_path)
    assert result.returncode == 0
    assert "MyApp" in result.stdout


def test_list_projects_shows_multiple(tmp_path):
    run("init_project.py", "--name", "Alpha", "--description", "First", cwd=tmp_path)
    run("init_project.py", "--name", "Beta", "--description", "Second", cwd=tmp_path)
    result = run("list_projects.py", cwd=tmp_path)
    assert "Alpha" in result.stdout
    assert "Beta" in result.stdout


# ---------------------------------------------------------------------------
# save_session.py + load_session.py
# ---------------------------------------------------------------------------

def test_save_and_load_field(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    run("save_session.py", "--id", pid, "--field", "status", "--data", '"spec"', cwd=tmp_path)
    result = run("load_session.py", "--id", pid, cwd=tmp_path)
    assert result.returncode == 0
    session = json.loads(result.stdout)
    assert session["status"] == "spec"


def test_save_requirements(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    req = json.dumps({
        "features": ["auth", "CRUD"],
        "constraints": ["GDPR"],
        "scaling": "small",
        "auth_required": True,
        "confirmed": True,
    })
    run("save_session.py", "--id", pid, "--field", "requirements", "--data", req, cwd=tmp_path)
    session = json.loads(run("load_session.py", "--id", pid, cwd=tmp_path).stdout)
    assert session["requirements"]["confirmed"] is True
    assert "auth" in session["requirements"]["features"]


def test_save_spec_field(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    spec = json.dumps({
        "feature_contracts": ["F001", "F002"],
        "model_contracts": ["M001"],
        "confirmed": True,
    })
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    session = json.loads(run("load_session.py", "--id", pid, cwd=tmp_path).stdout)
    assert session["spec"]["confirmed"] is True
    assert "F001" in session["spec"]["feature_contracts"]


def test_load_nonexistent_session_fails(tmp_path):
    result = run("load_session.py", "--id", "does-not-exist", cwd=tmp_path)
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# sync_context.py
# ---------------------------------------------------------------------------

def test_sync_context_runs(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    result = run("sync_context.py", "--id", pid, cwd=tmp_path)
    assert result.returncode == 0
    assert "FORGESTACK CONTEXT" in result.stdout
    assert "App" in result.stdout


def test_sync_context_shows_spec_summary_after_save(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    spec = json.dumps({"feature_contracts": ["F001", "F002"], "model_contracts": ["M001"], "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    result = run("sync_context.py", "--id", pid, cwd=tmp_path)
    assert "2 feature contracts" in result.stdout
    assert "1 model contracts" in result.stdout


def test_sync_context_shows_phase_doc_hints(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    run("save_session.py", "--id", pid, "--field", "status", "--data", '"spec"', cwd=tmp_path)
    result = run("sync_context.py", "--id", pid, cwd=tmp_path)
    assert "requirements.md" in result.stdout


def test_sync_context_nonexistent_session_fails(tmp_path):
    result = run("sync_context.py", "--id", "bad-id", cwd=tmp_path)
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# write_phase_doc.py
# ---------------------------------------------------------------------------

def test_write_phase_doc_requirements(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    req = json.dumps({"features": ["auth", "CRUD"], "constraints": ["GDPR"], "scaling": "small", "auth_required": True, "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "requirements", "--data", req, cwd=tmp_path)
    result = run("write_phase_doc.py", "--id", pid, "--phase", "requirements", cwd=tmp_path)
    assert result.returncode == 0
    doc = tmp_path / f"output/{pid}/docs/requirements.md"
    assert doc.exists()
    content = doc.read_text()
    assert "# Requirements: App" in content
    assert "auth" in content
    assert "GDPR" in content


def test_write_phase_doc_spec_creates_stub_when_missing(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    spec = json.dumps({"feature_contracts": ["F001"], "model_contracts": ["M001"], "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    result = run("write_phase_doc.py", "--id", pid, "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 0
    doc = tmp_path / f"output/{pid}/docs/spec.md"
    assert doc.exists()
    assert "F001" in doc.read_text()


def test_write_phase_doc_spec_preserves_existing_spec_md(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    docs_dir = tmp_path / f"output/{pid}/docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "spec.md").write_text("# Spec: App\n\n### F001 — Auth\n")
    spec = json.dumps({"feature_contracts": ["F001"], "model_contracts": [], "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    result = run("write_phase_doc.py", "--id", pid, "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 0
    content = (docs_dir / "spec.md").read_text()
    assert "F001" in content


def test_write_phase_doc_backlog(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    backlog = json.dumps([{
        "id": "t01", "title": "Set up DB schema", "description": "Create tables",
        "spec_refs": ["M001"], "layer": "database", "story_points": 2,
        "priority": 0, "status": "pending", "test_command": "pytest tests/test_db.py",
        "dependencies": [], "acceptance_criteria": ["Tables exist after migration"],
    }])
    run("save_session.py", "--id", pid, "--field", "backlog", "--data", backlog, cwd=tmp_path)
    result = run("write_phase_doc.py", "--id", pid, "--phase", "backlog", cwd=tmp_path)
    assert result.returncode == 0
    doc = tmp_path / f"output/{pid}/docs/backlog.md"
    assert doc.exists()
    content = doc.read_text()
    assert "Set up DB schema" in content
    assert "M001" in content


# ---------------------------------------------------------------------------
# validate_phase.py
# ---------------------------------------------------------------------------

def test_validate_blocks_spec_without_requirements(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    result = run("validate_phase.py", "--id", pid, "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout


def test_validate_blocks_spec_without_confirmed_requirements(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    req = json.dumps({"features": ["auth"], "confirmed": False})
    run("save_session.py", "--id", pid, "--field", "requirements", "--data", req, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 1
    assert "confirmed" in result.stdout.lower()


def test_validate_passes_spec_with_confirmed_requirements(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    req = json.dumps({"features": ["auth"], "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "requirements", "--data", req, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_validate_blocks_architecture_without_spec(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    result = run("validate_phase.py", "--id", pid, "--phase", "architecture", cwd=tmp_path)
    assert result.returncode == 1
    assert "BLOCKED" in result.stdout


def test_validate_blocks_architecture_with_unconfirmed_spec(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    spec = json.dumps({"feature_contracts": ["F001"], "model_contracts": [], "confirmed": False})
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "architecture", cwd=tmp_path)
    assert result.returncode == 1


def test_validate_passes_architecture_with_confirmed_spec(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    spec = json.dumps({"feature_contracts": ["F001"], "model_contracts": ["M001"], "confirmed": True})
    run("save_session.py", "--id", pid, "--field", "spec", "--data", spec, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "architecture", cwd=tmp_path)
    assert result.returncode == 0


def test_validate_blocks_planning_without_tech_stack(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    result = run("validate_phase.py", "--id", pid, "--phase", "planning", cwd=tmp_path)
    assert result.returncode == 1


def test_validate_passes_planning_with_tech_stack(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    stack = json.dumps({"language": "Python", "backend": "FastAPI", "database": "PostgreSQL"})
    run("save_session.py", "--id", pid, "--field", "tech_stack", "--data", stack, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "planning", cwd=tmp_path)
    assert result.returncode == 0


def test_validate_blocks_implementation_without_backlog(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    result = run("validate_phase.py", "--id", pid, "--phase", "implementation", cwd=tmp_path)
    assert result.returncode == 1


def test_validate_passes_implementation_with_backlog(tmp_path):
    pid = run("init_project.py", "--name", "App", "--description", "D", cwd=tmp_path).stdout.strip()
    backlog = json.dumps([{"id": "t01", "title": "Init", "status": "pending"}])
    run("save_session.py", "--id", pid, "--field", "backlog", "--data", backlog, cwd=tmp_path)
    result = run("validate_phase.py", "--id", pid, "--phase", "implementation", cwd=tmp_path)
    assert result.returncode == 0


def test_validate_nonexistent_session_fails(tmp_path):
    result = run("validate_phase.py", "--id", "bad-id", "--phase", "spec", cwd=tmp_path)
    assert result.returncode == 1
    assert "not found" in result.stdout.lower()
