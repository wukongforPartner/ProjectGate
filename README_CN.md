# ProjectGate Alpha v0.3.3

ProjectGate 是一个面向 AI 协作的项目治理层。它把项目文档、SOP、规则和事故经验编译成 AI 可以遵守的工作流。

## 从这里开始

第一次使用请先读 `QUICKSTART_CN.md`。

需要复制命令时看 `COMMANDS_CN.md`。

## 它提供什么

- 通用 Core 治理层
- Project Pack 编译器
- Codex Adapter
- 项目文档模板
- 示例 Docs Inbox
- 一键安装脚本
- Profile 命令：`-p L`、`-p M`、`-p H`

## 当前不承诺什么

- 还不是所有 AI 工具的完整硬门禁系统。
- 不训练模型。
- 不会未经 owner 审核自动激活规则。
- 不会默认修改项目文件。

## 快速安装

只初始化工作区：

```powershell
python install_projectgate_alpha.py --dry-run --workspace-root "D:\ProjectGate"
python install_projectgate_alpha.py --install --workspace-root "D:\ProjectGate"
```

从文档编译项目包：

```powershell
python install_projectgate_alpha.py --install `
  --workspace-root "D:\ProjectGate" `
  --project-name "MyProject" `
  --project-root "D:\MyProject" `
  --docs-dir "D:\MyProjectDocs" `
  --build-pack
```

编译并安装 Codex Skill：

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

Codex 中使用：

```text
/goal $projectgate -p L: Review this issue and produce an action queue. Do not modify project files.
```


背景与问题说明：`BACKGROUND_CN.md` / `BACKGROUND.md`。

## ProjectGate Runtime v0.2

Alpha v0.2.0 新增 Runtime Gate：SOP 和 KnownBugRules 不再只是文档结构。真实工作流必须先生成 `TaskRun.json`，把 active SOP / KnownBugRules 载入本次任务；阶段输出必须通过 stage gate；失败时进入 `REPAIR_AND_RECHECK`，修正后重新检查；最终交付前必须通过 delivery check。

## ProjectGate Knowledge Router v0.3

Alpha v0.3.0 新增知识路由与沉淀闭环：`L / M / H` 不再只是成本标签，也决定 SOP / KnownBugRule 的选择范围。成功且可复用的 TaskRun 可以生成 SOP candidate；失败事故可以生成 KnownBugRule candidate；candidate 必须 owner 批准后才进入 active。

## ProjectGate Auto Capture v0.3.3

Alpha v0.3.3 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。
