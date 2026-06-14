# Adapter Contract v0.1

An adapter maps ProjectGate assets into an AI tool's native configuration format.

## Inputs

- Project Pack
- Core references
- Active SOPs
- Active KnownBugRules
- Tool constraints

## Outputs

Examples:

- Project instruction file
- Skill or workflow package
- Hook templates
- Rules file
- Generic prompt bundle

## Rule

Adapters must not silently drop hard gates. Unsupported gates must be reported as `UNSUPPORTED_GATE`.
