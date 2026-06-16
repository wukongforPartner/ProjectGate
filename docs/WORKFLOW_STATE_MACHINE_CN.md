# ProjectGate / DreamStoryGate 工作流状态机与角色流转规格 v0.2

状态：静态表第一刀。

ProjectGate 不是命令集合，不是 prompt 包，不是多窗口协作手册。ProjectGate 是工作流状态机。Owner 只发起任务，并只提供 Owner 独有输入：目标、系统无法获得的事实、权限、风险授权、产品判断、停止或继续决定。

## 核心修正

```text
Owner 不是异常处理器。
Owner 不是工作流调度器。
Owner 不是 AI 质检员。
Owner 只在必须由 Owner 决定时出现。
```

除非 Owner 主动查看，否则中间错误过程不应该暴露给 Owner 管理。工作流必须能在内部持续迭代、返修、重跑事实收集、重审、重过 Gate，直到达到事实标准、需要 Owner 独有输入、确定不可继续，或 Owner 主动查看。

## 第一刀边界

本刀只新增：

```text
docs/WORKFLOW_STATE_MACHINE.md
docs/WORKFLOW_STATE_MACHINE_CN.md
core/projectgate_core_v0_1/workflow/*.json
core/projectgate_core_v0_1/workflow/projectgate_workflow_validator.py
tests/test_projectgate_workflow_state_machine.py
```

本刀不做：

```text
不实现 Orchestrator；
不改 runtime gates；
不改 adapters；
不改 DreamStory Pack；
不接 Qoder Hook；
不修改 Qoder settings。
```

## InternalRepairLoop

`INTERNAL_REPAIR_LOOP` 是本版新增核心状态。Gate FAIL 默认不是问 Owner，而是进入内部返修。只有无法内部继续，且需要 Owner 独有输入时，才进入 `NEED_USER_INPUT` 或 `NEED_OWNER_DECISION`。

## Gate 输出

GateDecision 包括：

```text
PASS
INTERNAL_REPAIR
NEED_MORE_FACTS_AUTOFIXABLE
NEED_USER_INPUT
NEED_OWNER_DECISION
UNRECOVERABLE_STOP
```

其中 `INTERNAL_REPAIR` 和 `NEED_MORE_FACTS_AUTOFIXABLE` 必须进入 `INTERNAL_REPAIR_LOOP`，不得暴露给 Owner。

## 验证

运行：

```bash
python core/projectgate_core_v0_1/workflow/projectgate_workflow_validator.py --root .
python -m unittest discover -s tests
```
