# ProjectGate Background and Problem Statement

## Background

More people are bringing AI into real projects: code, documentation, debugging, data analysis, planning, scripting, and release support.

For simple tasks, this can work well. For long-running complex projects, a structural problem appears quickly.

AI can be strong in a single answer, but unstable as a long-term collaborator. It may promise to stay read-only, then immediately propose a patch. It may treat assumptions as facts. It may proceed without current repository state. It may repeat errors that were already corrected. It may fail to load or follow existing SOPs, project gates, incident lessons, and team rules.

This is not only a model problem. It is a workflow problem.

**Project rules are documents. AI behavior is generated in the moment. A reliable executable layer is missing between them.**

Human teams reduce errors with process, role separation, review, approvals, SOPs, and incident reviews. Most AI collaboration still relies on placing rules in a prompt and hoping the model remembers them. That approach can work for small tasks, but it repeatedly fails in complex projects.

ProjectGate exists to fill that missing layer.

---

## The problem ProjectGate solves

ProjectGate is not primarily about making AI smarter.

It is about making AI work inside real projects according to facts, stages, roles, gates, and project knowledge.

It targets common failure modes:

1. **Proceeding without facts**  
   The AI lacks current code, configuration, logs, or state, but still gives conclusions, plans, or patches.

2. **Treating assumptions as facts**  
   The AI uses “probably,” “usually,” or “I think” as a substitute for evidence.

3. **Skipping stages**  
   A task should be read-only audit, but the AI jumps into design, fields, commands, patches, or release steps.

4. **Self-approval**  
   The same agent creates a proposal and approves it, without adversarial review or deterministic gates.

5. **Repeating known mistakes**  
   An incident was analyzed, but a future task repeats the same failure because the lesson was not turned into an active rule.

6. **Passive project documentation**  
   Teams have SOPs, rules, and incident notes, but AI may not load, understand, or apply them.

7. **Context and quota waste**  
   The model reads whole repositories or large logs directly instead of using compact evidence packs.

8. **The user becomes the workflow engine**  
   The user must constantly say “continue,” “do not patch,” “first collect facts,” or “write the report.”

ProjectGate moves these problems from model self-discipline into workflow and gate enforcement.

---

## What ProjectGate is

ProjectGate is a project governance layer for AI-assisted work.

It is not a model and not just a prompt template. It is a structure for compiling project knowledge into AI-operable workflow assets.

It contains:

- **Core**: generic governance rules such as no guessing, missing facts stop progress, stage gates, role separation, owner decisions, SOP lifecycle, and incident handling.
- **Project Pack**: project-specific rules, SOPs, known bug rules, task types, and evidence profiles.
- **Adapter**: converts Core + Project Pack into a target AI tool format, such as Codex Skill, AGENTS.md, or Markdown runbooks.
- **KnowledgeBase**: stores SOPs, incidents, known bug rules, task types, and promotion candidates.
- **Evidence / CodeMap tooling**: local scripts gather compact evidence before the model reasons over it.
- **Owner Decision protocol**: when judgment, risk acceptance, or write authorization is needed, the AI must stop and present options.

In short:

**ProjectGate turns project documentation into AI-executable workflow.**

---

## How it differs from a prompt

A normal prompt says:

> Please follow these rules.

ProjectGate says:

> The task must pass through stages.  
> Missing facts stop progress.  
> Some actions require authorization.  
> Old failures become active rules.  
> Successful workflows become SOPs.  
> Roles are separated.  
> Reports go to files.  
> The owner only intervenes when judgment is needed.

ProjectGate does not merely tell AI what to do. It decomposes work into executable structure:

```text
Documents
  -> structured Project Pack
  -> stage workflow
  -> evidence packs
  -> role separation
  -> gate checks
  -> reports
  -> owner decisions
  -> SOP / incident lifecycle
```

---

## It compiles project knowledge, not model weights

A core idea of ProjectGate is:

**Do not train the model. Compile the project knowledge.**

Every real project already has knowledge: overview, architecture, code style, review rules, testing, release process, incidents, collaboration habits, forbidden actions, and working SOPs.

ProjectGate turns these into structured assets:

```text
ProjectDocs
  -> AGENTS.md
  -> Project Pack
  -> SOP candidates
  -> KnownBugRule candidates
  -> Evidence profiles
  -> AI tool adapter package
```

The AI does not start from scratch every time. It enters a project environment with rails, signals, incident history, and operating procedures.

---

## Why role separation matters

In complex work, a single AI role can easily convince itself.

ProjectGate separates responsibilities:

- **FactCollector** gathers facts only.
- **Synthesizer** organizes options.
- **AdversaryReviewer** looks for missing facts, contradictions, and overreach.
- **Gatekeeper** performs deterministic checks and cannot be the proposal author.
- **Executor** performs approved actions.
- **Verifier** validates independently.
- **KnowledgeCurator** turns successful workflows and failures into candidates.
- **Owner** makes value judgments and grants authorization.

The purpose is simple:

**The answer generator cannot be the answer approver.**

---

## Why Owner Decision exists

AI can help move facts forward, but it must not replace the owner’s judgment.

Questions such as product direction, risk acceptance, project writes, release authorization, or rule activation require explicit owner decision.

ProjectGate uses a fixed format:

```text
OWNER_DECISION_REQUIRED

Question: ...

Options:
A. ...
B. ...
C. ...

Recommendation: A
Reason: ...

Reply with A, B, C, or a direct decision.
```

The user is no longer a constant workflow dispatcher. They intervene only where judgment is actually required.

---

## Why SOP and incident memory matter

AI collaboration often fails not because a mistake happens once, but because the same mistake happens again.

ProjectGate turns success and failure into reusable knowledge.

Successful workflow:

```text
correct workflow
  -> SOP_CANDIDATE
  -> owner review
  -> ACTIVE_SOP
  -> loaded in future matching tasks
```

Repeatable failure:

```text
incident
  -> KnownBugRuleCandidate
  -> owner review
  -> ACTIVE_KNOWN_BUG_RULE
  -> checked in future matching tasks
```

This moves project memory from “remember next time” into the next workflow itself.

---

## Where ProjectGate applies

ProjectGate began from the needs of a complex independent game project, but the underlying problem is general.

It applies to long-running projects that have:

- many documents
- many SOPs
- strict rules
- incident lessons
- AI participation
- staged risky work
- reusable processes
- low tolerance for guessing or unauthorized action

Potential domains include software engineering, game development, backend / DevOps, data analysis, content pipelines, research projects, legal or compliance review, product design, and open-source maintenance.

---

## Typical workflow

A user prepares project documents:

```text
ProjectDocsInbox/
  project_overview.md
  rules.md
  sop.md
  known_incidents.md
  release_rules.md
```

ProjectGate compiles a Project Pack:

```text
ProjectPack/
  AGENTS.md.template
  README_ProjectPack.md
  SOPs/
  KnownBugRules/
  TaskTypes/
  EvidenceProfiles/
```

An adapter installs it into an AI tool such as Codex.

Daily use:

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

The AI proceeds to reports, action queues, owner decisions, missing-fact blockers, or write authorization points.

---

## Core value

ProjectGate does not aim to make AI say more.

It aims to make AI do less wrong work, repeat fewer mistakes, guess less, waste less context, and convert project experience into reusable workflow.

It moves AI collaboration from prompt-driven to project-workflow-driven.

---

## Current stage

ProjectGate is currently in Alpha.

Implemented directions include:

- Core / Project Pack separation
- Codex Adapter
- document templates
- Project Pack compilation
- Codex Skill generation
- L / M / H profile flags
- basic SOP / Incident / KnownBugRule structure
- installation and self-test scripts

Still evolving:

- hard hooks
- deeper CodeGraph / tree-sitter / MCP tooling
- more AI adapters
- stronger SOP promotion review
- stronger known-bug machine validation
- cheaper smoke testing

---

## One-sentence summary

ProjectGate compiles project documents, SOPs, gates, and incident lessons into an AI workflow governance layer.

Its goal is not to replace people, but to make AI work inside long-running projects according to facts, process, roles, and authorization boundaries.

## ProjectGate Runtime v0.2

Alpha v0.2.0 adds Runtime Gate support. SOPs and KnownBugRules are no longer passive folders only. Real workflows must create a `TaskRun.json`, load active SOPs / KnownBugRules into the task, pass stage gates, use `REPAIR_AND_RECHECK` on gate failure, and pass a delivery check before final delivery.

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 adds knowledge routing and learning loops. `L / M / H` now controls SOP / KnownBugRule selection scope, not just cost. Successful reusable TaskRuns can create SOP candidates. Failures can create KnownBugRule candidates. Candidates require owner approval before becoming active.
