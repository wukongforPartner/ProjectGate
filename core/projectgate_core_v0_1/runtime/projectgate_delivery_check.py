#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib
from projectgate_autocapture import create_incident_and_candidate, create_sop_candidate_if_needed, safe


def main() -> int:
    ap = argparse.ArgumentParser(description='Verify a ProjectGate run cannot be delivered without loaded SOPs/rules and at least one passing gate.')
    ap.add_argument('--taskrun', required=True)
    args = ap.parse_args()
    try:
        path = pathlib.Path(args.taskrun).resolve()
        taskrun = json.loads(path.read_text(encoding='utf-8'))
        reasons = []
        if not taskrun.get('loadedSOPs'):
            reasons.append('no active SOPs were loaded into TaskRun')
        if not taskrun.get('loadedKnownBugRules'):
            reasons.append('no active KnownBugRules were loaded into TaskRun')
        gates = taskrun.get('gateHistory') or []
        if not any(g.get('result') == 'PASS' for g in gates):
            reasons.append('no passing stage gate recorded')
        if reasons:
            symptom = ' | '.join(reasons)
            try:
                create_incident_and_candidate(
                    path,
                    incident_id='AUTO-DELIVERY-CHECK-FAIL',
                    title='Delivery check failed',
                    symptom=symptom,
                    rule_id='PG-DELIVERY-CHECK-FAIL-001',
                    triggers=['delivery_check', str((taskrun.get('task') or {}).get('type') or 'unknown_task')],
                    on_fail='REPAIR_AND_RECHECK',
                )
            except Exception as capture_exc:
                reasons.append('auto incident capture failed: ' + str(capture_exc))
            print('RESULT=FAIL')
            print('FAILED_STAGE=DELIVERY_CHECK')
            print('NEXT_ACTION=REPAIR_AND_RECHECK')
            print('FAIL_REASON=' + ' | '.join(reasons))
            return 1
        sop_candidate = create_sop_candidate_if_needed(path)
        print('RESULT=PASS')
        print('DELIVERY_CHECK=PASS')
        print('AUTO_SOP_CANDIDATE=' + str(sop_candidate))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=DELIVERY_CHECK_EXCEPTION')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
