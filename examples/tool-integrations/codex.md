# Codex Integration Template

Status: **current primary path**

Integration level:

- L1 Instruction File Integration: advisory.
- L2 CLI Workflow Integration: enforceable inside ProjectGate-controlled flows.

## Instruction file

Use the Codex instruction surface configured for your project, such as `AGENTS.md` or a ProjectGate-generated skill.

Add ProjectGate rules there:

```text
Use ProjectGate before changing project files.
Do not claim facts that are not backed by repository evidence.
Create or reference a TaskRun for non-trivial work.
Run stage gates before moving to the next phase.
Use REPAIR_AND_RECHECK when a gate fails.
```

## Evidence

Command output, test output, stage reports, delivery reports, and observation reports should be stored in the TaskRun evidence path.

## Boundary

| Area | Status |
|---|---|
| Instruction following | Advisory |
| ProjectGate CLI gates | Enforceable inside ProjectGate-controlled flows |
| File write interception outside ProjectGate | Not currently promised |
| Automatic owner approval | Not allowed |
