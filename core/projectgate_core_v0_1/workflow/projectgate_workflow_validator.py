#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FILES = {
    'workflow_state_table': 'core/projectgate_core_v0_1/workflow/workflow_state_table.json',
    'role_state_table': 'core/projectgate_core_v0_1/workflow/role_state_table.json',
    'transition_rules': 'core/projectgate_core_v0_1/workflow/transition_rules.json',
    'owner_interaction_points': 'core/projectgate_core_v0_1/workflow/owner_interaction_points.json',
}

OWNER_STATES = {'IDLE', 'NEED_CLARIFICATION', 'NEED_USER_INPUT', 'NEED_OWNER_DECISION', 'STOP'}
INTERNAL_REPAIR_DECISIONS = {'INTERNAL_REPAIR', 'NEED_MORE_FACTS_AUTOFIXABLE'}
OWNER_DECISIONS = {'NEED_USER_INPUT', 'NEED_OWNER_DECISION'}


class ValidationError(Exception):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except Exception as exc:
        raise ValidationError(f'JSON load failed: {path}: {exc}')


def load_tables(root: Path) -> dict:
    tables = {}
    for key, rel in REQUIRED_FILES.items():
        path = root / rel
        if not path.exists():
            raise ValidationError(f'missing required workflow file: {rel}')
        tables[key] = load_json(path)
    return tables


def require_unique(items: list[dict], field: str, label: str) -> set[str]:
    seen: set[str] = set()
    for item in items:
        value = item.get(field)
        if not isinstance(value, str) or not value:
            raise ValidationError(f'{label} has missing {field}: {item}')
        if value in seen:
            raise ValidationError(f'duplicate {label} {field}: {value}')
        seen.add(value)
    return seen


def validate_workflow_tables(tables: dict) -> list[str]:
    errors: list[str] = []
    try:
        states = tables['workflow_state_table'].get('states', [])
        roles = tables['role_state_table'].get('roles', [])
        transition_rules = tables['transition_rules']
        owner_points = tables['owner_interaction_points']

        if not isinstance(states, list) or not states:
            raise ValidationError('workflow_state_table.states must be a non-empty list')
        if not isinstance(roles, list) or not roles:
            raise ValidationError('role_state_table.roles must be a non-empty list')

        state_ids = require_unique(states, 'id', 'state')
        role_ids = require_unique(roles, 'id', 'role')

        if 'INTERNAL_REPAIR_LOOP' not in state_ids:
            raise ValidationError('missing INTERNAL_REPAIR_LOOP state')
        internal_state = next(s for s in states if s['id'] == 'INTERNAL_REPAIR_LOOP')
        if internal_state.get('ownerVisible') is not False:
            raise ValidationError('INTERNAL_REPAIR_LOOP must be ownerVisible=false')
        if 'Owner' in internal_state.get('allowedRoles', []):
            raise ValidationError('Owner must not be an allowed role for INTERNAL_REPAIR_LOOP')

        for state in states:
            sid = state['id']
            if 'allowedRoles' not in state or not isinstance(state['allowedRoles'], list):
                raise ValidationError(f'state {sid} missing allowedRoles list')
            if 'transitions' not in state or not isinstance(state['transitions'], list):
                raise ValidationError(f'state {sid} missing transitions list')
            for role in state['allowedRoles']:
                if role not in role_ids:
                    raise ValidationError(f'state {sid} references unknown role {role}')
            for target in state['transitions']:
                if target not in state_ids:
                    raise ValidationError(f'state {sid} transition target missing: {target}')

        owner_role = next((r for r in roles if r['id'] == 'Owner'), None)
        if not owner_role:
            raise ValidationError('Owner role missing')
        owner_allowed = set(owner_role.get('allowedStates', []))
        if 'INTERNAL_REPAIR_LOOP' in owner_allowed:
            raise ValidationError('Owner role must not be allowed in INTERNAL_REPAIR_LOOP')
        missing_owner_states = OWNER_STATES - owner_allowed
        if missing_owner_states:
            raise ValidationError('Owner role missing required states: ' + ', '.join(sorted(missing_owner_states)))

        gate_role = next((r for r in roles if r['id'] == 'Gate'), None)
        if not gate_role:
            raise ValidationError('Gate role missing')
        if 'GateDecision' not in gate_role.get('outputs', []):
            raise ValidationError('Gate role must output GateDecision')
        for role in roles:
            if role['id'] != 'Gate' and 'GateDecision' in role.get('outputs', []):
                raise ValidationError(f'non-Gate role outputs GateDecision: {role["id"]}')

        decisions = transition_rules.get('gateDecisions', [])
        if not isinstance(decisions, list) or not decisions:
            raise ValidationError('transition_rules.gateDecisions must be a non-empty list')
        decision_ids = require_unique(decisions, 'id', 'gateDecision')
        required_decisions = {'PASS', 'INTERNAL_REPAIR', 'NEED_MORE_FACTS_AUTOFIXABLE', 'NEED_USER_INPUT', 'NEED_OWNER_DECISION', 'UNRECOVERABLE_STOP'}
        missing_decisions = required_decisions - decision_ids
        if missing_decisions:
            raise ValidationError('missing gate decisions: ' + ', '.join(sorted(missing_decisions)))
        for decision in decisions:
            did = decision['id']
            nxt = decision.get('nextState')
            if nxt not in state_ids:
                raise ValidationError(f'gate decision {did} routes to unknown state: {nxt}')
            if did in INTERNAL_REPAIR_DECISIONS:
                if nxt != 'INTERNAL_REPAIR_LOOP':
                    raise ValidationError(f'{did} must route to INTERNAL_REPAIR_LOOP')
                if decision.get('ownerVisible') is not False or decision.get('ownerRequired') is not False:
                    raise ValidationError(f'{did} must not be owner-visible or owner-required')
            if did in OWNER_DECISIONS:
                if decision.get('ownerVisible') is not True or decision.get('ownerRequired') is not True:
                    raise ValidationError(f'{did} must be owner-visible and owner-required')

        hidden_internal = set(owner_points.get('hiddenInternalStates', []))
        if 'INTERNAL_REPAIR_LOOP' not in hidden_internal:
            raise ValidationError('owner_interaction_points.hiddenInternalStates must include INTERNAL_REPAIR_LOOP')
        owner_prompt_states = set(owner_points.get('ownerPromptStates', []))
        illegal_prompt_states = owner_prompt_states - OWNER_STATES
        if illegal_prompt_states:
            raise ValidationError('ownerPromptStates includes illegal states: ' + ', '.join(sorted(illegal_prompt_states)))
        for rule_id in ['UI-OWNER-001', 'UI-OWNER-002', 'UI-OWNER-003', 'UI-OWNER-004', 'UI-OWNER-005']:
            if not any(rule.get('id') == rule_id for rule in owner_points.get('rules', [])):
                raise ValidationError(f'missing owner interaction rule {rule_id}')
    except ValidationError as exc:
        errors.append(str(exc))
    return errors


def validate_root(root: Path) -> list[str]:
    try:
        tables = load_tables(root)
    except ValidationError as exc:
        return [str(exc)]
    return validate_workflow_tables(tables)


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate ProjectGate workflow state machine static tables.')
    parser.add_argument('--root', default='.')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate_root(root)
    if errors:
        print('RESULT=FAIL')
        print('WORKFLOW_TABLES_VALID=FAIL')
        for err in errors:
            print('ERROR=' + err)
        return 1
    print('RESULT=PASS')
    print('WORKFLOW_TABLES_VALID=PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
