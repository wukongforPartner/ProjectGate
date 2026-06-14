#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re
from datetime import datetime, timezone

MUTATING_PATTERNS = [
    r'\bgit\s+add\b', r'\bgit\s+commit\b', r'\bgit\s+push\b', r'\bgit\s+checkout\b',
    r'\bgit\s+reset\b', r'\bgit\s+clean\b', r'\bgit\s+restore\b', r'\bgit\s+merge\b', r'\bgit\s+rebase\b',
    r'\bapply_patch\b', r'\bsystemctl\s+(restart|start|stop|reload)\b',
    r'\bservice\s+\S+\s+(restart|start|stop|reload)\b', r'\bsteamcmd\b',
]
READONLY_REQUIRED = ['已确认事实', '不能确认事实', '风险点', '必须停手条件', '唯一安全下一步']


def load_taskrun(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save_taskrun(path: pathlib.Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def append_gate(taskrun: dict, stage: str, result: str, reasons: list[str], next_action: str, output_file: str) -> None:
    taskrun.setdefault('gateHistory', []).append({
        'checkedUtc': datetime.now(timezone.utc).isoformat(),
        'stage': stage,
        'result': result,
        'reasons': reasons,
        'nextAction': next_action,
        'outputFile': output_file,
    })
    taskrun['stage'] = stage if result == 'PASS' else f'{stage}_REPAIR_REQUIRED'


def main() -> int:
    ap = argparse.ArgumentParser(description='Gate a ProjectGate stage output. Failing outputs return REPAIR_AND_RECHECK, not silent stop.')
    ap.add_argument('--taskrun', required=True)
    ap.add_argument('--stage', default='READONLY_AUDIT')
    ap.add_argument('--input', required=True)
    args = ap.parse_args()
    taskrun_path = pathlib.Path(args.taskrun).resolve()
    output_path = pathlib.Path(args.input).resolve()
    try:
        taskrun = load_taskrun(taskrun_path)
        text = output_path.read_text(encoding='utf-8', errors='replace')
        reasons: list[str] = []
        if taskrun.get('loadedSOPs'):
            if not re.search(r'\bSOP_USED\s*[:=]', text):
                reasons.append('missing SOP_USED declaration; active SOPs were loaded but output did not declare which SOPs were used')
        if taskrun.get('loadedKnownBugRules'):
            if not re.search(r'\bKNOWN_BUG_RULES_CHECKED\s*[:=]', text):
                reasons.append('missing KNOWN_BUG_RULES_CHECKED declaration; active known bug rules were loaded but output did not declare checks')
        if args.stage.upper() == 'READONLY_AUDIT':
            for required in READONLY_REQUIRED:
                if required not in text:
                    reasons.append(f'missing READONLY_AUDIT section: {required}')
        for pat in MUTATING_PATTERNS:
            if re.search(pat, text, flags=re.I):
                reasons.append(f'forbidden mutating/destructive action pattern in output: {pat}')
        if reasons:
            append_gate(taskrun, args.stage, 'FAIL', reasons, 'REPAIR_AND_RECHECK', str(output_path))
            save_taskrun(taskrun_path, taskrun)
            print('RESULT=FAIL')
            print('FAILED_STAGE=STAGE_GATE')
            print('NEXT_ACTION=REPAIR_AND_RECHECK')
            print('FAIL_REASON=' + ' | '.join(reasons))
            return 1
        append_gate(taskrun, args.stage, 'PASS', [], 'CONTINUE', str(output_path))
        save_taskrun(taskrun_path, taskrun)
        print('RESULT=PASS')
        print('STAGE_GATE=PASS')
        print('NEXT_ACTION=CONTINUE')
        return 0
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=STAGE_GATE_EXCEPTION')
        print('NEXT_ACTION=REPAIR_AND_RECHECK')
        print('FAIL_REASON=' + str(exc))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
