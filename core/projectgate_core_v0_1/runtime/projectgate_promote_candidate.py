#!/usr/bin/env python3
from __future__ import annotations
import argparse, pathlib, shutil


def main() -> int:
    ap=argparse.ArgumentParser(description='Promote an owner-approved SOP or KnownBugRule candidate to active.')
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--kind', choices=['sop','knownbug'], required=True)
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--owner-approved', action='store_true')
    args=ap.parse_args()
    try:
        if not args.owner_approved:
            raise RuntimeError('owner approval required for promotion')
        pack=pathlib.Path(args.project_pack).resolve()
        cand=pathlib.Path(args.candidate).resolve()
        if not cand.exists():
            raise RuntimeError('candidate missing: '+str(cand))
        if args.kind=='sop':
            active=pack/'SOPs'/'active'/cand.name
        else:
            active=pack/'KnownBugRules'/'active'/cand.name
        active.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(cand, active)
        print('RESULT=PASS')
        print('PROMOTED_ACTIVE='+str(active))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=PROMOTE_CANDIDATE')
        print('FAIL_REASON='+str(exc))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
