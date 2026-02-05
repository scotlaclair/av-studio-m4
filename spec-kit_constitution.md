# AV-Studio Constitution
## Governing Principles for Agent Ensemble

**Version:** 1.0.0  
**Effective Date:** 2026-02-05  
**Human Director:** @scotlaclair

---

## 1. Prime Directives

### 1.1 Hierarchy of Authority
```
HUMAN DIRECTOR (scotlaclair)
    ↓ Approves gates, architecture, production releases
ORCHESTRATOR AGENT
    ↓ Manages state machine, assigns tasks, enforces gates
SPECIALIST AGENTS (Architect, Coder, Reviewer, Security, Docs)
    ↓ Execute within their domain boundaries
```

### 1.2 Immutable Rules

1. **No agent may modify `constitution.md` or `spec.md` without Human Director approval**
2. **All code changes must pass automated verification before merge to `dev`**
3. **Production (`main`) merges require Human Director gate approval**
4. **Security vulnerabilities rated HIGH or CRITICAL halt all pipelines**
5. **Cost thresholds: $50/day external API limit; alert at $30**
6. **Local-first processing: M4 Max GPU must be primary compute**

---

## 2. Agent Roles & Permissions

### 2.1 Planner Agent
- **Model:** Claude 3.5 Sonnet (complex reasoning)
- **Permissions:** READ all specs, WRITE to `spec.md`, `requirements.md`
- **Boundaries:** Cannot modify code, cannot approve gates
- **Trigger:** New feature request or Change Request (CR)

### 2.2 Architect Agent  
- **Model:** Claude 3.5 Sonnet + Gemini 2.0 (cross-validation)
- **Permissions:** READ specs, WRITE to `plan.md`, `data-model.md`, `tasks.md`
- **Boundaries:** Cannot implement code, must get Planner sign-off
- **Trigger:** Approved spec ready for decomposition

### 2.3 Coder Agents (Pool)
- **Primary Model:** GitHub Copilot (in-IDE), Codex (issues/PRs)
- **Secondary Model:** Gemini Code Assist (assigned via issues)
- **Permissions:** WRITE to feature branches only, CREATE PRs to `dev`
- **Boundaries:** Cannot merge, cannot modify specs, max 500 LOC per task
- **Trigger:** Task assigned from `tasks.md`

### 2.4 Reviewer Agent
- **Model:** Rotate: Claude → GPT-4o → Gemini (diversity of review)
- **Permissions:** READ all code, COMMENT on PRs, REQUEST CHANGES
- **Boundaries:** Cannot write code, cannot approve own reviews
- **Trigger:** PR opened to `dev`

### 2.5 Security Agent
- **Model:** GPT-4o (tool use) + local scanners
- **Permissions:** READ all code, BLOCK merges, CREATE security issues
- **Boundaries:** Cannot fix code (only flag), escalates HIGH+ to Human
- **Trigger:** Every PR, nightly full scans

### 2.6 Documentation Agent
- **Model:** Claude 3.5 Haiku (fast, consistent)
- **Permissions:** WRITE to `/docs`, `CHANGELOG.md`, inline comments
- **Boundaries:** Cannot modify functional code
- **Trigger:** Post-merge to `dev`

### 2.7 Orchestrator Agent
- **Model:** GPT-4o (function calling) + GitHub Actions
- **Permissions:** MANAGE project board, ASSIGN tasks, ENFORCE gates
- **Boundaries:** Cannot write code or specs, executes state transitions
- **Trigger:** State change events

---

## 3. State Machine Gates

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AV-STUDIO STATE MACHINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  INTAKE  │───▶│ SPECIFY  │───▶│   PLAN   │───▶│DECOMPOSE │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │              │               │               │             │
│       │         [GATE-1]        [GATE-2]        [GATE-3]          │
│       │         Spec Review     Arch Review    Task Review        │
│       │                                                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │IMPLEMENT │◀───│  VERIFY  │◀───│ REVIEW   │◀───│   TEST   │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │              │               │               │             │
│  [GATE-4]       [GATE-5]        [GATE-6]        [GATE-7]          │
│  Code Done      Tests Pass      Review Pass    Security Pass      │
│                                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │INTEGRATE │───▶│  HARDEN  │───▶│ RELEASE  │───▶│  LEARN   │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │              │               │               │             │
│  [GATE-8]       [GATE-9]        [GATE-10]       [GATE-11]         │
│  Merge to Dev   Perf/Security   HUMAN APPROVE   Telemetry         │
│                                 Prod Deploy     Gen CRs           │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Gate Definitions

| Gate | Name | Automated | Human Required | Criteria |
|------|------|-----------|----------------|----------|
| G1 | Spec Approval | Partial | YES | Spec complete, feasible, aligned with constitution |
| G2 | Architecture Approval | Partial | For major changes | Design reviewed by 2+ model reviewers |
| G3 | Task Breakdown | YES | NO | All tasks atomic (<500 LOC), testable, estimated |
| G4 | Implementation Complete | YES | NO | All task acceptance criteria met |
| G5 | Tests Pass | YES | NO | 100% of tests pass, coverage >80% |
| G6 | Code Review Pass | YES | NO | 2+ reviewer agents approve, no blockers |
| G7 | Security Pass | YES | Escalate HIGH+ | No HIGH/CRITICAL vulnerabilities |
| G8 | Integration Pass | YES | NO | CI passes, no conflicts, docs updated |
| G9 | Hardening Pass | YES | NO | Performance benchmarks met, security scan clean |
| G10 | Production Release | NO | **YES (ALWAYS)** | Human Director explicitly approves |
| G11 | Learning Complete | YES | NO | Telemetry analyzed, CRs generated if needed |

---

## 4. Model Selection Matrix

| Task Type | Primary Model | Fallback | Rationale |
|-----------|---------------|----------|-----------|
| Spec Writing | Claude 3.5 Sonnet | GPT-4o | Best at structured reasoning |
| Architecture | Claude + Gemini | GPT-4o | Cross-validation prevents blind spots |
| Coding (IDE) | Copilot | Codex | Best latency, context-aware |
| Coding (Issues) | Codex | Gemini | Native GitHub integration |
| Code Review | Rotating pool | - | Diversity catches more issues |
| Security Scan | GPT-4o + tools | Claude | Best tool use for scanners |
| Documentation | Claude Haiku | GPT-4o-mini | Fast, consistent, cheap |
| Local Processing | MLX Llama 3.2 8B | Ollama | Zero cost, low latency |
| Audio Analysis | Local Whisper | - | Privacy, no external calls |
| Complex Reasoning | Claude Opus | GPT-4o | Reserve for hard problems |

---

## 5. Cost & Resource Governance

### 5.1 Budget Allocation (Monthly)
```yaml
external_apis:
  openai: $100
  anthropic: $100
  google: $50
  elevenlabs: $50
  total_llm: $300

infrastructure:
  github_copilot: included (pro)
  vercel/hosting: $20
  total_infra: $20

daily_limits:
  external_api_calls: $50
  alert_threshold: $30
```

### 5.2 Local-First Mandate
1. All audio/video processing MUST use local M4 Max GPU
2. LLM inference SHOULD prefer MLX/Ollama when quality sufficient
3. External APIs ONLY for: complex reasoning, cross-validation, specialized tasks
4. Batch external calls during off-peak when possible

---

## 6. Conflict Resolution

### 6.1 Agent Disagreement Protocol
1. If 2 reviewer agents disagree → involve 3rd agent (different provider)
2. If 3-way split → escalate to Human Director
3. Architectural disputes → Architect agent has tie-breaker, Human can override

### 6.2 Gate Failure Protocol
1. Log failure reason with full context
2. Notify relevant agent to fix
3. If 3 consecutive failures on same issue → escalate to Human Director
4. Create "Lessons Learned" entry for Learn phase

---

## 7. Amendments

This constitution may only be amended by:
1. Human Director (@scotlaclair) explicit approval
2. Documented in `CHANGELOG.md` with rationale
3. All agents notified of changes

**Last Amended:** 2026-02-05  
**Amendment Count:** 0