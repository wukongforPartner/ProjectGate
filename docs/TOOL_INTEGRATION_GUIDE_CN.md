# 工具接入指南

ProjectGate 可以按不同集成深度接入不同 AI 工具。

这份指南不声称 ProjectGate 已经完整支持所有 AI 工具。它只说明如何把 ProjectGate 接入某个工具，并明确哪些部分可强制，哪些部分只是建议。

## 接入等级

| 等级 | 名称 | 含义 | 强制状态 |
|---|---|---|---|
| L0 | 手动提示词接入 | 把 ProjectGate 规则手动贴进 prompt。 | 只是建议 |
| L1 | 指令文件接入 | 把 ProjectGate 规则放进工具自己的指令文件。 | 除非配合 ProjectGate CLI，否则只是建议 |
| L2 | CLI 工作流接入 | 用 `pg` / ProjectGate runtime 命令作为工作流主干。 | 在 ProjectGate 受控流程内可强制 |
| L3 | Adapter / MCP 接入 | 围绕 ProjectGate 构建工具 adapter 或 MCP server。 | 取决于具体工具，必须验证 |
| L4 | 硬运行时拦截 | 在 ProjectGate 外部拦截写文件、执行命令、提交、发版。 | 未来边界，当前不承诺 |

## 核心规则

AI 协作不应基于未证实事实继续推进。

任何工具接入都应该尽量保留这个顺序：

```text
任务开始
-> 载入项目事实、SOP、KnownBugRules
-> 产出阶段报告
-> 运行 ProjectGate stage gate
-> 失败后进入 REPAIR_AND_RECHECK
-> 最终交付前运行 delivery check
-> 保留 TaskRun 证据
```

## 每个工具接入文档必须回答的问题

1. 这个工具会读取什么指令文件或配置？
2. ProjectGate 规则应该放在哪里？
3. AI 如何启动或引用 TaskRun？
4. AI 如何提交 stage report？
5. 命令输出和测试结果如何作为证据保存？
6. gate 失败时如何进入 `REPAIR_AND_RECHECK`？
7. 哪些部分可强制、哪些只是建议、哪些尚未验证、哪些属于未来目标？

## 状态词汇

- **可强制**：ProjectGate 可以在受控流程内检查或阻断。
- **只是建议**：AI 工具被要求这样做，但 ProjectGate 单独无法强制。
- **尚未验证**：模式已记录，但未对该工具完成验证。
- **未来目标**：当前不支持。

## 当前模板

- Codex：`examples/tool-integrations/codex.md`
- Claude Code：`examples/tool-integrations/claude-code.md`
- Cursor：`examples/tool-integrations/cursor.md`
- 通用 Agent：`examples/tool-integrations/generic-agent.md`

## 推荐的最低接入方式

多数工具先从 L1 + L2 开始：

```text
L1：把 ProjectGate 规则放进工具指令文件。
L2：实际工作必须走 ProjectGate CLI 命令和 TaskRun 证据。
```

这样边界是诚实的：指令文件负责引导 AI，ProjectGate CLI gates 负责可检查的工作流门禁。
