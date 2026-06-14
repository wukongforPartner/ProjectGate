# ProjectGate Core v0.1

ProjectGate Core is a project-agnostic governance layer for AI-assisted work.

It turns project documents, operating procedures, review rules, and incident lessons into a structured workflow layer that an AI tool can follow.

Core does not contain any project-specific facts. Project-specific knowledge belongs in a Project Pack.

## Core responsibilities

- Stage-gated workflow
- Fact-first discipline
- Role separation
- Owner decision protocol
- Budget profiles
- Evidence pack and run cache policies
- SOP lifecycle
- Incident lifecycle
- Known bug rule lifecycle
- Adapter contract for AI tools
- Generic project-pack compilation scaffolding

## Not in Core

Core does not include project paths, repository names, domain terminology, release commands, or product-specific procedures.

## Typical flow

```text
project docs
  -> project pack compiler
  -> candidate project pack
  -> owner review
  -> active project pack
  -> adapter install/export
  -> AI workflow with gates
```

## First version boundary

v0.1 provides file structure, schemas, templates, validators, and lightweight compilers. It does not provide hard runtime hooks for every AI tool yet.
