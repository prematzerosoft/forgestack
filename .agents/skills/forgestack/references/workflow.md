# ForgeStack Workflow Reference

Complete SDLC orchestration procedure for building production-ready applications.

---

## Phase Overview

```
INTAKE → SPEC → ARCHITECTURE → PLANNING → IMPLEMENTATION (loop) → COMPLETE
```

Each phase writes its output to a file. The next phase loads only that file — not conversation history. Any interruption is fully recoverable.

| Phase | Load before starting | Write before finishing |
|-------|---------------------|------------------------|
| INTAKE | *(none)* | `docs/requirements.md` |
| SPEC | `docs/requirements.md` | `docs/spec.md` |
| ARCHITECTURE | `docs/spec.md` | `docs/architecture.md` + diagrams |
| PLANNING | `docs/spec.md` + `docs/architecture.md` | `docs/backlog.md` |
| IMPLEMENTATION | `docs/spec.md` (task spec_refs sections only) | task code files |

---

## Phase 1 — INTAKE

**Goal**: Produce a confirmed, structured requirements document.

**Steps**:
1. Run `list_projects.py` — ask user: new project or resume?
2. If new: `init_project.py --name "X" --description "Y"` → save project ID
3. Ask up to 5 questions:
   - Core features (concrete and implementable)
   - Auth required? What kind?
   - Scale: small / medium / large / enterprise
   - Technology preference (or "recommend")
   - Hard constraints (compliance, budget, existing infra)
4. Synthesize answers into `requirements` JSON
5. Read back to user → confirm → apply corrections
6. `save_session.py --field requirements --data '{...}'`
7. `write_phase_doc.py --id PROJECT_ID --phase requirements`
8. `save_session.py --field status --data '"spec"'`

**Output**: `session.requirements` object, `docs/requirements.md`, `status = spec`

---

## Phase 2 — SPEC

**Goal**: Write a behavioral contract (spec) for every feature. This is the single source of truth — code adapts to the spec, never the other way.

**Context**: Load `docs/requirements.md` only. Do not rely on conversation history.

**Steps**:
1. `sync_context.py` — restore awareness
2. Read `{output_dir}/docs/requirements.md`
3. For every feature, write an **F-contract**:
   - Endpoint, HTTP method
   - Request shape (required/optional fields, types, constraints)
   - All response codes + response bodies
   - Acceptance criteria (testable, specific)
   - Error cases (what input triggers each error response)
4. For every data entity, write an **M-contract**:
   - Field table: name, type, constraints
   - No tech decisions (e.g. don't say "PostgreSQL column") — implementation-neutral
5. Write all contracts to `{output_dir}/docs/spec.md`
6. Present the full spec to user — wait for confirmation — apply corrections
7. `save_session.py --field spec --data '{"feature_contracts":[...],"model_contracts":[...],"confirmed":true}'`
8. `save_session.py --field status --data '"architecture"'`

**Output**: `docs/spec.md`, `session.spec` index, `status = architecture`

---

## Phase 3 — ARCHITECTURE

**Goal**: Confirmed tech stack + 3 architecture diagrams.

**Context**: Load `docs/spec.md` only. Use the API surface, data shapes, and non-functional requirements defined there to drive stack decisions.

**Steps**:
1. `sync_context.py` — restore awareness; read `{output_dir}/docs/spec.md`
2. Based on the spec (feature complexity, constraints, scale), choose:
   - Language, backend framework, frontend (or API-only), database, auth, infrastructure
   - Prioritize fit-for-purpose over familiarity
3. Write 3 Mermaid diagram files to `{output_dir}/docs/diagrams/`:
   - `flowchart.mmd` — end-to-end user flow (`flowchart TD`)
   - `component.mmd` — all system components (`graph LR`)
   - `sequence.mmd` — primary interaction (`sequenceDiagram`)
4. Present stack rationale + all 3 diagrams inline to user
5. Wait for user confirmation — iterate until approved
6. `save_session.py --field tech_stack --data '{...}'`
7. `save_session.py --field diagrams --data '{...}'`
9. `write_phase_doc.py --id PROJECT_ID --phase architecture`
10. `save_session.py --field status --data '"planning"'`

**Output**: `session.tech_stack`, `session.diagrams`, `docs/architecture.md`, `status = planning`

---

## Phase 4 — PLANNING

**Goal**: Complete, ordered, weighted backlog with one test per task. Every task must reference the spec contracts it implements.

**Context**: Load `docs/spec.md` + `docs/architecture.md`. Every task must trace back to at least one F- or M-contract.

**Steps**:
1. `sync_context.py`; read `{output_dir}/docs/spec.md` and `{output_dir}/docs/architecture.md`
2. Decompose in this order (mandatory):
   ```
   0  scaffold   → project setup, env, linting, CI skeleton
   1  database   → schema migrations
   2  backend    → data models, ORM
   3  backend    → services, domain logic
   4  api        → REST/GraphQL routes
   5  auth       → middleware, guards
   6  frontend   → scaffold, router, layout
   7  frontend   → components per feature
   8  integration → frontend ↔ API wiring
   9  testing    → integration + E2E
   10 infra      → Docker, deployment
   11 infra      → CI/CD pipeline
   ```
3. Each task: `id`, `title`, `description`, `spec_refs`, `layer`, `story_points`, `priority`, `status: pending`, `test_command`, `dependencies`, `acceptance_criteria`
4. Story points: Fibonacci 1–8; anything ≥13 must be split
5. Every task MUST have `test_command` AND `spec_refs` — no exceptions. A task that can't reference a spec contract should not exist.
6. Present as table, wait for confirmation, apply feedback
7. `save_session.py --field backlog --data '[...]'`
8. `write_phase_doc.py --id PROJECT_ID --phase backlog`
9. `save_session.py --field status --data '"implementation"'`

**Output**: `session.backlog`, `docs/backlog.md`, `status = implementation`

---

## Phase 5 — IMPLEMENTATION LOOP

**Goal**: Implement and test every pending task in priority order, satisfying every acceptance criterion from the referenced spec contracts.

**For each `pending` task (by `priority` ascending)**:

### 5a. Context Injection (per task — not full session)
```bash
python .agents/skills/forgestack/scripts/sync_context.py --id PROJECT_ID
```
Then read **only the F- and M-contracts referenced in `task.spec_refs`** from `{output_dir}/docs/spec.md`. Do not load the full spec.

### 5b. Dependency Check
All tasks in `dependencies[]` must be `status: complete`. If not, implement them first.

### 5c. Implementation
- Write complete, production-ready code to `{output_dir}/`
- Scan existing files first to follow established patterns
- No TODOs, stubs, or placeholder logic
- All secrets via environment variables → `.env.example`
- Every acceptance criterion in `task.spec_refs` is your definition of done

### 5d. Test / Auto-Fix Loop
```bash
cd {output_dir} && {task.test_command}
```

| Result | Action |
|--------|--------|
| PASS | Mark `complete`, save session, move to next task |
| FAIL (attempt 1) | Diagnose, apply minimal fix, retry |
| FAIL (attempt 2) | Diagnose, apply different fix, retry |
| FAIL (attempt 3) | Diagnose, log error, mark `failed`, ask user |

### 5e. Save After Every Task
```bash
python .agents/skills/forgestack/scripts/save_session.py \
  --id PROJECT_ID --field backlog --data '[updated array]'
```

---

## Phase 5 — COMPLETE

**Steps**:
1. `save_session.py --field status --data '"complete"'`
2. Print summary:

```
✅ ForgeStack Build Complete

Project:    <name>
ID:         <project-id>
Output:     <output_dir>/
Stack:      <language> / <backend> / <frontend> / <database>

Tasks:      N complete, N failed
Story pts:  N total

Run the app:   <startup command from tech stack>
Resume later:  python .agents/skills/forgestack/scripts/load_session.py --id <id>
```

---

## Context Recovery (Interrupted Sessions)

If context is lost at any point:

```bash
python .agents/skills/forgestack/scripts/list_projects.py
python .agents/skills/forgestack/scripts/load_session.py --id PROJECT_ID
python .agents/skills/forgestack/scripts/sync_context.py --id PROJECT_ID
```

Pick up from `session.status`. Never restart from scratch.

---

## Task Layer Sequencing Rules

- A `frontend` task must always depend on its corresponding `api` task
- An `api` task must depend on the `backend` service/model task it exposes
- A `backend` task must depend on the `database` schema task for its entities
- `auth` must depend on at least one `api` task and one `backend` user model
- `testing` and `integration` tasks depend on all tasks they cover
- `infra` tasks depend on the full application being implemented

---

## Story Point Guidelines

| Points | Effort | Example |
|--------|--------|---------|
| 1 | Trivial | Add a single field to a schema, create a health check endpoint |
| 2 | Small | One simple CRUD endpoint with tests |
| 3 | Medium | Full feature with multiple endpoints and tests |
| 5 | Large | Auth system, complex UI page with state |
| 8 | XL | Full integration layer, entire frontend scaffold |
| 13+ | SPLIT | Must be decomposed — no 13-point tasks allowed |
