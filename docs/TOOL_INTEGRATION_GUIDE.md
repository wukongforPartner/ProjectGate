# Tool Integration Guide

ProjectGate can be connected to different AI tools at different integration levels.

This guide does not claim that every AI tool is fully supported. It explains how to connect ProjectGate to a tool while keeping the enforcement boundary honest.

## Integration levels

| Level | Name | Meaning | Enforcement status |
|---|---|---|---|
| L0 | Manual Prompt Integration | Paste ProjectGate rules into a prompt. | Advisory only |
| L1 | Instruction File Integration | Put ProjectGate rules into a tool-specific instruction file. | Advisory unless paired with ProjectGate CLI gates |
| L2 | CLI Workflow Integration | Use `pg` / ProjectGate runtime commands as the workflow spine. | Enforceable inside ProjectGate-controlled flows |
| L3 | Adapter / MCP Integration | Build a tool adapter or MCP server around ProjectGate. | Tool-specific, must be verified |
| L4 | Hard Runtime Interception | Block file writes, commands, commits, or releases outside ProjectGate. | Future boundary, not currently promised |

## The core rule

AI-assisted work should not move forward on unsupported facts.

Any integration should preserve this sequence:

```text
Task start
-> load project facts, SOPs, and KnownBugRules
-> produce a stage report
-> run a ProjectGate stage gate
-> repair and recheck on failure
-> run delivery checks before final delivery
-> keep TaskRun evidence
```

## What every tool integration must answer

1. What instruction file or configuration does the tool read?
2. Where should ProjectGate rules be placed?
3. How does the AI start or reference a TaskRun?
4. How does the AI submit a stage report?
5. How are command outputs and test results captured as evidence?
6. How does gate failure enter `REPAIR_AND_RECHECK`?
7. Which parts are enforceable, advisory, unverified, or future work?

## Status vocabulary

- **Enforceable**: ProjectGate can check or block this inside a ProjectGate-controlled flow.
- **Advisory**: The AI tool is instructed to do this, but ProjectGate cannot force it by itself.
- **Unverified**: The pattern is documented but not tested against that tool.
- **Future**: Not supported yet.

## Current templates

- Codex: `examples/tool-integrations/codex.md`
- Claude Code: `examples/tool-integrations/claude-code.md`
- Cursor: `examples/tool-integrations/cursor.md`
- Generic Agent: `examples/tool-integrations/generic-agent.md`
- QoderWork: `examples/tool-integrations/qoderwork.md`

## Recommended minimum integration

For most tools, start at L1 + L2:

```text
L1: Put ProjectGate rules into the tool's instruction file.
L2: Require actual work to go through ProjectGate CLI commands and TaskRun evidence.
```

This keeps the boundary honest: the instruction file can guide the AI, while ProjectGate CLI gates provide the enforceable workflow checks.
