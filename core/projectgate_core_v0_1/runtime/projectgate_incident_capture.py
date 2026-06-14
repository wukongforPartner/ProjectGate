#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re
from datetime import datetime, timezone


def safe(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+','_',text.strip())[:90].strip('_') or 'incident'


def main() -> int:
    ap=argparse.ArgumentParser(description='Capture an incident and create a KnownBugRule candidate. Does not promote it to active.')
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--taskrun', default='')
    ap.add_argument('--incident-id', required=True)
    ap.add_argument('--title', required=True)
    ap.add_argument('--symptom', required=True)
    ap.add_argument('--candidate-rule-id', required=True)
    ap.add_argument('--trigger', action='append', default=[])
    ap.add_argument('--on-fail', default='REPAIR_AND_RECHECK')
    args=ap.parse_args()
    try:
        pack=pathlib.Path(args.project_pack).resolve()
        ts=datetime.now().strftime('%Y%m%d_%H%M%S')
        inc_dir=pack/'Incidents'/'active_run'
        inc_dir.mkdir(parents=True,exist_ok=True)
        rule_dir=pack/'KnownBugRules'/'candidates'
        rule_dir.mkdir(parents=True,exist_ok=True)
        incident={
            'schema':'projectgate_incident_v0_3',
            'incidentId':args.incident_id,
            'title':args.title,
            'createdUtc':datetime.now(timezone.utc).isoformat(),
            'symptom':args.symptom,
            'taskrun':args.taskrun,
            'status':'captured',
            'nextAction':'create_known_bug_rule_candidate'
        }
        inc_path=inc_dir/(safe(args.incident_id)+'_'+ts+'.json')
        inc_path.write_text(json.dumps(incident,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        rule={'schema':'projectgate_known_bug_rule_candidate_v0_3','rules':[{'bugId':args.candidate_rule_id,'title':args.title,'trigger':args.trigger,'severity':'candidate','symptom':args.symptom,'onFail':args.on_fail,'ownerApproved':False,'sourceIncident':str(inc_path)}]}
        rule_path=rule_dir/(safe(args.candidate_rule_id)+'_'+ts+'.json')
        rule_path.write_text(json.dumps(rule,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('RESULT=PASS')
        print('INCIDENT='+str(inc_path))
        print('KNOWN_BUG_RULE_CANDIDATE='+str(rule_path))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=INCIDENT_CAPTURE')
        print('FAIL_REASON='+str(exc))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
