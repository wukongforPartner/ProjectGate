# ProjectGate QoderWork Adapter v0.1

把 ProjectGate Core + Project Pack 编译成 QoderWork 可上传 Skill 包，并同时生成 L2 工作流协议文件。

## 边界

这个 adapter 不提供 QoderWork 内部原生硬门禁。

它支持：

- 生成 L1 QoderWork Skill 包。
- 生成 ProjectGate CLI / TaskRun / stage gate / delivery check 的 L2 工作流协议文件。
- 打包 Core 与 Project Pack references。

它不支持：

- 自动上传 QoderWork。
- 原生命令拦截。
- OS 级强制。
- QoderWork 自动执行本地 ProjectGate CLI。

## 构建

```powershell
python ".\adapters\projectgate_qoderwork_adapter_v0_1\projectgate_qoderwork_adapter.py" build `
  --core-root ".\core\projectgate_core_v0_1" `
  --project-pack ".\examples\dreamstory_project_pack_v0_1" `
  --root-docs "." `
  --out "D:\ProjectGate\Compiled\dreamstory_qoderwork_package"
```

成功 sentinel：

```text
QODERWORK_L2_WORKFLOW_PACKAGE_READY
```
