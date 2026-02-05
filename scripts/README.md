# Phase 2: Task Issue Creation

This directory contains automation tools for creating GitHub issues from the task breakdown in `spec-kit/tasks.md`.

## Overview

Phase 2 creates individual GitHub issues for all 47 tasks defined in the spec-kit. Each issue includes:
- Task ID and title in format `[TASK-ID] Title`
- Full task details (type, priority, estimate, dependencies)
- Acceptance criteria as checkboxes
- Files to create/modify
- Proper labels (priority, phase, type)
- References to specification documents

## Methods

### Method 1: GitHub Actions Workflow (Recommended)

Trigger the workflow via GitHub UI or gh CLI:

```bash
# Create all issues
gh workflow run create-task-issues.yml

# Create issues for specific phase
gh workflow run create-task-issues.yml -f phase=1
```

### Method 2: Python Script

Run locally with gh CLI authenticated:

```bash
# Install dependencies
pip install PyYAML

# Create all issues
python scripts/create_task_issues.py

# Create issues for specific phase
python scripts/create_task_issues.py --phase 1

# Dry run to preview
python scripts/create_task_issues.py --dry-run
```

## Task Organization

### Phase 1: Foundation (11 tasks)
- **INFRA-001 to INFRA-003**: Infrastructure setup
- **CFG-001 to CFG-003**: Configuration system

### Phase 2: Gateway Layer (5 tasks)
- **GW-001 to GW-005**: Smart router, auth, rate limiting

### Phase 3: LLM Integration (4 tasks)
- **LLM-001 to LLM-004**: MLX, Ollama, external APIs, unified interface

### Phase 4: Audio Processing (6 tasks)
- **AUD-001 to AUD-006**: Demucs, Whisper, effects, pipeline

### Phase 5: Agent System (5 tasks)
- **AGT-001 to AGT-005**: Base agent, orchestrator, specialized agents

### Phase 6: API Layer (5 tasks)
- **API-001 to API-005**: FastAPI endpoints for all services

### Phase 7: MCP Server (3+ tasks)
- **MCP-001 to MCP-003+**: MCP server and tools

## Labels

Issues are automatically labeled with:

- **Priority**: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- **Type**: `type:infra`, `type:feature`, `type:test`, etc.
- **Phase**: `phase-1` through `phase-7`

## Notes

- INFRA-001 and INFRA-002 are already completed (PR #2)
- Dependencies are noted but not auto-linked (manual linking required)
- All issues reference the spec-kit documentation
