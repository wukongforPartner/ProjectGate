# ProjectGate Alpha Quick Start

This guide is for first-time users.

## What ProjectGate does

ProjectGate turns your project documents, SOPs, rules, and incident notes into an AI workflow layer.

The goal:

```text
You provide project documents.
ProjectGate builds a Project Pack.
Codex uses $projectgate with L/M/H profiles.
The AI works with facts, stages, reports, and owner decisions instead of improvising.
```

## Requirements

- Python 3
- Codex installed and signed in if you want Codex integration
- A project folder
- A folder containing your project docs / SOP / rules / incidents

## Step 1: Extract the package

Example:

```powershell
D:\ProjectGate_Alpha_v0_1_1
```

Open PowerShell there:

```powershell
cd "D:\ProjectGate_Alpha_v0_1_1"
```

## Step 2: Run local self-test

```powershell
python ".\scripts\alpha_selftest.py"
```

Expected:

```text
RESULT=PASS
ALPHA_SELFTEST=PASS
```

## Step 3: Initialize a ProjectGate workspace

Choose your own workspace path.

```powershell
python ".\install_projectgate_alpha.py" --dry-run --workspace-root "D:\ProjectGate"
python ".\install_projectgate_alpha.py" --install --workspace-root "D:\ProjectGate"
```

## Step 4: Prepare your project documents

Create a folder like:

```text
D:\MyProjectDocs\
  project_overview.md
  rules.md
  sop.md
  known_incidents.md
```

You can copy the template from:

```text
examples\ProjectDocsInbox_Template\
```

## Step 5: Compile a Project Pack

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

Output:

```text
D:\ProjectGate\ProjectPacks\MyProject\
```

## Step 6: Build and install Codex Skill

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack `
  --build-codex-pack `
  --install-codex-skill
```

This installs a user-level Codex skill:

```text
%USERPROFILE%\.agents\skills\projectgate
```

It does not install project `AGENTS.md` unless explicitly requested.

## Step 7: Use in Codex

Start Codex from your project root:

```powershell
cd "D:\MyProject"
codex
```

Use low-cost profile first:

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```

Profiles:

```text
-p L = low / light
-p M = medium / standard
-p H = high / deep
```

## Optional: Install project AGENTS.md

This writes into your project root. Do not do it until you are ready.

Dry-run first:

```powershell
python ".\install_projectgate_alpha.py" --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack `
  --build-codex-pack `
  --install-codex-skill `
  --install-project-agents-md
```

If `AGENTS.md` already exists, the installer should not overwrite it unless a force flag is used by the generated Codex pack installer.

## Safety model

ProjectGate Alpha defaults to:

- read-only first
- no guessing
- owner decision required for judgment or write authorization
- project writes only with explicit authorization
- repeatable workflows become SOP candidates
- repeatable failures become known-bug-rule candidates

## Current limitations

- Codex adapter is the first supported native adapter.
- Generic Markdown support is basic.
- Hard hooks are not fully installed by default.
- Candidate SOPs and known bug rules still require owner approval before becoming active.

## ProjectGate Runtime v0.2

Alpha v0.2.0 adds Runtime Gate support. SOPs and KnownBugRules are no longer passive folders only. Real workflows must create a `TaskRun.json`, load active SOPs / KnownBugRules into the task, pass stage gates, use `REPAIR_AND_RECHECK` on gate failure, and pass a delivery check before final delivery.
