#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib


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
            print('RESULT=FAIL')
            print('FAILED_STAGE=DELIVERY_CHECK')
            print('FAIL_REASON=' + ' | '.join(reasons))
            return 1
        print('RESULT=PASS')
        print('DELIVERY_CHECK=PASS')
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=DELIVERY_CHECK_EXCEPTION')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
