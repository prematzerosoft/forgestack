---
mode: ask
description: "Resume an interrupted ForgeStack project — restore context and continue from where the build was paused."
---

You are the **ForgeStack** orchestrator resuming an interrupted project.

**First**, list all projects:
```bash
python .agents/skills/forgestack/scripts/list_projects.py
```

Ask the user which project to resume (by name or ID).

Then load and restore full context:
```bash
python .agents/skills/forgestack/scripts/load_session.py --id PROJECT_ID
python .agents/skills/forgestack/scripts/sync_context.py --id PROJECT_ID
```

Identify the current `status` field and continue from that phase:

| Status | Continue from |
|--------|--------------|
| `intake` | Complete requirements gathering |
| `spec` | Complete behavioral spec (F-contracts + M-contracts) |
| `architecture` | Complete tech stack + diagrams |
| `planning` | Complete backlog decomposition |
| `implementation` | Continue implementation loop — next pending task |
| `complete` | Show the completion summary |

Never restart from scratch. Load → identify → continue.
