from __future__ import annotations
import json, pathlib, re, hashlib
from datetime import datetime, timezone

MOJIBAKE_RE = re.compile(r'(銆|宸|绛|Ã|â|�)')
GET_CONTENT_NO_UTF8_RE = re.compile(r'Get-Content(?![^\n\r]*-Encoding\s+UTF8)', re.I)
ACCESS_DENIED_RE = re.compile(r'(WinError\s*5|Access\s+denied|拒绝访问)', re.I)
REPAIR_RESULT_FILE_RE = re.compile(r'ProjectGate_.*_repair_result\.json', re.I)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe(text: str, limit: int = 96) -> str:
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', text.strip())[:limit].strip('_') or 'item'


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def save_taskrun(taskrun_path: pathlib.Path, taskrun: dict) -> None:
    save_json(taskrun_path, taskrun)


def task_type_from(taskrun: dict) -> str:
    return str((taskrun.get('task') or {}).get('type') or 'unknown_task')


def project_pack_from(taskrun: dict) -> pathlib.Path:
    pack = taskrun.get('projectPack')
    if not pack:
        raise RuntimeError('TaskRun missing projectPack')
    return pathlib.Path(pack).resolve()


def active_and_candidate_rules(pack: pathlib.Path) -> list[dict]:
    out = []
    for state in ['active', 'candidates']:
        root = pack / 'KnownBugRules' / state
        if not root.exists():
            continue
        for p in sorted(root.rglob('*.json')):
            try:
                data = load_json(p)
            except Exception:
                continue
            rules = []
            if isinstance(data, dict) and isinstance(data.get('rules'), list):
                rules = data['rules']
            elif isinstance(data, list):
                rules = data
            elif isinstance(data, dict):
                rules = [data]
            for rule in rules:
                if not isinstance(rule, dict):
                    continue
                out.append({
                    'state': state,
                    'path': str(p),
                    'bugId': str(rule.get('bugId') or rule.get('id') or p.stem),
                    'title': str(rule.get('title') or ''),
                    'trigger': [str(x).lower() for x in rule.get('trigger', []) if isinstance(x, str)],
                    'symptom': str(rule.get('symptom') or ''),
                })
    return out


def classify_existing_rule(taskrun: dict, rule_id: str, triggers: list[str], symptom: str) -> dict:
    pack = project_pack_from(taskrun)
    existing = active_and_candidate_rules(pack)
    loaded_ids = {str(x.get('id') or x.get('bugId')) for x in taskrun.get('loadedKnownBugRules', [])}
    trig = {x.lower() for x in triggers}
    exact = [r for r in existing if r['bugId'] == rule_id]
    overlap = [r for r in existing if trig and (trig & set(r.get('trigger', [])))]
    if exact:
        r = exact[0]
        if r['state'] == 'active' and r['bugId'] not in loaded_ids:
            reason = 'ACTIVE_RULE_NOT_SELECTED'
            meaning = 'A matching active rule exists but was not selected into this TaskRun. Router/scope is wrong or task classification is too narrow.'
        elif r['state'] == 'active' and r['bugId'] in loaded_ids:
            reason = 'ACTIVE_RULE_SELECTED_BUT_NOT_ENFORCED'
            meaning = 'A matching active rule was selected, but the workflow still hit the error. The machine check is missing, too weak, or not wired to the relevant observation.'
        else:
            reason = 'DUPLICATE_CANDIDATE_EXISTS'
            meaning = 'A candidate already exists. Do not generate another identical rule; link this incident to the existing candidate.'
        return {'matchType': 'exact', 'rule': r, 'analysis': reason, 'meaning': meaning}
    if overlap:
        r = overlap[0]
        if r['state'] == 'active' and r['bugId'] in loaded_ids:
            reason = 'RULE_TOO_COARSE_OR_NOT_FINE_GRAINED'
            meaning = 'A related active rule was selected, but it was too coarse to catch this exact variant. Split or refine the rule.'
        elif r['state'] == 'active':
            reason = 'RELATED_ACTIVE_RULE_NOT_SELECTED'
            meaning = 'A related active rule exists but was not selected. Improve router triggers or task type mapping.'
        else:
            reason = 'RELATED_CANDIDATE_EXISTS'
            meaning = 'A related candidate exists. Consider merging rather than creating many near-duplicates.'
        return {'matchType': 'trigger_overlap', 'rule': r, 'analysis': reason, 'meaning': meaning}
    return {'matchType': 'none', 'analysis': 'NEW_RULE_CANDIDATE_NEEDED', 'meaning': 'No similar active or candidate rule was found. Generate a new KnownBugRule candidate.'}


def append_taskrun_list(taskrun: dict, key: str, value: dict) -> None:
    taskrun.setdefault(key, []).append(value)


def create_incident_and_candidate(taskrun_path: pathlib.Path, incident_id: str, title: str, symptom: str, rule_id: str, triggers: list[str], on_fail: str = 'REPAIR_AND_RECHECK') -> dict:
    taskrun = load_json(taskrun_path)
    pack = project_pack_from(taskrun)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    analysis = classify_existing_rule(taskrun, rule_id, triggers, symptom)
    inc_dir = pack / 'Incidents' / 'active_run'
    rule_dir = pack / 'KnownBugRules' / 'candidates'
    inc_path = inc_dir / f'{safe(incident_id)}_{ts}.json'
    incident = {
        'schema': 'projectgate_incident_v0_3_1',
        'incidentId': incident_id,
        'title': title,
        'createdUtc': utc(),
        'symptom': symptom,
        'taskrun': str(taskrun_path),
        'triggers': triggers,
        'existingRuleAnalysis': analysis,
        'status': 'auto_captured',
    }
    save_json(inc_path, incident)
    candidate_path = None
    if analysis.get('analysis') not in {'DUPLICATE_CANDIDATE_EXISTS'}:
        candidate_path = rule_dir / f'{safe(rule_id)}_{ts}.json'
        candidate = {
            'schema': 'projectgate_known_bug_rule_candidate_v0_3_1',
            'rules': [{
                'bugId': rule_id,
                'title': title,
                'trigger': triggers,
                'severity': 'candidate',
                'symptom': symptom,
                'onFail': on_fail,
                'ownerApproved': False,
                'sourceIncident': str(inc_path),
                'existingRuleAnalysis': analysis,
            }]
        }
        save_json(candidate_path, candidate)
    record = {
        'incident': str(inc_path),
        'candidate': str(candidate_path) if candidate_path else '',
        'ruleId': rule_id,
        'existingRuleAnalysis': analysis,
        'createdUtc': utc(),
    }
    append_taskrun_list(taskrun, 'autoCapturedIncidents', record)
    if candidate_path:
        append_taskrun_list(taskrun, 'autoGeneratedKnownBugRuleCandidates', record)
    save_taskrun(taskrun_path, taskrun)
    return record


def create_sop_candidate_if_needed(taskrun_path: pathlib.Path, title: str | None = None) -> dict:
    taskrun = load_json(taskrun_path)
    gates = taskrun.get('gateHistory') or []
    if not any(g.get('result') == 'PASS' for g in gates):
        return {'created': False, 'reason': 'NO_PASSING_GATE'}
    pack = project_pack_from(taskrun)
    task_type = task_type_from(taskrun)
    outdir = pack / 'SOPs' / 'candidates'
    outdir.mkdir(parents=True, exist_ok=True)
    existing = list(outdir.glob(f'{safe(task_type)}_*.md'))
    if existing:
        rec = {'created': False, 'reason': 'SOP_CANDIDATE_ALREADY_EXISTS', 'path': str(existing[0])}
        taskrun.setdefault('autoGeneratedSOPCandidates', []).append(rec)
        save_taskrun(taskrun_path, taskrun)
        return rec
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = outdir / f'{safe(task_type)}_{ts}.md'
    used = ', '.join(str(x.get('id','')) for x in taskrun.get('loadedSOPs', [])) or 'none'
    rules = ', '.join(str(x.get('id','')) for x in taskrun.get('loadedKnownBugRules', [])) or 'none'
    gate_lines = '\n'.join(f"- {g.get('stage')}: {g.get('result')} -> {g.get('nextAction')}" for g in gates)
    text = f'''# {title or ('SOP candidate for ' + task_type)}\n\nStatus: SOP_CANDIDATE\n\nCreated UTC: {utc()}\n\nSource TaskRun: `{taskrun_path}`\n\n## Task\n\n- taskType: `{task_type}`\n- profile: `{(taskrun.get('task') or {}).get('profile','unknown')}`\n\n## Preconditions\n\n- ProjectGate Runtime must create TaskRun.json.\n- Knowledge Router must select active SOPs / KnownBugRules.\n- Stage outputs must declare `SOP_USED=` and `KNOWN_BUG_RULES_CHECKED=`.\n\n## Observed successful flow\n\n1. Start task with ProjectGate Runtime.\n2. Produce stage output in the configured run directory.\n3. Run stage gate.\n4. Run delivery check before final report.\n5. Confirm project working tree is clean when task is read-only.\n\n## Loaded SOPs\n\n{used}\n\n## Checked KnownBugRules\n\n{rules}\n\n## Gate history\n\n{gate_lines}\n\n## Promotion rule\n\nThis file is only a candidate. It must not become active unless the owner confirms that this flow is stable, reusable, and not merely an accidental success.\n'''
    out.write_text(text, encoding='utf-8', newline='\n')
    rec = {'created': True, 'path': str(out), 'createdUtc': utc()}
    taskrun.setdefault('autoGeneratedSOPCandidates', []).append(rec)
    save_taskrun(taskrun_path, taskrun)
    return rec


def detect_observation_issues(text: str) -> list[dict]:
    issues = []
    if MOJIBAKE_RE.search(text):
        issues.append({'ruleId': 'PG-WINDOWS-POWERSHELL-UTF8-READ-001', 'title': 'Windows PowerShell output contains mojibake', 'trigger': ['windows_utf8','powershell','markdown'], 'symptom': 'Observation text contains mojibake markers such as 銆 / 宸 / 绛 / Ã / â / �.', 'severity': 'fail'})
    if GET_CONTENT_NO_UTF8_RE.search(text):
        issues.append({'ruleId': 'PG-WINDOWS-POWERSHELL-GETCONTENT-UTF8-001', 'title': 'PowerShell Get-Content should specify UTF-8 for ProjectGate docs', 'trigger': ['windows_utf8','powershell','get_content'], 'symptom': 'Observation includes Get-Content without explicit -Encoding UTF8.', 'severity': 'candidate'})
    if ACCESS_DENIED_RE.search(text):
        issues.append({'ruleId': 'PG-RUNROOT-WRITABLE-PREFLIGHT-001', 'title': 'Run root must be writable before task_start', 'trigger': ['runroot','permission','windows'], 'symptom': 'Observation includes access denied / WinError 5 while writing run artifacts.', 'severity': 'fail'})
    if REPAIR_RESULT_FILE_RE.search(text):
        issues.append({'ruleId': 'PG-RELEASE-LOCAL-RESULT-FILE-NO-COMMIT-001', 'title': 'Local repair result JSON must not enter release tree', 'trigger': ['release','git','repair_result'], 'symptom': 'Observation references ProjectGate repair result JSON in git/release output.', 'severity': 'fail'})
    return issues
