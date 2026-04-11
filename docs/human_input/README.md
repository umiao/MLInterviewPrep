# Human Input Checklist

> Tasks requiring human-provided files before autonomous execution can continue.
> Use `/collect-input` to check status, get guidance, validate, and unblock tasks.

---

Pending:

- **EX-30 / EX-31 / EX-32 -- 3 failure-story placeholders** -- details:
  [`EX-30-32_failure_placeholders.md`](./EX-30-32_failure_placeholders.md).
  Seeded by `scripts/_seed_failure_placeholders.py` on 2026-04-11 as a
  follow-up to T-P0-351. The DB rows exist with empty STAR fields tagged
  `[NEEDS-INPUT]`; the user authors the real failure stories when ready.
  Until then, the `[Needs Input]` badge renders in the BehavioralQuestions
  UI and the STAR fields show "(missing -- pending user input)" fallbacks.

---

## Protocol

1. Read the detail file for the task you want to unblock
2. Follow the instructions to create/place the required files
3. Run `/collect-input validate <task-id>` to check your work
4. On pass, run `/collect-input unblock <task-id>` to remove the `[NEEDS-INPUT]` tag
