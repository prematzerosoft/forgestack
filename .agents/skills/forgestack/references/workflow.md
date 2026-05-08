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
   - **App type**: `web` | `mobile` | `desktop` | `cli` | `api`
     - `web` — browser UI | `mobile` — iOS/Android | `desktop` — native OS app | `cli` — command-line tool | `api` — backend only
   - Auth required? What kind?
   - Scale: small / medium / large / enterprise
   - Technology preference (or "recommend")
   - Hard constraints (compliance, budget, existing infra)
4. Detect (or ask) the **local runtime environment**:
   - Does the user have **Docker** available? (`docker --version`)
   - If not, what is their native runtime? (e.g. Node 20, Python 3.12, Bun)
   - What is the intended **deployment target**? (e.g. VPS, Fly.io, Vercel, Railway, local-only)
   - Store the result as `local_env: "docker" | "native" | "unknown"` and `deploy_target`
   - If unknown, default to `"native"` with a note — never assume Docker is present
5. Synthesize answers into `requirements` JSON
6. Read back to user → confirm → apply corrections
7. `save_session.py --field requirements --data '{...}'`
8. `write_phase_doc.py --id PROJECT_ID --phase requirements`
9. `save_session.py --field status --data '"spec"'`

**Output**: `session.requirements` object, `docs/requirements.md`, `status = spec`

---

## Phase 2 — SPEC

**Goal**: Write a behavioral contract (spec) for every feature. This is the single source of truth — code adapts to the spec, never the other way.

**Context**: Load `docs/requirements.md` only. Do not rely on conversation history.

**Steps**:
1. `sync_context.py` — restore awareness
2. Read `{output_dir}/docs/requirements.md`
3. For every feature, write an **F-contract** — format depends on `requirements.app_type`:

   **web / api / mobile** — HTTP endpoint contract:
   - Endpoint + HTTP method, request shape, all response codes + bodies
   - Acceptance criteria (testable, specific), error cases

   **desktop / cli** — action/command contract (no HTTP, no endpoint):
   - Trigger (menu item, keyboard shortcut, CLI flag), input, outcome
   - State stored or mutated, acceptance criteria, error cases

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
2. Based on the spec and `requirements.app_type`, choose:
   - **Language** — what genuinely fits (not your default)
   - **UI layer** — branch by `app_type`:
     - `web` → React, Vue, Next.js, SvelteKit, HTMX
     - `mobile` → React Native / Expo, Flutter, Swift, Kotlin
     - `desktop` → Tauri (Rust + web UI, lightest), Electron (Node + web UI), Flutter Desktop, .NET MAUI, Qt
     - `cli` → no UI; Go, Rust, Python+typer
     - `api` → no UI
   - **Backend / logic**: FastAPI, Express, Rails, Go Fiber, Spring Boot — or embedded in the desktop app if no server is needed
   - **Database**: SQL vs NoSQL; for desktop with no server, use SQLite embedded
   - **Auth**: JWT, sessions, OAuth2, magic links; for offline desktop use OS credential store / keychain
   - **Distribution**:
     - `web/api` → Docker, serverless, VPS, k8s
     - `desktop` → platform installers (`.dmg`, `.exe`, `.AppImage`), auto-updater
     - `mobile` → App Store / Play Store
     - `cli` → binary releases, Homebrew tap, package registry
3. Write 3 diagram files to `{output_dir}/docs/diagrams/` as **Markdown files** containing a fenced Mermaid code block. This format is directly previewable in VS Code (`Ctrl+Shift+V` / `Cmd+Shift+V`):
   - `flowchart.md` — end-to-end user flow (`flowchart TD`)
   - `component.md` — all system components (`graph LR`)
   - `sequence.md` — primary interaction (`sequenceDiagram`)

   Each file must follow this structure:
   ````markdown
   # <Diagram Title>

   > <one-line description>

   ```mermaid
   flowchart TD
     ...
   ```
   ````
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
                   Always includes: .env.example, README.md with local-run instructions
   1  environment → CONDITIONAL on requirements.app_type + requirements.local_env:

                   IF app_type == "web" or "api" or "mobile" (with backend):
                     IF local_env == "docker":
                       - docker-compose.yml (all services: app + db + cache etc.)
                       - Multi-stage Dockerfile per service (dev target + prod target)
                       - Same base image locally and on server (e.g. node:20-alpine)
                       - No globally-installed CLI tools as runtime deps
                     IF local_env == "native" (or Docker not available):
                       - Process manager script (e.g. Procfile or start.sh)
                       - SQLite for dev DB; in-memory/file-based cache fallback
                       - .env.example documents what to install natively
                       - README includes native install + deployment instructions
                     ALWAYS produce a Dockerfile + docker-compose.yml for the deploy_target
                     (CI/CD and production), regardless of local_env.

                   IF app_type == "desktop":
                     - No Docker needed for local dev
                     - Dev task: native build script (e.g. `cargo tauri dev`, `npm run electron:dev`)
                     - Package/installer task: platform-specific bundler config
                         Tauri     → tauri.conf.json + `cargo tauri build`
                         Electron  → electron-builder config + `npm run dist`
                         Flutter   → `flutter build macos/windows/linux`
                     - CI/CD: build installers per platform in GitHub Actions
                     - Auto-updater config if applicable

                   IF app_type == "cli":
                     - Native build script; single binary output
                     - Release workflow: cross-compile per platform, attach to GitHub Release

                   IF app_type == "mobile":
                     - Expo / React Native: `npx expo start` locally; EAS Build for distribution
                     - Flutter: `flutter run` locally; build per target (apk, ipa)

   2  database   → schema migrations
   3  backend    → data models, ORM
   4  backend    → services, domain logic
   5  api        → REST/GraphQL routes
   6  auth       → middleware, guards
   7  frontend   → scaffold, router, layout
   8  frontend   → components per feature
   9  integration → frontend ↔ API wiring
   10 testing    → integration + E2E
   11 infra      → CI/CD pipeline (builds Docker image, runs tests, pushes to registry)
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

## Phase 6 — COMPLETE

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
```

3. Print the **How to Run Locally** section — adapted to `requirements.app_type` + `requirements.local_env`:

```
── How to Run Locally ─────────────────────────────────────
1. Copy environment variables (if applicable):
     cp .env.example .env

── IF app_type == "web" or "api" ──────────────────────────
  IF local_env == "docker":
    docker compose up --build
    Open: <local URL> | Test: docker compose run --rm app <test command>
  IF local_env == "native":
    <install command>  +  <backend start>  +  <frontend start>
    Open: <local URL> | Test: <test command>

── IF app_type == "desktop" ───────────────────────────────
  Dev:  <dev start>  (e.g. cargo tauri dev / npm run electron:dev / flutter run)
  App opens as a native window — no browser needed
  Test: <test command>  |  Release: <build command>

── IF app_type == "mobile" ────────────────────────────────
  <start command>  (e.g. npx expo start / flutter run)
  Scan QR with Expo Go, or run on simulator | Test: <test command>

── IF app_type == "cli" ───────────────────────────────────
  <build command>  |  Run: <binary> --help  |  Test: <test command>
───────────────────────────────────────────────────────────
```

4. **Run the full test suite before launch**:
   ```bash
   cd {output_dir} && {full test command for the stack}
   ```
   - If all tests pass: proceed to launch offer
   - If any test fails: diagnose, apply a minimal fix, re-run — do not offer to launch until tests are green

5. **Offer to launch the app**:
   - Ask: *"Would you like me to start the app now so you can test it?"*
   - If yes: use the start command appropriate for `app_type` + `local_env` and stream logs.
   - While the app is running, **monitor stdout/stderr continuously**:
     - Surface any error, warning, or crash line to the user immediately
     - If a runtime error appears, diagnose and apply a fix, then restart — do not wait for the user to report it
   - If the app fails to start, read the error, apply a fix, and retry once.

5. Print resume pointer:
```
Resume later: python .agents/skills/forgestack/scripts/load_session.py --id <id>
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
