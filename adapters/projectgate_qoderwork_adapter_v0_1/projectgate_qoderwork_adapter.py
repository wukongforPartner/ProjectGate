#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import zipfile
from datetime import datetime, timezone

MARKER = '.projectgate-managed.json'
ZIP_NAME = 'qoderwork_skill.zip'

ROOT_DOC_RELATIVE_PATHS = [
    'README.md',
    'README_CN.md',
    'RUNTIME.md',
    'RUNTIME_CN.md',
    'SECURITY.md',
    'docs/TOOL_INTEGRATION_GUIDE.md',
    'docs/TOOL_INTEGRATION_GUIDE_CN.md',
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def is_relative_to(child: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_core_root(core_root: pathlib.Path) -> None:
    required = [
        core_root / 'README.md',
        core_root / 'README_CN.md',
        core_root / 'runtime' / 'projectgate_cli.py',
        core_root / 'runtime' / 'projectgate_stage_gate.py',
        core_root / 'runtime' / 'projectgate_delivery_check.py',
        core_root / 'workflow' / 'workflow_state_table.json',
        core_root / 'workflow' / 'role_state_table.json',
        core_root / 'workflow' / 'transition_rules.json',
        core_root / 'workflow' / 'owner_interaction_points.json',
        core_root / 'workflow' / 'projectgate_workflow_validator.py',
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise RuntimeError('core-root missing required files: ' + '; '.join(missing))


def validate_project_pack(project_pack: pathlib.Path) -> dict:
    manifest_path = project_pack / 'project_manifest.json'
    if not manifest_path.exists():
        raise RuntimeError('project-pack missing project_manifest.json: ' + str(project_pack))
    data = read_json(manifest_path)
    for key in ['projectId', 'projectName']:
        if not data.get(key):
            raise RuntimeError('project manifest missing key: ' + key)
    return data


def validate_output_target(out: pathlib.Path, force: bool, protected_roots: list[pathlib.Path]) -> None:
    out = out.resolve()
    home = pathlib.Path.home().resolve()
    if out == pathlib.Path(out.anchor).resolve():
        raise RuntimeError('unsafe output path is filesystem root: ' + str(out))
    if out == home:
        raise RuntimeError('unsafe output path is user home: ' + str(out))
    if len(out.parts) < 3:
        raise RuntimeError('unsafe output path is too shallow: ' + str(out))
    for root in protected_roots:
        root = root.resolve()
        if out == root or is_relative_to(out, root):
            raise RuntimeError('output path must not be inside protected source root: out=' + str(out) + ' root=' + str(root))
    if out.exists() and not force:
        raise RuntimeError('output exists; pass --force to replace: ' + str(out))


def ignore_runtime_artifacts(dirpath: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name == '__pycache__' or name.endswith('.pyc') or name == 'active_run':
            ignored.add(name)
    return ignored


def copytree_clean(src: pathlib.Path, dst: pathlib.Path) -> None:
    if not src.exists():
        raise RuntimeError('missing copy source: ' + str(src))
    shutil.copytree(src, dst, ignore=ignore_runtime_artifacts)


def copy_root_docs(root_docs: pathlib.Path, dst: pathlib.Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for rel in ROOT_DOC_RELATIVE_PATHS:
        src = root_docs / rel
        if not src.exists():
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def skill_text(manifest: dict) -> str:
    project_name = manifest.get('projectName') or manifest.get('projectId') or 'ProjectGate project'
    return f'''---\nname: projectgate-qoderwork\ndescription: ProjectGate QoderWork L2 workflow package for {project_name}. This package provides L1 instruction guidance plus an L2 workflow protocol. It does not provide native hard enforcement inside QoderWork.\n---\n\n# ProjectGate QoderWork L2 Workflow Package\n\nUse this Skill when working on the bundled project with ProjectGate discipline.\n\n## Enforcement boundary\n\nThis package is **not** native hard enforcement inside QoderWork.\n\nIt provides:\n\n- L1 instruction guidance for QoderWork.\n- L2 workflow protocol requiring ProjectGate CLI / TaskRun / stage gate / delivery check.\n- Bundled references for ProjectGate Core and the Project Pack.\n\nIt does not provide:\n\n- Automatic QoderWork upload.\n- Native command interception.\n- OS-level enforcement.\n- Automatic local CLI execution from QoderWork unless the host tool provides and verifies that capability.\n\n## Required workflow\n\nFor any real task:\n\n1. Create or reference a ProjectGate `TaskRun.json`.\n2. Produce a stage report using `STAGE_REPORT_TEMPLATE.md`.\n3. Do not advance stages until the user returns a `PG_STAGE_GATE=PASS` result.\n4. For commands, require `pg exec` or explicitly mark the action as `OUTSIDE_PROJECTGATE_CONTROLLED_FLOW`.\n5. Do not claim final completion until `PG_DELIVERY_CHECK=PASS` is returned.\n\n## Required stop conditions\n\nStop with `OWNER_DECISION_REQUIRED` when:\n\n- Product judgment is needed.\n- Write authorization is needed.\n- A gate fails.\n- A required fact is UNKNOWN.\n- A requested gate is listed in `UNSUPPORTED_GATES.md`.\n'''


def l2_workflow_text() -> str:
    return '''# QoderWork L2 Workflow Protocol\n\nStatus: L2_WORKFLOW_PROTOCOL\n\nThis file defines how a QoderWork conversation can be connected to ProjectGate Runtime without pretending QoderWork has native hard enforcement.\n\n## Minimum controlled loop\n\n1. User or host creates a ProjectGate TaskRun.\n2. QoderWork produces a stage report.\n3. User or host runs ProjectGate stage gate.\n4. QoderWork reads the gate result.\n5. If the gate failed, QoderWork enters REPAIR_AND_RECHECK.\n6. Commands must be run through `pg exec` when command evidence is required.\n7. Final completion requires delivery check PASS.\n\n## Required gate result tokens\n\n- `PG_TASKRUN=`\n- `PG_STAGE_GATE=PASS` or `PG_STAGE_GATE=FAIL`\n- `PG_DELIVERY_CHECK=PASS` or `PG_DELIVERY_CHECK=FAIL`\n- `PG_EXEC_LOG=` when a command was executed\n\n## Boundary\n\nThis workflow can enforce gates only when the user or host actually runs ProjectGate CLI commands and returns their result.\n'''


def stage_report_template() -> str:
    return '''# ProjectGate Stage Report\n\nSOP_USED=\nKNOWN_BUG_RULES_CHECKED=\nTASKRUN=\nSTAGE=\n\n## Confirmed Facts\n\n- \n\n## Unknown Facts\n\n- \n\n## Risks\n\n- \n\n## Stop Conditions\n\n- \n\n## Only Safe Next Step\n\n- \n'''


def gate_result_template() -> str:
    return '''# ProjectGate Gate Result\n\nTASKRUN=\nPG_STAGE_GATE=\nPG_DELIVERY_CHECK=\nPG_EXEC_LOG=\nNEXT_ACTION=\nFAIL_REASON=\n\n## Raw ProjectGate Output\n\n```text\n\n```\n'''


def unsupported_gates_text() -> str:
    return '''# Unsupported Gates\n\nThese gates are not provided by this QoderWork package.\n\nUNSUPPORTED_GATE=QODERWORK_NATIVE_CLI_EXECUTION_NOT_CONFIRMED\nUNSUPPORTED_GATE=QODERWORK_UPLOAD_NOT_AUTOMATED\nUNSUPPORTED_GATE=QODERWORK_COMMAND_INTERCEPTION_NOT_AVAILABLE\nUNSUPPORTED_GATE=OS_LEVEL_ENFORCEMENT_NOT_AVAILABLE\n\nIf a task requires any unsupported gate, stop with OWNER_DECISION_REQUIRED instead of pretending enforcement exists.\n'''


def manifest_payload(core_root: pathlib.Path, project_pack: pathlib.Path, project_manifest: dict) -> dict:
    return {
        'schema': 'projectgate_qoderwork_l2_workflow_package_v0_1',
        'adapter': 'projectgate_qoderwork_adapter_v0_1',
        'createdUtc': utc(),
        'coreRoot': str(core_root.resolve()),
        'projectPack': str(project_pack.resolve()),
        'projectManifest': project_manifest,
        'supported': ['L1_QODERWORK_SKILL_PACKAGE', 'L2_WORKFLOW_PROTOCOL'],
        'unsupportedGates': [
            'QODERWORK_NATIVE_CLI_EXECUTION_NOT_CONFIRMED',
            'QODERWORK_UPLOAD_NOT_AUTOMATED',
            'QODERWORK_COMMAND_INTERCEPTION_NOT_AVAILABLE',
            'OS_LEVEL_ENFORCEMENT_NOT_AVAILABLE',
        ],
    }


def write_package(out: pathlib.Path, core_root: pathlib.Path, project_pack: pathlib.Path, root_docs: pathlib.Path | None, force: bool) -> pathlib.Path:
    validate_core_root(core_root)
    project_manifest = validate_project_pack(project_pack)
    protected = [core_root, project_pack]
    if root_docs is not None:
        protected.append(root_docs)
    validate_output_target(out, force, protected)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    write_text(out / 'SKILL.md', skill_text(project_manifest))
    write_text(out / 'L2_WORKFLOW.md', l2_workflow_text())
    write_text(out / 'STAGE_REPORT_TEMPLATE.md', stage_report_template())
    write_text(out / 'GATE_RESULT_TEMPLATE.md', gate_result_template())
    write_text(out / 'UNSUPPORTED_GATES.md', unsupported_gates_text())
    write_text(out / 'PACK_MANIFEST.json', json.dumps(manifest_payload(core_root, project_pack, project_manifest), ensure_ascii=False, indent=2) + '\n')
    refs = out / 'references'
    copytree_clean(core_root, refs / 'core')
    copytree_clean(project_pack, refs / 'project')
    if root_docs is not None and root_docs.exists():
        copy_root_docs(root_docs, refs / 'root_docs')
    zip_path = out / ZIP_NAME
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.rglob('*')):
            if p.is_dir():
                continue
            rel = p.relative_to(out).as_posix()
            if rel == ZIP_NAME or '__pycache__' in rel.split('/') or rel.endswith('.pyc'):
                continue
            zf.write(p, rel)
    validate_zip(zip_path)
    return zip_path


def validate_zip(zip_path: pathlib.Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    required = {
        'SKILL.md',
        'L2_WORKFLOW.md',
        'STAGE_REPORT_TEMPLATE.md',
        'GATE_RESULT_TEMPLATE.md',
        'UNSUPPORTED_GATES.md',
        'PACK_MANIFEST.json',
        'references/project/project_manifest.json',
        'references/core/workflow/workflow_state_table.json',
        'references/core/workflow/role_state_table.json',
        'references/core/workflow/transition_rules.json',
        'references/core/workflow/owner_interaction_points.json',
        'references/core/workflow/projectgate_workflow_validator.py',
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError('zip missing required entries: ' + '; '.join(missing))
    if not any(name.startswith('references/core/') for name in names):
        raise RuntimeError('zip missing references/core entries')
    forbidden = [name for name in names if '__pycache__' in name.split('/') or name.endswith('.pyc')]
    if forbidden:
        raise RuntimeError('zip contains runtime artifacts: ' + '; '.join(forbidden[:8]))


def main() -> int:
    ap = argparse.ArgumentParser(description='Build a ProjectGate QoderWork L2 workflow package.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    build = sub.add_parser('build')
    build.add_argument('--core-root', required=True)
    build.add_argument('--project-pack', required=True)
    build.add_argument('--out', required=True)
    build.add_argument('--root-docs', default='')
    build.add_argument('--force', action='store_true')
    args = ap.parse_args()
    try:
        if args.cmd != 'build':
            raise RuntimeError('unknown command: ' + str(args.cmd))
        core_root = pathlib.Path(args.core_root).resolve()
        project_pack = pathlib.Path(args.project_pack).resolve()
        out = pathlib.Path(args.out).resolve()
        root_docs = pathlib.Path(args.root_docs).resolve() if args.root_docs else None
        zip_path = write_package(out, core_root, project_pack, root_docs, args.force)
        print('RESULT=PASS')
        print('QODERWORK_L2_WORKFLOW_PACKAGE_READY')
        print('OUT_DIR=' + str(out))
        print('ZIP_PATH=' + str(zip_path))
        print('SKILL_MD=' + str(out / 'SKILL.md'))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_ADAPTER_BUILD')
        print('FAIL_REASON=' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
