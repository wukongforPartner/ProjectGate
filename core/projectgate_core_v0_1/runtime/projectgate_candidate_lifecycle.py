#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re, shutil
from datetime import datetime, timezone

SAFE_RE = re.compile(r'[^A-Za-z0-9_.-]+')

def utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def safe(text: str, limit: int = 96) -> str:
    return SAFE_RE.sub('_', str(text).strip())[:limit].strip('_') or 'candidate'

def read_text(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8')

def read_json(path: pathlib.Path):
    return json.loads(read_text(path))

def write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def candidate_roots(pack: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    return [
        ('sop', pack / 'SOPs' / 'candidates'),
        ('knownbug', pack / 'KnownBugRules' / 'candidates'),
    ]

def rejected_root(pack: pathlib.Path, kind: str) -> pathlib.Path:
    return pack / ('SOPs' if kind == 'sop' else 'KnownBugRules') / 'rejected'

def merged_root(pack: pathlib.Path, kind: str) -> pathlib.Path:
    return pack / ('SOPs' if kind == 'sop' else 'KnownBugRules') / 'merged'

def active_root(pack: pathlib.Path, kind: str) -> pathlib.Path:
    return pack / ('SOPs' if kind == 'sop' else 'KnownBugRules') / 'active'

def review_root(pack: pathlib.Path) -> pathlib.Path:
    return pack / 'Reviews'

def knownbug_ids(path: pathlib.Path) -> list[str]:
    try:
        data = read_json(path)
    except Exception:
        return [path.stem]
    rules = []
    if isinstance(data, dict) and isinstance(data.get('rules'), list):
        rules = data['rules']
    elif isinstance(data, list):
        rules = data
    elif isinstance(data, dict):
        rules = [data]
    ids = []
    for i, rule in enumerate(rules):
        if isinstance(rule, dict):
            ids.append(str(rule.get('bugId') or rule.get('id') or f'{path.stem}:{i}'))
    return ids or [path.stem]

def sop_id(path: pathlib.Path) -> str:
    return path.stem

def iter_candidates(pack: pathlib.Path) -> list[dict]:
    out: list[dict] = []
    for kind, root in candidate_roots(pack):
        if not root.exists():
            continue
        patterns = ['*.md'] if kind == 'sop' else ['*.json']
        for pattern in patterns:
            for p in sorted(root.rglob(pattern)):
                ids = [sop_id(p)] if kind == 'sop' else knownbug_ids(p)
                out.append({
                    'kind': kind,
                    'ids': ids,
                    'primaryId': ids[0],
                    'path': p,
                    'relativePath': str(p.relative_to(pack)).replace('\\','/'),
                })
    return out

def find_candidate(pack: pathlib.Path, ident: str, kind: str | None = None) -> dict:
    ident_norm = str(ident).strip().lower()
    path_try = pathlib.Path(ident)
    if path_try.exists():
        p = path_try.resolve()
        if kind is None:
            kind = 'sop' if p.suffix.lower() == '.md' else 'knownbug'
        ids = [sop_id(p)] if kind == 'sop' else knownbug_ids(p)
        return {'kind': kind, 'ids': ids, 'primaryId': ids[0], 'path': p, 'relativePath': str(p)}
    matches = []
    for cand in iter_candidates(pack):
        if kind and cand['kind'] != kind:
            continue
        names = [cand['path'].name.lower(), cand['path'].stem.lower()] + [x.lower() for x in cand['ids']]
        if ident_norm in names:
            matches.append(cand)
    if not matches:
        raise RuntimeError('candidate not found: ' + ident)
    if len(matches) > 1:
        raise RuntimeError('candidate id is ambiguous: ' + ident + ' -> ' + ', '.join(m['relativePath'] for m in matches))
    return matches[0]

def review_file(pack: pathlib.Path, action: str, cand: dict) -> pathlib.Path:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return review_root(pack) / f"{safe(action)}_{safe(cand['primaryId'])}_{ts}.json"

def copy_or_move_candidate(pack: pathlib.Path, cand: dict, dest_root: pathlib.Path, action: str, move: bool) -> pathlib.Path:
    dest_root.mkdir(parents=True, exist_ok=True)
    src = cand['path']
    dest = dest_root / src.name
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        dest = dest_root / f"{stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
    if move:
        shutil.move(str(src), str(dest))
    else:
        shutil.copy2(src, dest)
    return dest

def cmd_list(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    candidates = iter_candidates(pack)
    print('RESULT=PASS')
    print('CANDIDATE_COUNT=' + str(len(candidates)))
    for c in candidates:
        print(f"CANDIDATE kind={c['kind']} id={c['primaryId']} path={c['relativePath']}")
    return 0

def cmd_show(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    cand = find_candidate(pack, args.id, args.kind)
    print('RESULT=PASS')
    print('CANDIDATE_KIND=' + cand['kind'])
    print('CANDIDATE_ID=' + cand['primaryId'])
    print('CANDIDATE_PATH=' + str(cand['path']))
    print('CONTENT_BEGIN')
    print(read_text(cand['path']).rstrip())
    print('CONTENT_END')
    return 0

def cmd_approve(args) -> int:
    if not args.owner_approved:
        raise RuntimeError('owner approval required: pass --owner-approved')
    pack = pathlib.Path(args.project_pack).resolve()
    cand = find_candidate(pack, args.id, args.kind)
    active = copy_or_move_candidate(pack, cand, active_root(pack, cand['kind']), 'approve', move=False)
    review = {
        'schema': 'projectgate_candidate_review_v0_4',
        'createdUtc': utc(),
        'action': 'approve',
        'kind': cand['kind'],
        'candidateId': cand['primaryId'],
        'source': str(cand['path']),
        'activePath': str(active),
        'ownerApproved': True,
        'reason': args.reason or '',
    }
    rf = review_file(pack, 'approve', cand)
    write_json(rf, review)
    print('RESULT=PASS')
    print('CANDIDATE_APPROVED=PASS')
    print('ACTIVE_PATH=' + str(active))
    print('REVIEW_FILE=' + str(rf))
    return 0

def cmd_reject(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    cand = find_candidate(pack, args.id, args.kind)
    rejected = copy_or_move_candidate(pack, cand, rejected_root(pack, cand['kind']), 'reject', move=True)
    review = {
        'schema': 'projectgate_candidate_review_v0_4',
        'createdUtc': utc(),
        'action': 'reject',
        'kind': cand['kind'],
        'candidateId': cand['primaryId'],
        'source': str(cand['path']),
        'rejectedPath': str(rejected),
        'reason': args.reason or '',
    }
    rf = review_file(pack, 'reject', cand)
    write_json(rf, review)
    print('RESULT=PASS')
    print('CANDIDATE_REJECTED=PASS')
    print('REJECTED_PATH=' + str(rejected))
    print('REVIEW_FILE=' + str(rf))
    return 0

def cmd_merge(args) -> int:
    pack = pathlib.Path(args.project_pack).resolve()
    src = find_candidate(pack, args.source, args.kind)
    dst = find_candidate(pack, args.target, src['kind'])
    merged = copy_or_move_candidate(pack, src, merged_root(pack, src['kind']), 'merge', move=True)
    review = {
        'schema': 'projectgate_candidate_review_v0_4',
        'createdUtc': utc(),
        'action': 'merge',
        'kind': src['kind'],
        'sourceCandidateId': src['primaryId'],
        'targetCandidateId': dst['primaryId'],
        'sourcePath': str(src['path']),
        'targetPath': str(dst['path']),
        'mergedSourcePath': str(merged),
        'reason': args.reason or '',
    }
    rf = review_file(pack, 'merge', src)
    write_json(rf, review)
    print('RESULT=PASS')
    print('CANDIDATE_MERGED=PASS')
    print('MERGED_SOURCE_PATH=' + str(merged))
    print('TARGET_CANDIDATE_PATH=' + str(dst['path']))
    print('REVIEW_FILE=' + str(rf))
    return 0

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description='Review ProjectGate SOP / KnownBugRule candidates.')
    ap.add_argument('--project-pack', required=True)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('list')
    show = sub.add_parser('show'); show.add_argument('id'); show.add_argument('--kind', choices=['sop','knownbug'])
    approve = sub.add_parser('approve'); approve.add_argument('id'); approve.add_argument('--kind', choices=['sop','knownbug']); approve.add_argument('--owner-approved', action='store_true'); approve.add_argument('--reason', default='')
    reject = sub.add_parser('reject'); reject.add_argument('id'); reject.add_argument('--kind', choices=['sop','knownbug']); reject.add_argument('--reason', default='')
    merge = sub.add_parser('merge'); merge.add_argument('source'); merge.add_argument('--into', dest='target', required=True); merge.add_argument('--kind', choices=['sop','knownbug']); merge.add_argument('--reason', default='')
    return ap

def main() -> int:
    try:
        args = build_parser().parse_args()
        if args.cmd == 'list': return cmd_list(args)
        if args.cmd == 'show': return cmd_show(args)
        if args.cmd == 'approve': return cmd_approve(args)
        if args.cmd == 'reject': return cmd_reject(args)
        if args.cmd == 'merge': return cmd_merge(args)
        raise RuntimeError('unknown command')
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=CANDIDATE_LIFECYCLE')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
