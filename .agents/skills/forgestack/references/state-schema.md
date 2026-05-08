# ForgeStack Session State Schema

Every project session is stored as a single JSON file at:
```
.forgestack/sessions/<project-id>.json
```

---

## Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` (UUID) | Unique project identifier |
| `name` | `string` | Short human-readable project name |
| `description` | `string` | One-sentence description of the app |
| `status` | `string` | Current workflow phase (see below) |
| `output_dir` | `string` | Relative path where generated code is written |
| `requirements` | `object` | Structured requirements from intake phase |
| `spec` | `object` | Behavioral contract index from spec phase |
| `tech_stack` | `object` | Confirmed technology stack from architecture phase |
| `diagrams` | `object` | Paths to generated Mermaid diagram files |
| `backlog` | `array<Task>` | Ordered list of implementation tasks |
| `last_error` | `string\|null` | Most recent error or fix attempt note |
| `created_at` | `string` (ISO 8601) | Project creation timestamp |
| `updated_at` | `string` (ISO 8601) | Last save timestamp |

---

## `status` Values

| Value | Meaning |
|-------|---------|
| `intake` | Requirements gathering in progress |
| `spec` | Behavioral spec writing in progress |
| `architecture` | Tech stack and diagrams in progress |
| `planning` | Backlog decomposition in progress |
| `implementation` | Coding loop active |
| `complete` | All tasks done, project delivered |

---

## `spec` Object

The session `spec` field stores a **contract index** only. The full spec content lives in `{output_dir}/docs/spec.md`.

```json
{
  "feature_contracts": ["F001", "F002", "F003"],
  "model_contracts": ["M001", "M002"],
  "confirmed": true
}
```

| Field | Description |
|-------|-------------|
| `feature_contracts` | Ordered list of F-contract IDs defined in `spec.md` |
| `model_contracts` | Ordered list of M-contract IDs defined in `spec.md` |
| `confirmed` | `true` once user has reviewed and approved the spec |

---

## `requirements` Object

```json
{
  "features": ["user registration", "task CRUD", "email notifications"],
  "constraints": ["GDPR compliant", "REST API only"],
  "scaling": "small|medium|large|enterprise",
  "preferred_stack": null,
  "auth_required": true,
  "auth_type": "JWT|sessions|OAuth2|magic_links|none",
  "local_env": "docker|native",
  "deploy_target": "fly.io|vercel|railway|vps|aws|local-only",
  "confirmed": true
}
```

| Field | Description |
|-------|-------------|
| `app_type` | `web|mobile|desktop|cli|api` — determines spec contract format, stack options, environment setup, and run instructions |
| `local_env` | `"docker"` if Docker is available on the user's machine; `"native"` otherwise |
| `deploy_target` | Where the app will be deployed in production (influences CI/CD and Dockerfile) |

> `app_type` controls spec contract format (HTTP vs action/command), stack recommendations, environment setup, and run instructions in COMPLETE. `local_env` defaults to `"native"` if unknown — never assume Docker is present.

---

## `tech_stack` Object

```json
{
  "language": "Python",
  "backend": "FastAPI",
  "frontend": "React + Vite",
  "database": "PostgreSQL",
  "auth": "JWT (python-jose)",
  "infrastructure": "Docker Compose",
  "rationale": {
    "language": "Python chosen for rapid iteration and rich ecosystem",
    "database": "PostgreSQL for relational data with JSONB flexibility",
    "frontend": "React chosen per user preference; Vite for fast builds"
  }
}
```

---

## `diagrams` Object

```json
{
  "flowchart": "docs/diagrams/flowchart.md",
  "component": "docs/diagrams/component.md",
  "sequence": "docs/diagrams/sequence.md"
}
```

---

## `Task` Object (`backlog` array items)

```json
{
  "id": "t01",
  "title": "Initialize database schema and migrations",
  "description": "Create users, tasks, and notifications tables with proper indexes",
  "layer": "database",
  "story_points": 3,
  "priority": 1,
  "status": "pending|in_progress|complete|failed",
  "test_command": "pytest tests/test_schema.py -v",
  "dependencies": ["t00"],
  "acceptance_criteria": [
    "All migrations run without error",
    "All expected columns and indexes present",
    "Rollback migration succeeds"
  ]
}
```

### `layer` Values

| Value | Description |
|-------|-------------|
| `scaffold` | Project setup, env, config, CI skeleton |
| `database` | Schema, migrations |
| `backend` | Data models, ORM, services, domain logic |
| `api` | HTTP routes, controllers, request/response schemas |
| `auth` | Authentication and authorization middleware |
| `frontend` | UI scaffold, components, pages |
| `integration` | Frontend ↔ API wiring, state management |
| `testing` | Integration and E2E tests |
| `infra` | Docker, deployment config, CI/CD pipelines |

### `status` Values

| Value | Description |
|-------|-------------|
| `pending` | Not yet started |
| `in_progress` | Currently being implemented |
| `complete` | Implemented and tests pass |
| `failed` | 3 auto-fix attempts exhausted; needs human intervention |

---

## Full Example Session

```json
{
  "id": "3f2a1b4c-...",
  "name": "TaskFlow",
  "description": "A GDPR-compliant task management API with email notifications",
  "status": "implementation",
  "output_dir": "output/3f2a1b4c-...",
  "requirements": {
    "features": ["user registration", "task CRUD", "email notifications"],
    "constraints": ["GDPR compliant"],
    "scaling": "medium",
    "preferred_stack": null,
    "auth_required": true,
    "auth_type": "JWT",
    "confirmed": true
  },
  "spec": {
    "feature_contracts": ["F001", "F002", "F003"],
    "model_contracts": ["M001", "M002"],
    "confirmed": true
  },
  "tech_stack": {
    "language": "Python",
    "backend": "FastAPI",
    "frontend": "React + Vite",
    "database": "PostgreSQL",
    "auth": "JWT",
    "infrastructure": "Docker Compose"
  },
  "diagrams": {
    "flowchart": "docs/diagrams/flowchart.md",
    "component": "docs/diagrams/component.md",
    "sequence": "docs/diagrams/sequence.md"
  },
  "backlog": [
    {
      "id": "t00",
      "title": "Scaffold project structure and dev environment",
      "layer": "scaffold",
      "story_points": 2,
      "priority": 0,
      "status": "complete",
      "test_command": "python -c 'import app; print(\"OK\")'",
      "dependencies": [],
      "acceptance_criteria": ["app imports without error", ".env.example present"]
    }
  ],
  "last_error": null,
  "created_at": "2025-01-01T00:00:00+00:00",
  "updated_at": "2025-01-01T01:00:00+00:00"
}
```
