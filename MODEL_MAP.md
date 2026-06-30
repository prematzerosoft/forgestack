# ForgeStack Model Map — Token-Optimized Route

Maps each ForgeStack phase to the most cost-efficient model. Mix models to reduce cost by ~70% vs. using Sonnet for everything.

---

## Model Selection Matrix

| Phase | Primary Model | Fallback | Cost | Rationale |
|-------|---------------|----------|------|-----------|
| **INTAKE** | Haiku | Flash | $$ | Interview synthesis is straightforward text processing |
| **SPEC** | Haiku | Sonnet | $$$ | Contract writing is formulaic; Haiku handles repetition well |
| **ARCHITECTURE** | Sonnet | Opus | $$$$ | Requires multi-factor reasoning; diagrams need spatial thinking |
| **PLANNING** | Haiku | Sonnet | $$$ | Task decomposition is mechanical; Haiku sufficient |
| **IMPLEMENTATION** | Flash | Sonnet | $$ | Code generation is high-volume; Flash fine for atomic tasks |
| **QA** | Haiku | Flash | $$ | Test execution is deterministic; pass/fail validation |
| **COMPLETE** | Flash | Haiku | $$ | Summary synthesis |

---

## Cost Breakdown (Per Project)

### Current Approach (All Sonnet)
```
INTAKE:           5k tokens @ Sonnet  = $0.075
SPEC:            20k tokens @ Sonnet  = $0.30
ARCHITECTURE:    40k tokens @ Sonnet  = $0.60
PLANNING:        20k tokens @ Sonnet  = $0.30
IMPLEMENTATION: 100k tokens @ Sonnet  = $1.50
QA:               5k tokens @ Sonnet  = $0.075
COMPLETE:         2k tokens @ Sonnet  = $0.03
─────────────────────────────────────────
Total: ~$3.30 per project
```

### Optimized Approach (Model-Mixed)
```
INTAKE:           4k tokens @ Haiku   = $0.00048
SPEC:            12k tokens @ Haiku   = $0.00144
ARCHITECTURE:    35k tokens @ Sonnet  = $0.525
PLANNING:        15k tokens @ Haiku   = $0.0018
IMPLEMENTATION:  60k tokens @ Flash   = $0.018
QA:               3k tokens @ Haiku   = $0.00036
COMPLETE:         1k tokens @ Flash   = $0.003
─────────────────────────────────────────
Total: ~$0.55 per project (-83% cost)
```

---

## Using Model Map in Agents

### In Agent YAML Frontmatter
```yaml
---
model: ["Claude Haiku 3.5 (copilot)", "Claude 3.5 Sonnet (copilot)"]
model_hint: "Use Haiku (interview synthesis cheap, straightforward)"
---
```

### In Agent Prompt
```markdown
## Model Hint
Use **Claude Haiku 3.5** for this phase (token-efficient).
Falls back to Sonnet if formula reasoning fails.

Do NOT use Opus; insufficient ROI for this phase.
```

### Runtime Override
```bash
# Agent can suggest override if needed
"Model hint: Switch to Sonnet if reaching Haiku token limit"
```

---

## When to Override

**Use Sonnet/Opus instead of Haiku if:**
- Task requires multi-turn reasoning (loops, backtracking)
- Generating complex diagrams (architecture phase)
- Code generation needs deep type inference
- Agent logs show Haiku confabulation or errors

**Stay with Haiku/Flash if:**
- Task is mechanical (decomposition, contract repetition)
- Output is deterministic (test execution, validation)
- High volume of similar tasks (100s of interviews, specs)

---

## Model Feature Comparison

| Feature | Haiku | Flash | Sonnet | Opus |
|---------|-------|-------|--------|------|
| Token speed | ⚡⚡⚡ | ⚡⚡ | ⚡ | ⚡ |
| Reasoning depth | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Code quality | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| JSON parsing | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Cost (per 1M tokens) | $0.80 | $3.00 | $7.50 | $15.00 |

---

## Multi-Model Example: Full Build

```
User: "Build me a task manager app"
↓
INTAKE @ Haiku
  Interview user → save requirements
  Cost: $0.00048
↓
SPEC @ Haiku
  Write F/M contracts (formulaic)
  Cost: $0.00144
↓
ARCHITECTURE @ Sonnet ← switch here (complex reasoning)
  Design stack, generate diagrams
  Cost: $0.525
↓
PLANNING @ Haiku
  Decompose to tasks (mechanical)
  Cost: $0.0018
↓
IMPLEMENTATION (per task) @ Flash
  Generate code atomically
  Cost: $0.018 per task × 20 tasks = $0.36 total
↓
QA @ Haiku
  Run tests, report results
  Cost: $0.00036

TOTAL: ~$0.90 (vs $3.30 @ Sonnet-only)
```

---

## Adoption Strategy

### Phase 1: Soft Launch
- Add `model_hint` to agent YAML frontmatter (non-breaking)
- Agents default to current behavior (backward compat)
- Documented in README as optional optimization

### Phase 2: Agent-Driven Selection
- Agents read MODEL_MAP.md at runtime
- Make recommendation: "Using Haiku for this phase (recommended)"
- User can override if needed

### Phase 3: Full Integration
- All agents default to model-mixed strategy
- Opt-out flag for users who prefer single model
- Central config file (MODEL_MAP.md) as source of truth

---

## Monitoring & Adjustment

Track per-project:
- Total tokens used (should be ~70% reduction)
- Per-phase model used
- Any Haiku→Sonnet fallbacks (indicates formula complexity)
- Quality metrics (spec compliance, test pass rate)

Adjust if:
- Haiku token cost > Sonnet (backtracking loops)
- Error rate > 2% (model too weak for phase)
- User complains about quality on specific phase

---

## Reference: Provider-Specific Model IDs

### OpenAI (Copilot, etc)
- Haiku → *(use Claude 3.5 Haiku via Claude integration if available)*
- Flash → `gpt-4o-mini`
- Sonnet → `gpt-4o`
- Opus → *(use gpt-4-turbo if needed)*

### Claude (native)
- Haiku → `claude-3-5-haiku-20241022`
- Flash → `claude-3-5-haiku-20241022` (note: no "Flash" in Claude; use Haiku)
- Sonnet → `claude-3-5-sonnet-20241022`
- Opus → `claude-3-opus-20250219`

### Gemini (Google)
- Haiku → `gemini-1.5-flash-8b` (lightweight)
- Flash → `gemini-2.0-flash`
- Sonnet → `gemini-2.0-pro` (or `gemini-pro`)
- Opus → *(use gemini-2.0-pro-exp if available)*

