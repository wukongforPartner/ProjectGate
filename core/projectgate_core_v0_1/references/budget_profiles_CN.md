# Budget Profiles v0.1

## low

用于 smoke test、初步拆分、低成本规划。

- 默认不使用 subagents。
- 优先使用本地脚本。
- 早停到 owner decision。

## medium

用于正常范围审查。

- 先 evidence pack，再定向读取。
- evidence 存在后才考虑 subagents。

## high

用于深度审查。

- 允许多个 evidence packs。
- evidence 存在后允许 subagents。
- 破坏性动作仍需 owner 授权。
