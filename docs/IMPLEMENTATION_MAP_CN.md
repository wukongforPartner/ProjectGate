# ProjectGate 实现映射表

本文档把门禁理念映射到 ProjectGate 当前真实实现。

这里不使用仓库中不存在的抽象名词。下面每一项都对应当前 ProjectGate 的概念或文件。

| 门禁概念 | ProjectGate 实现 |
| --- | --- |
| 当前任务状态 | `TaskRun.json` |
| 项目事实 | `project_manifest.json` |
| 标准安全路径 | `SOPs/active` |
| 已知失败路径 | `KnownBugRules/active` |
| 失败证据 | `Incidents/` |
| 阶段检查 | `core/projectgate_core_v0_1/runtime/projectgate_stage_gate.py` |
| 交付检查 | `core/projectgate_core_v0_1/runtime/projectgate_delivery_check.py` |
| 观察门禁 | `core/projectgate_core_v0_1/runtime/projectgate_observation_gate.py` |
| TaskRun 连续性 | `core/projectgate_core_v0_1/runtime/projectgate_taskrun_continuity_gate.py` |
| 候选审核 | `core/projectgate_core_v0_1/runtime/projectgate_candidate_lifecycle.py` |
| Project Pack 命令 | `core/projectgate_core_v0_1/runtime/projectgate_pack_manager.py` |
| 统一 CLI | `projectgate/cli.py`, `pg.py`, `pg.bat` |
| 安全边界 | `SECURITY.md` |
| 自动化测试 | `tests/test_projectgate_package_and_runtime.py` |

## 这些组件如何协作

1. 工作流先创建 `TaskRun.json`。
2. ProjectGate 载入相关项目事实、SOP 和 KnownBugRules。
3. 阶段输出必须通过 stage gate。
4. 最终交付必须通过 delivery check。
5. 运行观察可以生成 Incident 和 KnownBugRule 候选。
6. 候选不会自动生效，必须经过审核。
7. CLI 提供可重复的操作路径。
8. 测试验证关键入口和安全边界不会失效。

目标不是让 AI 承诺自己会遵守规则。

目标是让工作流留下可检查证据。
