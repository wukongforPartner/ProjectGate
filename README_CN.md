# 让你的 AI 强大 10^79

[为什么这成立](docs/CUBE_MODEL_CN.md)

ProjectGate 是一个 AI 工作流门禁系统，用来把不可靠的 AI 输出压回有证据的执行路径。

它要求 AI 协作必须经过事实、SOP、KnownBugRules、运行时门禁和可审查的 TaskRun 证据。

**当前 Alpha：** v0.4.6

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

## ProjectGate Auto Capture v0.4.5

Alpha v0.4.5 新增自动沉淀闭环：stage gate / delivery check 失败会自动生成 incident 和 KnownBugRule candidate；delivery check 成功会自动生成 SOP candidate。owner 只负责 approve / reject，不再负责手写候选规则。若已有同类规则，系统会记录是 active 规则未被选中、已选中但未执行、还是规则粒度不够。


## Operator Workflow v0.4.5

- 新增 candidate 生命周期工具，支持列出、查看、批准、拒绝、合并 SOP / KnownBugRule candidates。
- 新增 Project Pack 管理工具，支持 pack info、validate、export、controlled install。
- 新增 `projectgate_cli.py` 统一命令入口，覆盖 start、stage、delivery、observe、continuity、candidates、pack、status 与受控命令执行。
- 新增根目录 `pg.py` 与 `pg.bat`，减少本地长命令。
- 新增 `pg exec`，让 ProjectGate 受控命令自动写执行日志并运行 observation gate。

## v0.4.5 安全硬化

ProjectGate v0.4.5 明确当前执行边界，并加固安装器行为。

ProjectGate 是 ProjectGate 受控流程内的 AI 工作流证据层。它目前还不是操作系统级沙箱，也不是企业合规平台。

安全改动：

- ProjectGate 管理目录写入 `.projectgate-managed.json` 标记。
- 安装器拒绝覆盖未标记的非 ProjectGate 目录。
- 覆盖已有管理目录前会先备份。
- 增加 workspace-root 与目标路径深度检查，降低误删风险。
- 新增 `SECURITY.md`，说明当前执行边界与 Alpha 限制。


## v0.4.5 Packaging and Test Foundation

ProjectGate v0.4.5 增加 Python package 入口与自动化测试基础。

新增：

- `pyproject.toml`
- `projectgate/cli.py`
- `projectgate/__init__.py`
- `tests/test_projectgate_package_and_runtime.py`

`pg.py` 现在是兼容 shim，不再直接硬编码 runtime 文件路径。正式入口通过 `projectgate.cli:main` 路由。

测试基础覆盖：

- package / pg 入口
- 安装器安全拒绝
- managed backup
- candidate lifecycle
- runtime start / stage / delivery
- observation gate
- pg exec

运行：

```powershell
python -m unittest discover -s tests
```


## v0.4.5 理念文档

ProjectGate v0.4.5 增加理念文档与实现映射文档。

新增文档：

- `docs/WHY_GATES_MATTER_CN.md`
- `docs/CUBE_MODEL_CN.md`
- `docs/IMPLEMENTATION_MAP_CN.md`

这些文档解释门禁为什么是搜索空间压缩，以不绑定任何私有项目名称的方式呈现魔方模型，并把理念映射到当前 ProjectGate 真实实现文件。

## v0.4.5 首页标题

ProjectGate v0.4.5 将魔方模型主标题和证据链接放到 README 顶部。

## v0.4.5 公开首页同步

ProjectGate v0.4.5 将公开首页与当前魔方模型定位对齐。

- README 直接以 `让你的 AI 强大 10^79` 开场。
- 魔方模型说明直接跟在标题下方。
- 首屏说明 ProjectGate 是面向证据化执行路径的 AI 工作流门禁系统。


## v0.4.6 文档路径清理

ProjectGate v0.4.6 移除公开文档中的私有本地路径。

- 快速开始文档现在优先指向公开 GitHub 仓库。
- Codex adapter README 改为使用仓库相对路径，不再使用本地机器路径。
- 没有 runtime 行为变化。
