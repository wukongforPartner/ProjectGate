#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib
from datetime import datetime, timezone

DIRS = ['ProjectPacks', 'KnowledgeBase', 'Runs', 'Adapters', 'Config']


def main() -> int:
    ap = argparse.ArgumentParser(description='Initialize a ProjectGate workspace at a user-selected path.')
    ap.add_argument('--workspace-root', required=True)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = pathlib.Path(args.workspace_root).resolve()
    if args.dry_run:
        for d in DIRS:
            print('DRY_RUN mkdir ' + str(root / d))
        print('DRY_RUN write ' + str(root / 'Config' / 'projectgate.config.json'))
        print('RESULT=PASS')
        print('DRY_RUN=PASS')
        return 0
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    cfg = {
        'schema': 'projectgate_config_v0_1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'workspaceRoot': str(root),
        'projectsRoot': str(root / 'ProjectPacks'),
        'knowledgeRoot': str(root / 'KnowledgeBase'),
        'runsRoot': str(root / 'Runs'),
        'adaptersRoot': str(root / 'Adapters')
    }
    (root / 'Config' / 'projectgate.config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('RESULT=PASS')
    print('WORKSPACE_ROOT=' + str(root))
    print('CONFIG_FILE=' + str(root / 'Config' / 'projectgate.config.json'))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
