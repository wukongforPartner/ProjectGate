#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, shutil, zipfile
from datetime import datetime, timezone

REQUIRED_FILES = ['project_manifest.json', 'AGENTS.md.template', 'README_ProjectPack.md']
REQUIRED_DIRS = ['SOPs', 'KnownBugRules', 'TaskTypes', 'EvidenceProfiles']


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))

def validate_pack(pack: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (pack / rel).exists():
            errors.append('missing file: ' + rel)
    for rel in REQUIRED_DIRS:
        if not (pack / rel).exists():
            errors.append('missing dir: ' + rel)
    manifest_path = pack / 'project_manifest.json'
    if manifest_path.exists():
        try:
            data = read_json(manifest_path)
            for key in ['projectId', 'projectName']:
                if not data.get(key):
                    errors.append('manifest missing key: ' + key)
        except Exception as exc:
            errors.append('invalid manifest json: ' + str(exc))
    return errors

def count_files(root: pathlib.Path, pattern: str) -> int:
    if not root.exists():
        return 0
    return sum(1 for _ in root.rglob(pattern))

def cmd_info(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    if not pack.exists():
        raise RuntimeError('project pack missing: ' + str(pack))
    manifest = {}
    if (pack / 'project_manifest.json').exists():
        manifest = read_json(pack / 'project_manifest.json')
    errors = validate_pack(pack)
    print('RESULT=PASS' if not errors else 'RESULT=FAIL')
    print('PACK=' + str(pack))
    print('PROJECT_ID=' + str(manifest.get('projectId','')))
    print('PROJECT_NAME=' + str(manifest.get('projectName','')))
    print('PACK_VERSION=' + str(manifest.get('packVersion','')))
    print('ACTIVE_SOPS=' + str(count_files(pack / 'SOPs' / 'active', '*.md')))
    print('CANDIDATE_SOPS=' + str(count_files(pack / 'SOPs' / 'candidates', '*.md')))
    print('ACTIVE_KNOWN_BUG_RULE_FILES=' + str(count_files(pack / 'KnownBugRules' / 'active', '*.json')))
    print('CANDIDATE_KNOWN_BUG_RULE_FILES=' + str(count_files(pack / 'KnownBugRules' / 'candidates', '*.json')))
    if errors:
        print('VALIDATION_ERRORS=' + ' | '.join(errors))
        return 1
    print('PROJECT_PACK_VALID=PASS')
    return 0

def cmd_validate(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    errors = validate_pack(pack)
    if errors:
        print('RESULT=FAIL')
        print('FAILED_STAGE=PACK_VALIDATE')
        print('FAIL_REASON=' + ' | '.join(errors))
        return 1
    print('RESULT=PASS')
    print('PROJECT_PACK_VALID=PASS')
    print('PACK=' + str(pack))
    return 0

def ignore_names(dirpath, names):
    ignored = set()
    for name in names:
        if name == '__pycache__' or name.endswith('.pyc'):
            ignored.add(name)
        if name == 'active_run':
            ignored.add(name)
    return ignored

def cmd_export(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    errors = validate_pack(pack)
    if errors:
        raise RuntimeError('pack is invalid: ' + ' | '.join(errors))
    out = pathlib.Path(args.out).resolve()
    if out.exists() and out.is_dir():
        raise RuntimeError('output path is a directory: ' + str(out))
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() != '.zip':
        raise RuntimeError('export output must be .zip')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(pack.rglob('*')):
            if p.is_dir():
                continue
            rel = p.relative_to(pack)
            parts = set(rel.parts)
            if '__pycache__' in parts or 'active_run' in parts or p.suffix == '.pyc':
                continue
            zf.write(p, 'project_pack/' + rel.as_posix())
    print('RESULT=PASS')
    print('PROJECT_PACK_EXPORTED=' + str(out))
    return 0

def cmd_install(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    errors = validate_pack(pack)
    if errors:
        raise RuntimeError('pack is invalid: ' + ' | '.join(errors))
    dest = pathlib.Path(args.dest).resolve()
    if args.dry_run:
        print('RESULT=PASS')
        print('DRY_RUN=PASS')
        print('INSTALL_SOURCE=' + str(pack))
        print('INSTALL_DEST=' + str(dest))
        return 0
    if dest.exists():
        if not args.force:
            raise RuntimeError('install destination exists, pass --force to replace: ' + str(dest))
        shutil.rmtree(dest)
    shutil.copytree(pack, dest, ignore=ignore_names)
    print('RESULT=PASS')
    print('PROJECT_PACK_INSTALLED=' + str(dest))
    return 0

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description='ProjectGate Project Pack manager.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ['info', 'validate']:
        sp = sub.add_parser(name); sp.add_argument('--project-pack', required=True)
    ex = sub.add_parser('export'); ex.add_argument('--project-pack', required=True); ex.add_argument('--out', required=True)
    ins = sub.add_parser('install'); ins.add_argument('--project-pack', required=True); ins.add_argument('--dest', required=True); ins.add_argument('--dry-run', action='store_true'); ins.add_argument('--force', action='store_true')
    return ap

def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.cmd == 'info': return cmd_info(args)
        if args.cmd == 'validate': return cmd_validate(args)
        if args.cmd == 'export': return cmd_export(args)
        if args.cmd == 'install': return cmd_install(args)
        raise RuntimeError('unknown command')
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=PACK_MANAGER')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
