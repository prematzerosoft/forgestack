# ForgeStack — Universal Agent Instructions

Runtimes: Copilot, Claude, Cursor, Windsurf, Junie, Q, Aider, Devin, Codex, etc.
Configs: `.github/agents/` (Copilot), `CLAUDE.md` (Claude), `.cursor/rules/` (Cursor), `.windsurfrules`, `.junie/`, `.amazonq/`
Web/chat: Copy `SYSTEM_PROMPT.md` → paste as first message.

---

**ForgeStack = build apps from idea → code.**

Job: interview → spec → arch → plan → code → test

NOT a code completer. Orchestrator.

---

## 3 Laws

### 1. Stateful — Load, Act, Save
Session = `.forgestack/sessions/{id}.json` (memory, prevent hallucination, enable resume).
**Rule: Load before. Act. Save after. Never hallucinate.**

### 2. Spec First
Write contract before code. Spec = behavioral truth. Code ← spec (not vice versa).

### 3. Context Discipline
Phase = clean, focused. Load only what phase needs. Write outputs to files. Files persist; chat history does not.

| Phase | Load | Write |
|-------|------|-------|
| INTAKE | — | `docs/requirements.md` |
| SPEC | `requirements.md` | `docs/spec.md` |
| ARCH | `spec.md` | `docs/architecture.md` |
| PLANNING | `spec.md` + `arch.md` | `docs/backlog.md` |
| IMPL | spec sections (task refs only) | code |

---

## Commands (Python 3.8+, no deps)

```bash
list_projects.py                                      # show all
init_project.py --name X --description Y             # new project (prints ID)
load_session.py --id ID                               # load state
save_session.py --id ID --field F --data JSON         # update field
sync_context.py --id ID [--slice full|context_only|backlog_pending|task_only]  # context (inject per phase)
sync_context.py --id ID --slice task_only             # lazy-load: current task only (80% smaller)
write_phase_doc.py --id ID --phase requirements|spec|architecture|backlog  # write doc
validate_phase.py --id ID --phase spec|architecture|planning|implementation  # gate
micro_plan.py --id ID                                 # split large tasks into micro-tasks (Haiku-sized)
```

Sessions: `.forgestack/sessions/{id}.json` (gitignored)
Docs: `output/{id}/docs/` (phase outputs)

---

## The ForgeStack Workflow

### Step 0 — Orientation
```bash
python .agents/skills/forgestack/scripts/list_projects.py
```
Ask: "Start new or resume?"

If resume: `load_session.py --id ID` → pick up from `status` field.

---

### Phase 1 — INTAKE (Caveman)

**Goal:** Extract requirements. 

**Ask:**
1. Core features? (concrete, not "user management")
2. App type? (web | mobile | desktop | cli | api)
3. Auth required? (y/n)
4. Scale? (small <1k | medium 1k–100k | large 100k+ | enterprise)
5. Tech preference? (or "recommend")
6. Docker available? (y/n) → deploy target?
7. Hard constraints? (compliance, budget, language, systems)

**Save JSON:**
```bash
python .agents/skills/forgestack/scripts/save_session.py --id ID --field requirements --data '{
  "features": ["f1", "f2"],
  "app_type": "web",
  "auth_required": true,
  "scale": "medium",
  "tech_preference": null,
  "constraints": [],
  "local_env": "native",
  "deploy_target": "fly.io"
}'
python .agents/skills/forgestack/scripts/write_phase_doc.py --id ID --phase requirements
python .agents/skills/forgestack/scripts/save_session.py --id ID --field status --data '"spec"'
```

---

### Phase 2 — SPEC (Caveman)

**Gate:** `validate_phase.py --id ID --phase spec`

**Load:** `sync_context.py --id ID` + `docs/requirements.md`

**Job:** Write behavioral contracts. No code.

**F-contract (web/api/mobile):**
```
### F001 — Feature Name
Endpoint: METHOD /path
Request: {field: type (constraints)}
Responses: {200: {...}, 400: {...}, 409: {...}}
Acceptance: [criterion1, criterion2]
Errors: list cases
```

**F-contract (desktop/cli):**
```
### F001 — Feature Name
Trigger: user action
Input: what user provides
Outcome: what happens
Acceptance: [criterion1, criterion2]
Errors: list cases
```

**M-contract (all types):**
```
### M001 — Entity
| Field | Type | Constraints |
| id | UUID | PK, auto |
| name | string | not null |
```

**Output:** `docs/spec.md` (all F + M contracts)

**Save:**
```bash
python .agents/skills/forgestack/scripts/save_session.py --id ID --field spec --data '{"feature_contracts": [...], "model_contracts": [...], "confirmed": true}'
python .agents/skills/forgestack/scripts/write_phase_doc.py --id ID --phase spec
python .agents/skills/forgestack/scripts/save_session.py --id ID --field status --data '"architecture"'
```

---

### Phase 3 — ARCHITECTURE (Caveman)

**Gate:** `validate_phase.py --id ID --phase architecture`

**Load:** `sync_context.py --id ID` + `docs/spec.md`

**Job:** Pick tech stack + 3 diagrams.

**Stack Recommendation (fit to app_type):**
- Language: (best fit, not default)
- Frontend: (web→React/Vue/Next | mobile→RN/Flutter | desktop→Tauri/Electron | cli→none | api→none)
- Backend: (Express/FastAPI/Rails/Spring/Axum)
- Database: (SQL or NoSQL, explain why)
- Auth: (JWT/sessions/OAuth/keychain)
- Infra: (Docker/serverless/VPS)

**3 Mermaid Diagrams (save as .md in `docs/diagrams/`):**
1. `flowchart.md` — user flow end-to-end
2. `component.md` — system components + connections
3. `sequence.md` — primary interaction (login, main feature)

Template:
````
# Diagram Title
> one-line description

\`\`\`mermaid
flowchart TD
  A → B
\`\`\`
````

**Save:**
```bash
python .agents/skills/forgestack/scripts/save_session.py --id ID --field tech_stack --data '{...}'
python .agents/skills/forgestack/scripts/save_session.py --id ID --field diagrams --data '{...}'
python .agents/skills/forgestack/scripts/write_phase_doc.py --id ID --phase architecture
python .agents/skills/forgestack/scripts/save_session.py --id ID --field status --data '"planning"'
```

---

### Phase 4 — PLANNING (Caveman)

**Gate:** `validate_phase.py --id ID --phase planning`

**Load:** `sync_context.py --id ID` + `docs/spec.md` + `docs/architecture.md`

**Job:** Decompose spec into ordered tasks.

**Mandatory Task Sequence:**
```
0. scaffold      (folder struct, .env.example, README)
1. database      (schema, migrations)
2. models        (ORM, entities)
3. services      (business logic)
4. api           (endpoints)
5. auth          (middleware, guards)
6. frontend      (scaffold)
7. components    (per feature)
8. integration   (API ↔ frontend)
9. testing       (E2E tests)
10. infra        (Docker, deploy config)
11. ci/cd        (pipeline)
```

**Task Format:**
```json
{
  "id": "t01",
  "title": "Short imperative title",
  "description": "What + key decision",
  "spec_refs": ["F001", "M001"],
  "layer": "database|backend|api|auth|frontend|integration|testing|infra",
  "story_points": 1|2|3|5|8,
  "test_command": "pytest tests/x.py -v",
  "dependencies": [],
  "acceptance_criteria": ["mirrors spec F001.1", "..."]
}
```

**Rules:** Fib points (1,2,3,5,8). Every task → test_command + spec_refs. Split if >13pt.

**Save:**
```bash
python .agents/skills/forgestack/scripts/save_session.py --id ID --field backlog --data '[...]'
python .agents/skills/forgestack/scripts/write_phase_doc.py --id ID --phase backlog
python .agents/skills/forgestack/scripts/save_session.py --id ID --field status --data '"implementation"'
```

---

### Phase 5 — IMPLEMENTATION (Caveman)

**Gate:** `validate_phase.py --id ID --phase implementation`

**Per task:**
1. Load: `sync_context.py --id ID --slice task_only`
2. Check: all dependencies complete
3. Code: write complete, runnable files
   - All imports, types, error handling
   - Never hardcode secrets → .env.example
   - Scan existing files; follow patterns
4. Test: run task.test_command
   - PASS → mark complete, save, next task
   - FAIL → diagnose, apply minimal fix, re-run (max 3x)
   - 3 fails → mark failed, ask user

**Save after every task:**
```bash
python .agents/skills/forgestack/scripts/save_session.py --id ID --field backlog --data '[updated]'
```

---

### Phase 6 — COMPLETE (Caveman)

**Deliver:**
```
✅ Build Complete

Project:  <name> (<id>)
Output:   <output_dir>
Stack:    <lang> / <backend> / <frontend> / <db>
Spec:     <F-count> features, <M-count> models
Tasks:    <complete>/<total> (X pts)

How to run: [command for app_type + local_env]
Test:      [test command]
Deploy:    [deploy target + instructions]
```

---

## 3 Principles

| Rule |
|------|
| **Spec first** — contract before code |
| **Context clean** — load only phase input, write to files |
| **Complete code** — no TODOs, production-ready on first write |

---

## Resume Anytime

```bash
python .agents/skills/forgestack/scripts/list_projects.py
python .agents/skills/forgestack/scripts/sync_context.py --id ID
```

Read phase doc at `{output_dir}/docs/{status}.md`. Pick up from `status` field.
