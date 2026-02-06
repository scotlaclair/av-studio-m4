#!/usr/bin/env python3
"""
Script to create GitHub issues from spec-kit/tasks.md

This script parses the tasks.md file and creates GitHub issues for each task
using the GitHub CLI (gh). It requires 'gh' to be installed and authenticated.

Usage:
    python scripts/create_task_issues.py [--phase PHASE] [--dry-run]

Options:
    --phase PHASE   Create issues for specific phase (1-7) or 'all' (default: all)
    --dry-run       Print what would be created without actually creating issues
"""

import re
import sys
import argparse
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    sys.exit(1)


def parse_tasks_file(file_path):
    """Parse the tasks.md file and extract all task definitions."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Find all YAML blocks
    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)

    tasks = []

    for block in yaml_blocks:
        try:
            # Parse YAML block which may contain multiple tasks
            items = yaml.safe_load(block)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and 'id' in item:
                        tasks.append(item)
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing YAML block: {e}")
            continue

    return tasks


def determine_phase(task_id):
    """Determine phase number from task ID."""
    phase_map = {
        'INFRA-': 1, 'CFG-': 1,
        'GW-': 2,
        'LLM-': 3,
        'AUD-': 4,
        'AGT-': 5,
        'API-': 6,
        'MCP-': 7,
    }

    for prefix, phase in phase_map.items():
        if task_id.startswith(prefix):
            return phase
    return 0


def format_issue_body(task):
    """Format the issue body from task data."""
    task_id = task['id']

    body_parts = [
        f"## Task: {task_id}",
        "",
        f"**Type:** {task.get('type', 'N/A')}",
        f"**Priority:** {task.get('priority', 'N/A')}",
        f"**Estimate:** {task.get('estimate', 'N/A')} hours",
        f"**Assignee Type:** {task.get('assignee', 'N/A')}",
        "",
    ]

    # Add dependencies
    if task.get('dependencies'):
        deps = task['dependencies']
        if deps:
            body_parts.append("### Dependencies")
            for dep in deps:
                body_parts.append(f"- Task: `{dep}` (will be linked after all issues are created)")
            body_parts.append("")

    # Add acceptance criteria
    if task.get('acceptance_criteria'):
        body_parts.append("### Acceptance Criteria")
        for criterion in task['acceptance_criteria']:
            body_parts.append(f"- [ ] {criterion}")
        body_parts.append("")

    # Add files to create
    if task.get('files_to_create'):
        body_parts.append("### Files to Create")
        for file in task['files_to_create']:
            body_parts.append(f"- `{file}`")
        body_parts.append("")

    # Add files to modify
    if task.get('files_to_modify'):
        body_parts.append("### Files to Modify")
        for file in task['files_to_modify']:
            body_parts.append(f"- `{file}`")
        body_parts.append("")

    # Add tests
    if task.get('tests'):
        body_parts.append("### Tests")
        for test in task['tests']:
            body_parts.append(f"- `{test}`")
        body_parts.append("")

    # Add reference to spec
    body_parts.extend([
        "---",
        "",
        "### References",
        "- **Task Breakdown:** [spec-kit/tasks.md](../blob/main/spec-kit/tasks.md)",
        "- **Specification:** [spec-kit/spec.md](../blob/main/spec-kit/spec.md)",
        "- **Architecture Plan:** [spec-kit/plan.md](../blob/main/spec-kit/plan.md)",
        "- **Constitution:** [spec-kit/constitution.md](../blob/main/spec-kit/constitution.md)",
    ])

    return "\n".join(body_parts)


def get_labels(task):
    """Determine GitHub labels for a task."""
    labels = []
    task_id = task['id']

    # Priority label
    priority = task.get('priority', 'P2')
    priority_labels = {
        'P0': 'P0-critical',
        'P1': 'P1-high',
        'P2': 'P2-medium',
        'P3': 'P3-low',
    }
    if priority in priority_labels:
        labels.append(priority_labels[priority])

    # Type label
    task_type = task.get('type', 'feature')
    labels.append(f"type:{task_type}")

    # Phase label
    phase = determine_phase(task_id)
    if phase > 0:
        labels.append(f"phase-{phase}")

    return labels


def create_issue(task, dry_run=False):
    """Create a GitHub issue for a task."""
    task_id = task['id']
    title = f"[{task_id}] {task['title']}"
    body = format_issue_body(task)
    labels = get_labels(task)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"Would create issue: {title}")
        print(f"Labels: {', '.join(labels)}")
        print(f"\nBody preview (first 200 chars):")
        print(body[:200] + "...")
        return True

    # Create the issue using gh CLI
    labels_str = ','.join(labels)

    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
        '--label', labels_str
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issue_url = result.stdout.strip()
        print(f"✓ Created: {title}")
        print(f"  URL: {issue_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create issue {title}")
        print(f"  Error: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from spec-kit/tasks.md'
    )
    parser.add_argument(
        '--phase',
        default='all',
        help='Create issues for specific phase (1-7) or "all" (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be created without actually creating issues'
    )

    args = parser.parse_args()

    # Find the project root (where spec-kit/ is located)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tasks_file = project_root / 'spec-kit' / 'tasks.md'

    if not tasks_file.exists():
        print(f"Error: {tasks_file} not found")
        sys.exit(1)

    # Parse tasks
    print(f"Parsing {tasks_file}...")
    tasks = parse_tasks_file(tasks_file)
    print(f"Found {len(tasks)} tasks\n")

    # Filter by phase if specified
    phase_filter = args.phase
    if phase_filter != 'all':
        try:
            phase_num = int(phase_filter)
            if phase_num < 1 or phase_num > 7:
                print("Error: Phase must be between 1 and 7")
                sys.exit(1)
        except ValueError:
            print("Error: Phase must be a number (1-7) or 'all'")
            sys.exit(1)

    # Create issues
    created_count = 0
    failed_count = 0

    for task in tasks:
        task_id = task['id']
        task_phase = determine_phase(task_id)

        # Filter by phase if specified
        if phase_filter != 'all' and str(task_phase) != phase_filter:
            continue

        success = create_issue(task, dry_run=args.dry_run)
        if success:
            created_count += 1
        else:
            failed_count += 1

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    if args.dry_run:
        print(f"  Would create: {created_count} issues")
    else:
        print(f"  Created: {created_count} issues")
        if failed_count > 0:
            print(f"  Failed: {failed_count} issues")

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
