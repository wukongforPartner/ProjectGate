#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, sys
from projectgate_autocapture import load_json, save_json, detect_observation_issues, create_incident_and_candidate


def main() -> int:
    ap = argparse.ArgumentParser(description='Check that a ProjectGate goal uses one primary TaskRun unless child runs are explicitly declared.')
    ap.add_argument('--taskrun', required=True)
    ap.add_argument('--input', required=True, help='Transcript or report text containing observed TaskRun paths.')
    args = ap.parse_args()
    taskrun_path = pathlib.Path(args.taskrun).resolve()
    input_path = pathlib.Path(args.input).resolve()
    try:
        taskrun = load_json(taskrun_path)
        text = input_path.read_text(encoding='utf-8')
        issues = [i for i in detect_observation_issues(text) if i.get('ruleId') == 'PG-RUNTIME-SINGLE-PRIMARY-TASKRUN-001']
        result = 'PASS'
        next_action = 'CONTINUE'
        records = []
        if issues:
            result = 'FAIL'
            next_action = 'REPAIR_AND_RECHECK'
            for idx, issue in enumerate(issues, start=1):
                rec = create_incident_and_candidate(
                    taskrun_path,
                    f"AUTO-{issue['ruleId']}-{idx}",
                    issue['title'],
                    issue['symptom'],
                    issue['ruleId'],
                    issue.get('trigger', []),
                    next_action,
                )
                records.append(rec)
        taskrun = load_json(taskrun_path)
        taskrun.setdefault('gateHistory', []).append({
            'stage': 'TASKRUN_CONTINUITY',
            'result': result,
            'nextAction': next_action,
            'input': str(input_path),
            'records': records,
        })
        taskrun['stage'] = 'TASKRUN_CONTINUITY_CHECKED' if result == 'PASS' else 'TASKRUN_CONTINUITY_FAILED'
        save_json(taskrun_path, taskrun)
        if result == 'PASS':
            print('RESULT=PASS')
            print('TASKRUN_CONTINUITY_GATE=PASS')
            print('NEXT_ACTION=CONTINUE')
            return 0
        print('RESULT=FAIL')
        print('FAILED_STAGE=TASKRUN_CONTINUITY_GATE')
        print('NEXT_ACTION=REPAIR_AND_RECHECK')
        print('AUTO_CAPTURED=' + str(len(records)))
        return 1
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=TASKRUN_CONTINUITY_GATE')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
