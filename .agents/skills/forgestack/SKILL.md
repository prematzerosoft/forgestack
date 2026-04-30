---
name: forgestack
description: "Build complete full-stack production-ready applications autonomously. Use when: build an app, create a project, new application, scaffold, full stack, generate code, requirements to code, production ready app, new software project, develop application, create a system, SDLC automation."
argument-hint: "Describe the app to build, or say 'resume <project-id>' to continue"
---

# ForgeStack Skill

ForgeStack transforms your idea into a production-ready, full-stack application through an orchestrated five-phase workflow: Requirements → Architecture → Planning → Build → Validate.

## When to Use

- "Build me a task management app with React and FastAPI"
- "Create a REST API for an e-commerce platform with auth"
- "I need a full-stack app with a database and admin panel"
- "Resume ForgeStack project abc123"
- "Continue building MyApp"
- "What's the status of my ForgeStack project?"

## How It Works

### New Project
Tell ForgeStack what you want to build. It will:
1. **Interview you** for requirements (features, scaling, stack preference)
2. **Blueprint** the architecture with tech stack + Mermaid diagrams
3. **Plan** a weighted agile backlog (Database → Backend → API → Frontend → Tests → Infra)
4. **Build** every task with complete, production-ready code
5. **Validate** each task with automated tests, auto-fixing failures up to 3 times

### Resume a Project
Any interrupted build can be resumed from exactly where it left off:
```bash
python .agents/skills/forgestack/scripts/list_projects.py
python .agents/skills/forgestack/scripts/load_session.py --id <project-id>
```

## Session Scripts

All project state persists in `.forgestack/sessions/` via Python scripts (Python 3.8+, zero external deps):

| Script | Purpose |
|--------|---------|
| `init_project.py` | Create a new project session, prints project ID |
| `load_session.py --id ID` | Read full project state as JSON |
| `save_session.py --id ID --field F --data D` | Update a single session field |
| `sync_context.py --id ID` | Get compact awareness summary for context injection |
| `list_projects.py` | List all known project IDs and names |

See [state-schema](./references/state-schema.md) for the full session JSON format.

## Full Workflow

For the complete step-by-step SDLC procedure used by the orchestrator, see [workflow](./references/workflow.md).

## Provider Support

ForgeStack works with any AI agent runtime:

| Runtime | Entry Point |
|---------|------------|
| Any (universal) | `AGENTS.md` (root) |
| VS Code Copilot | `.github/agents/forgestack.agent.md` |
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursor/rules/forgestack.mdc` |
| OpenAI Codex | `AGENTS.md` |
| Gemini CLI | `AGENTS.md` |
