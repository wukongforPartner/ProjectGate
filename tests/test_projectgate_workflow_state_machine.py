#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
VALIDATOR_PATH = ROOT / 'core' / 'projectgate_core_v0_1' / 'workflow' / 'projectgate_workflow_validator.py'
WORKFLOW_DIR = ROOT / 'core' / 'projectgate_core_v0_1' / 'workflow'


def load_validator():
    spec = importlib.util.spec_from_file_location('projectgate_workflow_validator', VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_tables():
    validator = load_validator()
    return validator.load_tables(ROOT)


def run_validator(root=ROOT, expect=0):
    proc = subprocess.run([PY, str(VALIDATOR_PATH), '--root', str(root)], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    if proc.returncode != expect:
        raise AssertionError(f'expected exit {expect}, got {proc.returncode}\n{proc.stdout}')
    return proc.stdout


class ProjectGateWorkflowStateMachineTests(unittest.TestCase):
    def test_validator_cli_passes_current_tables(self):
        out = run_validator()
        self.assertIn('RESULT=PASS', out)
        self.assertIn('WORKFLOW_TABLES_VALID=PASS', out)

    def test_internal_repair_loop_is_hidden_from_owner(self):
        tables = load_tables()
        states = {s['id']: s for s in tables['workflow_state_table']['states']}
        self.assertIn('INTERNAL_REPAIR_LOOP', states)
        internal = states['INTERNAL_REPAIR_LOOP']
        self.assertFalse(internal['ownerVisible'])
        self.assertNotIn('Owner', internal['allowedRoles'])
        owner_points = tables['owner_interaction_points']
        self.assertIn('INTERNAL_REPAIR_LOOP', owner_points['hiddenInternalStates'])
        self.assertNotIn('INTERNAL_REPAIR_LOOP', owner_points['ownerPromptStates'])

    def test_autofixable_gate_decisions_do_not_route_to_owner(self):
        tables = load_tables()
        decisions = {d['id']: d for d in tables['transition_rules']['gateDecisions']}
        for decision_id in ['INTERNAL_REPAIR', 'NEED_MORE_FACTS_AUTOFIXABLE']:
            decision = decisions[decision_id]
            self.assertEqual(decision['nextState'], 'INTERNAL_REPAIR_LOOP')
            self.assertFalse(decision['ownerVisible'])
            self.assertFalse(decision['ownerRequired'])

    def test_every_transition_target_exists(self):
        tables = load_tables()
        state_ids = {s['id'] for s in tables['workflow_state_table']['states']}
        for state in tables['workflow_state_table']['states']:
            for target in state['transitions']:
                self.assertIn(target, state_ids, f'{state["id"]} -> {target}')
        for decision in tables['transition_rules']['gateDecisions']:
            self.assertIn(decision['nextState'], state_ids)

    def test_non_gate_roles_cannot_emit_gate_decision(self):
        tables = load_tables()
        for role in tables['role_state_table']['roles']:
            if role['id'] == 'Gate':
                self.assertIn('GateDecision', role['outputs'])
            else:
                self.assertNotIn('GateDecision', role['outputs'], role['id'])

    def test_negative_owner_visible_autofixable_route_fails(self):
        tables = load_tables()
        with tempfile.TemporaryDirectory(prefix='pg_workflow_negative_') as td:
            fake = pathlib.Path(td)
            workflow = fake / 'core' / 'projectgate_core_v0_1' / 'workflow'
            workflow.mkdir(parents=True)
            for name, table in [
                ('workflow_state_table.json', tables['workflow_state_table']),
                ('role_state_table.json', tables['role_state_table']),
                ('transition_rules.json', tables['transition_rules']),
                ('owner_interaction_points.json', tables['owner_interaction_points']),
            ]:
                table_copy = copy.deepcopy(table)
                if name == 'transition_rules.json':
                    for decision in table_copy['gateDecisions']:
                        if decision['id'] == 'NEED_MORE_FACTS_AUTOFIXABLE':
                            decision['nextState'] = 'NEED_OWNER_DECISION'
                            decision['ownerVisible'] = True
                            decision['ownerRequired'] = True
                (workflow / name).write_text(json.dumps(table_copy, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            out = run_validator(fake, expect=1)
            self.assertIn('WORKFLOW_TABLES_VALID=FAIL', out)
            self.assertIn('NEED_MORE_FACTS_AUTOFIXABLE must route to INTERNAL_REPAIR_LOOP', out)

    def test_negative_missing_internal_repair_state_fails(self):
        tables = load_tables()
        with tempfile.TemporaryDirectory(prefix='pg_workflow_negative_') as td:
            fake = pathlib.Path(td)
            workflow = fake / 'core' / 'projectgate_core_v0_1' / 'workflow'
            workflow.mkdir(parents=True)
            bad_states = copy.deepcopy(tables['workflow_state_table'])
            bad_states['states'] = [s for s in bad_states['states'] if s['id'] != 'INTERNAL_REPAIR_LOOP']
            for name, table in [
                ('workflow_state_table.json', bad_states),
                ('role_state_table.json', tables['role_state_table']),
                ('transition_rules.json', tables['transition_rules']),
                ('owner_interaction_points.json', tables['owner_interaction_points']),
            ]:
                (workflow / name).write_text(json.dumps(table, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            out = run_validator(fake, expect=1)
            self.assertIn('WORKFLOW_TABLES_VALID=FAIL', out)
            self.assertIn('missing INTERNAL_REPAIR_LOOP state', out)


if __name__ == '__main__':
    unittest.main()
