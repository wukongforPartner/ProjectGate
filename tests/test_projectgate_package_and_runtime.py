from __future__ import annotations
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def run(cmd, cwd=None, expect=0):
    proc = subprocess.run([str(x) for x in cmd], cwd=cwd or ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    if proc.returncode != expect:
        raise AssertionError(f'command failed: {cmd}\nexit={proc.returncode}\n{proc.stdout}')
    return proc.stdout


class ProjectGatePackageAndRuntimeTests(unittest.TestCase):
    def test_pg_entrypoint_pack_info(self):
        out = run([PY, ROOT / 'pg.py', 'pack', 'info', '--project-pack', ROOT / 'examples' / 'dreamstory_project_pack_v0_1'])
        self.assertIn('RESULT=PASS', out)
        self.assertIn('PROJECT_PACK_VALID=PASS', out)

    def test_package_entrypoint_locates_runtime(self):
        out = run([PY, '-m', 'projectgate.cli', 'pack', 'validate', '--project-pack', ROOT / 'examples' / 'dreamstory_project_pack_v0_1'])
        self.assertIn('PROJECT_PACK_VALID=PASS', out)

    def test_installer_refuses_unmarked_directory(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_safety_') as td:
            ws = pathlib.Path(td) / 'Workspace'
            target = ws / 'Core' / 'projectgate_core_v0_1'
            target.mkdir(parents=True)
            sentinel = target / 'user_file.txt'
            sentinel.write_text('keep\n', encoding='utf-8')
            out = run([PY, ROOT / 'install_projectgate_alpha.py', '--install', '--workspace-root', ws], expect=1)
            self.assertIn('refusing to overwrite unmarked non-ProjectGate directory', out)
            self.assertTrue(sentinel.exists())

    def test_installer_managed_backup_on_second_install(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_managed_') as td:
            ws = pathlib.Path(td) / 'Workspace'
            out1 = run([PY, ROOT / 'install_projectgate_alpha.py', '--install', '--workspace-root', ws])
            self.assertIn('PROJECTGATE_ALPHA=PASS', out1)
            self.assertTrue((ws / 'Core' / 'projectgate_core_v0_1' / '.projectgate-managed.json').exists())
            out2 = run([PY, ROOT / 'install_projectgate_alpha.py', '--install', '--workspace-root', ws])
            self.assertIn('BACKUP_DIR=', out2)
            self.assertIn('PROJECTGATE_ALPHA=PASS', out2)

    def test_candidate_lifecycle_knownbug(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_candidates_') as td:
            pack = pathlib.Path(td) / 'pack'
            shutil.copytree(ROOT / 'examples' / 'dreamstory_project_pack_v0_1', pack)
            cand = pack / 'KnownBugRules' / 'candidates'
            cand.mkdir(parents=True, exist_ok=True)
            (cand / 'PG-TEST-001.json').write_text(json.dumps({'rules':[{'bugId':'PG-TEST-001','title':'t','trigger':['t']}]}), encoding='utf-8')
            cli = ROOT / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py'
            out = run([PY, cli, 'candidates', '--project-pack', pack, 'list'])
            self.assertIn('PG-TEST-001', out)
            out = run([PY, cli, 'candidates', '--project-pack', pack, 'approve', 'PG-TEST-001', '--owner-approved', '--reason', 'test'])
            self.assertIn('CANDIDATE_APPROVED=PASS', out)
            self.assertTrue((pack / 'KnownBugRules' / 'active' / 'PG-TEST-001.json').exists())

    def test_runtime_start_stage_continuity(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_runtime_') as td:
            run_root = pathlib.Path(td) / 'runs'
            pack = pathlib.Path(td) / 'pack'
            shutil.copytree(ROOT / 'examples' / 'dreamstory_project_pack_v0_1', pack)
            cli = ROOT / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py'
            out = run([PY, cli, 'start', '--project-pack', pack, '--task-type', 'dreamstory_runtime_fact_entry_map', '--task-title', 'unit test', '-p', 'L', '--run-root', run_root])
            self.assertIn('RESULT=PASS', out)
            task_line = [line for line in out.splitlines() if line.startswith('TASKRUN=')][0]
            taskrun = pathlib.Path(task_line.split('=', 1)[1])
            report = taskrun.parent / 'READONLY_AUDIT.md'
            report.write_text('# unit\n\nSOP_USED=runtime_fact_entry_map\nKNOWN_BUG_RULES_CHECKED=DREAMSTORY-RUNTIME-FACT-SINGLE-ENTRY-001\n\n## 已确认事实\n- ok\n\n## 不能确认事实\n- ok\n\n## 风险点\n- ok\n\n## 必须停手条件\n- ok\n\n## 唯一安全下一步\n- ok\n', encoding='utf-8')
            out = run([PY, cli, 'stage', '--taskrun', taskrun, '--stage', 'READONLY_AUDIT', '--input', report])
            self.assertIn('STAGE_GATE=PASS', out)
            transcript = taskrun.parent / 'TRANSCRIPT.txt'
            transcript.write_text('TASKRUN=' + str(taskrun) + '\n', encoding='utf-8')
            out = run([PY, cli, 'continuity', '--taskrun', taskrun, '--input', transcript])
            self.assertIn('TASKRUN_CONTINUITY_GATE=PASS', out)




    def test_codex_adapter_builds_skill_with_workflow_payload(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_codex_') as td:
            out_dir = pathlib.Path(td) / 'codex'
            adapter = ROOT / 'adapters' / 'projectgate_codex_adapter_v0_1' / 'projectgate_codex_adapter.py'
            out = run([
                PY,
                adapter,
                'build',
                '--core-root', ROOT / 'core' / 'projectgate_core_v0_1',
                '--project-pack', ROOT / 'examples' / 'dreamstory_project_pack_v0_1',
                '--out', out_dir,
            ])
            self.assertIn('CODEX_PACK=', out)
            skill_root = out_dir / 'projectgate'
            self.assertTrue((skill_root / 'SKILL.md').exists())
            self.assertTrue((skill_root / 'scripts' / 'workflow' / 'workflow_state_table.json').exists())
            self.assertTrue((skill_root / 'scripts' / 'workflow' / 'projectgate_workflow_validator.py').exists())
            self.assertTrue((skill_root / 'references' / 'workflow' / 'WORKFLOW_STATE_MACHINE.md').exists())
            selftest = skill_root / 'scripts' / 'projectgate_skill_selftest.py'
            selftest_out = run([PY, selftest], cwd=skill_root)
            self.assertIn('PROJECTGATE_SKILL_SELFTEST=PASS', selftest_out)


    def test_qoderwork_adapter_builds_l2_workflow_package(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_qoderwork_') as td:
            out_dir = pathlib.Path(td) / 'qoderwork'
            adapter = ROOT / 'adapters' / 'projectgate_qoderwork_adapter_v0_1' / 'projectgate_qoderwork_adapter.py'
            out = run([
                PY,
                adapter,
                'build',
                '--core-root', ROOT / 'core' / 'projectgate_core_v0_1',
                '--project-pack', ROOT / 'examples' / 'dreamstory_project_pack_v0_1',
                '--root-docs', ROOT,
                '--out', out_dir,
            ])
            self.assertIn('QODERWORK_L2_WORKFLOW_PACKAGE_READY', out)
            zip_path = out_dir / 'qoderwork_skill.zip'
            self.assertTrue(zip_path.exists())
            for name in [
                'SKILL.md',
                'L2_WORKFLOW.md',
                'STAGE_REPORT_TEMPLATE.md',
                'GATE_RESULT_TEMPLATE.md',
                'UNSUPPORTED_GATES.md',
                'PACK_MANIFEST.json',
            ]:
                self.assertTrue((out_dir / name).exists(), name)
            skill_text = (out_dir / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('does not provide native hard enforcement inside QoderWork', skill_text)
            unsupported_text = (out_dir / 'UNSUPPORTED_GATES.md').read_text(encoding='utf-8')
            self.assertIn('UNSUPPORTED_GATE=QODERWORK_NATIVE_CLI_EXECUTION_NOT_CONFIRMED', unsupported_text)
            with zipfile.ZipFile(zip_path) as zf:
                names = set(zf.namelist())
            self.assertIn('SKILL.md', names)
            self.assertIn('L2_WORKFLOW.md', names)
            self.assertIn('UNSUPPORTED_GATES.md', names)
            self.assertIn('references/project/project_manifest.json', names)
            self.assertIn('references/core/workflow/workflow_state_table.json', names)
            self.assertIn('references/core/workflow/projectgate_workflow_validator.py', names)
            self.assertTrue(any(name.startswith('references/core/') for name in names))
            self.assertFalse(any('__pycache__' in name.split('/') or name.endswith('.pyc') for name in names))


    def test_qoderwork_workflow_runner_start_gate_and_delivery(self):
        with tempfile.TemporaryDirectory(prefix='pg_test_qoderwork_runner_') as td:
            scratch = pathlib.Path(td)
            run_root = scratch / 'runs'
            source_pack = ROOT / 'examples' / 'dreamstory_project_pack_v0_1'
            project_pack = scratch / 'dreamstory_project_pack_v0_1'
            shutil.copytree(
                source_pack,
                project_pack,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'Incidents', 'candidates')
            )
            runner = ROOT / 'adapters' / 'projectgate_qoderwork_adapter_v0_1' / 'projectgate_qoderwork_workflow_runner.py'
            out = run([
                PY, runner, 'start',
                '--project-pack', project_pack,
                '--task-type', 'dreamstory_runtime_fact_entry_map',
                '--task-title', 'unit qoderwork runner',
                '-p', 'L',
                '--run-root', run_root,
            ])
            self.assertIn('QODERWORK_RUNNER_START=PASS', out)
            task_line = [line for line in out.splitlines() if line.startswith('TASKRUN=')][0]
            input_line = [line for line in out.splitlines() if line.startswith('QODERWORK_INPUT=')][0]
            taskrun = pathlib.Path(task_line.split('=', 1)[1])
            self.assertTrue(taskrun.exists())
            self.assertTrue(pathlib.Path(input_line.split('=', 1)[1]).exists())

            bad_report = taskrun.parent / 'bad_worker_output.md'
            bad_report.write_text('# bad\n', encoding='utf-8')
            fail_out = run([PY, runner, 'gate', '--taskrun', taskrun, '--stage', 'READONLY_AUDIT', '--input', bad_report], expect=1)
            self.assertIn('QODERWORK_REPAIR_INPUT=', fail_out)
            self.assertFalse((source_pack / 'Incidents').exists(), 'runner test must not write autocapture artifacts into the real DreamStory example pack')
            self.assertFalse((source_pack / 'KnownBugRules' / 'candidates').exists(), 'runner test must not write KnownBugRule candidates into the real DreamStory example pack')
            self.assertFalse((source_pack / 'SOPs' / 'candidates').exists(), 'runner test must not write SOP candidates into the real DreamStory example pack')

            good_report = taskrun.parent / 'good_worker_output.md'
            good_report.write_text(
                '# good\n\n'
                'SOP_USED=runtime_fact_entry_map\n'
                'KNOWN_BUG_RULES_CHECKED=DREAMSTORY-RUNTIME-FACT-SINGLE-ENTRY-001\n'
                'TASKRUN=' + str(taskrun) + '\n'
                'STAGE=READONLY_AUDIT\n\n'
                '## 已确认事实\n- ok\n\n'
                '## 不能确认事实\n- ok\n\n'
                '## 风险点\n- ok\n\n'
                '## 必须停手条件\n- ok\n\n'
                '## 唯一安全下一步\n- ok\n',
                encoding='utf-8'
            )
            pass_out = run([PY, runner, 'gate', '--taskrun', taskrun, '--stage', 'READONLY_AUDIT', '--input', good_report, '--next-stage', 'FACT_COLLECTION'])
            self.assertIn('STAGE_GATE=PASS', pass_out)
            self.assertIn('QODERWORK_NEXT_INPUT=', pass_out)

            delivery_out = run([PY, runner, 'delivery', '--taskrun', taskrun])
            self.assertIn('DELIVERY_CHECK=PASS', delivery_out)
            self.assertIn('QODERWORK_RUNNER_DELIVERY=PASS', delivery_out)


if __name__ == '__main__':
    unittest.main()
