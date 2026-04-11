# Human Input Checklist

> Tasks requiring human-provided files before autonomous execution can continue.
> Use `/collect-input` to check status, get guidance, validate, and unblock tasks.

---

Pending:

_(none -- all open human-input slots have been resolved as of 2026-04-11)_

Resolved:

- **EX-30 / EX-31 / EX-32 failure-story placeholders** --
  [`EX-30-32_failure_placeholders.md`](./EX-30-32_failure_placeholders.md).
  EX-30 was populated with the Hash Capability Misdesign pure-failure story
  (T-P1-357). EX-31 and EX-32 were deleted after a coverage audit showed
  every failure-ask question already had real-content examples linked
  (EX-02, EX-13, EX-17, EX-18, EX-23, BLOG-01/02/03/04). The
  `[Needs Input]` badge no longer renders in the BehavioralQuestions UI.

---

## Protocol

1. Read the detail file for the task you want to unblock
2. Follow the instructions to create/place the required files
3. Run `/collect-input validate <task-id>` to check your work
4. On pass, run `/collect-input unblock <task-id>` to remove the `[NEEDS-INPUT]` tag
