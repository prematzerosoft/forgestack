# ForgeStack

**Autonomous full-stack application factory for AI coding assistants.**

Clone this repo into your workspace and your AI assistant — Copilot, Claude, Cursor, Codex, or any AGENTS.md-compatible runtime — transforms into a Virtual Technical Lead that builds complete, tested, production-ready applications from requirements to deployed code.

---

## What ForgeStack Does

1. **INTAKE** — Interviews you to capture features, scale, constraints, and preferences
2. **SPEC** — Writes a behavioral contract (F-contracts + M-contracts) for every feature before any code is written
3. **ARCHITECTURE** — Recommends a technology stack and generates flowchart, component, and sequence diagrams
4. **PLANNING** — Decomposes the project into a weighted agile backlog (Fibonacci story points, spec refs, one test per task)
5. **IMPLEMENTATION** — Writes complete production code for each task, in dependency order, with an auto-fix loop on test failures
6. **DELIVERY** — Produces a runnable, tested, fully-scaffolded application in `output/<project-id>/`

All decisions are persisted to `.forgestack/sessions/` so any interruption is fully recoverable.

---

## Quick Start

### 1. Clone Into Your Workspace

```bash
git clone https://github.com/prematzerosoft/forgestack .forgestack-agent
```

Or add as a git submodule:
```bash
git submodule add https://github.com/prematzerosoft/forgestack .forgestack-agent
```

### 2. No Installation Required

The session scripts are plain Python 3.8+ with zero external dependencies. No `pip install`, no venv needed.

### 3. Invoke Your AI Assistant

| Runtime | How to Invoke |
|---------|--------------|
| **VS Code Copilot** | Open Chat → type `@ForgeStack build me a task manager` |
| **VS Code Copilot (prompt)** | Open Chat → `/new-project` |
| **Claude Code** | Start a session — `CLAUDE.md` loads automatically |
| **Cursor** | Open Chat — `.cursor/rules/forgestack.mdc` loads automatically |
| **Windsurf** | Open Cascade — `.windsurfrules` loads automatically |
| **JetBrains Junie** | Open Junie — `.junie/guidelines.md` loads automatically |
| **Amazon Q Developer** | Open Q Chat — `.amazonq/rules/forgestack.md` loads automatically |
| **OpenAI Codex** | `AGENTS.md` at repo root is read automatically |
| **Gemini CLI** | `AGENTS.md` at repo root is read automatically |
| **Aider** | `AGENTS.md` at repo root is read automatically |
| **Devin** | `AGENTS.md` at repo root is read automatically |
| **ChatGPT / Gemini web / Claude.ai** | Copy `SYSTEM_PROMPT.md` → paste as first message |
| **Any other chat UI** | Copy `SYSTEM_PROMPT.md` → paste as first message |
| **Any AGENTS.md runtime** | `AGENTS.md` at repo root is read automatically |

---

## Directory Structure

```
forgestack/
│
├── AGENTS.md                          # Universal entry point (all AGENTS.md runtimes)
├── CLAUDE.md                          # Claude Code adapter
├── SYSTEM_PROMPT.md                   # Copy-paste starter for any chat UI (ChatGPT, Gemini web, etc.)
├── LICENSE                            # MIT
│
├── .github/
│   ├── agents/
│   │   ├── forgestack.agent.md        # VS Code Copilot — main orchestrator (@ForgeStack)
│   │   ├── intake.agent.md            # Sub-agent: requirements gathering
│   │   ├── architect.agent.md         # Sub-agent: tech stack + diagrams
│   │   ├── planner.agent.md           # Sub-agent: backlog decomposition
│   │   ├── implementer.agent.md       # Sub-agent: code generation
│   │   └── qa.agent.md                # Sub-agent: test execution + auto-fix
│   └── prompts/
│       ├── new-project.prompt.md      # /new-project slash command
│       ├── resume-project.prompt.md   # /resume-project slash command
│       └── project-status.prompt.md  # /project-status slash command
│
├── .agents/
│   └── skills/
│       └── forgestack/
│           ├── SKILL.md               # Provider-neutral skill definition
│           ├── scripts/               # Session management (Python, no deps)
│           │   ├── list_projects.py
│           │   ├── init_project.py
│           │   ├── load_session.py
│           │   ├── save_session.py
│           │   ├── sync_context.py
│           │   └── write_phase_doc.py
│           └── references/
│               ├── state-schema.md    # Full session JSON schema
│               └── workflow.md        # Detailed SDLC procedure
│
├── .cursor/
│   └── rules/
│       └── forgestack.mdc             # Cursor IDE adapter
│
├── .windsurfrules                     # Windsurf (Cascade) adapter
│
├── .junie/
│   └── guidelines.md                  # JetBrains Junie adapter
│
├── .amazonq/
│   └── rules/
│       └── forgestack.md              # Amazon Q Developer adapter
│
└── .forgestack/                       # Runtime data (gitignored)
    └── sessions/
        └── <project-id>.json          # Persistent session state per project
```

---

## Session Awareness

ForgeStack never loses context. Every phase saves state to `.forgestack/sessions/<id>.json`. To recover from any interruption:

```bash
python .agents/skills/forgestack/scripts/list_projects.py
python .agents/skills/forgestack/scripts/sync_context.py --id PROJECT_ID
```

Then tell your AI assistant: `resume project PROJECT_ID`.

---

## Session Scripts

All scripts run from the repo root. Python 3.8+, zero dependencies.

```bash
# List all projects
python .agents/skills/forgestack/scripts/list_projects.py

# Start a new project (prints project ID)
python .agents/skills/forgestack/scripts/init_project.py --name "MyApp" --description "..."

# Load full session JSON
python .agents/skills/forgestack/scripts/load_session.py --id PROJECT_ID

# Update a session field
python .agents/skills/forgestack/scripts/save_session.py --id PROJECT_ID --field status --data '"planning"'

# Get compact awareness summary (inject at start of each phase)
python .agents/skills/forgestack/scripts/sync_context.py --id PROJECT_ID
```

---

## Requirements

- Python 3.8+ (for session scripts)
- An AI assistant with file-system access (Copilot, Claude Code, Cursor, Codex, etc.)
- No other dependencies

---

## License

MIT — see [LICENSE](LICENSE).

---

## Contributing

Issues and PRs welcome. See [AGENTS.md](AGENTS.md) for the full workflow specification that all agents follow.

This repository is being bootstrapped as an open-source MIT project for the Forgestack orchestrator.