#!/usr/bin/env python3
from __future__ import annotations
import pathlib, runpy, sys
ROOT = pathlib.Path(__file__).resolve().parent
CLI = ROOT / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py'
if not CLI.exists():
    print('RESULT=FAIL')
    print('FAILED_STAGE=PG_ENTRYPOINT')
    print('FAIL_REASON=projectgate_cli.py missing: ' + str(CLI))
    raise SystemExit(1)
sys.argv = ['pg'] + sys.argv[1:]
runpy.run_path(str(CLI), run_name='__main__')
