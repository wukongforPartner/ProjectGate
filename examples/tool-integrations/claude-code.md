# Claude Code Integration Template

Status: **instruction-file template**

Integration level:

- L1 Instruction File Integration: advisory.
- L2 CLI Workflow Integration: possible when the user runs ProjectGate commands.

## Instruction file

Use the tool's project instruction mechanism, such as a project-level `CLAUDE.md` when available in the user's setup.

Place ProjectGate rules there:

```text
ProjectGate is the workflow authority for this project.
Do not advance on unsupported facts.
Before patching, confirm project state and required evidence.
Run ProjectGate stage and delivery checks when applicable.
Gate failure means REPAIR_AND_RECHECK, not final delivery.
```

## Boundary

| Area | Status |
|---|---|
| Instruction file behavior | Advisory |
| Manual ProjectGate CLI checks | Enforceable if the workflow uses ProjectGate commands |
| Native Claude Code adapter | Future |
| Hard runtime interception | Future |
