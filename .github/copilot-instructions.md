# Copilot Instructions for av-studio-m4

## Branch Strategy
- **Default branch**: `dev`
- **All PRs should target**: `dev` branch
- **Production branch**: `main` (protected, PRs only from `dev`)

## AI Agent Permissions
The following AI agents have autonomy on the `dev` branch:
- @copilot (GitHub Copilot bot)
- @claude
- @codex
- @gemini-code-assist

## Workflow
1. All feature branches should be created from `dev`
2. All pull requests from agents should target `dev`
3. When `dev` is stable and tested, create a PR from `dev` to `main`
4. `main` branch is protected and represents production-ready code

## Development Guidelines
- Work freely on `dev` branch
- Run tests before merging to `dev`
- Only merge to `main` after thorough testing on `dev`
