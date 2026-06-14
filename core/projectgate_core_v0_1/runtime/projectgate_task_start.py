#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re
from datetime import datetime, timezone
from projectgate_build_knowledge_index import build_index
from projectgate_select_knowledge import select as select_knowledge

PROFILE_ALIASES = {
    'l': 'L', 'low': 'L', 'light': 'L',
    'm': 'M', 'med': 'M', 'medium': 'M', 'standard': 'M', 'normal': 'M',
    'h': 'H', 'high': 'H', 'deep': 'H',
}
SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')


def safe(text: str) -> str:
    return SAFE_RE.sub('_', text.strip())[:80].strip('_') or 'task'


def normalize_profile(raw: str) -> str:
    key = PROFILE_ALIASES.get((raw or 'L').strip().lower())
    if not key:
        raise RuntimeError('unknown profile, use L/M/H or low/medium/high')
    return key


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def list_active_sops(pack: pathlib.Path) -> list[dict]:
    root = pack / 'SOPs' / 'active'
    out: list[dict] = []
    if root.exists():
        for p in sorted(root.rglob('*.md')):
            if p.name.endswith('_CN.md'):
                continue
            out.append({'id': p.stem, 'path': str(p), 'relativePath': str(p.relative_to(pack)).replace('\\', '/')})
    return out


def list_active_known_bug_rules(pack: pathlib.Path) -> list[dict]:
    root = pack / 'KnownBugRules' / 'active'
    out: list[dict] = []
    if root.exists():
        for p in sorted(root.rglob('*.json')):
            try:
                data = read_json(p)
                if isinstance(data, dict) and isinstance(data.get('rules'), list):
                    for i, rule in enumerate(data['rules']):
                        out.append({'id': str(rule.get('bugId') or rule.get('id') or f'{p.stem}:{i}'), 'source': str(p), 'relativePath': str(p.relative_to(pack)).replace('\\', '/')})
                elif isinstance(data, list):
                    for i, rule in enumerate(data):
                        if isinstance(rule, dict):
                            out.append({'id': str(rule.get('bugId') or rule.get('id') or f'{p.stem}:{i}'), 'source': str(p), 'relativePath': str(p.relative_to(pack)).replace('\\', '/')})
                elif isinstance(data, dict):
                    out.append({'id': str(data.get('bugId') or data.get('id') or p.stem), 'source': str(p), 'relativePath': str(p.relative_to(pack)).replace('\\', '/')})
            except Exception as exc:
                out.append({'id': f'INVALID:{p.stem}', 'source': str(p), 'error': str(exc), 'relativePath': str(p.relative_to(pack)).replace('\\', '/')})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description='Start a ProjectGate runtime task and force SOP/KnownBugRules into TaskRun.json.')
    ap.add_argument('--project-pack', required=True)
    ap.add_argument('--task-type', required=True)
    ap.add_argument('--task-title', required=True)
    ap.add_argument('-p', '--profile', default='L')
    ap.add_argument('--run-root', required=True)
    args = ap.parse_args()
    try:
        pack = pathlib.Path(args.project_pack).resolve()
        if not pack.exists():
            raise RuntimeError(f'project pack missing: {pack}')
        manifest_path = pack / 'project_manifest.json'
        if not manifest_path.exists():
            raise RuntimeError(f'project manifest missing: {manifest_path}')
        manifest = read_json(manifest_path)
        profile = normalize_profile(args.profile)
        knowledge_index = build_index(pack)
        selected_knowledge = select_knowledge(knowledge_index, args.task_type, 'TASK_STARTED', profile)
        sops = [x for x in selected_knowledge if x.get('kind') == 'SOP']
        rules = [x for x in selected_knowledge if x.get('kind') == 'KnownBugRule']
        run_root = pathlib.Path(args.run_root).resolve()
        run_id = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + safe(args.task_type)
        run_dir = run_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        taskrun = {
            'schema': 'projectgate_taskrun_runtime_v0_2',
            'createdUtc': datetime.now(timezone.utc).isoformat(),
            'runId': run_id,
            'projectPack': str(pack),
            'projectManifest': manifest,
            'task': {'type': args.task_type, 'title': args.task_title, 'profile': profile},
            'stage': 'TASK_STARTED',
            'loadedSOPs': sops,
            'loadedKnownBugRules': rules,
            'knowledgeSelection': {'mode': 'routed_v0_3', 'selectedCount': len(selected_knowledge), 'indexItemCount': knowledge_index.get('itemCount', 0)},
            'requiredRuntimeGates': [
                'ACTIVE_SOPS_LOADED',
                'ACTIVE_KNOWN_BUG_RULES_LOADED',
                'OUTPUT_MUST_DECLARE_SOP_USED',
                'OUTPUT_MUST_DECLARE_KNOWN_BUG_RULES_CHECKED',
                'STAGE_BOUNDARY_CHECK',
            ],
            'gateHistory': [],
            'ownerDecisions': [],
            'incidents': [],
            'deliverables': [],
        }
        out = run_dir / 'TaskRun.json'
        out.write_text(json.dumps(taskrun, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('RESULT=PASS')
        print('TASKRUN=' + str(out))
        print('RUN_DIR=' + str(run_dir))
        print('PROFILE=' + profile)
        print('LOADED_SOPS=' + str(len(sops)))
        print('LOADED_KNOWN_BUG_RULES=' + str(len(rules)))
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=TASK_START')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
