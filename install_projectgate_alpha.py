#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, shutil, subprocess, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
CORE_SRC = ROOT / 'core' / 'projectgate_core_v0_1'
CODEX_ADAPTER_SRC = ROOT / 'adapters' / 'projectgate_codex_adapter_v0_1'
DOCS_TEMPLATE = ROOT / 'examples' / 'ProjectDocsInbox_Template'
MARKER = '.projectgate-managed.json'


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')


def is_relative_to(child: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_safe_workspace_root(ws: pathlib.Path) -> pathlib.Path:
    ws = ws.resolve()
    home = pathlib.Path.home().resolve()
    if ws == pathlib.Path(ws.anchor).resolve():
        raise RuntimeError(f'unsafe workspace root is filesystem root: {ws}')
    if ws == home:
        raise RuntimeError(f'unsafe workspace root is user home: {ws}')
    if ws == ROOT:
        raise RuntimeError(f'unsafe workspace root is ProjectGate source root: {ws}')
    if len(ws.parts) < 3:
        raise RuntimeError(f'unsafe workspace root is too shallow: {ws}')
    return ws


def marker_payload(kind: str, src: pathlib.Path, dst: pathlib.Path) -> dict:
    return {
        'schema': 'projectgate_managed_directory_v0_4_1',
        'managedBy': 'ProjectGate',
        'kind': kind,
        'source': str(src.resolve()),
        'destination': str(dst.resolve()),
        'createdUtc': datetime.now(timezone.utc).isoformat(),
    }


def looks_like_legacy_projectgate_dir(dst: pathlib.Path, kind: str) -> bool:
    if kind == 'core':
        return (dst / 'scripts' / 'projectgate_core_selftest.py').exists() and (dst / 'references').exists()
    if kind == 'adapter':
        return (dst / 'projectgate_codex_adapter.py').exists()
    if kind == 'template':
        return (dst / 'README.md').exists() or any(dst.glob('*'))
    return False


def validate_managed_target(dst: pathlib.Path, workspace_root: pathlib.Path, kind: str) -> None:
    dst = dst.resolve()
    workspace_root = workspace_root.resolve()
    home = pathlib.Path.home().resolve()
    forbidden = {pathlib.Path(dst.anchor).resolve(), workspace_root, home, ROOT.resolve()}
    if dst in forbidden:
        raise RuntimeError(f'unsafe overwrite target: {dst}')
    if not is_relative_to(dst, workspace_root):
        raise RuntimeError(f'overwrite target outside workspace root: dst={dst} workspace={workspace_root}')
    rel_parts = dst.relative_to(workspace_root).parts
    if len(rel_parts) < 2:
        raise RuntimeError(f'overwrite target too shallow under workspace: {dst}')
    if dst.exists():
        marker = dst / MARKER
        if not marker.exists() and not looks_like_legacy_projectgate_dir(dst, kind):
            raise RuntimeError(f'refusing to overwrite unmarked non-ProjectGate directory: {dst}')


def backup_existing(dst: pathlib.Path) -> pathlib.Path | None:
    if not dst.exists():
        return None
    backup = dst.with_name(dst.name + '_backup_before_replace_' + utc_stamp())
    if backup.exists():
        raise RuntimeError(f'backup path already exists: {backup}')
    shutil.move(str(dst), str(backup))
    return backup


def copytree_managed(src: pathlib.Path, dst: pathlib.Path, workspace_root: pathlib.Path, dry_run: bool, kind: str) -> None:
    if not src.exists():
        raise RuntimeError(f'missing source: {src}')
    validate_managed_target(dst, workspace_root, kind)
    if dry_run:
        action = 'replace-managed' if dst.exists() else 'copy-managed'
        print(f'DRY_RUN {action} {src} -> {dst}')
        return
    backup = backup_existing(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    (dst / MARKER).write_text(json.dumps(marker_payload(kind, src, dst), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if backup:
        print('BACKUP_DIR=' + str(backup))


def copytree_if_missing(src: pathlib.Path, dst: pathlib.Path, workspace_root: pathlib.Path, dry_run: bool, kind: str) -> None:
    if not src.exists():
        raise RuntimeError(f'missing source: {src}')
    validate_managed_target(dst, workspace_root, kind)
    if dry_run:
        print(f'DRY_RUN copy-if-missing {src} -> {dst}')
        return
    if not dst.exists():
        shutil.copytree(src, dst)
        (dst / MARKER).write_text(json.dumps(marker_payload(kind, src, dst), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end='')
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description='ProjectGate Alpha v0.4.1 installer and bootstrapper.')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--install', action='store_true')
    ap.add_argument('--workspace-root', required=True, help='Where to install ProjectGate workspace. User-chosen path.')
    ap.add_argument('--project-name', default='')
    ap.add_argument('--project-root', default='')
    ap.add_argument('--docs-dir', default='')
    ap.add_argument('--build-pack', action='store_true')
    ap.add_argument('--build-codex-pack', action='store_true')
    ap.add_argument('--install-codex-skill', action='store_true')
    ap.add_argument('--home', default=str(pathlib.Path.home()))
    ap.add_argument('--install-project-agents-md', action='store_true')
    ap.add_argument('--force-project-agents-md', action='store_true')
    args = ap.parse_args()
    if not args.dry_run and not args.install:
        print('RESULT=FAIL')
        print('FAIL_REASON=Pass --dry-run or --install')
        return 2
    dry = args.dry_run
    ws = validate_safe_workspace_root(pathlib.Path(args.workspace_root))
    core_dst = ws / 'Core' / 'projectgate_core_v0_1'
    adapter_dst = ws / 'Adapters' / 'projectgate_codex_adapter_v0_1'
    docs_template_dst = ws / 'Templates' / 'ProjectDocsInbox_Template'
    try:
        copytree_managed(CORE_SRC, core_dst, ws, dry, 'core')
        copytree_managed(CODEX_ADAPTER_SRC, adapter_dst, ws, dry, 'adapter')
        copytree_if_missing(DOCS_TEMPLATE, docs_template_dst, ws, dry, 'template')
        if not dry:
            code = run([sys.executable, str(core_dst / 'scripts' / 'projectgate_core_selftest.py')])
            if code != 0:
                print('INSTALL_RESULT=FAIL')
                return code
            code = run([sys.executable, str(core_dst / 'scripts' / 'projectgate_init_workspace.py'), '--workspace-root', str(ws)])
            if code != 0:
                print('INSTALL_RESULT=FAIL')
                return code
        else:
            print(f'DRY_RUN init workspace {ws}')
        pack_out = None
        if args.build_pack:
            if not args.project_name or not args.project_root or not args.docs_dir:
                raise RuntimeError('--project-name, --project-root, and --docs-dir are required with --build-pack')
            pack_out = ws / 'ProjectPacks' / args.project_name
            cmd = [sys.executable, str(core_dst / 'scripts' / 'projectgate_compile_project_pack.py'),
                   '--project-name', args.project_name,
                   '--project-root', args.project_root,
                   '--docs-dir', args.docs_dir,
                   '--out-pack', str(pack_out)]
            if dry:
                cmd.append('--dry-run')
            code = run(cmd)
            if code != 0:
                print('INSTALL_RESULT=FAIL')
                return code
        if args.build_codex_pack:
            if pack_out is None:
                if not args.project_name:
                    raise RuntimeError('--project-name required with --build-codex-pack when --build-pack is not used')
                pack_out = ws / 'ProjectPacks' / args.project_name
            codex_pack = ws / 'Compiled' / f'{args.project_name}_codex_pack'
            cmd = [sys.executable, str(adapter_dst / 'projectgate_codex_adapter.py'), 'build',
                   '--core-root', str(core_dst),
                   '--project-pack', str(pack_out),
                   '--out', str(codex_pack)]
            if dry:
                print('DRY_RUN run ' + ' '.join(cmd))
            else:
                code = run(cmd)
                if code != 0:
                    print('INSTALL_RESULT=FAIL')
                    return code
            if args.install_codex_skill:
                install_script = codex_pack / 'install_projectgate_codex_pack.py'
                cmd = [sys.executable, str(install_script), '--install' if args.install else '--dry-run', '--home', args.home]
                if args.install_project_agents_md:
                    cmd.extend(['--install-project-agents-md', '--project-root', args.project_root])
                    if args.force_project_agents_md:
                        cmd.append('--force-project-agents-md')
                if dry:
                    print('DRY_RUN run ' + ' '.join(cmd))
                else:
                    code = run(cmd)
                    if code != 0:
                        print('INSTALL_RESULT=FAIL')
                        return code
        print('RESULT=PASS')
        print('PROJECTGATE_ALPHA=PASS')
        print('WORKSPACE_ROOT=' + str(ws))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=ALPHA_INSTALL')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
