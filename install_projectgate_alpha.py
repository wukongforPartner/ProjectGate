#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
CORE_SRC = ROOT / 'core' / 'projectgate_core_v0_1'
CODEX_ADAPTER_SRC = ROOT / 'adapters' / 'projectgate_codex_adapter_v0_1'
DOCS_TEMPLATE = ROOT / 'examples' / 'ProjectDocsInbox_Template'


def copytree_clean(src: pathlib.Path, dst: pathlib.Path, dry_run: bool) -> None:
    if not src.exists():
        raise RuntimeError(f'missing source: {src}')
    if dry_run:
        print(f'DRY_RUN copy {src} -> {dst}')
        return
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def copytree_if_missing(src: pathlib.Path, dst: pathlib.Path, dry_run: bool) -> None:
    if not src.exists():
        raise RuntimeError(f'missing source: {src}')
    if dry_run:
        print(f'DRY_RUN copy-if-missing {src} -> {dst}')
        return
    if not dst.exists():
        shutil.copytree(src, dst)


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end='')
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description='ProjectGate Alpha v0.3.0 installer and bootstrapper.')
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
    ws = pathlib.Path(args.workspace_root).resolve()
    core_dst = ws / 'Core' / 'projectgate_core_v0_1'
    adapter_dst = ws / 'Adapters' / 'projectgate_codex_adapter_v0_1'
    docs_template_dst = ws / 'Templates' / 'ProjectDocsInbox_Template'
    try:
        copytree_clean(CORE_SRC, core_dst, dry)
        copytree_clean(CODEX_ADAPTER_SRC, adapter_dst, dry)
        copytree_if_missing(DOCS_TEMPLATE, docs_template_dst, dry)
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
