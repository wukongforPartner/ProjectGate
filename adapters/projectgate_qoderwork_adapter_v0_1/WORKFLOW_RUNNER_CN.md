# ProjectGate QoderWork Workflow Runner

ProjectGate 是工作流 owner。QoderWork 只是 worker channel。

这个 runner 负责创建 TaskRun、生成 QoderWork 任务包、接收 worker 输出文件、运行 ProjectGate gate，并生成下一阶段任务包或返修任务包。

## 边界

这不是 prompt 调参。runner 负责任务状态和 gate 决策。

它不假设 QoderWork 已有 API、MCP、hook 或本地命令执行能力。如果以后确认 QoderWork 有这些接口，可以只替换运输层，不改变 gate 模型。

## 命令

```powershell
python ".\adapters\projectgate_qoderwork_adapter_v0_1\projectgate_qoderwork_workflow_runner.py" start `
  --project-pack ".\examples\dreamstory_project_pack_v0_1" `
  --task-type "dreamstory_runtime_fact_entry_map" `
  --task-title "readonly query" `
  -p H `
  --run-root "E:\DreamStoryTools\ContextExports\ProjectGateRuns"
```

然后把生成的 `QODERWORK_INPUT` 文件交给 QoderWork。把 worker 输出保存成 Markdown 文件后，运行 `accept` 和 `gate`。
