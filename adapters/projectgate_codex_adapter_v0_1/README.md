# ProjectGate Codex Adapter v0.1

Compiles ProjectGate Core + a Project Pack into a Codex-installable package.

## Profile command names

Use English or short flags:

- `-p L` / `--profile L` / `low` / `light`
- `-p M` / `--profile M` / `medium` / `standard`
- `-p H` / `--profile H` / `high` / `deep`

Primary docs use `-p L`, `-p M`, `-p H`.

## Build

From the ProjectGate repository root:

```powershell
python ".\adapters\projectgate_codex_adapter_v0_1\projectgate_codex_adapter.py" build `
  --core-root ".\core\projectgate_core_v0_1" `
  --project-pack ".\examples\dreamstory_project_pack_v0_1" `
  --out ".\compiled\projectgate_dreamstory_codex_pack_v0_1"
```

## Install generated pack

Inside generated pack:

```powershell
python install_projectgate_codex_pack.py --dry-run
python install_projectgate_codex_pack.py --install
```
