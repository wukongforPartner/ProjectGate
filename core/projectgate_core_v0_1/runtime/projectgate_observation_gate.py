#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib
from projectgate_autocapture import create_incident_and_candidate, detect_observation_issues, safe


def main() -> int:
    ap = argparse.ArgumentParser(description='Scan tool transcript / observation text and auto-capture incidents / KnownBugRule candidates.')
    ap.add_argument('--taskrun', required=True)
    ap.add_argument('--input', required=True)
    args = ap.parse_args()
    try:
        taskrun_path = pathlib.Path(args.taskrun).resolve()
        input_path = pathlib.Path(args.input).resolve()
        text = input_path.read_text(encoding='utf-8', errors='replace')
        issues = detect_observation_issues(text)
        records = []
        for issue in issues:
            rec = create_incident_and_candidate(
                taskrun_path,
                incident_id='AUTO-' + safe(issue['ruleId']),
                title=issue['title'],
                symptom=issue['symptom'],
                rule_id=issue['ruleId'],
                triggers=issue['trigger'],
                on_fail='REPAIR_AND_RECHECK',
            )
            records.append(rec)
        fail_count = sum(1 for x in issues if x.get('severity') == 'fail')
        if fail_count:
            print('RESULT=FAIL')
            print('FAILED_STAGE=OBSERVATION_GATE')
            print('NEXT_ACTION=REPAIR_AND_RECHECK')
            print('AUTO_CAPTURED=' + str(len(records)))
            return 1
        print('RESULT=PASS')
        print('OBSERVATION_GATE=PASS')
        print('AUTO_CAPTURED=' + str(len(records)))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=OBSERVATION_GATE_EXCEPTION')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
