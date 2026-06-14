# ProjectGate Alpha v0.1

ProjectGate is a project-agnostic governance layer for AI-assisted work.

It helps convert project documents, SOPs, rules, and incident lessons into a structured AI workflow layer.


## Start here

Background and problem statement: `BACKGROUND.md` / `BACKGROUND_CN.md`.


Read `QUICKSTART.md` first.

中文文档：`QUICKSTART_CN.md`。

For copy-paste commands, see `COMMANDS.md`.

中文命令速查：`COMMANDS_CN.md`。

## What it gives you

- Core governance rules
- Project Pack compiler
- Codex adapter
- Generic documentation template
- Example docs inbox
- One installer script
- Low / medium / high profile syntax: `-p L`, `-p M`, `-p H`

## What it does not promise yet

- It is not a complete hard-gate system for every AI tool.
- It does not train a model.
- It does not automatically promote rules without owner review.
- It does not modify your project unless you explicitly authorize adapter installation steps.

## Quick install

Initialize a workspace only:

```powershell
python install_projectgate_alpha.py --dry-run --workspace-root "D:\ProjectGate"
python install_projectgate_alpha.py --install --workspace-root "D:\ProjectGate"
```

Compile a project pack from docs:

```powershell
python install_projectgate_alpha.py --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

Build and install a Codex pack:

```powershell
python install_projectgate_alpha.py --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack `
  --build-codex-pack `
  --install-codex-skill
```

Use in Codex:

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```
