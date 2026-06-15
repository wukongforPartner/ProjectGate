#!/usr/bin/env python3
from __future__ import annotations
import os
import pathlib
import runpy
import sys


def find_repo_root(start: pathlib.Path | None = None) -> pathlib.Path:
    env_root = os.environ.get('PROJECTGATE_ALPHA_ROOT') or os.environ.get('PROJECTGATE_ROOT')
    if env_root:
        root = pathlib.Path(env_root).resolve()
        if (root / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py').exists():
            return root
        raise RuntimeError('PROJECTGATE_ALPHA_ROOT does not contain ProjectGate runtime: ' + str(root))
    cur = (start or pathlib.Path(__file__).resolve()).resolve()
    for candidate in [cur.parent, *cur.parents]:
        if (candidate / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py').exists():
            return candidate
    raise RuntimeError('Could not locate ProjectGate repo root. Set PROJECTGATE_ALPHA_ROOT.')


def main() -> int:
    try:
        root = find_repo_root()
        cli = root / 'core' / 'projectgate_core_v0_1' / 'runtime' / 'projectgate_cli.py'
        sys.argv = ['pg'] + sys.argv[1:]
        runpy.run_path(str(cli), run_name='__main__')
        return 0
    except SystemExit as exc:
        code = exc.code
        if isinstance(code, int):
            return code
        return 0 if code is None else 1
    except Exception as exc:
        print('RESULT=FAIL')
        print('FAILED_STAGE=PG_PACKAGE_ENTRYPOINT')
        print('FAIL_REASON=' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
