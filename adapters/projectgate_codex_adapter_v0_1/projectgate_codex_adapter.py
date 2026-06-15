#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, shutil, re, subprocess, sys
from datetime import datetime, timezone

SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')


def safe(text: str) -> str:
    return SAFE_RE.sub('_', text.strip())[:80].strip('_') or 'project'


MARKER = '.projectgate-managed.json'


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')


def is_relative_to(child: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def marker_payload(kind: str, dst: pathlib.Path) -> dict:
    return {
        'schema': 'projectgate_managed_directory_v0_4_1',
        'managedBy': 'ProjectGate',
        'kind': kind,
        'destination': str(dst.resolve()),
        'createdUtc': datetime.now(timezone.utc).isoformat(),
    }


def looks_like_legacy_codex_pack(path: pathlib.Path) -> bool:
    return (path / 'PACK_MANIFEST.json').exists() and (path / 'projectgate' / 'SKILL.md').exists()


def validate_replace_target(dst: pathlib.Path, kind: str) -> None:
    dst = dst.resolve()
    home = pathlib.Path.home().resolve()
    forbidden = {pathlib.Path(dst.anchor).resolve(), home}
    if dst in forbidden:
        raise RuntimeError(f'unsafe replace target: {dst}')
    if len(dst.parts) < 3:
        raise RuntimeError(f'replace target too shallow: {dst}')
    if dst.exists():
        marker = dst / MARKER
        if not marker.exists() and kind == 'codex_pack' and not looks_like_legacy_codex_pack(dst):
            raise RuntimeError(f'refusing to replace unmarked non-ProjectGate output: {dst}')
        if not marker.exists() and kind != 'codex_pack':
            raise RuntimeError(f'refusing to replace unmarked non-ProjectGate output: {dst}')


def backup_existing(dst: pathlib.Path) -> pathlib.Path | None:
    if not dst.exists():
        return None
    backup = dst.with_name(dst.name + '_backup_before_replace_' + utc_stamp())
    if backup.exists():
        raise RuntimeError(f'backup path already exists: {backup}')
    shutil.move(str(dst), str(backup))
    return backup


def prepare_managed_output(dst: pathlib.Path, kind: str) -> pathlib.Path | None:
    validate_replace_target(dst, kind)
    backup = backup_existing(dst)
    dst.mkdir(parents=True, exist_ok=True)
    (dst / MARKER).write_text(json.dumps(marker_payload(kind, dst), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if backup:
        print('BACKUP_DIR=' + str(backup))
    return backup


def copytree(src: pathlib.Path, dst: pathlib.Path) -> None:
    prepare_managed_output(dst, 'copytree')
    copytree_merge(src, dst)
    (dst / MARKER).write_text(json.dumps(marker_payload('copytree', dst), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copytree_merge(src: pathlib.Path, dst: pathlib.Path) -> None:
    for p in src.rglob('*'):
        rel = p.relative_to(src)
        target = dst / rel
        if p.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)


def read_manifest(pack: pathlib.Path) -> dict:
    p = pack / 'project_manifest.json'
    if not p.exists():
        raise RuntimeError(f'missing project manifest: {p}')
    return json.loads(p.read_text(encoding='utf-8'))


def write_skill(out: pathlib.Path, manifest: dict) -> None:
    project_name = manifest.get('projectName', 'Project')
    project_id = manifest.get('projectId', safe(project_name).lower())
    text = f'''---
name: projectgate
description: Use this skill for ProjectGate workflows in the current project. Supports profile flags `-p L`, `-p M`, and `-p H` for low, medium, and high depth. It applies fact-first workflow, stage gates, owner decisions, SOP lookup, incident recording, evidence packs, and project-pack rules.
---

# ProjectGate Codex Skill

Project: {project_name} (`{project_id}`)

## Command profile

The user should specify only a profile when needed:

- `-p L` or `--profile L`: low-cost triage and smoke.
- `-p M` or `--profile M`: normal bounded review.
- `-p H` or `--profile H`: deep read-only review.

If omitted, use `-p L`.

Do not ask the user to restate cache, role, fact, or Git read-only constraints. Load them from `references/core/` and `references/project/`.

## Required startup behavior

1. Read project `AGENTS.md` if present.
2. Load Core governance from `references/core/`.
3. Load Project Pack rules from `references/project/`.
4. Look up active SOPs and active known bug rules.
5. Use the requested profile to choose cost/depth.
6. Default to read-only audit for ambiguous or high-risk tasks.
7. Write full reports to the configured run directory when file writes outside the project are allowed.
8. Stop with `OWNER_DECISION_REQUIRED` for product judgment, write authorization, FAIL, UNKNOWN, unsupported gates, or budget escalation.

## Runtime enforcement behavior

ProjectGate is not just a set of instructions. For task types with active SOPs and active KnownBugRules, they must enter the runtime flow:

1. Start each real workflow by creating a `TaskRun.json` with `scripts/runtime/projectgate_task_start.py`.
2. The task output must declare `SOP_USED=` and `KNOWN_BUG_RULES_CHECKED=`.
3. Every stage output must pass `scripts/runtime/projectgate_stage_gate.py`.
4. Gate failures use `REPAIR_AND_RECHECK`: repair the output according to gate fail reasons and rerun the gate.
5. Final delivery must pass `scripts/runtime/projectgate_delivery_check.py`.

If a matching SOP or KnownBugRule exists but is not loaded into `TaskRun.json`, the workflow is invalid.

## L / M / H profile behavior

- `-p L`: low-cost triage, smoke tests, and narrow read-only checks. Load always-on rules plus minimal task-type matches.
- `-p M`: standard bounded project work. Load relevant task, stage, and tool rules. Produce entry maps or anchor maps when requested, but do not patch without owner authorization.
- `-p H`: deep high-risk review. Use routed deep knowledge, not blind full-context loading. Suitable for runtime facts, cross-system entry maps, and pre-patch audits.

## Knowledge growth rule

Do not load every SOP and KnownBugRule into every task. Use Runtime Knowledge Router scripts to select relevant active knowledge. Successful reusable TaskRuns may create SOP candidates. Failures may create Incident / KnownBugRule candidates. Candidates are not active until owner approval.

## Automatic success / failure capture

Within the ProjectGate Runtime flow, success and failure must create candidates automatically:

- stage gate failure -> auto incident + KnownBugRule candidate.
- delivery check failure -> auto incident + KnownBugRule candidate.
- successful delivery check -> auto SOP candidate when no candidate exists for the task type.
- observation gate can scan transcripts/logs for mojibake, missing UTF-8 PowerShell reads, run-root permission failures, and local repair result files.

The owner only approves or rejects candidates. The owner should not be asked to manually write candidates.

## Destructive action rule

No project file writes, patching, mutating Git, release, service, deployment, or external destructive action may occur without explicit owner authorization.

## Knowledge loop

Reusable workflows produce SOP candidates. Repeatable failures produce incidents and known-bug-rule candidates. Candidates do not become active without owner approval.
'''
    (out / 'projectgate' / 'SKILL.md').write_text(text, encoding='utf-8', newline='\n')


def write_scripts(out: pathlib.Path) -> None:
    scripts = out / 'projectgate' / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    (scripts / 'projectgate_skill_selftest.py').write_text(r'''#!/usr/bin/env python3
from __future__ import annotations
import pathlib, json

REQUIRED = [
    'SKILL.md',
    'references/core/core_governance.md',
    'references/core/stage_gate.md',
    'references/core/owner_decision_protocol.md',
    'references/project/project_manifest.json',
    'references/project/AGENTS.md.template',
    'references/project/README_ProjectPack.md',
    'scripts/runtime/projectgate_task_start.py',
    'scripts/runtime/projectgate_stage_gate.py',
    'scripts/runtime/projectgate_delivery_check.py',
    'scripts/runtime/projectgate_observation_gate.py',
    'scripts/runtime/projectgate_taskrun_continuity_gate.py',
    'scripts/runtime/projectgate_cli.py',
    'scripts/runtime/projectgate_pack_manager.py',
    'scripts/runtime/projectgate_candidate_lifecycle.py',
    'scripts/runtime/projectgate_autocapture.py',
    'scripts/runtime/projectgate_promote_candidate.py',
    'scripts/runtime/projectgate_incident_capture.py',
    'scripts/runtime/projectgate_sop_candidate.py',
    'scripts/runtime/projectgate_select_knowledge.py',
    'scripts/runtime/projectgate_build_knowledge_index.py'
]


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    errors = []
    for rel in REQUIRED:
        p = root / rel
        if not p.exists():
            errors.append(f'missing: {rel}')
        elif p.is_file() and not p.read_text(encoding='utf-8', errors='replace').strip():
            errors.append(f'empty: {rel}')
    try:
        json.loads((root / 'references/project/project_manifest.json').read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'invalid project manifest: {exc}')
    if errors:
        print('RESULT=FAIL')
        print('FAILED_STAGE=PROJECTGATE_SKILL_SELFTEST')
        print('FAIL_REASON=' + '; '.join(errors))
        return 1
    print('RESULT=PASS')
    print('PROJECTGATE_SKILL_SELFTEST=PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
''', encoding='utf-8', newline='\n')
    (scripts / 'projectgate_profile.py').write_text(r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse
ALIASES = {
    'l': 'L', 'low': 'L', 'light': 'L',
    'm': 'M', 'med': 'M', 'medium': 'M', 'standard': 'M', 'normal': 'M',
    'h': 'H', 'high': 'H', 'deep': 'H',
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--profile', default='L')
    args = ap.parse_args()
    key = ALIASES.get(args.profile.strip().lower())
    if not key:
        print('RESULT=FAIL')
        print('FAIL_REASON=unknown profile, use L/M/H or low/medium/high')
        return 2
    print('RESULT=PASS')
    print('PROFILE=' + key)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
''', encoding='utf-8', newline='\n')


def write_installer(out: pathlib.Path) -> None:
    (out / 'install_projectgate_codex_pack.py').write_text(r'''#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
SKILL_SRC = ROOT / 'projectgate'
PROJECT_AGENTS_TEMPLATE = SKILL_SRC / 'references' / 'project' / 'AGENTS.md.template'


MARKER = '.projectgate-managed.json'


def looks_like_projectgate_skill(dst: pathlib.Path) -> bool:
    return (dst / 'SKILL.md').exists() and (dst / 'references' / 'project' / 'project_manifest.json').exists()


def marker_payload(dst: pathlib.Path) -> str:
    return '{\n  "schema": "projectgate_managed_directory_v0_4_1",\n  "managedBy": "ProjectGate",\n  "kind": "codex_skill",\n  "destination": "' + str(dst).replace('\\', '/') + '"\n}\n'


def validate_skill_target(dst: pathlib.Path):
    dst = dst.resolve()
    home = pathlib.Path.home().resolve()
    if dst == pathlib.Path(dst.anchor).resolve() or dst == home:
        raise RuntimeError(f'unsafe skill install target: {dst}')
    if len(dst.parts) < 4:
        raise RuntimeError(f'skill install target too shallow: {dst}')
    if dst.exists() and not (dst / MARKER).exists() and not looks_like_projectgate_skill(dst):
        raise RuntimeError(f'refusing to replace unmarked non-ProjectGate skill directory: {dst}')


def backup_existing(dst: pathlib.Path):
    if not dst.exists():
        return None
    backup = dst.with_name(dst.name + '_backup_before_replace')
    i = 1
    while backup.exists():
        i += 1
        backup = dst.with_name(dst.name + '_backup_before_replace_' + str(i))
    shutil.move(str(dst), str(backup))
    return backup


def copytree_clean(src: pathlib.Path, dst: pathlib.Path, dry_run: bool):
    validate_skill_target(dst)
    if dry_run:
        print(f'DRY_RUN copy-managed {src} -> {dst}')
        return
    backup = backup_existing(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    (dst / MARKER).write_text(marker_payload(dst), encoding='utf-8')
    if backup:
        print('BACKUP_DIR=' + str(backup))


def install_project_agents_md(project_root: pathlib.Path, dry_run: bool, force: bool):
    if not project_root.exists():
        raise RuntimeError(f'project root missing: {project_root}')
    target = project_root / 'AGENTS.md'
    if target.exists() and not force:
        raise RuntimeError(f'AGENTS.md already exists: {target}')
    if dry_run:
        print(f'DRY_RUN copy {PROJECT_AGENTS_TEMPLATE} -> {target}')
        return
    shutil.copy2(PROJECT_AGENTS_TEMPLATE, target)


def run_selftest(skill_dst: pathlib.Path) -> int:
    script = skill_dst / 'scripts' / 'projectgate_skill_selftest.py'
    proc = subprocess.run([sys.executable, str(script)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end='')
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--install', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--home', default=str(pathlib.Path.home()))
    ap.add_argument('--install-project-agents-md', action='store_true')
    ap.add_argument('--project-root', default='')
    ap.add_argument('--force-project-agents-md', action='store_true')
    args = ap.parse_args()
    if not args.install and not args.dry_run:
        print('RESULT=FAIL')
        print('FAIL_REASON=Pass --dry-run or --install')
        return 2
    home = pathlib.Path(args.home).resolve()
    skill_dst = home / '.agents' / 'skills' / 'projectgate'
    try:
        copytree_clean(SKILL_SRC, skill_dst, args.dry_run)
        if args.install_project_agents_md:
            if not args.project_root:
                raise RuntimeError('--project-root required with --install-project-agents-md')
            install_project_agents_md(pathlib.Path(args.project_root).resolve(), args.dry_run, args.force_project_agents_md)
        if args.dry_run:
            print('RESULT=PASS')
            print('DRY_RUN=PASS')
            return 0
        code = run_selftest(skill_dst)
        if code != 0:
            print('INSTALL_RESULT=FAIL')
            return code
        print('INSTALL_RESULT=PASS')
        print('SKILL_PATH=' + str(skill_dst))
        print('PROJECT_AGENTS_MD=' + (str(pathlib.Path(args.project_root).resolve() / 'AGENTS.md') if args.install_project_agents_md else 'NOT_INSTALLED'))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=INSTALL')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
''', encoding='utf-8', newline='\n')


def build(args) -> int:
    core = pathlib.Path(args.core_root).resolve()
    pack = pathlib.Path(args.project_pack).resolve()
    out = pathlib.Path(args.out).resolve()
    manifest = read_manifest(pack)
    prepare_managed_output(out, 'codex_pack')
    (out / 'projectgate' / 'references' / 'core').mkdir(parents=True)
    (out / 'projectgate' / 'references' / 'project').mkdir(parents=True)
    # Core references only, not whole core package.
    copytree_merge(core / 'references', out / 'projectgate' / 'references' / 'core')
    # Project pack all relevant files.
    for name in ['project_manifest.json', 'AGENTS.md.template', 'README_ProjectPack.md']:
        shutil.copy2(pack / name, out / 'projectgate' / 'references' / 'project' / name)
    for dirname in ['rules', 'SOPs', 'KnownBugRules', 'TaskTypes', 'EvidenceProfiles']:
        if (pack / dirname).exists():
            copytree_merge(pack / dirname, out / 'projectgate' / 'references' / 'project' / dirname)
    write_skill(out, manifest)
    write_scripts(out)

    runtime_src = core / 'runtime'
    if runtime_src.exists():
        copytree_merge(runtime_src, out / 'projectgate' / 'scripts' / 'runtime')
    write_installer(out)
    (out / 'README_INSTALL.md').write_text(f'''# ProjectGate Codex Pack\n\nGenerated for project: {manifest.get('projectName')}\n\n## Install\n\n```powershell\npython install_projectgate_codex_pack.py --dry-run\npython install_projectgate_codex_pack.py --install\n```\n\n## Optional project AGENTS.md\n\n```powershell\npython install_projectgate_codex_pack.py --dry-run --install-project-agents-md --project-root "<PROJECT_ROOT>"\n```\n\n## Use\n\n```text\n/goal $projectgate -p L: <task>\n/goal $projectgate -p M: <task>\n/goal $projectgate -p H: <task>\n```\n''', encoding='utf-8', newline='\n')
    package_manifest = {
        'schema': 'projectgate_codex_pack_v0_1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'project': manifest,
        'profileSyntax': ['-p L', '-p M', '-p H', '--profile L', '--profile M', '--profile H']
    }
    (out / 'PACK_MANIFEST.json').write_text(json.dumps(package_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (out / MARKER).write_text(json.dumps(marker_payload('codex_pack', out), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('RESULT=PASS')
    print('CODEX_PACK=' + str(out))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--core-root', required=True)
    b.add_argument('--project-pack', required=True)
    b.add_argument('--out', required=True)
    args = ap.parse_args()
    if args.cmd == 'build':
        return build(args)
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
