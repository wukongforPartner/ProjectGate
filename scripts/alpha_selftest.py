#!/usr/bin/env python3
from __future__ import annotations
import pathlib, subprocess, sys, tempfile, shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(cmd):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout, end='')
    if p.stderr:
        print(p.stderr, file=sys.stderr, end='')
    return p.returncode


def main() -> int:
    required = [
        'install_projectgate_alpha.py',
    'core/projectgate_core_v0_1/runtime/projectgate_task_start.py',
    'core/projectgate_core_v0_1/runtime/projectgate_stage_gate.py',
    'core/projectgate_core_v0_1/runtime/projectgate_delivery_check.py',
    'core/projectgate_core_v0_1/runtime/projectgate_observation_gate.py',
    'core/projectgate_core_v0_1/runtime/projectgate_taskrun_continuity_gate.py',
    'pg.bat',
    'pg.py',
    'core/projectgate_core_v0_1/runtime/projectgate_cli.py',
    'core/projectgate_core_v0_1/runtime/projectgate_pack_manager.py',
    'core/projectgate_core_v0_1/runtime/projectgate_candidate_lifecycle.py',
    'core/projectgate_core_v0_1/runtime/projectgate_autocapture.py',
    'core/projectgate_core_v0_1/runtime/projectgate_promote_candidate.py',
    'core/projectgate_core_v0_1/runtime/projectgate_incident_capture.py',
    'core/projectgate_core_v0_1/runtime/projectgate_sop_candidate.py',
    'core/projectgate_core_v0_1/runtime/projectgate_select_knowledge.py',
    'core/projectgate_core_v0_1/runtime/projectgate_build_knowledge_index.py',
        'README.md',
        'core/projectgate_core_v0_1/scripts/projectgate_core_selftest.py',
        'adapters/projectgate_codex_adapter_v0_1/projectgate_codex_adapter.py',
        'examples/ProjectDocsInbox_Template/01_project_overview.md'
    ]
    errors = []
    for rel in required:
        if not (ROOT / rel).exists():
            errors.append(f'missing: {rel}')
    if errors:
        print('RESULT=FAIL')
        print('FAIL_REASON=' + '; '.join(errors))
        return 1
    code = run([sys.executable, str(ROOT / 'core/projectgate_core_v0_1/scripts/projectgate_core_selftest.py')])
    if code != 0:
        return code
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='projectgate_alpha_test_'))
    try:
        code = run([sys.executable, str(ROOT / 'install_projectgate_alpha.py'), '--dry-run', '--workspace-root', str(tmp / 'Workspace')])
        if code != 0:
            return code
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('RESULT=PASS')
    print('ALPHA_SELFTEST=PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
