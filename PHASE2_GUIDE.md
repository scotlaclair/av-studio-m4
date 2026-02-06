# Phase 2 Completion Guide

## Overview

Phase 2 involves creating 34 GitHub issues from the task breakdown in `spec-kit/tasks.md`. The automation tools have been created and are ready to use.

## Automated Tools Created

1. **GitHub Actions Workflow**: `.github/workflows/create-task-issues.yml`
   - Triggers manually via GitHub UI or CLI
   - Has proper permissions to create issues
   - Can create all issues or filter by phase

2. **Python Script**: `scripts/create_task_issues.py`
   - Can be run locally with gh CLI
   - Supports dry-run mode for preview
   - Flexible phase filtering

## How to Complete Phase 2

### Option 1: GitHub Actions (Recommended)

This method works best because GitHub Actions has the necessary permissions.

1. **Merge this PR first** (or push to main branch)

2. **Trigger the workflow** via GitHub UI:
   - Go to **Actions** tab
   - Select **"Create Task Issues from spec-kit/tasks.md"**
   - Click **"Run workflow"**
   - Choose phase (default: "all")
   - Click **"Run workflow"**

3. **Or use gh CLI**:
   ```bash
   # After PR is merged to main
   gh workflow run create-task-issues.yml

   # Or create for specific phase
   gh workflow run create-task-issues.yml -f phase=1
   ```

### Option 2: Local Script

If you prefer to run locally:

1. **Install dependencies**:
   ```bash
   pip install PyYAML
   ```

2. **Authenticate gh CLI** (if not already):
   ```bash
   gh auth login
   ```

3. **Run the script**:
   ```bash
   # Preview what will be created (dry-run)
   python scripts/create_task_issues.py --dry-run

   # Create all issues
   python scripts/create_task_issues.py

   # Create issues for specific phase
   python scripts/create_task_issues.py --phase 1
   ```

## What Gets Created

### Summary by Phase

- **Phase 1** (6 tasks): INFRA-001 to INFRA-003, CFG-001 to CFG-003
- **Phase 2** (5 tasks): GW-001 to GW-005
- **Phase 3** (4 tasks): LLM-001 to LLM-004
- **Phase 4** (6 tasks): AUD-001 to AUD-006
- **Phase 5** (5 tasks): AGT-001 to AGT-005
- **Phase 6** (5 tasks): API-001 to API-005
- **Phase 7** (3 tasks): MCP-001 to MCP-003

**Total: 34 issues** (32 tasks + some with subtasks)

### Issue Format

Each issue includes:
- **Title**: `[TASK-ID] Task title`
- **Labels**: Priority (P0-P3), Type (feature/infra/etc), Phase (1-7)
- **Body**:
  - Task metadata (type, priority, estimate, assignee type)
  - Dependencies (if any)
  - Acceptance criteria (as checkboxes)
  - Files to create/modify
  - Test files needed
  - Links to spec documentation

## Post-Creation Tasks

After all issues are created:

1. **Verify Issue Count**: Should have 32-34 issues created
2. **Check Labels**: All issues should have priority, type, and phase labels
3. **Review Dependencies**: Some issues reference dependencies by task ID
4. **Update Issue #1**: Mark Phase 2 as complete
5. **Close this PR**: Phase 1 and 2 automation complete

## Labels Expected

The script will use these labels (they'll be auto-created if they don't exist):

- **Priority**: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`
- **Type**: `type:infra`, `type:feature`, `type:test`, `type:docs`, `type:refactor`
- **Phase**: `phase-1`, `phase-2`, `phase-3`, `phase-4`, `phase-5`, `phase-6`, `phase-7`

## Notes

- **INFRA-001** and **INFRA-002** are already completed (in PR #2 - Phase 1)
- You may want to immediately close those issues as done
- **CFG-001** to **CFG-003** should be started next as they're P0 dependencies
- The issues will NOT auto-link dependencies - that needs to be done manually or with a follow-up script

## Troubleshooting

### "Label not found" errors
GitHub will auto-create labels that don't exist, so this shouldn't be an issue.

### "Permission denied" errors
Make sure you're using GitHub Actions (which has `issues: write` permission) or that your gh CLI is properly authenticated.

### Script doesn't find tasks.md
Make sure you're running from the repository root directory.

## Next Steps After Phase 2

Once all issues are created:

1. Start working on **CFG-001** (Implement settings module)
2. Follow the task dependencies in order
3. Reference the spec-kit documentation for each task
4. Create PRs with max 500 lines as specified in the constitution

---

**Created by**: Phase 1/2 Setup
**Status**: Ready to execute
