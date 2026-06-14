# ProjectGate Codex Adapter v0.1

把 ProjectGate Core + Project Pack 编译成 Codex 可安装包。

## Profile 命令

使用英文或缩写：

- `-p L` / `--profile L` / `low` / `light`
- `-p M` / `--profile M` / `medium` / `standard`
- `-p H` / `--profile H` / `high` / `deep`

主文档推荐使用 `-p L`、`-p M`、`-p H`。

## 构建

```powershell
python projectgate_codex_adapter.py build `
  --core-root "D:\ProjectGate\projectgate_core_v0_1" `
  --project-pack "D:\ProjectGate\ProjectPacks\MyProject" `
  --out "D:\ProjectGate\Compiled\MyProject_codex_pack"
```
