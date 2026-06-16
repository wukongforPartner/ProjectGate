#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime

STAGE_READONLY = 'READONLY_AUDIT'


def repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def runtime_script(name: str) -> pathlib.Path:
    return repo_root() / 'core' / 'projectgate_core_v0_1' / 'runtime' / name


def run_python(script: pathlib.Path, args: list[str]) -> tuple[int, str]:
    cmd = [sys.executable, str(script)] + [str(a) for a in args]
    proc = subprocess.run(cmd, cwd=str(repo_root()), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    return proc.returncode, proc.stdout or ''


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def parse_key(output: str, key: str) -> str:
    prefix = key + '='
    for line in output.splitlines():
        if line.startswith(prefix):
            return line.split('=', 1)[1].strip()
    return ''


def safe_stage(stage: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', stage.strip())[:80].strip('_') or 'STAGE'


def stamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def taskrun_dir(taskrun: pathlib.Path) -> pathlib.Path:
    return taskrun.resolve().parent


def make_worker_input(taskrun: pathlib.Path, stage: str, task_title: str, mode: str, failure_reason: str = '', next_stage: str = '') -> pathlib.Path:
    run_dir = taskrun_dir(taskrun)
    stage_safe = safe_stage(stage)
    if mode == 'repair':
        out = run_dir / f'QODERWORK_REPAIR_INPUT_{stage_safe}_{stamp()}.md'
        title = 'QoderWork Repair Task Packet'
    elif mode == 'next':
        out = run_dir / f'QODERWORK_INPUT_{safe_stage(next_stage or stage)}_{stamp()}.md'
        title = 'QoderWork Next Stage Task Packet'
    else:
        out = run_dir / f'QODERWORK_INPUT_{stage_safe}_{stamp()}.md'
        title = 'QoderWork Stage Task Packet'
    text = f'''# {title}\n\nTASKRUN={taskrun}\nSTAGE={next_stage or stage}\nTASK_TITLE={task_title}\n\n## Workflow owner\n\nProjectGate is the workflow owner. QoderWork is a worker channel.\n\n## Required output contract\n\nThe worker output must be a stage report file with these fields:\n\n```text\nSOP_USED=\nKNOWN_BUG_RULES_CHECKED=\nTASKRUN={taskrun}\nSTAGE={next_stage or stage}\n```\n\nFor READONLY_AUDIT, include these sections exactly:\n\n- 已确认事实\n- 不能确认事实\n- 风险点\n- 必须停手条件\n- 唯一安全下一步\n\n## Failure reason, if this is repair\n\n```text\n{failure_reason}\n```\n\n## Stop rules\n\nDo not modify project files.\nDo not output patches unless a later ProjectGate stage explicitly authorizes writes.\nDo not advance stages yourself. ProjectGate runner will run the gate and generate the next packet.\n'''
    write_text(out, text)
    return out


def cmd_start(args) -> int:
    start_script = runtime_script('projectgate_task_start.py')
    code, output = run_python(start_script, [
        '--project-pack', args.project_pack,
        '--task-type', args.task_type,
        '--task-title', args.task_title,
        '-p', args.profile,
        '--run-root', args.run_root,
    ])
    print(output, end='')
    if code != 0:
        return code
    taskrun_raw = parse_key(output, 'TASKRUN')
    run_dir_raw = parse_key(output, 'RUN_DIR')
    if not taskrun_raw:
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_START')
        print('FAIL_REASON=projectgate_task_start.py did not return TASKRUN=')
        return 1
    taskrun = pathlib.Path(taskrun_raw).resolve()
    worker_input = make_worker_input(taskrun, args.stage, args.task_title, 'stage')
    print('RESULT=PASS')
    print('QODERWORK_RUNNER_START=PASS')
    print('TASKRUN=' + str(taskrun))
    if run_dir_raw:
        print('RUN_DIR=' + run_dir_raw)
    print('QODERWORK_INPUT=' + str(worker_input))
    return 0


def cmd_accept(args) -> int:
    taskrun = pathlib.Path(args.taskrun).resolve()
    source = pathlib.Path(args.input).resolve()
    if not taskrun.exists():
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_ACCEPT')
        print('FAIL_REASON=TaskRun missing: ' + str(taskrun))
        return 1
    if not source.exists():
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_ACCEPT')
        print('FAIL_REASON=input report missing: ' + str(source))
        return 1
    out = taskrun_dir(taskrun) / f'QODERWORK_STAGE_REPORT_{safe_stage(args.stage)}_{stamp()}.md'
    shutil.copy2(source, out)
    print('RESULT=PASS')
    print('QODERWORK_STAGE_REPORT_ACCEPTED=PASS')
    print('ACCEPTED_REPORT=' + str(out))
    return 0


def cmd_gate(args) -> int:
    taskrun = pathlib.Path(args.taskrun).resolve()
    report = pathlib.Path(args.input).resolve()
    if not taskrun.exists():
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_GATE')
        print('FAIL_REASON=TaskRun missing: ' + str(taskrun))
        return 1
    if not report.exists():
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_GATE')
        print('FAIL_REASON=stage report missing: ' + str(report))
        return 1
    stage_script = runtime_script('projectgate_stage_gate.py')
    code, output = run_python(stage_script, ['--taskrun', str(taskrun), '--stage', args.stage, '--input', str(report)])
    result_file = taskrun_dir(taskrun) / f'PG_GATE_RESULT_{safe_stage(args.stage)}_{stamp()}.txt'
    write_text(result_file, output)
    print(output, end='')
    print('PG_GATE_RESULT_FILE=' + str(result_file))
    if code == 0 and 'STAGE_GATE=PASS' in output:
        next_stage = args.next_stage or 'NEXT_STAGE_OWNER_DECISION_REQUIRED'
        next_input = make_worker_input(taskrun, args.stage, args.task_title, 'next', next_stage=next_stage)
        print('QODERWORK_NEXT_INPUT=' + str(next_input))
        return 0
    repair_input = make_worker_input(taskrun, args.stage, args.task_title, 'repair', failure_reason=output)
    print('QODERWORK_REPAIR_INPUT=' + str(repair_input))
    return code if code != 0 else 1


def cmd_delivery(args) -> int:
    taskrun = pathlib.Path(args.taskrun).resolve()
    if not taskrun.exists():
        print('RESULT=FAIL')
        print('FAILED_STAGE=QODERWORK_RUNNER_DELIVERY')
        print('FAIL_REASON=TaskRun missing: ' + str(taskrun))
        return 1
    delivery_script = runtime_script('projectgate_delivery_check.py')
    code, output = run_python(delivery_script, ['--taskrun', str(taskrun)])
    result_file = taskrun_dir(taskrun) / f'PG_DELIVERY_RESULT_{stamp()}.txt'
    write_text(result_file, output)
    print(output, end='')
    print('PG_DELIVERY_RESULT_FILE=' + str(result_file))
    if code == 0:
        print('QODERWORK_RUNNER_DELIVERY=PASS')
    return code


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description='ProjectGate QoderWork workflow runner. ProjectGate owns task state; QoderWork is a worker channel.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    st = sub.add_parser('start')
    st.add_argument('--project-pack', required=True)
    st.add_argument('--task-type', required=True)
    st.add_argument('--task-title', required=True)
    st.add_argument('-p', '--profile', default='L')
    st.add_argument('--run-root', required=True)
    st.add_argument('--stage', default=STAGE_READONLY)

    ac = sub.add_parser('accept')
    ac.add_argument('--taskrun', required=True)
    ac.add_argument('--stage', default=STAGE_READONLY)
    ac.add_argument('--input', required=True)

    gt = sub.add_parser('gate')
    gt.add_argument('--taskrun', required=True)
    gt.add_argument('--stage', default=STAGE_READONLY)
    gt.add_argument('--input', required=True)
    gt.add_argument('--task-title', default='')
    gt.add_argument('--next-stage', default='')

    de = sub.add_parser('delivery')
    de.add_argument('--taskrun', required=True)
    return ap


def main() -> int:
    args = build_parser().parse_args()
    if args.cmd == 'start':
        return cmd_start(args)
    if args.cmd == 'accept':
        return cmd_accept(args)
    if args.cmd == 'gate':
        return cmd_gate(args)
    if args.cmd == 'delivery':
        return cmd_delivery(args)
    print('RESULT=FAIL')
    print('FAILED_STAGE=QODERWORK_RUNNER')
    print('FAIL_REASON=unknown command')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
