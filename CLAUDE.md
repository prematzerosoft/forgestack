# ForgeStack — Claude Code Instructions

> Claude Code reads this file automatically. All instructions below are active.
> Full workflow: see `AGENTS.md` (universal instructions).

---

**ForgeStack = build apps from idea → code.**

## 3 Laws
1. **Stateful** — Load session before acting. Save after. Never hallucinate.
2. **Spec first** — Write contract before code. Spec = truth.
3. **Context clean** — Load only phase needs. Files persist, chat doesn't.

---

## Commands (Python 3.8+, no deps)

```bash
list_projects.py                                          # show all
init_project.py --name X --description Y                 # new project (prints ID)
load_session.py --id ID                                   # load state
save_session.py --id ID --field F --data JSON             # update field
sync_context.py --id ID [--slice full|task_only]          # context (inject before phase)
sync_context.py --id ID --slice task_only                 # lazy-load current task only
write_phase_doc.py --id ID --phase requirements|spec|arch|backlog  # write doc
validate_phase.py --id ID --phase spec|arch|planning|impl # gate (exits 1 if blocked)
micro_plan.py --id ID                                      # split large tasks into micro-tasks
```

---

## Workflow

### Always First
```bash
python .agents/skills/forgestack/scripts/list_projects.py
```
Ask: "Start new or resume?"
If resume: `load_session.py --id ID` → continue from `status` field.

### Phase 1 — INTAKE
Interview → save requirements JSON → `write_phase_doc.py --phase requirements` → status = "spec"

### Phase 2 — SPEC
Load requirements → write F/M contracts → save spec JSON → `write_phase_doc.py --phase spec` → status = "architecture"

### Phase 3 — ARCHITECTURE
Load spec → pick stack + 3 Mermaid diagrams → save + `write_phase_doc.py --phase architecture` → status = "planning"

### Phase 4 — PLANNING
Load spec + arch → decompose to tasks → save backlog → `write_phase_doc.py --phase backlog` → status = "implementation"

### Phase 5 — IMPLEMENTATION
For each pending task:
1. Load: `sync_context.py --id ID --slice task_only`
2. Check dependencies complete
3. Write complete, runnable code
4. Run test_command
5. PASS → mark complete, save, next
6. FAIL → fix, retry (max 3x)
7. Save progress

### Phase 6 — COMPLETE
Print summary + run instructions + offer to launch app.

---

## Key Points

- Every phase outputs to file: `docs/requirements.md`, `docs/spec.md`, `docs/architecture.md`, `docs/backlog.md`
- Spec = single source of truth (code adapts to spec, never vice versa)
- No TODOs, no stubs, no placeholders (complete code only)
- Every task → spec_refs + test_command
- Fibonacci points: 1, 2, 3, 5, 8 (split if >13)
- User confirmation after every phase

---

## Model Hint

See `MODEL_MAP.md` for cost-efficient model selection per phase:
- **INTAKE @ Haiku** (interview synthesis)
- **SPEC @ Haiku** (formula contracts)
- **ARCHITECTURE @ Sonnet** (complex reasoning, diagrams)
- **PLANNING @ Haiku** (mechanical decomposition)
- **IMPLEMENTATION @ Flash** (code generation)
- **QA @ Haiku** (test execution)

---

## Resume Anytime

```bash
python .agents/skills/forgestack/scripts/sync_context.py --id ID
```

Read phase doc at `output/{ID}/docs/{status}.md`. Continue from there.
