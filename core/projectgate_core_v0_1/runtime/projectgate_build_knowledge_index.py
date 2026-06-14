#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib
from datetime import datetime, timezone


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding='utf-8'))


def infer_triggers(name: str, text: str = '') -> list[str]:
    src = (name + ' ' + text[:500]).lower()
    pairs = [
        ('runtime_fact', ['runtime_fact', 'runtime fact', 'entry_map', 'entry map']),
        ('patch', ['patch', 'anchor', 'script_delivery']),
        ('release', ['release', 'tag', 'publish']),
        ('windows_utf8', ['utf-8', 'encoding', 'powershell']),
        ('codex_smoke', ['smoke', 'taskrun', 'delivery_check']),
    ]
    out=[]
    for key, needles in pairs:
        if any(n in src for n in needles):
            out.append(key)
    return sorted(set(out))


def index_sops(pack: pathlib.Path) -> list[dict]:
    out=[]
    for state in ['active','candidates']:
        root=pack/'SOPs'/state
        if not root.exists():
            continue
        for p in sorted(root.rglob('*.md')):
            if p.name.endswith('_CN.md'):
                continue
            text=p.read_text(encoding='utf-8', errors='replace')
            out.append({
                'id': p.stem,
                'kind': 'SOP',
                'state': state,
                'relativePath': str(p.relative_to(pack)).replace('\\','/'),
                'triggers': infer_triggers(p.stem, text),
                'alwaysOn': False,
            })
    return out


def index_known_bug_rules(pack: pathlib.Path) -> list[dict]:
    out=[]
    for state in ['active','candidates']:
        root=pack/'KnownBugRules'/state
        if not root.exists():
            continue
        for p in sorted(root.rglob('*.json')):
            try:
                data=read_json(p)
            except Exception as exc:
                out.append({'id':'INVALID:'+p.stem,'kind':'KnownBugRule','state':state,'relativePath':str(p.relative_to(pack)).replace('\\','/'),'error':str(exc),'triggers':[],'alwaysOn':False})
                continue
            rules=[]
            if isinstance(data, dict) and isinstance(data.get('rules'), list):
                rules=data['rules']
            elif isinstance(data, list):
                rules=data
            elif isinstance(data, dict):
                rules=[data]
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    continue
                out.append({
                    'id': str(rule.get('bugId') or rule.get('id') or f'{p.stem}:{i}'),
                    'kind':'KnownBugRule',
                    'state':state,
                    'relativePath':str(p.relative_to(pack)).replace('\\','/'),
                    'triggers': sorted(set(str(x).lower() for x in rule.get('trigger', []) if isinstance(x, str))),
                    'severity': rule.get('severity','unknown'),
                    'alwaysOn': bool(rule.get('alwaysOn', False)),
                })
    return out


def build_index(pack: pathlib.Path) -> dict:
    items=index_sops(pack)+index_known_bug_rules(pack)
    return {
        'schema':'projectgate_knowledge_index_v0_3',
        'createdUtc':datetime.now(timezone.utc).isoformat(),
        'projectPack':str(pack),
        'itemCount':len(items),
        'items':items,
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--out', default='')
    args=ap.parse_args()
    try:
        pack=pathlib.Path(args.project_pack).resolve()
        if not (pack/'project_manifest.json').exists():
            raise RuntimeError('missing project_manifest.json')
        idx=build_index(pack)
        out=pathlib.Path(args.out).resolve() if args.out else pack/'knowledge_index.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(idx, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print('RESULT=PASS')
        print('KNOWLEDGE_INDEX='+str(out))
        print('ITEM_COUNT='+str(idx['itemCount']))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=BUILD_KNOWLEDGE_INDEX')
        print('FAIL_REASON='+str(exc))
        return 1

if __name__=='__main__':
    raise SystemExit(main())
