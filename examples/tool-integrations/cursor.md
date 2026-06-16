# Cursor Integration Template

Status: **instruction-file template**

Integration level:

- L1 Instruction File Integration: advisory.
- L2 CLI Workflow Integration: possible when the user runs ProjectGate commands.

## Instruction files

Cursor projects can use rule files such as `.cursor/rules` depending on the user's Cursor setup.

Add a ProjectGate rule file that says:

```text
This project uses ProjectGate.
Do not assume project facts without evidence.
Do not produce final completion claims without TaskRun evidence.
If a required fact is missing, stop and ask for evidence or run a read-only check.
ProjectGate gate failure requires REPAIR_AND_RECHECK.
```

## Boundary

| Area | Status |
|---|---|
| Cursor rule file | Advisory |
| ProjectGate CLI checks | Enforceable inside ProjectGate-controlled flows |
| Automatic Cursor enforcement | Unverified |
| Hard runtime interception | Future |
