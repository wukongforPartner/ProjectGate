#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib

REQUIRED_DIRS = ['SOPs', 'KnownBugRules', 'TaskTypes', 'EvidenceProfiles']
REQUIRED_FILES = ['project_manifest.json', 'AGENTS.md.template', 'README_ProjectPack.md']


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--pack', required=True)
    args = ap.parse_args()
    root = pathlib.Path(args.pack).resolve()
    errors = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f'missing file: {rel}')
    for rel in REQUIRED_DIRS:
        if not (root / rel).exists():
            errors.append(f'missing dir: {rel}')
    if (root / 'project_manifest.json').exists():
        try:
            json.loads((root / 'project_manifest.json').read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'invalid manifest json: {exc}')
    if errors:
        print('RESULT=FAIL')
        print('FAILED_STAGE=VALIDATE_PROJECT_PACK')
        print('FAIL_REASON=' + '; '.join(errors))
        return 1
    print('RESULT=PASS')
    print('PROJECT_PACK_VALID=PASS')
    print('PACK=' + str(root))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
