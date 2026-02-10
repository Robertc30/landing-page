# Standard Operating Procedure (SOP) — TechQuest.AI

This document defines the high-agency workflow for all automated operations.

## 1. Pre-Flight Protocol
Before starting any task:
- [ ] View `implementation_plan.md` to confirm the current objective.
- [ ] View relevant `SKILL.md` or domain documentation.
- [ ] Update `ACTIVE-AGENTS.md` with the current task label and start time.

## 2. Execution Protocol (Pseudo-PR)
Every logical change must be:
1. **Verified**: Tested locally (using Playwright where applicable).
2. **Committed**: Using descriptive `feat:`, `fix:`, or `refactor:` prefixes.
3. **Pushed**: Immediately pushed to `master` to ensure the live environment reflects the latest state.

## 3. Reporting Protocol
After execution:
- [ ] Update `task.md` with progress.
- [ ] Log any unexpected behaviors or systemic improvements in `LEARNINGS.md`.
- [ ] Finalize the task in `ACTIVE-AGENTS.md`.

## 4. Quality Control (QC)
- [ ] Regularly run `qc-review.py` or equivalent visual audit scripts.
- [ ] Ensure 100% design system parity across all new files.
