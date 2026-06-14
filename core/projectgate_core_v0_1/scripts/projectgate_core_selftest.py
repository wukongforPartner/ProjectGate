#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib

REQUIRED = [
    'README.md',
    'references/core_governance.md',
    'references/stage_gate.md',
    'references/role_contracts.md',
    'references/owner_decision_protocol.md',
    'references/budget_profiles.md',
    'references/knowledge_lifecycle.md',
    'references/adapter_contract.md',
    'templates/AGENTS.md.template',
    'templates/README_ProjectPack.template.md',
    'schemas/project_manifest.schema.json',
]
DEFAULT_FORBIDDEN_TERMS = []



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=str(pathlib.Path(__file__).resolve().parents[1]))
    ap.add_argument('--forbidden-terms-file', default='', help='Optional newline-separated terms that must not appear in core files.')
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    errors = []
    forbidden_terms = list(DEFAULT_FORBIDDEN_TERMS)
    if args.forbidden_terms_file:
        forbidden_terms.extend([line.strip() for line in pathlib.Path(args.forbidden_terms_file).read_text(encoding='utf-8').splitlines() if line.strip()])
    for rel in REQUIRED:
        p = root / rel
        if not p.exists():
            errors.append(f'missing required file: {rel}')
        elif p.is_file() and not p.read_text(encoding='utf-8', errors='replace').strip():
            errors.append(f'empty required file: {rel}')
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.md', '.json', '.py', '.txt'}:
            text = p.read_text(encoding='utf-8', errors='replace')
            for term in forbidden_terms:
                if term in text:
                    errors.append(f'forbidden project-specific term in core: {term} at {p.relative_to(root)}')
    for p in root.rglob('*.json'):
        try:
            json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'invalid json: {p.relative_to(root)}: {exc}')
    if errors:
        print('RESULT=FAIL')
        print('FAILED_STAGE=CORE_SELFTEST')
        print('FAIL_REASON=' + '; '.join(errors))
        return 1
    print('RESULT=PASS')
    print('CORE_SELFTEST=PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
