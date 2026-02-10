# Learnings & Insights

## Current Best Practices
- **Bento Logic**: Grouping information into high-context cards significantly reduces visual noise.
- **Terminal Constraints**: Always verify terminal permissions (Scratch vs Workspace) before running commands.
- **Atomic Pushes**: Frequent small pushes trigger faster GitHub Pages builds and reveal issues earlier.

## Issues & Mitigations
- **Playwright Environment**: Playwright requires a shell with full PATH access; running in `scratch` repo is the most reliable method.
