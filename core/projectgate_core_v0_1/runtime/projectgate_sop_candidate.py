#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re
from datetime import datetime, timezone


def safe(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+','_',text.strip())[:80].strip('_') or 'task'


def main() -> int:
    ap=argparse.ArgumentParser(description='Create an SOP candidate from a successful TaskRun. Does not promote it to active.')
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--taskrun', required=True)
    ap.add_argument('--title', default='')
    args=ap.parse_args()
    try:
        pack=pathlib.Path(args.project_pack).resolve()
        taskrun_path=pathlib.Path(args.taskrun).resolve()
        tr=json.loads(taskrun_path.read_text(encoding='utf-8'))
        gates=tr.get('gateHistory') or []
        if not any(g.get('result')=='PASS' for g in gates):
            raise RuntimeError('cannot create SOP candidate: no passing gate in TaskRun')
        task=tr.get('task',{})
        task_type=task.get('type','unknown_task')
        title=args.title or f"SOP candidate for {task_type}"
        outdir=pack/'SOPs'/'candidates'
        outdir.mkdir(parents=True, exist_ok=True)
        ts=datetime.now().strftime('%Y%m%d_%H%M%S')
        out=outdir/(safe(task_type)+'_'+ts+'.md')
        used=', '.join(x.get('id','') for x in tr.get('loadedSOPs',[])) or 'none'
        rules=', '.join(x.get('id','') for x in tr.get('loadedKnownBugRules',[])) or 'none'
        gate_lines='\n'.join(f"- {g.get('stage')}: {g.get('result')} -> {g.get('nextAction')}" for g in gates)
        text=f'''# {title}

Status: SOP_CANDIDATE

Created UTC: {datetime.now(timezone.utc).isoformat()}

Source TaskRun: `{taskrun_path}`

## Task

- taskType: `{task_type}`
- profile: `{task.get('profile','unknown')}`

## Preconditions

- ProjectGate Runtime must create TaskRun.json.
- Active SOPs and KnownBugRules must be selected and recorded.
- Stage outputs must declare `SOP_USED=` and `KNOWN_BUG_RULES_CHECKED=`.

## Observed successful flow

1. Start task with ProjectGate Runtime.
2. Produce stage output in the configured run directory.
3. Run stage gate.
4. Run delivery check before final report.
5. Confirm project working tree is clean when task is read-only.

## Loaded SOPs

{used}

## Checked KnownBugRules

{rules}

## Gate history

{gate_lines}

## Promotion rule

This file is only a candidate. It must not become active unless the owner confirms that this flow is stable, reusable, and not merely an accidental success.
'''
        out.write_text(text, encoding='utf-8', newline='\n')
        print('RESULT=PASS')
        print('SOP_CANDIDATE='+str(out))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=SOP_CANDIDATE')
        print('FAIL_REASON='+str(exc))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
