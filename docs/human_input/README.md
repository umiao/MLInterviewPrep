# Human Input Checklist

> Tasks requiring human-provided files before autonomous execution can continue.
> Use `/collect-input` to check status, get guidance, validate, and unblock tasks.

---

No tasks currently require human input.

---

## Protocol

1. Read the detail file for the task you want to unblock
2. Follow the instructions to create/place the required files
3. Run `/collect-input validate <task-id>` to check your work
4. On pass, run `/collect-input unblock <task-id>` to remove the `[NEEDS-INPUT]` tag
