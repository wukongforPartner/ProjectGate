#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re
from projectgate_build_knowledge_index import build_index

PROFILE_ALIASES={'l':'L','low':'L','light':'L','m':'M','medium':'M','standard':'M','normal':'M','h':'H','high':'H','deep':'H'}


def tokens(text: str) -> set[str]:
    raw = re.findall(r'[a-zA-Z0-9_]+', text.lower())
    out = set(raw)
    for item in raw:
        out.update(part for part in item.split('_') if part)
        parts = [part for part in item.split('_') if part]
        for i in range(len(parts)-1):
            out.add(parts[i] + '_' + parts[i+1])
    return out


def normalize_profile(raw: str) -> str:
    key=PROFILE_ALIASES.get((raw or 'L').strip().lower())
    if not key:
        raise RuntimeError('unknown profile, use L/M/H')
    return key


def item_matches(item: dict, task_tokens: set[str], stage_tokens: set[str]) -> bool:
    if item.get('alwaysOn'):
        return True
    triggers=set(str(x).lower() for x in item.get('triggers', []))
    if triggers and (triggers & task_tokens or triggers & stage_tokens):
        return True
    return False


def select(index: dict, task_type: str, stage: str, profile: str) -> list[dict]:
    profile=normalize_profile(profile)
    task_tokens=tokens(task_type)
    stage_tokens=tokens(stage)
    active=[x for x in index.get('items', []) if x.get('state')=='active']
    if profile=='H':
        return active
    matched=[x for x in active if item_matches(x, task_tokens, stage_tokens)]
    if profile=='M':
        return matched
    return matched


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--task-type', required=True)
    ap.add_argument('--stage', default='READONLY_AUDIT')
    ap.add_argument('-p','--profile', default='L')
    ap.add_argument('--out', default='')
    args=ap.parse_args()
    try:
        pack=pathlib.Path(args.project_pack).resolve()
        idx=build_index(pack)
        selected=select(idx,args.task_type,args.stage,args.profile)
        payload={'schema':'projectgate_selected_knowledge_v0_3','profile':normalize_profile(args.profile),'taskType':args.task_type,'stage':args.stage,'selectedCount':len(selected),'selected':selected}
        if args.out:
            out=pathlib.Path(args.out).resolve()
            out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print('SELECTED_KNOWLEDGE='+str(out))
        print('RESULT=PASS')
        print('PROFILE='+payload['profile'])
        print('SELECTED_COUNT='+str(len(selected)))
        for item in selected:
            print(f"SELECTED={item.get('kind')}:{item.get('id')}")
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=SELECT_KNOWLEDGE')
        print('FAIL_REASON='+str(exc))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
