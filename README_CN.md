## 联系方式

* 微信：songfoguixi
* 邮箱：[346636594@qq.com](mailto:346636594@qq.com)


# ProjectGate Alpha v0.1.1

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

## 联系方式

- 微信：songfoguixi
- 邮箱：346636594@qq.com
