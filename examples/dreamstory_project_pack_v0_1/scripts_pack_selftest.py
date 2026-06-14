#!/usr/bin/env python3
from __future__ import annotations
import pathlib, json

REQUIRED = [
    'project_manifest.json', 'AGENTS.md.template', 'README_ProjectPack.md',
    'rules/dreamstory_boundaries.md',
    'SOPs/active/runtime_fact_entry_map.md',
    'SOPs/active/patch_anchor_map.md',
    'KnownBugRules/active/dreamstory_known_bug_rules_seed_v0_1.json',
    'TaskTypes/active/dreamstory_task_types_seed_v0_1.json',
    'EvidenceProfiles/player_feedback_triage.json'
]


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent
    errors = []
    for rel in REQUIRED:
        p = root / rel
        if not p.exists():
            errors.append(f'missing: {rel}')
        elif not p.read_text(encoding='utf-8', errors='replace').strip():
            errors.append(f'empty: {rel}')
    for p in root.rglob('*.json'):
        try:
            json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'invalid json {p.relative_to(root)}: {exc}')
    if errors:
        print('RESULT=FAIL')
        print('FAILED_STAGE=DREAMSTORY_PACK_SELFTEST')
        print('FAIL_REASON=' + '; '.join(errors))
        return 1
    print('RESULT=PASS')
    print('DREAMSTORY_PACK_SELFTEST=PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
