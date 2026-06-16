# ProjectGate QoderWork Adapter v0.1

Builds a QoderWork uploadable Skill package plus an L2 workflow protocol package from ProjectGate Core and a Project Pack.

## Boundary

This adapter does not provide native hard enforcement inside QoderWork.

It supports:

- L1 QoderWork Skill package generation.
- L2 workflow protocol files for ProjectGate CLI / TaskRun / stage gate / delivery check.
- Bundled references for Core and Project Pack.

It does not support:

- Automatic QoderWork upload.
- Native command interception.
- OS-level enforcement.
- Automatic local CLI execution from QoderWork.

## Build

```powershell
python ".\adapters\projectgate_qoderwork_adapter_v0_1\projectgate_qoderwork_adapter.py" build `
  --core-root ".\core\projectgate_core_v0_1" `
  --project-pack ".\examples\dreamstory_project_pack_v0_1" `
  --root-docs "." `
  --out "D:\ProjectGate\Compiled\dreamstory_qoderwork_package"
```

Expected sentinel:

```text
QODERWORK_L2_WORKFLOW_PACKAGE_READY
```
