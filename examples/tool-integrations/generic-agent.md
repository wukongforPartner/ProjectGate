# Generic Agent Integration Template

Status: **manual template**

Integration level:

- L0 Manual Prompt Integration: advisory.
- L2 CLI Workflow Integration: enforceable only if ProjectGate commands are actually used.

## Prompt template

Paste this into any AI tool before a non-trivial task:

```text
This project uses ProjectGate.

Rules:
1. Do not claim unsupported project facts.
2. Before patching, list confirmed facts, unknown facts, risks, stop conditions, and the only safe next step.
3. Use ProjectGate TaskRun evidence for stage transitions.
4. If a gate fails, enter REPAIR_AND_RECHECK.
5. Do not treat advisory instructions as proof of enforcement.
```

## Boundary

| Area | Status |
|---|---|
| Prompt instructions | Advisory |
| External ProjectGate CLI checks | Enforceable if actually run |
| Automatic tool enforcement | Not available |
| Hard runtime interception | Future |
