# ProjectGate QoderWork Workflow Runner

ProjectGate is the workflow owner. QoderWork is a worker channel.

This runner creates TaskRuns, generates QoderWork task packets, accepts worker output files, runs ProjectGate gates, and generates the next or repair packet.

## Boundary

This is not prompt tuning. The runner owns task state and gate decisions.

It does not assume QoderWork has an API, MCP, hook, or local command execution. If QoderWork later exposes one of those interfaces, the transport layer can be automated without changing the gate model.

## Commands

```powershell
python ".\adapters\projectgate_qoderwork_adapter_v0_1\projectgate_qoderwork_workflow_runner.py" start `
  --project-pack ".\examples\dreamstory_project_pack_v0_1" `
  --task-type "dreamstory_runtime_fact_entry_map" `
  --task-title "readonly query" `
  -p H `
  --run-root "E:\DreamStoryTools\ContextExports\ProjectGateRuns"
```

Then give the generated `QODERWORK_INPUT` file to QoderWork. Save the worker output as a Markdown file and run `accept` and `gate`.
